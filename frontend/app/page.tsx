import Link from 'next/link'
"use client"
import useSWR from 'swr'
import axios from 'axios'

const fetcher = (url: string) => axios.get(url).then(r => r.data)

export default function Dashboard() {
  const { data, error } = useSWR('/api/dashboard', fetcher)

  return (
    <div className="container">
      <div className="card">
        <h1>ダッシュボード</h1>
        <p><Link href="/login">ログイン</Link> · <Link href="/equipments">設備一覧</Link></p>
        {error && <div>エラー</div>}
        {!data && <div>読み込み中...</div>}
        {data && (
          <>
            <h2>KPI</h2>
            <div className="kpi-row">
              <div className="kpi"><div className="label">今日の点検予定</div><div className="val">{data.kpi.today_total}</div></div>
              <div className="kpi"><div className="label">完了数</div><div className="val">{data.kpi.ok}</div></div>
              <div className="kpi"><div className="label">NG件数</div><div className="val">{data.kpi.ng}</div></div>
            </div>
            <h2 style={{marginTop:16}}>設備の最新ステータス</h2>
            <ul>
              {data.latest_status.map((e: any) => (
                <li key={e.equipment_id}>{e.name} — {e.status}</li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  )
}
