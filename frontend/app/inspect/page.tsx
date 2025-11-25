"use client"
import { useState, useEffect } from 'react'
import axios from 'axios'
import { useSearchParams } from 'next/navigation'

type Item = { id: number; item_name: string; item_type: string }

export default function InspectPage() {
  const searchParams = useSearchParams()
  const qEquipment = searchParams?.get('equipment_id') || ''
  const [equipmentId, setEquipmentId] = useState(qEquipment)
  const [items, setItems] = useState<Item[]>([])
  const [responses, setResponses] = useState<Record<number, any>>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (qEquipment) setEquipmentId(qEquipment)
  }, [qEquipment])

  async function loadTemplate() {
    if (!equipmentId) return alert('equipment_id を入力またはQRで読み取ってください')
    try {
      // For simplicity, templates are read by a default type or you can map by equipment
      const r = await axios.get(`/api/templates/default`)
      setItems(r.data)
      // init responses
      const init: Record<number, any> = {}
      r.data.forEach((it: Item) => init[it.id] = { status: it.item_type === 'ok_ng' ? 'OK' : null, numeric_value: null, photo_url: null })
      setResponses(init)
    } catch (e) {
      alert('テンプレートの読み込みに失敗しました')
    }
  }

  async function handleFileSelect(itemId: number, file: File) {
    if (!file) return
    const filename = `inspection_${equipmentId}_${itemId}_${Date.now()}.jpg`
    try {
      const r = await axios.post('/api/upload-url', { filename })
      const { upload_url, public_url } = r.data
      // PUT the file to signed URL
      await fetch(upload_url, {
        method: 'PUT',
        headers: { 'Content-Type': file.type || 'application/octet-stream' },
        body: file,
      })
      setResponses(prev => ({ ...prev, [itemId]: { ...prev[itemId], photo_url: public_url } }))
    } catch (e) {
      console.error(e)
      alert('写真アップロードに失敗しました')
    }
  }

  async function submitInspection() {
    if (!equipmentId) return alert('equipment_id が必要です')
    setLoading(true)
    try {
      for (const it of items) {
        const resp = responses[it.id] || {}
        const payload: any = {
          equipment_id: Number(equipmentId),
          template_item_id: it.id,
          status: resp.status ?? null,
          numeric_value: resp.numeric_value ?? null,
          photo_url: resp.photo_url ?? null,
          comment: resp.comment ?? null,
        }
        await axios.post('/api/inspections', payload)
      }
      alert('点検データを送信しました')
      // optionally reset
      setItems([])
      setResponses({})
    } catch (e) {
      console.error(e)
      alert('点検データの送信に失敗しました')
    }
    setLoading(false)
  }

  return (
    <div className="container">
      <div className="card">
        <h1>点検実施（モバイル向け）</h1>
        <label>
          equipment_id（QRから読み取ったID）
          <input value={equipmentId} onChange={(e) => setEquipmentId(e.target.value)} />
        </label>
        <div style={{ marginTop: 8 }}>
          <button className="btn btn-primary" onClick={loadTemplate}>テンプレート読み込み</button>
        </div>

        <div style={{ marginTop: 16 }}>
          {items.length === 0 && <div>テンプレートを読み込んでください</div>}
          {items.map((it) => (
            <div key={it.id} className="item-card inspect-item">
              <div><strong>{it.item_name}</strong> ({it.item_type})</div>
              {it.item_type === 'ok_ng' && (
                <div>
                  <label htmlFor={`select-${it.id}`} style={{display:'block', fontSize:14, marginBottom:6}}>判定</label>
                  <select id={`select-${it.id}`} value={responses[it.id]?.status ?? 'OK'} onChange={(e) => setResponses(prev => ({ ...prev, [it.id]: { ...prev[it.id], status: e.target.value } }))}>
                    <option value="OK">OK</option>
                    <option value="NG">NG</option>
                  </select>
                </div>
              )}
              {it.item_type === 'numeric' && (
                <div>
                  <label htmlFor={`num-${it.id}`} style={{display:'block', fontSize:14, marginBottom:6}}>値</label>
                  <input id={`num-${it.id}`} type="number" value={responses[it.id]?.numeric_value ?? ''} onChange={(e) => setResponses(prev => ({ ...prev, [it.id]: { ...prev[it.id], numeric_value: e.target.value ? Number(e.target.value) : null } }))} />
                </div>
              )}
              <div style={{ marginTop: 8 }}>
                <label htmlFor={`file-${it.id}`} style={{display:'block', fontSize:14, marginBottom:6}}>写真を撮影 / 選択</label>
                <input id={`file-${it.id}`} aria-label={`写真アップロード ${it.item_name}`} type="file" accept="image/*" capture="environment" onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFileSelect(it.id, f) }} />
                {responses[it.id]?.photo_url && <div><small>写真: </small><img src={responses[it.id].photo_url} className="responsive" style={{ width: 120 }} alt={`点検写真 — ${it.item_name}`} /></div>}
              </div>
              <div style={{ marginTop: 8 }}>
                <label htmlFor={`comment-${it.id}`} style={{display:'block', fontSize:14, marginBottom:6}}>コメント（任意）</label>
                <textarea id={`comment-${it.id}`} placeholder="コメント" value={responses[it.id]?.comment ?? ''} onChange={(e) => setResponses(prev => ({ ...prev, [it.id]: { ...prev[it.id], comment: e.target.value } }))} />
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 10 }}>
          <button className="btn btn-primary" onClick={submitInspection} disabled={loading || items.length === 0}>{loading ? '送信中...' : '点検を送信'}</button>
        </div>
      </div>
    </div>
  )
}
