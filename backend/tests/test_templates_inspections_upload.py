import json

def test_templates_inspections_and_upload(client, monkeypatch):
    # 1) create a template
    tmpl_payload = {
        "equipment_type": "pump",
        "item_name": "Check valve",
        "item_type": "ok_ng",
        "order_index": 1
    }
    r = client.post('/templates', json=tmpl_payload)
    assert r.status_code == 200
    tmpl = r.json()
    assert tmpl['equipment_type'] == 'pump'
    assert 'id' in tmpl

    tmpl_id = tmpl['id']

    # 2) list templates for type
    r2 = client.get('/templates/pump')
    assert r2.status_code == 200
    templates = r2.json()
    assert any(t['id'] == tmpl_id for t in templates)

    # 3) create an equipment to inspect
    eq_payload = {"name": "Pump B", "model": "PB-2", "location": "Basement"}
    r3 = client.post('/equipments', json=eq_payload)
    assert r3.status_code == 200
    eq = r3.json()
    eq_id = eq['id']

    # 4) create an inspection record
    ins_payload = {
        "equipment_id": eq_id,
        "template_item_id": tmpl_id,
        "status": "OK",
        "numeric_value": None,
        "photo_url": None,
        "comment": "all good"
    }
    r4 = client.post('/inspections', json=ins_payload)
    assert r4.status_code == 200
    ins = r4.json()
    assert ins['equipment_id'] == eq_id

    # 5) retrieve inspections for equipment
    r5 = client.get(f'/inspections/{eq_id}')
    assert r5.status_code == 200
    found = any(i['id'] == ins['id'] for i in r5.json())
    assert found

    # 6) test upload-url endpoint with GCS signer mocked
    import app.main as main_module

    def fake_signed_url(bucket, blob_name, expiration=900):
        return f"https://signed.example/{blob_name}"

    monkeypatch.setattr(main_module, 'generate_v4_put_object_signed_url', fake_signed_url)

    r6 = client.post('/upload-url', json={"filename": "abc.jpg"})
    assert r6.status_code == 200
    body = r6.json()
    assert 'upload_url' in body and 'public_url' in body
    assert body['upload_url'].startswith('https://signed.example')
