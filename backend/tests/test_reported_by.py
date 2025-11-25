from fastapi.testclient import TestClient
from app.main import app


def test_reported_by_fallback_dev(client: TestClient):
    # Create equipment first
    resp = client.post('/equipments', json={'name': 'Pump A'})
    assert resp.status_code == 200
    eq = resp.json()

    payload = {
        'equipment_id': eq['id'],
        'status': 'OK',
        'comment': 'Checked by dev fallback'
    }
    r = client.post('/inspections', json=payload)
    assert r.status_code == 200
    rec = r.json()
    # When no Authorization header is provided, auth.get_current_user returns dev-anonymous
    assert 'reported_by' in rec
    assert rec['reported_by'] == 'dev-anonymous'


def test_reported_by_with_token(client: TestClient):
    # Create equipment
    resp = client.post('/equipments', json={'name': 'Pump B'})
    assert resp.status_code == 200
    eq = resp.json()

    payload = {
        'equipment_id': eq['id'],
        'status': 'NG',
        'comment': 'Checked with token'
    }
    # Provide a fake token string; backend fallback will accept it and produce a dev uid
    headers = {'Authorization': 'Bearer faketoken1234'}
    r = client.post('/inspections', json=payload, headers=headers)
    assert r.status_code == 200
    rec = r.json()
    assert 'reported_by' in rec
    assert rec['reported_by'].startswith('dev-')
