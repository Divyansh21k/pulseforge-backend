"""
Voice Assistant – Vapi webhook router
======================================
Handles all messages from Vapi:
  - tool-calls          → dispatch to voice_service tool functions
  - end-of-call-report  → send post-call summary email
  - call-start          → (logged; could be used for personalized greeting)
  - speech-update       → ignored (informational only)

Also exposes:
  - GET  /api/voice/vapi-webhook-test → liveness check
  - POST /api/voice/outbound-call    → initiate outbound call via Vapi
  - GET  /api/voice/status           → voice activity stats for the web dashboard
"""

import json
import logging
from collections import Counter
from datetime import datetime, timezone, timedelta

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.communication import Communication
from app.services import voice_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])


# ---------------------------------------------------------------------------
# Liveness
# ---------------------------------------------------------------------------

@router.get("/vapi-webhook-test")
async def vapi_webhook_test():
    """
    Simple GET endpoint to verify the ngrok tunnel is alive and the server is reachable.
    Open https://<your-ngrok-url>/api/voice/vapi-webhook-test in a browser to confirm.
    """
    return {"status": "ok", "message": "HackBridge Vapi webhook endpoint is reachable!"}


# ---------------------------------------------------------------------------
# Main Vapi webhook
# ---------------------------------------------------------------------------

