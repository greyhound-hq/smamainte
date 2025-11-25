**VS Code 初回セットアップ**

- Python拡張をインストール
- Node.js と npm をインストール
- `.env` をルートに作成（`.env.example` を参照）
- Python仮想環境を作成して依存をインストール

Commands:

```bash
# backend
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# frontend
cd frontend
npm install
```

Optional: run backend locally

```bash
uvicorn backend.app.main:app --reload --port 8080
```
