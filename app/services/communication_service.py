import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
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
    "voice_call_summary": {
        "subject": "📞 Your HackBridge Call Summary",
        "body": (
            "Hi {name},<br><br>"
            "Thanks for calling the HackBridge AI Voice Assistant! Here's a summary of your call:<br><br>"
            "<strong>Summary:</strong><br>{summary}<br><br>"
            "<strong>Call Transcript (excerpt):</strong><br>"
            "<pre style='background:#f4f4f4;padding:12px;border-radius:6px;font-size:13px;'>{transcript}</pre>"
            "<br>If you need anything else, call us again or visit the web dashboard.<br><br>"
            "— The HackBridge Team"
        ),
        "channel": "email",
    },
    "voice_team_match": {
        "subject": "🤝 HackBridge AI Found You a Team Match!",
        "body": (
            "Hi {name},<br><br>"
            "Our AI Voice Assistant found a great team match for your skills!<br><br>"
            "<strong>Recommended Team:</strong> {team_name}<br>"
            "<strong>Current Members:</strong> {member_names}<br>"
            "<strong>Your Skills:</strong> {skills}<br>"
            "<strong>What this team needs:</strong> {gaps}<br><br>"
            "To connect with them, call the HackBridge Voice Assistant and say "
            "<em>'Request introduction to team {team_name}'</em>, "
            "or visit the web dashboard to reach out directly.<br><br>"
            "— The HackBridge AI Matchmaker"
        ),
        "channel": "email",
    },
    "voice_reviewer_schedule": {
        "subject": "📋 Your HackBridge Review Assignments",
        "body": (
            "Hi {name},<br><br>"
            "Here are your current project review assignments from HackBridge:<br><br>"
            "{assignments_text}<br><br>"
            "Please submit all evaluations before the deadline. "
            "You can access the evaluation interface on the web dashboard.<br><br>"
            "— The HackBridge Team"
        ),
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

        # --- Send email via Gmail SMTP ---
        if t["channel"] == "email":
            if not settings.gmail_sender_email or not settings.gmail_app_password:
                logger.warning(
                    "[CommunicationService] GMAIL_SENDER_EMAIL or GMAIL_APP_PASSWORD is not set — "
                    "skipping email send. Check your .env file."
                )
                record.status = "skipped_no_config"
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
                f"[CommunicationService] Sending email via Gmail SMTP → "
                f"to='{participant.email}', subject='{subject}'"
            )

            try:
                # Build the email message
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"PulseForge <{settings.gmail_sender_email}>"
                msg["To"] = participant.email

                # Plain-text fallback + HTML version
                plain_body = body.replace("<br>", "\n").replace("<br/>", "\n")
                msg.attach(MIMEText(plain_body, "plain"))
                msg.attach(MIMEText(f"<p>{body}</p>", "html"))

                # Connect to Gmail's SMTP server over TLS (port 465)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(
                        settings.gmail_sender_email.strip(),
                        settings.gmail_app_password.strip(),
                    )
                    server.sendmail(
                        settings.gmail_sender_email.strip(),
                        participant.email,
                        msg.as_string(),
                    )

                logger.info(
                    f"[CommunicationService] ✅ Email sent successfully to '{participant.email}'"
                )
                record.status = "sent"
                db.commit()

            except smtplib.SMTPAuthenticationError:
                logger.error(
                    "[CommunicationService] ❌ Gmail authentication failed!\n"
                    "  👉 Make sure you are using a Gmail APP PASSWORD (not your normal Gmail password).\n"
                    "  Generate one at: myaccount.google.com → Security → App Passwords"
                )
                record.status = "failed_auth"
                db.commit()
            except smtplib.SMTPException as exc:
                logger.error(f"[CommunicationService] ❌ Gmail SMTP error: {exc}")
                record.status = "failed_smtp"
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
