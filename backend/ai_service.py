import os
import json
import time
import logging
from typing import Optional, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from google import genai
from google.genai import types

load_dotenv()

logger = logging.getLogger(__name__)

class ReportAnalysisResult(BaseModel):
    """
    Structured schema for LLM extraction, duplicate matching, and conflict detection.
    """
    incident_type: str = Field(
        description="Category of crisis event (e.g. flood, fire, medical, infrastructure, storm, hazmat, search_and_rescue, general)"
    )
    location: str = Field(
        description="Specific address, intersection, landmark, or geographic area mentioned. If none given, output 'Unknown'"
    )
    urgency: Literal['low', 'medium', 'high', 'critical'] = Field(
        description="Assessed urgency level based on risk to human life, safety, or critical infrastructure"
    )
    people_affected_estimate: Optional[int] = Field(
        default=None,
        description="Estimated number of people injured, trapped, or displaced, if mentioned or reasonably inferred. Null if unknown."
    )
    suggested_title: str = Field(
        description="Concise, factual headline summarizing the incident (max 60 characters)"
    )
    match_decision: Literal['MATCH', 'NEW'] = Field(
        description="'MATCH' if this report describes an existing active incident listed below; 'NEW' if it is a distinct, separate event"
    )
    matched_incident_id: Optional[int] = Field(
        default=None,
        description="The integer ID of the matched incident from the provided list. Must be null if match_decision is 'NEW'."
    )
    has_contradiction: bool = Field(
        description="True if this report directly contradicts or disputes key claims (e.g., claims roads are clear, no fire exists, disputes casualty count) of the matched incident. False otherwise."
    )
    contradiction_reason: Optional[str] = Field(
        default=None,
        description="A concise single-line explanation of the contradiction if has_contradiction is true; null otherwise"
    )
    confidence_score: float = Field(
        default=0.85,
        description="Confidence score between 0.0 and 1.0 representing certainty of extraction, matching, and conflict assessment."
    )
    reasoning_snippet: str = Field(
        description="Concise 1-2 sentence explanation of why this report was matched to an existing incident or deemed a new incident, citing specific landmarks, keywords, or time/location overlap."
    )


def _get_fallback_result(raw_text: str, reason: str) -> dict:
    """
    Deterministic fallback when LLM call fails or returns invalid output.
    Ensures zero data loss.
    """
    clean_text = raw_text.strip()
    first_line = clean_text.split('\n')[0]
    title = first_line[:57] + '...' if len(first_line) > 60 else first_line
    return {
        'status': 'fallback',
        'fallback_reason': reason,
        'data': {
            'incident_type': 'general',
            'location': 'Unknown',
            'urgency': 'medium',
            'people_affected_estimate': None,
            'suggested_title': title or 'Reported Incident',
            'match_decision': 'NEW',
            'matched_incident_id': None,
            'has_contradiction': False,
            'contradiction_reason': None,
            'confidence_score': 0.5,
            'reasoning_snippet': f"Fallback deterministic triage applied ({reason})."
        }
    }


