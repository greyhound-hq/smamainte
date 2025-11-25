"use client"
import { useState } from 'react'
import { initFirebase, signInAnon } from '../../lib/firebaseClient'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleAnonSignIn() {
    setLoading(true)
    try {
      initFirebase()
      const token = await signInAnon()
      if (token) {
        localStorage.setItem('idToken', token)
        alert('Signed in anonymously (token saved to localStorage)')
      } else {
        alert('Signed in (no token)')
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('auth error', err)
      alert('Auth failed: ' + String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h1>ログイン</h1>
        <p>このサンプルはFirebase Authを想定しています。匿名ログインで簡易認証を行います。</p>
        <label htmlFor="login-email">
          メール (オプション)
        </label>
        <input id="login-email" name="email" type="email" autoComplete="email" aria-label="メールアドレス" value={email} onChange={e => setEmail(e.target.value)} />
        <div style={{marginTop:12}}>
          <button type="button" className="btn btn-primary" aria-label="匿名ログイン" onClick={handleAnonSignIn} disabled={loading}>{loading ? 'Signing...' : '匿名ログイン'}</button>
        </div>
      </div>
    </div>
  )
}
