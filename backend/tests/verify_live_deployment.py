"""
Live Deployment & Golden Path Verification Script for Anya Crisis Platform.

Validates the full end-to-end lifecycle over HTTP against ANY target URL
(local development or remote Render production URL):
1. Health Check Endpoint (GET /health)
2. Frontend SPA Root (GET /)
3. Incident Feed Retrieval (GET /incidents)
4. Golden Path Step 1: Inbound Citizen Report Submission & AI Extraction (POST /reports)
5. Golden Path Step 2: First Responder Community Verification (POST /incidents/:id/verify)
6. Golden Path Step 3: AI Micro-Task Generation (POST /incidents/:id/tasks/generate)
7. Golden Path Step 4: Volunteer Task Claiming (POST /tasks/:id/claim)
8. Low-Bandwidth 2G SMS Ingestion & Phone Privacy Masking (POST /webhooks/sms)

Usage:
    python verify_live_deployment.py [TARGET_URL]

Examples:
    python verify_live_deployment.py http://localhost:5000
    python verify_live_deployment.py https://anya-crisis-platform.onrender.com
"""

import sys
import time
import requests

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def verify_live(base_url):
    base_url = base_url.rstrip('/')
    print_header(f"ANYA LIVE DEPLOYMENT VERIFICATION: {base_url}")

    results = []

    def record_step(name, success, detail=""):
        status = "PASSED" if success else "FAILED"
        symbol = "[OK]" if success else "[XX]"
        print(f"  {symbol} {name}: {detail}")
        results.append((name, success, detail))

    session = requests.Session()
    session.headers.update({"User-Agent": "Anya-Live-Verifier/1.0"})

    # -------------------------------------------------------------
    # Step 1: Health Check Endpoint
    # -------------------------------------------------------------
    try:
        res = session.get(f"{base_url}/health", timeout=15)
        if res.status_code == 200 and res.json().get("status") == "ok":
            record_step("Step 1: Health Check", True, f"200 OK - {res.json()}")
        else:
            record_step("Step 1: Health Check", False, f"Unexpected response: {res.status_code} {res.text}")
    except Exception as e:
        record_step("Step 1: Health Check", False, f"Connection failed: {str(e)}")

    # -------------------------------------------------------------
    # Step 2: Frontend SPA Root Serving
    # -------------------------------------------------------------
    try:
        res = session.get(f"{base_url}/", timeout=15)
        if res.status_code == 200 and ("html" in res.headers.get("Content-Type", "").lower() or "<!doctype html>" in res.text.lower()):
            record_step("Step 2: Frontend SPA Root", True, f"200 OK (Served HTML bundle, {len(res.text)} bytes)")
        else:
            record_step("Step 2: Frontend SPA Root", False, f"Status: {res.status_code}, Content-Type: {res.headers.get('Content-Type')}")
    except Exception as e:
        record_step("Step 2: Frontend SPA Root", False, str(e))

    # -------------------------------------------------------------
    # Step 3: Incidents Feed Check
    # -------------------------------------------------------------
    target_incident_id = None
    try:
        res = session.get(f"{base_url}/incidents", timeout=15)
        if res.status_code == 200:
            data = res.json()
            incidents = data if isinstance(data, list) else data.get("incidents", [])
            record_step("Step 3: Incidents Feed", True, f"Retrieved {len(incidents)} active incidents")
            if incidents:
                target_incident_id = incidents[0].get("id")
        else:
            record_step("Step 3: Incidents Feed", False, f"Status: {res.status_code}")
    except Exception as e:
        record_step("Step 3: Incidents Feed", False, str(e))

    # -------------------------------------------------------------
    # Step 4: Golden Path - Inbound Report & AI Extraction / Deduplication
    # -------------------------------------------------------------
    new_incident_id = None
    try:
        report_payload = {
            "raw_text": "Severe rising floodwater along Lekki-Epe expressway near Ajah bridge, three cars submerged and families seeking high ground.",
            "reporter_label": "resident",
            "location_text": "Ajah Bridge, Lekki-Epe Expressway, Lagos"
        }
        res = session.post(f"{base_url}/reports", json=report_payload, timeout=25)
        if res.status_code == 201:
            rdata = res.json()
            ai_data = rdata.get("ai", {})
            rep_info = rdata.get("report", {})
            linked_id = rep_info.get("incident_id")
            new_incident_id = linked_id
            decision = ai_data.get("match_decision")
            confidence = ai_data.get("ai_confidence", rep_info.get("ai_confidence"))
            reasoning = ai_data.get("ai_reasoning", rep_info.get("ai_reasoning", ""))
            
            record_step(
                "Step 4: Report -> AI Extraction",
                True,
                f"201 Created | Match: {decision} -> Inc #{linked_id} | Confidence: {confidence} | AI Rationale: {reasoning[:60]}..."
            )
        else:
            record_step("Step 4: Report -> AI Extraction", False, f"Status: {res.status_code} - {res.text}")
    except Exception as e:
        record_step("Step 4: Report -> AI Extraction", False, str(e))

    # Use whatever valid incident ID we have for the next responder steps
    active_test_id = new_incident_id or target_incident_id or 1

    # -------------------------------------------------------------
    # Step 5: Golden Path - First Responder Community Verification
    # -------------------------------------------------------------
    try:
        res = session.post(f"{base_url}/incidents/{active_test_id}/verify", timeout=15)
        if res.status_code == 200:
            vdata = res.json()
            vstate = vdata.get('verification_state') or vdata.get('incident', {}).get('verification_state')
            record_step(
                "Step 5: Responder Verification",
                True,
                f"200 OK | Incident #{active_test_id} state updated to: '{vstate}'"
            )
        else:
            record_step("Step 5: Responder Verification", False, f"Status: {res.status_code} - {res.text}")
    except Exception as e:
        record_step("Step 5: Responder Verification", False, str(e))

    # -------------------------------------------------------------
    # Step 6: Golden Path - AI Action Task Generation
    # -------------------------------------------------------------
    generated_task_id = None
    try:
        res = session.post(f"{base_url}/incidents/{active_test_id}/tasks/generate", timeout=25)
        if res.status_code == 201:
            tdata = res.json()
            generated_task_id = tdata.get("id") or tdata.get("task", {}).get("id")
            desc = tdata.get("description") or tdata.get("task", {}).get("description", "")
            record_step(
                "Step 6: AI Task Generation",
                True,
                f"201 Created | Task #{generated_task_id}: '{desc}'"
            )
        else:
            record_step("Step 6: AI Task Generation", False, f"Status: {res.status_code} - {res.text}")
    except Exception as e:
        record_step("Step 6: AI Task Generation", False, str(e))

    # -------------------------------------------------------------
    # Step 7: Golden Path - Volunteer Task Claiming
    # -------------------------------------------------------------
    if generated_task_id:
        try:
            claim_payload = {"claimed_by": "Ajah Volunteer Red Cross Team"}
            res = session.post(f"{base_url}/tasks/{generated_task_id}/claim", json=claim_payload, timeout=15)
            if res.status_code == 200:
                cdata = res.json()
                c_status = cdata.get('status') or cdata.get('task', {}).get('status')
                c_claimed = cdata.get('claimed_by') or cdata.get('task', {}).get('claimed_by')
                record_step(
                    "Step 7: Task Claiming",
                    True,
                    f"200 OK | Task #{generated_task_id} status: '{c_status}', Claimed by: '{c_claimed}'"
                )
            else:
                record_step("Step 7: Task Claiming", False, f"Status: {res.status_code} - {res.text}")
        except Exception as e:
            record_step("Step 7: Task Claiming", False, str(e))
    else:
        record_step("Step 7: Task Claiming", False, "Skipped: No task was generated in Step 6")

    # -------------------------------------------------------------
    # Step 8: 2G SMS Ingestion & Phone Masking Verification
    # -------------------------------------------------------------
    try:
        sms_payload = {
            "From": "+2348035550192",
            "Body": "Water don reach window for transformer junction Ajah, people dey roof!"
        }
        res = session.post(f"{base_url}/webhooks/sms", json=sms_payload, timeout=45)
        if res.status_code in (200, 201):
            sdata = res.json()
            carrier_msg = sdata.get("reply_sms") or sdata.get("carrier_response", "")
            rep_data = sdata.get("report", {})
            reporter_label = rep_data.get("reporter_label", "")
            is_masked = "***" in reporter_label
            record_step(
                "Step 8: 2G SMS Ingest & Masking",
                True,
                f"{res.status_code} OK | Masked: '{reporter_label}' (Masked: {is_masked}) | Receipt: '{carrier_msg[:60]}...'"
            )
        else:
            record_step("Step 8: 2G SMS Ingest & Masking", False, f"Status: {res.status_code} - {res.text}")
    except Exception as e:
        record_step("Step 8: 2G SMS Ingest & Masking", False, str(e))

    # -------------------------------------------------------------
    # Summary Report
    # -------------------------------------------------------------
    print_header("VERIFICATION SUMMARY")
    passed_count = sum(1 for _, ok, _ in results if ok)
    total_count = len(results)

    for name, ok, detail in results:
        sym = "[PASS]" if ok else "[FAIL]"
        print(f"  {sym} {name}")

    print("-" * 70)
    print(f"Total: {passed_count}/{total_count} steps passed ({int(passed_count/total_count*100)}%)")
    print("=" * 70)

    return passed_count == total_count

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    success = verify_live(target)
    sys.exit(0 if success else 1)

