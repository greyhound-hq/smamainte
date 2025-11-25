import useSWR from '../../../lib/useSWR'
import axios from 'axios'

const fetcher = (url: string) => axios.get(url).then(r => r.data)

export default function EquipmentDetail({ params }: { params: { id: string } }) {
  const { data } = useSWR(`/api/equipments/${params.id}`, fetcher)
  const { data: recs } = useSWR(`/api/inspections/${params.id}`, fetcher)

  return (
    <div className="container">
      <div className="card">
        <h1>設備詳細</h1>
        {!data && <div>読み込み中...</div>}
        {data && (
          <div>
            <h2>{data.name}</h2>
            <p>モデル: {data.model}</p>
            <p>場所: {data.location}</p>
            {data.qr_code_url && <img src={data.qr_code_url} alt={`QRコード — ${data.name}`} style={{width:200}} className="responsive" />}
          </div>
        )}

        <h3 style={{marginTop:12}}>最新点検履歴</h3>
        {!recs && <div>読み込み中...</div>}
        {recs && (
          <ul>
            {recs.map((r: any) => (
              <li key={r.id}>{r.timestamp} — {r.status || r.numeric_value || '—'}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
