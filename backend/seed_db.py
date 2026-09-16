"""
Seed script for Anya crisis coordination demo.
Resets the database and populates realistic Nigerian crisis scenarios:
1. Incident 1 (Dedup Case): Flash flooding on Lekki-Epe Expressway near Ajah (3 near-duplicate reports)
2. Incident 2 (Conflict Case): Fire dispute at Balogun Market, Lagos Island (2 contradictory reports)
3. Incident 3 (Resolved Case): Fallen PHCN high-tension pole on Aminu Kano Crescent, Wuse 2, Abuja (Verified, 1 claimed task)
4. Incident 4 (Low Urgency): Burst water pipe on Isaac John Street, Ikeja GRA
5. Incident 5 (Low Urgency): Large fallen tree branch on Ring Road, Ibadan
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from models import db, Incident, Report, Task

def seed_database(database_url=None):
    if database_url:
        os.environ['DATABASE_URL'] = database_url

    app = create_app()
    with app.app_context():
        target_uri = app.config['SQLALCHEMY_DATABASE_URI']
        # Mask password in log output if present
        display_uri = target_uri
        if '@' in target_uri:
            prefix, rest = target_uri.split('://', 1)
            user_pass, host_db = rest.split('@', 1)
            display_uri = f"{prefix}://***:***@{host_db}"
        print(f"Target Database: {display_uri}")
        print("Resetting database schema...")
        db.drop_all()
        db.create_all()

        now = datetime.now(timezone.utc)

        # -------------------------------------------------------------
        # Incident 1: Flooding on Lekki-Epe Expressway, Ajah (Dedup Case)
        # -------------------------------------------------------------
        inc1 = Incident(
            title="Severe Flash Flooding on Lekki-Epe Expressway near Ajah",
            type="flood",
            location_text="Lekki-Epe Expressway, Ajah, Lagos",
            lat=6.4698,
            lng=3.5852,
            urgency="critical",
            verification_state="corroborated",
            people_affected_estimate=25,
            created_at=now - timedelta(minutes=45),
            updated_at=now - timedelta(minutes=10)
        )
        db.session.add(inc1)
        db.session.flush()

        # 3 near-duplicate reports for Incident 1
        rep1_a = Report(
            incident_id=inc1.id,
            raw_text="Heavy downpour has submerged the Lekki-Epe Expressway by Ajah bridge, flood water entering ground floor shops and several cars completely stalled.",
            reporter_label="resident",
            ai_reasoning="Initiated primary incident record for severe flash flooding on Lekki-Epe Expressway at Ajah bridge.",
            ai_confidence=0.96,
            created_at=now - timedelta(minutes=45)
        )
        rep1_b = Report(
            incident_id=inc1.id,
            raw_text="Ajah underbridge towards Abraham Adesanya is flooded waist-deep, vehicles cannot pass and commuters are stranded.",
            reporter_label="resident",
            ai_reasoning="Matched Incident #1 (Lekki flood) with high spatial correlation: 'Ajah underbridge' / 'Abraham Adesanya' describes the same arterial corridor with consistent waist-deep water levels.",
            ai_confidence=0.93,
            created_at=now - timedelta(minutes=30)
        )
        rep1_c = Report(
            incident_id=inc1.id,
            raw_text="Water rising fast near Ajah market by Lekki-Epe express, shop owners trying to salvage goods and families trapped in compound.",
            reporter_label="resident",
            ai_reasoning="Corroborated Incident #1: Report references 'Ajah market by Lekki-Epe express', confirming escalating flood impact on commercial stalls within the same 45-minute window.",
            ai_confidence=0.91,
            created_at=now - timedelta(minutes=12)
        )
        db.session.add_all([rep1_a, rep1_b, rep1_c])

        # -------------------------------------------------------------
        # Incident 2: Balogun Market Fire Dispute (Conflict Case)
        # -------------------------------------------------------------
        inc2 = Incident(
            title="Reported Smoke and Fire at Balogun Market, Lagos Island",
            type="fire",
            location_text="Balogun Market, Lagos Island",
            lat=6.4551,
            lng=3.3841,
            urgency="high",
            verification_state="disputed",
            people_affected_estimate=5,
            created_at=now - timedelta(minutes=60),
            updated_at=now - timedelta(minutes=15)
        )
        db.session.add(inc2)
        db.session.flush()

        # 2 contradictory reports for Incident 2
        rep2_a = Report(
            incident_id=inc2.id,
            raw_text="Massive fire outbreak at commercial plaza in Balogun Market, thick black smoke rising from upper floor clothes shop.",
            reporter_label="resident",
            ai_reasoning="Initiated primary fire incident for reported blaze at commercial plaza in Balogun Market, Lagos Island.",
            ai_confidence=0.90,
            created_at=now - timedelta(minutes=60)
        )
        rep2_b = Report(
            incident_id=inc2.id,
            raw_text="I am standing at Balogun Market right by the main plaza. There is NO active fire, only someone burning cartons in the waste bin that has already been put out. Business is normal.",
            reporter_label="resident",
            ai_reasoning="Matched Incident #2 (Balogun Market) but flagged critical contradiction: On-scene resident reports NO active plaza fire, identifying source as an already-extinguished waste bin.",
            ai_confidence=0.88,
            created_at=now - timedelta(minutes=18)
        )
        db.session.add_all([rep2_a, rep2_b])

        # -------------------------------------------------------------
        # Incident 3: Collapsed High-Tension PHCN Pole, Abuja (Resolved Case)
        # -------------------------------------------------------------
        inc3 = Incident(
            title="Collapsed High-Tension PHCN Pole across Aminu Kano Crescent",
            type="infrastructure",
            location_text="Aminu Kano Crescent, Wuse 2, Abuja",
            lat=9.0765,
            lng=7.4721,
            urgency="high",
            verification_state="verified",
            people_affected_estimate=0,
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(minutes=25)
        )
        db.session.add(inc3)
        db.session.flush()

        rep3 = Report(
            incident_id=inc3.id,
            raw_text="Concrete electricity pole collapsed across the road on Aminu Kano near Banex Plaza, live wires sparking on the tarmac.",
            reporter_label="first_responder",
            ai_reasoning="Initiated high-urgency electrical hazard incident for collapsed PHCN concrete high-tension pole on Aminu Kano Crescent, Wuse 2, Abuja.",
            ai_confidence=0.98,
            created_at=now - timedelta(hours=2)
        )
        task3 = Task(
            incident_id=inc3.id,
            description="Isolate power grid with AEDC and establish safety perimeter on Aminu Kano Crescent",
            status="claimed",
            claimed_by="Federal Road Safety Corps Unit 3",
            created_at=now - timedelta(minutes=80)
        )
        db.session.add_all([rep3, task3])

        # -------------------------------------------------------------
        # Incident 4: Burst Water Pipe, Ikeja GRA (Low-Urgency Variety)
        # -------------------------------------------------------------
        inc4 = Incident(
            title="Burst Water Pipe Flooding Sidewalk on Isaac John Street",
            type="infrastructure",
            location_text="Isaac John Street, Ikeja GRA, Lagos",
            lat=6.5882,
            lng=3.3587,
            urgency="low",
            verification_state="unverified",
            people_affected_estimate=0,
            created_at=now - timedelta(hours=3),
            updated_at=now - timedelta(hours=3)
        )
        db.session.add(inc4)
        db.session.flush()

        rep4 = Report(
            incident_id=inc4.id,
            raw_text="Water gushing from broken Lagos Water Corporation pipe onto the pedestrian walkway along Isaac John Street.",
            reporter_label="resident",
            ai_reasoning="Initiated low-urgency municipal infrastructure incident for burst water utility main along Isaac John Street sidewalk, Ikeja GRA.",
            ai_confidence=0.94,
            created_at=now - timedelta(hours=3)
        )
        db.session.add(rep4)

        # -------------------------------------------------------------
        # Incident 5: Fallen Tree Branch, Ibadan (Low-Urgency Variety)
        # -------------------------------------------------------------
        inc5 = Incident(
            title="Large Tree Branch Partially Blocking Ring Road, Ibadan",
            type="infrastructure",
            location_text="MKO Abiola Way / Ring Road, Ibadan",
            lat=7.3563,
            lng=3.8647,
            urgency="low",
            verification_state="unverified",
            people_affected_estimate=0,
            created_at=now - timedelta(hours=4),
            updated_at=now - timedelta(hours=4)
        )
        db.session.add(inc5)
        db.session.flush()

        rep5 = Report(
            incident_id=inc5.id,
            raw_text="A big branch broke off during the morning storm and is blocking the slow lane of Ring Road near the Challenge junction.",
            reporter_label="resident",
            ai_reasoning="Initiated low-urgency roadway hazard incident for fallen storm tree branch partially obstructing Ring Road near Challenge junction, Ibadan.",
            ai_confidence=0.92,
            created_at=now - timedelta(hours=4)
        )
        db.session.add(rep5)

        db.session.commit()

        print("\n" + "=" * 70)
        print("DATABASE SEEDING COMPLETE (NIGERIAN CRISIS SCENARIOS)")
        print("=" * 70)
        print(f"1. [DEDUP] Incident #{inc1.id}: {inc1.title} ({inc1.verification_state}) - 3 reports")
        print(f"2. [CONFLICT] Incident #{inc2.id}: {inc2.title} ({inc2.verification_state}) - 2 reports")
        print(f"3. [VERIFIED+CLAIMED] Incident #{inc3.id}: {inc3.title} ({inc3.verification_state}) - 1 task: '{task3.description}'")
        print(f"4. [LOW-URGENCY] Incident #{inc4.id}: {inc4.title} ({inc4.verification_state})")
        print(f"5. [LOW-URGENCY] Incident #{inc5.id}: {inc5.title} ({inc5.verification_state})")
        print("=" * 70)

if __name__ == '__main__':
    custom_url = None
    if '--url' in sys.argv:
        try:
            idx = sys.argv.index('--url')
            custom_url = sys.argv[idx + 1]
        except IndexError:
            print("Error: --url specified without a database connection string.")
            sys.exit(1)
    seed_database(database_url=custom_url)

