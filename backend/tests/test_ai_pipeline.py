import os
import sys
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Incident, Report

def print_separator(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def run_all_tests():
    app = create_app()
    client = app.test_client()

    with app.app_context():
        # Start from a clean database
        db.drop_all()
        db.create_all()

    print_separator("TEST SUITE: ANYA AI EXTRACTION, MATCHING & CONFLICT PIPELINE")

    # -------------------------------------------------------------
    # Scenario 1: New Incident (Flash Flood)
    # -------------------------------------------------------------
    print_separator("SCENARIO 1: New Incident (Flash Flood)")
    payload_1 = {
        "raw_text": "Flash flood water rising rapidly on Elm Street near 4th Ave, ground floors starting to flood, about 10 families trapped.",
        "reporter_label": "resident"
    }
    res_1 = client.post('/reports', json=payload_1)
    print(f"Status: {res_1.status_code}")
    data_1 = res_1.json
    print(f"AI Status: {data_1['ai']['status']}")
    print(f"Decision: {data_1['ai']['match_decision']}")
    print(f"Extracted: {json.dumps(data_1['ai']['extracted'], indent=2)}")
    print(f"Created Incident ID: {data_1['incident']['id']} | Title: {data_1['incident']['title']}")
    
    assert res_1.status_code == 201
    assert data_1['ai']['match_decision'] == 'NEW'
    assert data_1['incident']['id'] == 1
    assert data_1['report']['incident_id'] == 1
    inc_1_id = data_1['incident']['id']

    # -------------------------------------------------------------
    # Scenario 2: New Incident 2 (Structural Fire at different location)
    # -------------------------------------------------------------
    print_separator("SCENARIO 2: Distinct Second Incident (Fire on Baker Street)")
    payload_2 = {
        "raw_text": "Industrial warehouse fire on Baker Street, thick black smoke billowing from roof, 3 workers injured outside.",
        "reporter_label": "first_responder"
    }
    res_2 = client.post('/reports', json=payload_2)
    print(f"Status: {res_2.status_code}")
    data_2 = res_2.json
    print(f"Decision: {data_2['ai']['match_decision']}")
    print(f"Extracted: {json.dumps(data_2['ai']['extracted'], indent=2)}")
    print(f"Created Incident ID: {data_2['incident']['id']} | Title: {data_2['incident']['title']}")

    assert res_2.status_code == 201
    assert data_2['ai']['match_decision'] == 'NEW'
    assert data_2['incident']['id'] != inc_1_id
    inc_2_id = data_2['incident']['id']

    # -------------------------------------------------------------
    # Scenario 3: Exact Duplicate Report of Incident 1
    # -------------------------------------------------------------
    print_separator("SCENARIO 3: Exact Duplicate Report (Same text on Elm Street)")
    res_3 = client.post('/reports', json=payload_1)
    data_3 = res_3.json
    print(f"Decision: {data_3['ai']['match_decision']}")
    print(f"Matched Incident ID: {data_3['ai']['matched_incident_id']}")
    print(f"Has Contradiction: {data_3['ai']['has_contradiction']}")
    
    assert res_3.status_code == 201
    assert data_3['ai']['match_decision'] == 'MATCH'
    assert data_3['ai']['matched_incident_id'] == inc_1_id
    assert data_3['report']['incident_id'] == inc_1_id
    assert data_3['ai']['has_contradiction'] is False

    # -------------------------------------------------------------
    # Scenario 4: Paraphrased / Near-Duplicate of Incident 1
    # -------------------------------------------------------------
    print_separator("SCENARIO 4: Paraphrased Report (Elm St Flooding)")
    payload_4 = {
        "raw_text": "Elm St is completely submerged near fourth avenue, water level waist high and cars cannot pass.",
        "reporter_label": "resident"
    }
    res_4 = client.post('/reports', json=payload_4)
    data_4 = res_4.json
    print(f"Decision: {data_4['ai']['match_decision']}")
    print(f"Matched Incident ID: {data_4['ai']['matched_incident_id']}")
    print(f"Has Contradiction: {data_4['ai']['has_contradiction']}")

    assert res_4.status_code == 201
    assert data_4['ai']['match_decision'] == 'MATCH'
    assert data_4['ai']['matched_incident_id'] == inc_1_id
    assert data_4['ai']['has_contradiction'] is False

    # -------------------------------------------------------------
    # Scenario 5: Corroboration with New Information for Incident 2
    # -------------------------------------------------------------
    print_separator("SCENARIO 5: Corroboration with New Casualty Details (Baker Street)")
    payload_5 = {
        "raw_text": "Update on Baker Street warehouse fire: crews are on scene battling the roof flames, 2 additional people treated for smoke inhalation.",
        "reporter_label": "responder"
    }
    res_5 = client.post('/reports', json=payload_5)
    data_5 = res_5.json
    print(f"Decision: {data_5['ai']['match_decision']}")
    print(f"Matched Incident ID: {data_5['ai']['matched_incident_id']}")
    print(f"Has Contradiction: {data_5['ai']['has_contradiction']}")
    print(f"Incident Verification State: {data_5['incident']['verification_state']}")

    assert res_5.status_code == 201
    assert data_5['ai']['match_decision'] == 'MATCH'
    assert data_5['ai']['matched_incident_id'] == inc_2_id
    assert data_5['ai']['has_contradiction'] is False
    assert data_5['incident']['verification_state'] == 'corroborated'

    # -------------------------------------------------------------
    # Scenario 6: Direct Contradiction / Dispute for Incident 2
    # -------------------------------------------------------------
    print_separator("SCENARIO 6: Direct Contradiction / Dispute (Baker Street Fire)")
    payload_6 = {
        "raw_text": "I am standing right outside the Baker Street warehouse. There is NO fire at all, completely false alarm, building is intact and empty.",
        "reporter_label": "resident"
    }
    res_6 = client.post('/reports', json=payload_6)
    data_6 = res_6.json
    print(f"Decision: {data_6['ai']['match_decision']}")
    print(f"Matched Incident ID: {data_6['ai']['matched_incident_id']}")
    print(f"Has Contradiction: {data_6['ai']['has_contradiction']}")
    print(f"Contradiction Reason: {data_6['ai']['contradiction_reason']}")
    print(f"Incident Verification State: {data_6['incident']['verification_state']}")

    assert res_6.status_code == 201
    assert data_6['ai']['match_decision'] == 'MATCH'
    assert data_6['ai']['matched_incident_id'] == inc_2_id
    assert data_6['ai']['has_contradiction'] is True
    assert data_6['ai']['contradiction_reason'] is not None
    assert data_6['incident']['verification_state'] == 'disputed'

    # -------------------------------------------------------------
    # Scenario 7: Ambiguous / Minimal Text Report
    # -------------------------------------------------------------
    print_separator("SCENARIO 7: Ambiguous / Minimal Text Report")
    payload_7 = {
        "raw_text": "Need urgent medical help immediately!",
        "reporter_label": "resident"
    }
    res_7 = client.post('/reports', json=payload_7)
    data_7 = res_7.json
    print(f"Decision: {data_7['ai']['match_decision']}")
    print(f"Extracted: {json.dumps(data_7['ai']['extracted'], indent=2)}")

    assert res_7.status_code == 201
    assert data_7['ai']['match_decision'] == 'NEW'

    # -------------------------------------------------------------
    # Scenario 8: Disambiguation with Multiple Active Incidents
    # -------------------------------------------------------------
    print_separator("SCENARIO 8: Disambiguation Across Multiple Active Incidents")
    payload_8 = {
        "raw_text": "Water rescue team just arrived at Elm St near 4th to evacuate stranded residents from upper windows.",
        "reporter_label": "first_responder"
    }
    res_8 = client.post('/reports', json=payload_8)
    data_8 = res_8.json
    print(f"Decision: {data_8['ai']['match_decision']}")
    print(f"Matched Incident ID: {data_8['ai']['matched_incident_id']} (Expected: {inc_1_id})")

    assert res_8.status_code == 201
    assert data_8['ai']['match_decision'] == 'MATCH'
    assert data_8['ai']['matched_incident_id'] == inc_1_id

    # -------------------------------------------------------------
    # Scenario 9: Simulated LLM Failure -> Zero Loss Fallback
    # -------------------------------------------------------------
    print_separator("SCENARIO 9: LLM Failure Simulation -> Graceful Fallback")
    # Temporarily corrupt API key in environment to force failure
    original_key = os.environ.get('GEMINI_API_KEY')
    os.environ['GEMINI_API_KEY'] = 'INVALID_FAKE_KEY_FOR_FALLBACK_TEST'
    
    payload_9 = {
        "raw_text": "Strong sulfur and gas odor detected near Central Library on Oak Street.",
        "reporter_label": "resident"
    }
    res_9 = client.post('/reports', json=payload_9)
    data_9 = res_9.json
    print(f"Status: {res_9.status_code}")
    print(f"AI Status: {data_9['ai']['status']}")
    print(f"Fallback Reason: {data_9['ai']['fallback_reason']}")
    print(f"Incident Urgency: {data_9['incident']['urgency']}")
    print(f"Incident Verification: {data_9['incident']['verification_state']}")
    print(f"Report ID: {data_9['report']['id']} | Linked Incident ID: {data_9['report']['incident_id']}")

    # Restore real API key
    if original_key:
        os.environ['GEMINI_API_KEY'] = original_key
    else:
        del os.environ['GEMINI_API_KEY']

    assert res_9.status_code == 201
    assert data_9['ai']['status'] == 'fallback'
    assert data_9['incident']['urgency'] == 'medium'
    assert data_9['incident']['verification_state'] == 'unverified'
    assert data_9['report']['incident_id'] == data_9['incident']['id']

    # -------------------------------------------------------------
    # Scenario 10: Validation Error Handling
    # -------------------------------------------------------------
    print_separator("SCENARIO 10: Validation Error Handling")
    res_10 = client.post('/reports', json={})
    print(f"Status for empty payload: {res_10.status_code}, Response: {res_10.json}")
    assert res_10.status_code == 400

    # -------------------------------------------------------------
    # Verify Incident Detail and Linked Reports
    # -------------------------------------------------------------
    print_separator("FINAL VERIFICATION: Incident Detail & Linked Reports")
    res_inc_1 = client.get(f'/incidents/{inc_1_id}')
    print(f"Incident 1 Reports Count: {len(res_inc_1.json['reports'])}")
    # Incident 1 had: Scenario 1 (initial), Scenario 3 (exact dup), Scenario 4 (paraphrase), Scenario 8 (update)
    assert len(res_inc_1.json['reports']) == 4

    res_inc_2 = client.get(f'/incidents/{inc_2_id}')
    print(f"Incident 2 Reports Count: {len(res_inc_2.json['reports'])}, State: {res_inc_2.json['verification_state']}")
    # Incident 2 had: Scenario 2 (initial), Scenario 5 (corroborate), Scenario 6 (dispute)
    assert len(res_inc_2.json['reports']) == 3
    assert res_inc_2.json['verification_state'] == 'disputed'

    print("\n" + "*" * 70)
    print("  ALL 10 COMPREHENSIVE AI PIPELINE SCENARIOS PASSED PERFECTLY!")
    print("*" * 70)

if __name__ == '__main__':
    run_all_tests()

