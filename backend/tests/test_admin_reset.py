import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Incident

def test_admin_reset_endpoint():
    app = create_app()
    client = app.test_client()

    print("\n" + "=" * 70)
    print("TEST: ADMIN RESET-DB ENDPOINT AUTHENTICATION & RESEEDING")
    print("=" * 70)

    # 1. Test when ADMIN_RESET_TOKEN is not configured in env
    if 'ADMIN_RESET_TOKEN' in os.environ:
        del os.environ['ADMIN_RESET_TOKEN']

    print("\n--- 1. Testing unconfigured ADMIN_RESET_TOKEN (Should return 401) ---")
    res_unconfigured = client.post('/admin/reset-db')
    assert res_unconfigured.status_code == 401
    assert "not configured" in res_unconfigured.json['error']
    print(f"Unconfigured token rejected correctly: {res_unconfigured.json}")

    # Set secret token for remaining tests
    SECRET = "test-secret-token-2026"
    os.environ['ADMIN_RESET_TOKEN'] = SECRET

    # 2. Test request with missing token
    print("\n--- 2. Testing missing token (Should return 401) ---")
    res_missing = client.post('/admin/reset-db')
    assert res_missing.status_code == 401
    assert "Unauthorized" in res_missing.json['error']
    print(f"Missing token rejected correctly: {res_missing.json}")

    # 3. Test request with invalid token
    print("\n--- 3. Testing wrong token (Should return 401) ---")
    res_wrong = client.post('/admin/reset-db', headers={'X-Admin-Token': 'wrong-token'})
    assert res_wrong.status_code == 401
    print(f"Wrong token rejected correctly: {res_wrong.json}")

    # 4. Test request with valid X-Admin-Token header
    print("\n--- 4. Testing valid X-Admin-Token header (Should return 200 & reseed) ---")
    res_header = client.post('/admin/reset-db', headers={'X-Admin-Token': SECRET})
    assert res_header.status_code == 200
    assert res_header.json['status'] == 'ok'
    print(f"Reset via header successful: {res_header.json}")

    # Verify database was reseeded
    with app.app_context():
        count = Incident.query.count()
        assert count == 5, f"Expected 5 seeded incidents, got {count}"
        print(f"Verified {count} benchmark incidents in database.")

    # 5. Test request with valid query param (?token=...)
    print("\n--- 5. Testing valid ?token= query parameter (Should return 200) ---")
    res_query = client.post(f'/admin/reset-db?token={SECRET}')
    assert res_query.status_code == 200
    assert res_query.json['status'] == 'ok'
    print(f"Reset via query parameter successful: {res_query.json}")

    # 6. Test request with Authorization: Bearer <token>
    print("\n--- 6. Testing valid Authorization: Bearer header (Should return 200) ---")
    res_bearer = client.post('/admin/reset-db', headers={'Authorization': f'Bearer {SECRET}'})
    assert res_bearer.status_code == 200
    assert res_bearer.json['status'] == 'ok'
    print(f"Reset via Bearer token successful: {res_bearer.json}")

    print("\n" + "*" * 70)
    print("ALL ADMIN RESET-DB TESTS PASSED PERFECTLY!")
    print("*" * 70)

if __name__ == '__main__':
    test_admin_reset_endpoint()

