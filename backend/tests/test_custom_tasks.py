import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Incident, Task

def test_custom_tasks_and_ai_generation():
    app = create_app()
    client = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()

    print("\n" + "=" * 70)
    print("TEST: AI SUGGESTED TASK & CUSTOM RESPONDER TASK PIPELINE")
    print("=" * 70)

    # 1. Create a test incident
    print("\n--- 1. Submitting test report to create incident ---")
    res_rep = client.post('/reports', json={
        "raw_text": "Flash flood waters rising on Elm Street near 4th Ave, ground floors flooding.",
        "reporter_label": "resident"
    })
    assert res_rep.status_code == 201
    inc_id = res_rep.json['incident']['id']
    print(f"Created Incident #{inc_id}")

    # Mark verified
    client.post(f'/incidents/{inc_id}/verify')

    # 2. Test AI Suggested Task Generation
    print("\n--- 2. Testing AI Suggested Task Generation ---")
    res_ai_task = client.post(f'/incidents/{inc_id}/tasks/generate')
    assert res_ai_task.status_code == 201
    ai_task = res_ai_task.json
    desc = ai_task['description']
    print(f"AI Generated Task: #{ai_task['id']} - \"{desc}\"")
    # Verify description is not a weird 1-word or truncated response
    word_count = len(desc.split())
    print(f"AI Task Word Count: {word_count}")
    assert word_count >= 4, f"AI task should be a descriptive phrase, got: '{desc}'"
    assert ai_task['status'] == 'open'
    assert ai_task['incident_id'] == inc_id

    # 3. Test Custom Task Creation (Success)
    print("\n--- 3. Testing Custom Task Creation (POST /incidents/:id/tasks) ---")
    custom_desc = "Coordinate 2 inflatable dinghies at Elm St North intersection"
    res_custom = client.post(f'/incidents/{inc_id}/tasks', json={
        "description": custom_desc,
        "claimed_by": "Volunteer Rescue Group A"
    })
    assert res_custom.status_code == 201
    custom_task = res_custom.json
    print(f"Custom Task Created: #{custom_task['id']} - \"{custom_task['description']}\"")
    assert custom_task['description'] == custom_desc
    assert custom_task['incident_id'] == inc_id
    assert custom_task['claimed_by'] == "Volunteer Rescue Group A"
    custom_task_id = custom_task['id']

    # 4. Test Custom Task Creation with Empty Description (400)
    print("\n--- 4. Testing Validation: Empty Description returns 400 ---")
    res_empty = client.post(f'/incidents/{inc_id}/tasks', json={"description": "   "})
    assert res_empty.status_code == 400
    print(f"Empty description rejected correctly: {res_empty.json}")

    # 5. Test Non-Existent Incident (404)
    print("\n--- 5. Testing Validation: Non-existent Incident returns 404 ---")
    res_404 = client.post('/incidents/99999/tasks', json={"description": "Some task"})
    assert res_404.status_code == 404
    print("Non-existent incident rejected correctly with 404.")

    # 6. Test Claiming the Custom Task
    print(f"\n--- 6. Testing Claiming Custom Task #{custom_task_id} ---")
    res_claim = client.post(f'/tasks/{custom_task_id}/claim', json={
        "claimed_by": "Red Cross Team Beta"
    })
    assert res_claim.status_code == 200
    assert res_claim.json['status'] == 'claimed'
    assert res_claim.json['claimed_by'] == 'Red Cross Team Beta'
    print(f"Task #{custom_task_id} claimed: {res_claim.json['claimed_by']}")

    # 7. Test Incident Detail View contains both tasks
    print(f"\n--- 7. Verifying Incident #{inc_id} reflects both tasks ---")
    res_detail = client.get(f'/incidents/{inc_id}')
    assert res_detail.status_code == 200
    tasks = res_detail.json['tasks']
    print(f"Total tasks linked to Incident #{inc_id}: {len(tasks)}")
    assert len(tasks) == 2
    task_descriptions = [t['description'] for t in tasks]
    assert custom_desc in task_descriptions
    assert desc in task_descriptions

    print("\n" + "*" * 70)
    print("ALL CUSTOM TASK & AI GENERATION TESTS PASSED PERFECTLY!")
    print("*" * 70)

if __name__ == '__main__':
    test_custom_tasks_and_ai_generation()

