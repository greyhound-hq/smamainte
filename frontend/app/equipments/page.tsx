import Link from 'next/link'
import { useSWR } from 'swr'
import axios from 'axios'

const fetcher = (url: string) => axios.get(url).then(r => r.data)

export default function EquipmentsPage() {
  const { data } = useSWR('/api/equipments', fetcher)
  return (
    <div className="container">
      <div className="card">
        <h1>設備一覧</h1>
        {!data && <div>読み込み中...</div>}
        {data && (
          <ul>
            {data.map((e: any) => (
              <li key={e.id}><Link href={`/equipments/${e.id}`}>{e.name}</Link></li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
