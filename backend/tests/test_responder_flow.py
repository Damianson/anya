import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Incident, Report, Task

def test_responder_flow():
    app = create_app()
    client = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()

    print("--- 1. Submitting new report ---")
    res = client.post('/reports', json={
        "raw_text": "Flash flood waters rising on Elm Street near 4th Ave, ground floors flooding.",
        "reporter_label": "resident"
    })
    assert res.status_code == 201
    inc_id = res.json['incident']['id']
    print(f"Created Incident #{inc_id} with initial state: {res.json['incident']['verification_state']}")
    assert res.json['incident']['verification_state'] == 'unverified'

    print(f"\n--- 2. Responder marks Incident #{inc_id} as VERIFIED ---")
    res_verify = client.post(f'/incidents/{inc_id}/verify')
    print(f"Status: {res_verify.status_code}, Verification State: {res_verify.json['verification_state']}")
    assert res_verify.status_code == 200
    assert res_verify.json['verification_state'] == 'verified'

    print(f"\n--- 3. Generate suggested task for verified Incident #{inc_id} ---")
    res_task = client.post(f'/incidents/{inc_id}/tasks/generate')
    print(f"Status: {res_task.status_code}")
    task_data = res_task.json
    print(f"Task Generated: #{task_data['id']} - \"{task_data['description']}\" [Status: {task_data['status']}]")
    assert res_task.status_code == 201
    assert task_data['status'] == 'open'
    assert task_data['incident_id'] == inc_id
    task_id = task_data['id']

    print(f"\n--- 4. Responder claims Task #{task_id} ---")
    res_claim = client.post(f'/tasks/{task_id}/claim', json={"claimed_by": "Search & Rescue Unit 4"})
    print(f"Status: {res_claim.status_code}")
    claimed_data = res_claim.json
    print(f"Claimed Task Status: {claimed_data['status']}, Claimed By: {claimed_data['claimed_by']}")
    assert res_claim.status_code == 200
    assert claimed_data['status'] == 'claimed'
    assert claimed_data['claimed_by'] == 'Search & Rescue Unit 4'

    print(f"\n--- 5. Responder marks Incident #{inc_id} as DISPUTED ---")
    res_dispute = client.post(f'/incidents/{inc_id}/dispute')
    print(f"Status: {res_dispute.status_code}, Verification State: {res_dispute.json['verification_state']}")
    assert res_dispute.status_code == 200
    assert res_dispute.json['verification_state'] == 'disputed'

    print("\n--- 6. Public list verification (GET /incidents) ---")
    res_list = client.get('/incidents')
    assert res_list.status_code == 200
    incidents = res_list.json
    print(f"Incident in list state: {incidents[0]['verification_state']}")
    print(f"Incident tasks count: {len(incidents[0]['tasks'])}")
    assert incidents[0]['verification_state'] == 'disputed'
    assert len(incidents[0]['tasks']) == 1
    assert incidents[0]['tasks'][0]['status'] == 'claimed'

    print("\nALL RESPONDER VERIFICATION & TASK FLOW TESTS PASSED!")

if __name__ == '__main__':
    test_responder_flow()

