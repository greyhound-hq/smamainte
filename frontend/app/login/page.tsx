"use client"
import { useState } from 'react'
import { signInWithEmail, signUpWithEmail, getAuthToken } from '../../lib/supabaseClient'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [isSignUp, setIsSignUp] = useState(false)
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!email || !password) {
      alert('メールアドレスとパスワードを入力してください')
      return
    }

    setLoading(true)
    try {
      if (isSignUp) {
        await signUpWithEmail(email, password)
        alert('登録しました。確認メールをチェックしてください。')
      } else {
        await signInWithEmail(email, password)
        const token = await getAuthToken()
        if (token) {
          localStorage.setItem('authToken', token)
          alert('ログインしました')
          router.push('/')
        }
      }
    } catch (err: any) {
      console.error('auth error', err)
      alert('認証エラー: ' + (err.message || String(err)))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h1>{isSignUp ? 'アカウント登録' : 'ログイン'}</h1>
        <p>Supabase Auth でメール＋パスワード認証を行います。</p>
        <form onSubmit={handleSubmit}>
          <label htmlFor="login-email">
            メールアドレス
          </label>
          <input
            id="login-email"
            name="email"
            type="email"
            autoComplete="email"
            aria-label="メールアドレス"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
          />
          <label htmlFor="login-password" style={{ marginTop: 12 }}>
            パスワード
          </label>
          <input
            id="login-password"
            name="password"
            type="password"
            autoComplete="current-password"
            aria-label="パスワード"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
          <div style={{ marginTop: 16 }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? '処理中...' : isSignUp ? '登録' : 'ログイン'}
            </button>
          </div>
        </form>
        <div style={{ marginTop: 16 }}>
          <button
            type="button"
            className="btn"
            onClick={() => setIsSignUp(!isSignUp)}
            disabled={loading}
          >
            {isSignUp ? 'ログインに切り替え' : 'アカウント登録に切り替え'}
          </button>
        </div>
      </div>
    </div>
  )
}
