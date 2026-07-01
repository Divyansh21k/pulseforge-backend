"""
Voice Assistant – Vapi webhook router
Demo feature for HackBridge final presentation.
Handles tool-calls from Vapi and returns results the AI reads back to the caller.
"""

import json
import httpx
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.event import Event
from app.models.participant import Participant
from app.models.team import Team, TeamMember

router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])

# ── Resend credentials ──────────────────────────────────────────────────────
RESEND_API_KEY = "re_87JhQY9A_btDFrznTaYWnTyTfmrwbr7Ev"
RESEND_FROM    = "onboarding@resend.dev"


# ── Webhook entry-point ─────────────────────────────────────────────────────
@router.post("/vapi-webhook")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Vapi calls this endpoint whenever the AI agent needs to run a tool.
    Expected body:
    {
      "message": {
        "type": "tool-calls",
        "toolCalls": [
          { "id": "...", "function": { "name": "...", "arguments": "{}" } }
        ]
      }
    }
    """
    body    = await request.json()
    message = body.get("message", {})

    if message.get("type") != "tool-calls":
        return {"results": []}

    results = []
    for call in message.get("toolCalls", []):
        call_id = call.get("id", "")
        fn_name = call.get("function", {}).get("name", "")
        raw_args = call.get("function", {}).get("arguments", "{}")
        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

        if fn_name == "get_upcoming_events":
            result = _get_upcoming_events(db)
        elif fn_name == "register_participant":
            result = _register_participant(args, db)
        elif fn_name == "find_teams_by_skills":
            result = _find_teams_by_skills(args, db)
        else:
            result = f"Unknown tool: {fn_name}"

        results.append({"toolCallId": call_id, "result": result})

    return {"results": results}


# ── Tool implementations ────────────────────────────────────────────────────

def _get_upcoming_events(db: Session) -> str:
    events = (
        db.query(Event)
        .filter(Event.status == "upcoming")
        .limit(5)
        .all()
    )
    if not events:
        # Fall back to any event if no upcoming ones exist
        events = db.query(Event).limit(5).all()
    if not events:
        return "There are no hackathon events registered yet."

    lines = []
    for e in events:
        date_str = e.start_date.strftime("%B %d, %Y") if e.start_date else "date TBD"
        lines.append(f"{e.name} (theme: {e.theme or 'General'}, date: {date_str})")
    return "Upcoming hackathons: " + "; ".join(lines)


def _register_participant(args: dict, db: Session) -> str:
    name   = args.get("name", "").strip()
    email  = args.get("email", "").strip()
    skills = args.get("skills", "").strip()

    if not name or not email:
        return "I need your full name and email address to register you."

    # Check duplicate
    existing = db.query(Participant).filter(Participant.email == email).first()
    if existing:
        _send_email(
            to=email,
            subject="You're already registered for HackBridge!",
            body=f"Hi {name}, you're already in our system. See you at the hackathon!",
        )
        return f"{name}, you are already registered! A reminder email has been sent to {email}."

    participant = Participant(
        full_name=name,
        email=email,
        raw_skills_text=skills,
        role="participant",
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)

    _send_email(
        to=email,
        subject="🎉 You're registered for HackBridge!",
        body=(
            f"Hi {name},<br><br>"
            f"You're officially registered for HackBridge!<br>"
            f"<b>Your skills:</b> {skills or 'Not provided'}<br><br>"
            f"We'll match you with a team soon. Stay tuned!"
        ),
    )
    return (
        f"Done! {name} is now registered. "
        f"A confirmation email has been sent to {email}."
    )


def _find_teams_by_skills(args: dict, db: Session) -> str:
    skill_query = args.get("skills", "").lower().strip()
    if not skill_query:
        return "Please tell me which skills you are looking for."

    # Load all teams with their members
    teams = db.query(Team).all()
    matching = []

    for team in teams:
        members = (
            db.query(Participant)
            .join(TeamMember, TeamMember.participant_id == Participant.id)
            .filter(TeamMember.team_id == team.id)
            .all()
        )
        # Collect all skills text from team members
        team_skills = " ".join(
            (m.raw_skills_text or "") for m in members
        ).lower()

        if skill_query in team_skills or any(
            skill_query in (m.raw_skills_text or "").lower() for m in members
        ):
            member_names = ", ".join(m.full_name for m in members) or "no members yet"
            matching.append(f"{team.name} (members: {member_names})")

    if not matching:
        return (
            f"No teams found with '{skill_query}' skills right now. "
            f"You could start a new team!"
        )

    return f"Teams matching '{skill_query}': " + "; ".join(matching[:5])


# ── Email helper ────────────────────────────────────────────────────────────

def _send_email(to: str, subject: str, body: str) -> None:
    """Send an email via the Resend REST API (fire-and-forget for demo)."""
    try:
        httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": RESEND_FROM,
                "to": [to],
                "subject": subject,
                "html": f"<p>{body}</p>",
            },
            timeout=10,
        )
    except Exception as exc:
        print(f"[Voice] Email send failed: {exc}")
