# Supabase Setup Guide

このガイドでは、Supabase を使用して認証・データベース・ストレージを設定する方法を説明します。

## 1. Supabase プロジェクトの作成

1. [Supabase Console](https://supabase.com/dashboard) にアクセス
2. 「New Project」をクリック
3. プロジェクト名・データベースパスワードを設定
4. リージョンを選択（日本の場合は `Northeast Asia (Tokyo)` 推奨）
5. プロジェクトが作成されるまで数分待機

## 2. データベーススキーマの作成

Supabase Dashboard > **SQL Editor** で以下を実行：

```sql
-- Equipments table
CREATE TABLE equipments (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  model VARCHAR(200),
  location VARCHAR(200),
  photo_url VARCHAR(1000),
  qr_code_url VARCHAR(1000),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

-- Check templates table
CREATE TABLE check_templates (
  id SERIAL PRIMARY KEY,
  equipment_type VARCHAR(200) NOT NULL,
  item_name VARCHAR(200) NOT NULL,
  item_type VARCHAR(50) NOT NULL,
  order_index INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inspection records table
CREATE TABLE inspection_records (
  id SERIAL PRIMARY KEY,
  equipment_id INT REFERENCES equipments(id) NOT NULL,
  template_item_id INT REFERENCES check_templates(id),
  status VARCHAR(10),
  numeric_value FLOAT,
  photo_url VARCHAR(1000),
  comment TEXT,
  reported_by VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  display_name VARCHAR(200),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_inspection_equipment ON inspection_records(equipment_id);
CREATE INDEX idx_inspection_created ON inspection_records(created_at DESC);
```

## 3. Row Level Security (RLS) の設定

認証されたユーザーのみがデータにアクセスできるようにします：

```sql
-- Enable RLS on all tables
ALTER TABLE equipments ENABLE ROW LEVEL SECURITY;
ALTER TABLE check_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspection_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read/write
CREATE POLICY "Allow authenticated access" ON equipments
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated access" ON check_templates
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated access" ON inspection_records
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated access" ON users
  FOR ALL USING (auth.role() = 'authenticated');
```

## 4. Storage バケットの作成

Supabase Dashboard > **Storage** で：

1. 「New bucket」をクリック
2. バケット名: `inspection-images`
3. Public bucket: ✓（チェックを入れる）
4. 「Create bucket」をクリック

### Storage ポリシーの設定

`inspection-images` バケットで以下のポリシーを追加：

```sql
-- Allow authenticated users to upload
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'inspection-images');

-- Allow public read access
CREATE POLICY "Allow public read"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'inspection-images');
```

## 5. 認証の設定

Supabase Dashboard > **Authentication** > **Providers**:

1. **Email** を有効化
2. 「Confirm email」を無効化（開発中のみ、本番では有効推奨）
3. その他のプロバイダー（Google, GitHub など）も必要に応じて有効化

## 6. フロントエンド環境変数の設定

Supabase Dashboard > **Settings** > **API** から以下を取得：

### `frontend/.env.local` を作成：

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 7. バックエンド環境変数の設定

Supabase Dashboard > **Settings** > **API** > **JWT Settings** から `JWT Secret` を取得：

### `backend/.env` を作成：

```bash
DATABASE_URL=postgresql://postgres:your-password@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
GCS_BUCKET=your-gcs-bucket
GCP_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
SUPABASE_JWT_SECRET=your-jwt-secret-here
ADMIN_EMAILS=admin@example.com
ADMIN_UIDS=
SECRET_KEY=changeme
ALLOW_ORIGINS=http://localhost:3000
```

**注意**: `DATABASE_URL` は Supabase の PostgreSQL 接続文字列を使用できますが、このアプリは FastAPI + SQLAlchemy で独自のバックエンドを持つため、Supabase の Database を直接使うか、既存の PostgreSQL を使うかを選択できます。

## 8. 型定義の自動生成（オプション）

Supabase CLI をインストールして型定義を自動生成：

```bash
npm install -g supabase
supabase login
supabase link --project-ref your-project-ref
supabase gen types typescript --local > frontend/types/supabase.ts
```

## 9. ローカル開発の起動

### バックエンド：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### フロントエンド：

```bash
cd frontend
npm install
npm run dev
```

## 10. テスト

### 1. アカウント登録

1. http://localhost:3000/login を開く
2. メールアドレスとパスワードを入力
3. 「アカウント登録に切り替え」をクリック
4. 「登録」をクリック

### 2. ログイン

1. 登録したメールアドレスとパスワードでログイン
2. localStorage に `authToken` が保存されることを確認

### 3. 写真アップロード

1. http://localhost:3000/inspect を開く
2. Equipment ID を入力
3. 写真をアップロード
4. Supabase Storage > `inspection-images` バケットに画像が保存されることを確認

## 11. GitHub Actions の設定（CI/CD）

GitHub リポジトリの **Settings** > **Secrets and variables** > **Actions** で以下を追加：

| Secret Name | Value |
|-------------|-------|
| `SUPABASE_JWT_SECRET` | JWT Secret from Supabase Dashboard |
| `DATABASE_URL` | PostgreSQL connection string |
| `ADMIN_EMAILS` | `admin@example.com` |

`.github/workflows/staging-verify.yml` の該当箇所を更新：

```yaml
- name: Start backend
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    SUPABASE_JWT_SECRET: ${{ secrets.SUPABASE_JWT_SECRET }}
    ADMIN_EMAILS: ${{ secrets.ADMIN_EMAILS }}
  run: |
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
```

## 12. 本番デプロイ（Cloud Run）

### バックエンド：

```bash
# Dockerfile に環境変数を注入
gcloud run deploy smamainte-backend \
  --source . \
  --region asia-northeast1 \
  --set-env-vars="DATABASE_URL=$DATABASE_URL,SUPABASE_JWT_SECRET=$SUPABASE_JWT_SECRET,ADMIN_EMAILS=$ADMIN_EMAILS"
```

### フロントエンド（Vercel 推奨）：

```bash
# Vercel にデプロイ
vercel --prod
# Environment variables を Vercel Dashboard で設定
```

## トラブルシューティング

### "Invalid auth token" (401)

- JWT Secret が正しく設定されているか確認
- トークンの有効期限が切れていないか確認（Supabase のトークンは1時間有効）

### "Admin privileges required" (403)

- `ADMIN_EMAILS` にログインユーザーのメールアドレスが含まれているか確認
- バックエンドの `.env` を再読み込み（uvicorn を再起動）

### Storage アップロードエラー

- バケット名が `inspection-images` であることを確認
- Storage ポリシーが正しく設定されているか確認
- Public bucket が有効になっているか確認

## 参考リンク

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Auth](https://supabase.com/docs/guides/auth)
- [Supabase Storage](https://supabase.com/docs/guides/storage)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
