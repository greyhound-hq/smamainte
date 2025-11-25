import './globals.css'
import Link from 'next/link'

export const metadata = {
  title: 'simple-cmms',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <header className="app-header">
          <div style={{display:'flex', alignItems:'center', gap:8}}>
            <h1 className="app-title">simple-cmms</h1>
          </div>
          <nav className="app-nav">
            <Link href="/">ダッシュボード</Link>
            <Link href="/equipments">設備</Link>
            <Link href="/inspect">点検</Link>
            <Link href="/admin">管理</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  )
}
