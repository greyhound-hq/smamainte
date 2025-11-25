def test_create_and_list_equipment(client):
    payload = {"name": "Pump A", "model": "P-1", "location": "Floor 1"}
    r = client.post('/equipments', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data['name'] == 'Pump A'
    assert 'id' in data

    eq_id = data['id']
    r2 = client.get(f'/equipments/{eq_id}')
    assert r2.status_code == 200
    assert r2.json()['id'] == eq_id

    r3 = client.get('/equipments')
    assert r3.status_code == 200
    found = any(e['id'] == eq_id for e in r3.json())
    assert found
