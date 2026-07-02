import logging
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session
from app.models.communication import Communication
from app.models.participant import Participant
from app.core.config import settings
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

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


def send_notification(
    db: Session | None,
    participant_id: int,
    template_key: str,
    context: dict,
):
    """
    Send a notification to a participant.

    IMPORTANT for FastAPI BackgroundTasks:
    When called from background_tasks.add_task(), the request-scoped 'db' session
    is already closed by the time the task runs. Pass db=None in that case and
    this function will open (and close) its own session.
    """
    # Use a fresh session when called from a background task (db may be closed)
    _own_session = db is None
    if _own_session:
        db = SessionLocal()
        logger.info(f"[CommunicationService] Created new DB session for background task (participant_id={participant_id})")

    try:
        t = TEMPLATES.get(template_key)
        if not t:
            raise ValueError(f"Unknown template key: {template_key}")

        subject = t["subject"].format(**context)
        body = t["body"].format(**context)

        # Persist a communication record — default status is 'pending' until we know the send outcome
        record = Communication(
            participant_id=participant_id,
            template_key=template_key,
            channel=t["channel"],
            subject=subject,
            body=body,
            status="pending",
            sent_at=datetime.now(timezone.utc),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(f"[CommunicationService] Communication record created: id={record.id}, template='{template_key}'")

        # --- Send email via Resend ---
        if t["channel"] == "email":
            if not settings.resend_api_key:
                logger.warning(
                    "[CommunicationService] RESEND_API_KEY is not set in environment — "
                    "skipping email send. Check your .env file."
                )
                record.status = "skipped_no_api_key"
                db.commit()
                return record

            participant = db.query(Participant).filter(Participant.id == participant_id).first()
            if not participant or not participant.email:
                logger.warning(
                    f"[CommunicationService] Cannot send email: participant id={participant_id} "
                    f"not found or has no email address."
                )
                record.status = "failed_no_recipient"
                db.commit()
                return record

            logger.info(
                f"[CommunicationService] Sending email via Resend → to='{participant.email}', "
                f"subject='{subject}'"
            )

            payload = {
                "from": settings.resend_from_email,
                "to": [participant.email],
                "subject": subject,
                "html": f"<p>{body}</p>",
            }
            logger.info(f"[CommunicationService] Resend payload: {payload}")

            try:
                response = httpx.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.resend_api_key.strip()}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=10,
                )

                # --- Full response logging ---
                logger.info(
                    f"[CommunicationService] Resend HTTP {response.status_code}: {response.text}"
                )

                if response.status_code >= 400:
                    logger.error(
                        f"[CommunicationService] ❌ Resend API returned an error!\n"
                        f"  Status : {response.status_code}\n"
                        f"  Body   : {response.text}\n"
                        f"  👉 Common causes:\n"
                        f"     - 'onboarding@resend.dev' only works when sending TO the account owner's email on the free plan.\n"
                        f"     - You may need to verify a custom domain in Resend and change the 'from' address.\n"
                        f"     - Double-check RESEND_API_KEY in your .env."
                    )
                    record.status = "failed"
                else:
                    logger.info(
                        f"[CommunicationService] ✅ Email sent to '{participant.email}' | "
                        f"Resend id: {response.json().get('id', 'N/A')}"
                    )
                    record.status = "sent"

                db.commit()

            except httpx.TimeoutException as exc:
                logger.error(f"[CommunicationService] Resend request timed out: {exc}")
                record.status = "failed_timeout"
                db.commit()
            except Exception as exc:
                logger.exception(f"[CommunicationService] Unexpected error sending email: {exc}")
                record.status = "failed_exception"
                db.commit()

        return record

    finally:
        if _own_session:
            db.close()
            logger.info("[CommunicationService] Closed background-task DB session.")


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
