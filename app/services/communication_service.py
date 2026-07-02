from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session
from app.models.communication import Communication
from app.models.participant import Participant
from app.core.config import settings

TEMPLATES = {
    "registration_confirmed": {
        "subject": "You're registered for the hackathon!",
        "body": "Hi {name}, your registration is confirmed. Get ready to build something amazing!",
        "channel": "email",
    },
    "team_formed": {
        "subject": "Your team is set — let's go!",
        "body": "Hi {name}, your team '{team_name}' has been formed. Start collaborating!",
        "channel": "email",
    },
    "project_submitted": {
        "subject": "Project submission received",
        "body": "Hi {name}, we received your project '{project_title}'. Reviewers will be assigned shortly.",
        "channel": "email",
    },
    "reviewer_assigned": {
        "subject": "You have a new project to review",
        "body": "Hi {name}, you've been assigned to review '{project_title}'. Please submit your evaluation by the deadline.",
        "channel": "email",
    },
    "results_published": {
        "subject": "Hackathon results are live!",
        "body": "Hi {name}, the results are in! Visit the dashboard to see the final rankings.",
        "channel": "email",
    },
    "bias_flag_alert": {
        "subject": "[Admin] Bias flag detected",
        "body": "A potential {bias_type} bias was detected for project '{project_title}'. Please review.",
        "channel": "email",
    },
    "voice_participant_status": {
        "subject": "Your Hackathon Status",
        "body": "Hi {name}, here is your requested status update from the AI Assistant:<br><br>{status_text}",
        "channel": "email",
    },
    "voice_team_intro": {
        "subject": "HackBridge Matchmaking: Introduction",
        "body": "Hi team, meet {name}! They are interested in joining your team '{team_name}'. {name}'s skills are: {skills}. <br><br>Please connect and see if it's a good match!",
        "channel": "email",
    },
}


def send_notification(db: Session, participant_id: int, template_key: str, context: dict):
    t = TEMPLATES.get(template_key)
    if not t:
        raise ValueError(f"Unknown template: {template_key}")

    subject = t["subject"].format(**context)
    body = t["body"].format(**context)

    # Save to DB
    record = Communication(
        participant_id=participant_id,
        template_key=template_key,
        channel=t["channel"],
        subject=subject,
        body=body,
        status="sent",
        sent_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Send email
    if t["channel"] == "email" and settings.resend_api_key:
        participant = db.query(Participant).filter(Participant.id == participant_id).first()
        if participant and participant.email:
            try:
                response = httpx.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                    json={
                        "from": "onboarding@resend.dev",
                        "to": [participant.email],
                        "subject": subject,
                        "html": f"<p>{body}</p>",
                    },
                    timeout=10,
                )
                if response.status_code >= 400:
                    print(f"[CommunicationService] Resend API Error ({response.status_code}): {response.text}")
                else:
                    print(f"[CommunicationService] Email sent successfully to {participant.email}")
            except Exception as exc:
                print(f"[CommunicationService] Email send exception: {exc}")

    return record


def get_notifications_for_participant(db: Session, participant_id: int):
    return (
        db.query(Communication)
        .filter(Communication.participant_id == participant_id)
        .order_by(Communication.sent_at.desc())
        .all()
    )


def get_all_notifications(db: Session, limit: int = 100):
    return (
        db.query(Communication)
        .order_by(Communication.sent_at.desc())
        .limit(limit)
        .all()
    )