def analyze_report(raw_text: str, reporter_label: str = 'resident', active_incidents: list = None) -> dict:
    """
    Executes one LLM call using Google Gemini API to extract details,
    match against active incidents, and detect conflicts.
    Falls back gracefully if the API fails or is unconfigured.
    """
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        logger.warning("No GEMINI_API_KEY found in environment. Using deterministic fallback.")
        return _get_fallback_result(raw_text, "Missing GEMINI_API_KEY")

    # Format the active incidents context (last 10-15)
    incidents_context = ""
    if active_incidents:
        formatted_incidents = []
        for inc in active_incidents:
            formatted_incidents.append(
                f"- Incident ID #{inc.get('id')}:\n"
                f"  Title: {inc.get('title')}\n"
                f"  Type: {inc.get('type')}\n"
                f"  Location: {inc.get('location_text')}\n"
                f"  Urgency: {inc.get('urgency')}\n"
                f"  Verification State: {inc.get('verification_state')}\n"
                f"  People Affected: {inc.get('people_affected_estimate')}"
            )
        incidents_context = "\n".join(formatted_incidents)
    else:
        incidents_context = "No currently active incidents. This is the first incident in the system."

    prompt = f"""You are Anya, an AI crisis-coordination triage assistant.
Analyze this incoming crisis report, extract core attributes, determine whether it matches an existing active incident or is new, and check for any factual contradictions.

ACTIVE OPEN INCIDENTS:
{incidents_context}

INCOMING REPORT:
- Reporter: {reporter_label}
- Text: \"\"\"{raw_text}\"\"\"

TASK REQUIREMENTS:
1. Extraction: Extract incident_type, specific location (or 'Unknown'), urgency ('low', 'medium', 'high', 'critical'), people_affected_estimate (integer or null), and a suggested_title (under 60 chars).
2. Deduplication & Matching:
   - Compare against the ACTIVE OPEN INCIDENTS above.
   - If this report is an exact duplicate, paraphrase, update, or describes the same physical crisis event at/near the same location, set match_decision: "MATCH" and set matched_incident_id to that incident's ID.
   - If it describes a separate event at a different place or different time, set match_decision: "NEW" and matched_incident_id: null.
3. Conflict Detection:
   - If match_decision is "MATCH": Check if this report contradicts or disputes what is currently recorded for the matched incident (e.g. reporting the road is open vs collapsed, reporting a false alarm, or disputing major facts). If so, set has_contradiction: true and provide a one-line contradiction_reason. If it confirms or adds info without conflict, set has_contradiction: false and contradiction_reason: null.
   - If match_decision is "NEW": set has_contradiction: false and contradiction_reason: null.
4. Explainability & Confidence:
   - Provide a concise 1-2 sentence reasoning_snippet explaining why the report was matched to an existing incident or classified as a new event, explicitly citing landmarks, keywords, or contradictions.
   - Provide a numerical confidence_score between 0.0 and 1.0 reflecting your assessment certainty.

Output structured JSON matching the requested schema."""

    model_name = os.environ.get('GEMINI_MODEL', 'gemini-3.6-flash')
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=ReportAnalysisResult.model_json_schema(),
                    temperature=0.1,
                )
            )

            if not response.text:
                logger.warning("Empty response received from Gemini API.")
                return _get_fallback_result(raw_text, "Empty LLM response")

            # Parse and validate with Pydantic
            parsed_json = json.loads(response.text)
            validated = ReportAnalysisResult.model_validate(parsed_json)
            
            return {
                'status': 'success',
                'data': validated.model_dump()
            }

        except ValidationError as ve:
            logger.error(f"Gemini response validation error: {ve}")
            return _get_fallback_result(raw_text, f"Pydantic validation error: {str(ve)}")
        except Exception as e:
            err_msg = str(e)
            if attempt < max_attempts - 1 and ("503" in err_msg or "429" in err_msg or "UNAVAILABLE" in err_msg):
                wait_secs = 2 * (attempt + 1)
                logger.warning(f"Transient Gemini API error ({err_msg}). Retrying in {wait_secs}s...")
                time.sleep(wait_secs)
                continue
            logger.error(f"Gemini API call failed: {e}")
            return _get_fallback_result(raw_text, f"API Exception: {err_msg}")


def generate_suggested_task(incident_data: dict) -> str:
    """
    Suggests a concise, actionable emergency response task for a verified incident.
    Falls back to a deterministic task description if AI is unavailable.
    """
    title = incident_data.get('title', 'Emergency Incident')
    inc_type = incident_data.get('type', 'general')
    location = incident_data.get('location_text', 'the reported area')
    urgency = incident_data.get('urgency', 'medium')
    affected = incident_data.get('people_affected_estimate')

    fallback_task = f"Deploy {inc_type} response team to {location}"

    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        return fallback_task

    prompt = f"""You are Anya, an emergency dispatch assistant.
Given this verified crisis incident:
- Title: {title}
- Incident Type: {inc_type}
- Location: {location}
- Urgency: {urgency}
- People Affected: {affected if affected is not None else 'Unknown'}

Suggest ONE single, highly specific, actionable operational task for emergency responders or volunteers to execute immediately (under 80 characters, no quotes or prefix).
Examples:
- "Deploy 2 inflatable rescue boats to Elm St for evacuation"
- "Set up emergency water distribution point at Central High School"
- "Cordon off downed high-voltage lines at 5th and Main"
"""
    model_name = os.environ.get('GEMINI_MODEL', 'gemini-3.6-flash')
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=50,
            )
        )
        if response.text:
            task_text = response.text.strip().strip('"').strip("'")
            if task_text:
                return task_text
    except Exception as e:
        logger.warning(f"Task generation LLM call failed: {e}")

    return fallback_task

