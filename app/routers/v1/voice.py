"""
Voice Assistant – Vapi webhook router
Demo feature for HackBridge final presentation.
Handles tool-calls from Vapi and returns results the AI reads back to the caller.
"""

import json
import httpx
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.services import voice_service

router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])

@router.post("/vapi-webhook")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Vapi calls this endpoint whenever the AI agent needs to run a tool.
    Expected body:
    {
      "message": {
        "type": "tool-calls",
        "call": {
          "customer": {
            "number": "+1234567890"
          }
        },
        "toolCalls": [
          { "id": "...", "function": { "name": "...", "arguments": "{}" } }
        ]
      }
    }
    """
    body = await request.json()
    message = body.get("message", {})

    if message.get("type") != "tool-calls":
        return {"results": []}

    # Attempt to extract caller phone number from Vapi payload
    caller_phone = message.get("call", {}).get("customer", {}).get("number", "")

    results = []
    for call in message.get("toolCalls", []):
        call_id = call.get("id", "")
        fn_name = call.get("function", {}).get("name", "")
        raw_args = call.get("function", {}).get("arguments", "{}")
        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

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

        results.append({"toolCallId": call_id, "result": result})

    return {"results": results}


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
            headers={"Authorization": f"Bearer {settings.vapi_api_key}"},
            json={
                "phoneNumberId": settings.vapi_phone_number_id,
                "assistantId": settings.vapi_assistant_id,
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

