from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.communication import Communication

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
}


def send_notification(db: Session, participant_id: int, template_key: str, context: dict):
    t = TEMPLATES.get(template_key)
    if not t:
        raise ValueError(f"Unknown template: {template_key}")

    record = Communication(
        participant_id=participant_id,
        template_key=template_key,
        channel=t["channel"],
        subject=t["subject"].format(**context),
        body=t["body"].format(**context),
        status="sent",
        sent_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
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
