import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Incident, Report, Task

def verify_e2e_flow():
    app = create_app()
    client = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()

    # Step 1: Resident submits report
    res_post = client.post('/reports', json={
        "raw_text": "Severe mudslide blocking Canyon Road, 2 vehicles trapped.",
        "reporter_label": "resident"
    })
    assert res_post.status_code == 201
    inc_id = res_post.json['incident']['id']

    # Step 2: Public-facing view confirms initial state
    res_pub1 = client.get('/incidents')
    assert res_pub1.status_code == 200
    assert res_pub1.json[0]['id'] == inc_id
    assert res_pub1.json[0]['verification_state'] == 'unverified'
    print(f"Initial public state confirmed: {res_pub1.json[0]['verification_state']}")

    # Step 3: Responder marks VERIFIED
    res_verify = client.post(f'/incidents/{inc_id}/verify')
    assert res_verify.status_code == 200

    # Step 4: Confirm public view reflects 'verified' after refresh
    res_pub2 = client.get('/incidents')
    assert res_pub2.json[0]['verification_state'] == 'verified'
    print(f"Public state after responder verification: {res_pub2.json[0]['verification_state']}")

    # Step 5: Responder generates task & claims it
    res_task = client.post(f'/incidents/{inc_id}/tasks/generate')
    assert res_task.status_code == 201
    task_id = res_task.json['id']

    res_claim = client.post(f'/tasks/{task_id}/claim', json={"claimed_by": "Highway Patrol"})
    assert res_claim.status_code == 200

    # Step 6: Public detail view confirms task presence
    res_detail = client.get(f'/incidents/{inc_id}')
    assert len(res_detail.json['tasks']) == 1
    assert res_detail.json['tasks'][0]['status'] == 'claimed'
    print(f"Public detail view confirmed task: {res_detail.json['tasks'][0]['description']} (Status: {res_detail.json['tasks'][0]['status']})")

    # Step 7: Responder disputes
    res_dispute = client.post(f'/incidents/{inc_id}/dispute')
    assert res_dispute.status_code == 200

    # Step 8: Confirm public view reflects 'disputed' after refresh
    res_pub3 = client.get('/incidents')
    assert res_pub3.json[0]['verification_state'] == 'disputed'
    print(f"Public state after responder dispute: {res_pub3.json[0]['verification_state']}")

    print("\nE2E VERIFICATION: Public-facing incident view accurately reflects all responder state changes after refresh!")

if __name__ == '__main__':
    verify_e2e_flow()

