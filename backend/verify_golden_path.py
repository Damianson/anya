"""
Golden Path End-to-End Verification Script for Anya.
Tests the full lifecycle sequentially against the seeded Nigerian crisis database:
1. Report submission
2. AI extraction & deduplication matching (links to existing Lekki-Epe flood)
3. Conflict detection on a second report (flags dispute)
4. Human First Responder verification (POST /incidents/:id/verify)
5. AI-assisted task generation (POST /incidents/:id/tasks/generate)
6. Human task claiming (POST /tasks/:id/claim)
7. Public view synchronization check (GET /incidents and GET /incidents/:id)
"""

import os
import sys
import json

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from seed_db import seed_database

def run_golden_path():
    print("\n" + "=" * 70)
    print("STEP 0: RESEEDING DATABASE TO KNOWN NIGERIAN BENCHMARK STATE")
    print("=" * 70)
    seed_database()

    app = create_app()
    client = app.test_client()

    print("\n" + "=" * 70)
    print("STEP 1 & 2: INBOUND REPORT -> AI EXTRACTION & DEDUPLICATION MATCHING")
    print("=" * 70)
    report_text = "Flood level along Lekki-Epe by Ajah roundabout is now reaching vehicle engines, more families calling for help."
    print(f"Submitting Inbound Report:\n\"{report_text}\"")

    res_report = client.post('/reports', json={
        "raw_text": report_text,
        "reporter_label": "resident",
        "location_text": "Ajah Roundabout, Lekki-Epe Expressway"
    })
    
    assert res_report.status_code == 201, f"Report submission failed: {res_report.status_code}"
    report_json = res_report.json
    ai_analysis = report_json['ai']

    print(f"\nAI Triage Status: {ai_analysis['status']}")
    print(f"Match Decision: {ai_analysis['match_decision']}")
    print(f"Matched Incident ID: {ai_analysis['matched_incident_id']}")
    print(f"Has Contradiction: {ai_analysis['has_contradiction']}")
    print(f"Extracted Incident Type: {ai_analysis['extracted']['incident_type']}")
    print(f"Extracted Location: {ai_analysis['extracted']['location']}")
    print(f"Linked Report ID #{report_json['report']['id']} -> Incident #{report_json['report']['incident_id']}")

    # Verification of deduplication
    assert ai_analysis['match_decision'] == 'MATCH', "Expected AI to MATCH existing Lekki-Epe flood incident"
    assert ai_analysis['matched_incident_id'] == 1, "Expected AI to match Incident #1"
    assert report_json['report']['incident_id'] == 1, "Report should be linked to Incident #1"
    assert ai_analysis['has_contradiction'] is False, "Expected no contradiction on this corroborating report"
    print(">> STEP 1 & 2 PASSED: Report successfully matched and linked to Incident #1 without creating a duplicate!")

    print("\n" + "=" * 70)
    print("STEP 3: CONFLICT REPORT -> CONTRADICTION DETECTION")
    print("=" * 70)
    conflict_text = "Lagos Water Corporation has completely fixed the pipe on Isaac John Street, the sidewalk is 100% dry and clear."
    print(f"Submitting Contradictory Report for Incident #4:\n\"{conflict_text}\"")

    res_conflict = client.post('/reports', json={
        "raw_text": conflict_text,
        "reporter_label": "resident"
    })
    assert res_conflict.status_code == 201
    conflict_json = res_conflict.json
    ai_conflict = conflict_json['ai']

    print(f"Conflict AI Decision: {ai_conflict['match_decision']}")
    print(f"Matched Incident ID: {ai_conflict['matched_incident_id']}")
    print(f"Has Contradiction: {ai_conflict['has_contradiction']}")
    print(f"Contradiction Reason: {ai_conflict['contradiction_reason']}")
    print(f"Incident Verification State: {conflict_json['incident']['verification_state']}")

    assert ai_conflict['match_decision'] == 'MATCH', "Expected AI to match Isaac John pipe incident"
    assert ai_conflict['matched_incident_id'] == 4, "Expected AI to match Incident #4"
    assert ai_conflict['has_contradiction'] is True, "Expected contradiction to be flagged"
    assert conflict_json['incident']['verification_state'] == 'disputed', "Incident state should update to disputed"
    print(">> STEP 3 PASSED: Conflict accurately detected and incident marked as 'disputed'!")

    print("\n" + "=" * 70)
    print("STEP 4: RESPONDER TRIAGE & AUTHORITATIVE VERIFICATION")
    print("=" * 70)
    print("First Responder reviews Incident #1 (Lekki flood) and marks it VERIFIED via POST /incidents/1/verify...")
    res_verify = client.post('/incidents/1/verify')
    assert res_verify.status_code == 200
    verified_data = res_verify.json
    print(f"Incident #1 State: {verified_data['verification_state']}")
    assert verified_data['verification_state'] == 'verified', "Expected verification_state to be 'verified'"
    print(">> STEP 4 PASSED: First Responder officially verified Incident #1!")

    print("\n" + "=" * 70)
    print("STEP 5: AI-ASSISTED TASK GENERATION FOR VERIFIED INCIDENT")
    print("=" * 70)
    print("First Responder clicks 'Generate Suggested Task' via POST /incidents/1/tasks/generate...")
    res_task = client.post('/incidents/1/tasks/generate')
    assert res_task.status_code == 201
    task_data = res_task.json
    print(f"Generated Task ID #{task_data['id']}: \"{task_data['description']}\"")
    print(f"Status: {task_data['status']} | Incident ID: {task_data['incident_id']}")
    assert task_data['status'] == 'open'
    assert task_data['incident_id'] == 1
    assert len(task_data['description']) > 5
    task_id = task_data['id']
    print(">> STEP 5 PASSED: Task generated successfully and linked to Incident #1 with status 'open'!")

    print("\n" + "=" * 70)
    print("STEP 6: RESPONDER CLAIMS TASK")
    print("=" * 70)
    print(f"First Responder claims Task #{task_id} via POST /tasks/{task_id}/claim...")
    res_claim = client.post(f'/tasks/{task_id}/claim', json={
        "claimed_by": "Lagos State Emergency Management Agency (LASEMA) Unit 5"
    })
    assert res_claim.status_code == 200
    claim_data = res_claim.json
    print(f"Task #{task_id} Status: {claim_data['status']} | Claimed By: {claim_data['claimed_by']}")
    assert claim_data['status'] == 'claimed'
    assert claim_data['claimed_by'] == 'Lagos State Emergency Management Agency (LASEMA) Unit 5'
    print(">> STEP 6 PASSED: Task claimed successfully!")

    print("\n" + "=" * 70)
    print("STEP 7: PUBLIC-FACING VIEW SYNCHRONIZATION")
    print("=" * 70)
    print("Querying public incident list (GET /incidents) and detail view (GET /incidents/1)...")
    res_public_list = client.get('/incidents')
    assert res_public_list.status_code == 200
    incidents_list = res_public_list.json

    inc_1_public = next((i for i in incidents_list if i['id'] == 1), None)
    assert inc_1_public is not None
    print(f"Public Feed Incident #1 Title: {inc_1_public['title']}")
    print(f"Public Feed Verification State: {inc_1_public['verification_state']}")
    print(f"Public Feed Total Tasks: {len(inc_1_public['tasks'])}")
    print(f"Public Feed Total Reports: {inc_1_public['report_count']}")

    assert inc_1_public['verification_state'] == 'verified'
    assert inc_1_public['report_count'] == 4  # 3 seeded + 1 newly submitted
    assert len(inc_1_public['tasks']) == 1
    assert inc_1_public['tasks'][0]['status'] == 'claimed'

    res_public_detail = client.get('/incidents/1')
    assert res_public_detail.status_code == 200
    detail_data = res_public_detail.json
    assert len(detail_data['reports']) == 4
    assert len(detail_data['tasks']) == 1

    print(">> STEP 7 PASSED: Public feed accurately reflects the updated verified state, 4 linked reports, and the claimed task!")

    print("\n" + "*" * 70)
    print("  FULL GOLDEN PATH END-TO-END VERIFICATION SUCCEEDED WITH ZERO FAILURES!")
    print("*" * 70)

if __name__ == '__main__':
    run_golden_path()