@router.post("/vapi-webhook")
async def vapi_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Vapi calls this endpoint for every message type during a call.

    Tool-call response format (identical for Server URL and API Request tools):
      {"results": [{"toolCallId": "...", "result": "..."}]}

    For non-tool-call events (end-of-call-report, call-start, etc.) we return
      {"results": []}
    """
    body = await request.json()

    # ── DEBUG LOGGING ────────────────────────────────────────────────────────
    logger.info("[VapiWebhook] <<<< INCOMING PAYLOAD >>>>")
    logger.info(json.dumps(body, indent=2, default=str))
    print("[VapiWebhook] INCOMING:", json.dumps(body, default=str))

    message = body.get("message", {})
    msg_type = message.get("type", "<none>")
    logger.info(f"[VapiWebhook] message.type = '{msg_type}'")

    # ── Caller phone ──────────────────────────────────────────────────────────
    caller_phone = (
        message.get("call", {}).get("customer", {}).get("number", "")
        or body.get("call", {}).get("customer", {}).get("number", "")
    )
    logger.info(f"[VapiWebhook] caller_phone = '{caller_phone}'")

    # ── END-OF-CALL-REPORT ───────────────────────────────────────────────────
    if msg_type == "end-of-call-report":
        call_id = message.get("call", {}).get("id", body.get("call", {}).get("id", ""))
        transcript = message.get("transcript", "")
        summary = message.get("summary", "")
        logger.info(f"[VapiWebhook] End-of-call-report received. call_id={call_id}")
        voice_service.handle_call_end(
            call_id=call_id,
            transcript=transcript,
            summary=summary,
            caller_phone=caller_phone,
            background_tasks=background_tasks,
            db=db,
        )
        return {"results": []}

    # ── CALL-START ────────────────────────────────────────────────────────────
    if msg_type == "call-start":
        logger.info(f"[VapiWebhook] Call started from {caller_phone}")
        return {"results": []}

    # ── NON-TOOL-CALL MESSAGES ────────────────────────────────────────────────
    if msg_type != "tool-calls":
        logger.info(f"[VapiWebhook] Ignoring non-tool-calls message type: {msg_type}")
        return {"results": []}

    # ── EXTRACT TOOL CALLS ───────────────────────────────────────────────────
    # Server URL tools  → message.toolCalls
    # API Request tools → message.toolWithToolCallList[].toolCall
    tool_calls = message.get("toolCalls") or []
    if tool_calls:
        logger.info(f"[VapiWebhook] Using 'toolCalls' branch ({len(tool_calls)} call(s))")
    elif "toolWithToolCallList" in message:
        raw_list = message["toolWithToolCallList"]
        tool_calls = [item["toolCall"] for item in raw_list if "toolCall" in item]
        logger.info(
            f"[VapiWebhook] Using 'toolWithToolCallList' branch — "
            f"raw entries: {len(raw_list)}, valid: {len(tool_calls)}"
        )
        if not tool_calls:
            logger.warning("[VapiWebhook] toolWithToolCallList present but no 'toolCall' keys found!")
    else:
        logger.warning("[VapiWebhook] No toolCalls or toolWithToolCallList found.")

    results = []

    for call in tool_calls:
        call_id = call.get("id", "")
        fn = call.get("function", {})
        fn_name = fn.get("name", "")
        raw_args = fn.get("arguments", "{}")
        args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})

        logger.info(f"[VapiWebhook] Dispatching tool: '{fn_name}' (id={call_id}) args={args}")

        # ── TOOL DISPATCH ─────────────────────────────────────────────────────
        # Priority 1 — fixed existing tools
        if fn_name == "get_upcoming_events":
            result = voice_service.get_upcoming_events(db)

        elif fn_name == "get_hackathon_info":
            result = voice_service.get_hackathon_info(db)

        elif fn_name == "register_participant":
            result = voice_service.register_participant(args, caller_phone, background_tasks, db)

        elif fn_name == "find_teams_by_skills":
            result = voice_service.find_teams_by_skills(args, db)

        elif fn_name == "get_participant_status":
            result = voice_service.get_participant_status(args, caller_phone, background_tasks, db)

        elif fn_name == "request_team_join":
            result = voice_service.request_team_join(args, caller_phone, background_tasks, db)

        elif fn_name == "get_reviewer_assignments":
            result = voice_service.get_reviewer_assignments(args, caller_phone, db)

        elif fn_name == "create_hackathon_event":
            result = voice_service.create_hackathon_event(args, caller_phone, background_tasks, db)

        # Priority 2 — new tools
        elif fn_name == "get_project_rankings":
            result = voice_service.get_project_rankings(db)

        elif fn_name == "get_project_feedback":
            result = voice_service.get_project_feedback(args, db)

        elif fn_name == "get_team_details":
            result = voice_service.get_team_details(args, db)

        elif fn_name == "find_team_for_me":
            result = voice_service.find_team_for_me(args, caller_phone, background_tasks, db)

        elif fn_name == "get_analytics_overview":
            result = voice_service.get_analytics_overview(db)

        else:
            result = f"I'm sorry, I don't recognise the tool '{fn_name}'. Please try a different request."
            logger.warning(f"[VapiWebhook] Unknown tool name received: '{fn_name}'")

        logger.info(
            f"[VapiWebhook] Tool result for '{fn_name}': "
            f"{result[:200]}{'...' if len(result) > 200 else ''}"
        )
        results.append({"toolCallId": call_id, "result": result})

    response_body = {"results": results}
    logger.info("[VapiWebhook] <<<< OUTGOING RESPONSE >>>>")
    logger.info(json.dumps(response_body, indent=2, default=str))
    print("[VapiWebhook] OUTGOING:", json.dumps(response_body, default=str))

    return response_body


# ---------------------------------------------------------------------------
# Outbound call
# ---------------------------------------------------------------------------

class OutboundCallRequest(BaseModel):
    phone_number: str


@router.post("/outbound-call")
async def create_outbound_call(call_req: OutboundCallRequest):
    """Initiates an outbound call to the provided phone number using Vapi."""
    if not settings.vapi_api_key or not settings.vapi_assistant_id or not settings.vapi_phone_number_id:
        raise HTTPException(
            status_code=500,
            detail=(
                "Vapi credentials not configured. "
                "Please add VAPI_API_KEY, VAPI_ASSISTANT_ID, and VAPI_PHONE_NUMBER_ID to your .env file."
            ),
        )

    try:
        response = httpx.post(
            "https://api.vapi.ai/call/phone",
            headers={"Authorization": f"Bearer {settings.vapi_api_key.strip()}"},
            json={
                "phoneNumberId": settings.vapi_phone_number_id.strip(),
                "assistantId": settings.vapi_assistant_id.strip(),
                "customer": {"number": call_req.phone_number},
            },
            timeout=15,
        )
        if response.status_code >= 400:
            logger.error(f"[Vapi Outbound] Error {response.status_code}: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return {"status": "success", "message": "Call initiated successfully", "data": response.json()}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[Vapi Outbound] Unexpected exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Voice Activity Status  (powers the web dashboard voice panel)
# ---------------------------------------------------------------------------

@router.get("/status")
def get_voice_status(db: Session = Depends(get_db)):
    """
    Returns voice assistant activity statistics for the web dashboard.
    Derived from the communications log — no separate data store needed.
    """
    voice_templates = {
        "registration_confirmed",
        "voice_participant_status",
        "voice_team_intro",
        "voice_call_summary",
        "voice_team_match",
        "voice_reviewer_schedule",
    }

    # Pull all voice-related communication records
    all_comms = (
        db.query(Communication)
        .filter(Communication.template_key.in_(voice_templates))
        .order_by(Communication.sent_at.desc())
        .limit(500)
        .all()
    )

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_comms = [
        c for c in all_comms
        if c.sent_at and c.sent_at.replace(tzinfo=timezone.utc) >= today_start
    ]

    # Count tool-type activity from template keys used
    tool_counter = Counter(c.template_key for c in all_comms)

    # Approximate: each voice_call_summary = 1 completed call
    # Each registration_confirmed from voice = 1 voice registration
    total_calls = tool_counter.get("voice_call_summary", 0)
    registrations_via_voice = tool_counter.get("registration_confirmed", 0)
    team_intros_sent = tool_counter.get("voice_team_intro", 0)
    team_matches_sent = tool_counter.get("voice_team_match", 0)
    status_checks = tool_counter.get("voice_participant_status", 0)

    recent_activity = [
        {
            "template": c.template_key,
            "subject": c.subject,
            "status": c.status,
            "sent_at": c.sent_at.isoformat() if c.sent_at else None,
        }
        for c in all_comms[:10]
    ]

    return {
        "summary": {
            "total_calls_completed": total_calls,
            "emails_sent_today": len(today_comms),
            "total_emails_sent": len(all_comms),
            "registrations_via_voice": registrations_via_voice,
            "team_intros_sent": team_intros_sent,
            "team_matches_found": team_matches_sent,
            "status_checks_performed": status_checks,
        },
        "recent_activity": recent_activity,
        "tools_available": [
            "get_upcoming_events",
            "get_hackathon_info",
            "register_participant",
            "find_teams_by_skills",
            "get_participant_status",
            "request_team_join",
            "get_reviewer_assignments",
            "create_hackathon_event",
            "get_project_rankings",
            "get_project_feedback",
            "get_team_details",
            "find_team_for_me",
            "get_analytics_overview",
        ],
    }
