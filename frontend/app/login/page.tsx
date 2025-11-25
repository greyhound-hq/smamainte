"use client"
import { useState } from 'react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  return (
    <div className="container">
      <div className="card">
        <h1>ログイン</h1>
        <p>このサンプルはFirebase Authを想定しています。実装は最小限。</p>
        <label>
          メール
          <input value={email} onChange={e => setEmail(e.target.value)} />
        </label>
        <div style={{marginTop:12}}>
          <button className="btn btn-primary" onClick={() => alert('Stub: implement Firebase auth')}>ログイン</button>
        </div>
      </div>
    </div>
  )
}
