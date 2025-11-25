import useSWR from 'swr'
import axios from 'axios'

const fetcher = (url: string) => axios.get(url).then(r=>r.data)

export default function AdminPage(){
  const {data} = useSWR('/api/equipments', fetcher)

  async function exportCsv(){
    const res = await axios.get('/api/inspections')
    const csv = 'id,equipment_id,template_item_id,status,numeric_value,photo_url,comment,timestamp\n' +
      res.data.map((r:any)=>[r.id,r.equipment_id,r.template_item_id,r.status,r.numeric_value,r.photo_url, '"'+(r.comment||'')+'"', r.timestamp].join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'inspections.csv'
    a.click()
  }

  return (
    <div className="container">
      <div className="card">
        <h1>管理画面</h1>
        <button className="btn btn-primary" onClick={exportCsv}>CSVエクスポート（簡易）</button>
        <h2 style={{marginTop:12}}>設備一覧</h2>
        {!data && <div>読み込み中...</div>}
        {data && <ul>{data.map((e:any)=>(<li key={e.id}>{e.name}</li>))}</ul>}
      </div>
    </div>
  )
}
