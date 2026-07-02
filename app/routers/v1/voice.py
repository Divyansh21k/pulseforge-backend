"""
Voice Assistant – Vapi webhook router
Demo feature for HackBridge final presentation.
Handles tool-calls from Vapi and returns results the AI reads back to the caller.
"""

import json
import logging
import httpx
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.services import voice_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])


@router.get("/vapi-webhook-test")
async def vapi_webhook_test():
    """
    Simple GET endpoint to verify the ngrok tunnel is alive and the server is reachable.
    Open https://<your-ngrok-url>/api/voice/vapi-webhook-test in a browser to confirm.
    """
    return {"status": "ok", "message": "PulseForge Vapi webhook endpoint is reachable!"}


@router.post("/vapi-webhook")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Vapi calls this endpoint whenever the AI agent needs to run a tool.

    For Server URL tools, Vapi sends:
      message.toolCalls = [{"id": "...", "function": {"name": "...", "arguments": "{}"}}]

    For API Request (Custom Tool) tools, Vapi sends:
      message.toolWithToolCallList = [{"tool": {...}, "toolCall": {"id": "...", "function": {...}}}]

    Response format (identical for both):
      {"results": [{"toolCallId": "...", "result": "..."}]}
    """
    # --- DEBUG: Log the raw incoming payload ---
    body = await request.json()
    logger.info("[VapiWebhook] <<<< INCOMING PAYLOAD >>>>")
    logger.info(json.dumps(body, indent=2, default=str))
    print("[VapiWebhook] INCOMING:", json.dumps(body, default=str))  # also print for uvicorn stdout

    message = body.get("message", {})
    msg_type = message.get("type", "<none>")
    logger.info(f"[VapiWebhook] message.type = '{msg_type}'")

    if msg_type != "tool-calls":
        logger.info(f"[VapiWebhook] Ignoring non-tool-calls message type: {msg_type}")
        return {"results": []}

    # Attempt to extract caller phone number from Vapi payload
    caller_phone = message.get("call", {}).get("customer", {}).get("number", "")
    logger.info(f"[VapiWebhook] caller_phone = '{caller_phone}'")

    results = []

    # ----------------------------------------------------------------
    # Extract tool calls:
    #   - Server URL tools  → message.toolCalls
    #   - API Request tools → message.toolWithToolCallList[].toolCall
    # ----------------------------------------------------------------
    tool_calls = message.get("toolCalls") or []
    if tool_calls:
        logger.info(f"[VapiWebhook] Using 'toolCalls' branch ({len(tool_calls)} call(s))")
    elif "toolWithToolCallList" in message:
        raw_list = message["toolWithToolCallList"]
        tool_calls = [item["toolCall"] for item in raw_list if "toolCall" in item]
        logger.info(
            f"[VapiWebhook] Using 'toolWithToolCallList' branch — "
            f"raw entries: {len(raw_list)}, valid toolCalls extracted: {len(tool_calls)}"
        )
        if not tool_calls:
            logger.warning("[VapiWebhook] toolWithToolCallList was present but NO 'toolCall' keys found in items!")
            logger.warning(f"[VapiWebhook] raw_list contents: {json.dumps(raw_list, default=str)}")
    else:
        logger.warning("[VapiWebhook] No toolCalls or toolWithToolCallList found in message.")
        logger.warning(f"[VapiWebhook] Full message keys: {list(message.keys())}")

    for call in tool_calls:
        call_id = call.get("id", "")
        fn = call.get("function", {})
        fn_name = fn.get("name", "")
        raw_args = fn.get("arguments", "{}")
        args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})

        logger.info(f"[VapiWebhook] Dispatching tool: '{fn_name}' (id={call_id}) args={args}")

        if fn_name == "get_upcoming_events":
            result = voice_service.get_upcoming_events(db)
        elif fn_name == "get_hackathon_info":
            result = voice_service.get_hackathon_info(db)
        elif fn_name == "register_participant":
            result = voice_service.register_participant(args, caller_phone, db)
        elif fn_name == "find_teams_by_skills":
            result = voice_service.find_teams_by_skills(args, db)
        elif fn_name == "get_participant_status":
            result = voice_service.get_participant_status(args, caller_phone, db)
        elif fn_name == "request_team_join":
            result = voice_service.request_team_join(args, caller_phone, db)
        elif fn_name == "get_reviewer_assignments":
            result = voice_service.get_reviewer_assignments(args, caller_phone, db)
        elif fn_name == "create_hackathon_event":
            result = voice_service.create_hackathon_event(args, caller_phone, db)
        else:
            result = f"Unknown tool: {fn_name}"
            logger.warning(f"[VapiWebhook] Unknown tool name received: '{fn_name}'")

        logger.info(f"[VapiWebhook] Tool result for '{fn_name}': {result[:200]}{'...' if len(result) > 200 else ''}")
        results.append({"toolCallId": call_id, "result": result})

    response_body = {"results": results}
    logger.info(f"[VapiWebhook] <<<< OUTGOING RESPONSE >>>>")
    logger.info(json.dumps(response_body, indent=2, default=str))
    print("[VapiWebhook] OUTGOING:", json.dumps(response_body, default=str))

    return response_body


class OutboundCallRequest(BaseModel):
    phone_number: str

@router.post("/outbound-call")
async def create_outbound_call(call_req: OutboundCallRequest):
    """
    Initiates an outbound call to the provided phone number using Vapi.
    """
    if not settings.vapi_api_key or not settings.vapi_assistant_id or not settings.vapi_phone_number_id:
        raise HTTPException(
            status_code=500, 
            detail="Vapi credentials not configured. Please add VAPI_API_KEY, VAPI_ASSISTANT_ID, and VAPI_PHONE_NUMBER_ID to your environment variables."
        )

    try:
        response = httpx.post(
            "https://api.vapi.ai/call/phone",
            headers={"Authorization": f"Bearer {settings.vapi_api_key.strip()}"},
            json={
                "phoneNumberId": settings.vapi_phone_number_id.strip(),
                "assistantId": settings.vapi_assistant_id.strip(),
                "customer": {
                    "number": call_req.phone_number
                }
            },
            timeout=15
        )
        if response.status_code >= 400:
            print(f"[Vapi Outbound] Error {response.status_code}: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        return {"status": "success", "message": "Call initiated successfully", "data": response.json()}
    except Exception as e:
        print(f"[Vapi Outbound] Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

