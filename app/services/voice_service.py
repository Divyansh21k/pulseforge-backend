import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.participant import Participant
from app.models.team import Team, TeamMember
from app.models.project import Project
from app.models.reviewer import ReviewerAssignment
from app.repositories.participant_repository import ParticipantRepository
from app.services.communication_service import send_notification

def normalize_spoken_email(email: str) -> str:
    """Normalizes spoken email addresses (e.g., 'john dot doe at gmail dot com' -> 'john.doe@gmail.com')"""
    if not email:
        return ""
    email = email.lower()
    email = email.replace(" at ", "@")
    email = email.replace(" dot ", ".")
    email = re.sub(r"\s+", "", email)
    return email


def format_vapi_response(text: str) -> str:
    return f"[SYSTEM: Read the following exactly to the user:] {text}"


def get_upcoming_events(db: Session) -> str:
    events = db.query(Event).filter(Event.status == "upcoming").limit(5).all()
    if not events:
        events = db.query(Event).limit(5).all()
    if not events:
        return format_vapi_response("There are no hackathon events registered yet.")

    lines = []
    for e in events:
        date_str = e.start_date.strftime("%B %d, %Y") if e.start_date else "date TBD"
        lines.append(f"{e.name} (theme: {e.theme or 'General'}, date: {date_str})")
    return format_vapi_response("Upcoming hackathons: " + "; ".join(lines))


def get_hackathon_info(db: Session) -> str:
    # Gets general information about the current or next event
    event = db.query(Event).filter(Event.status == "upcoming").first()
    if not event:
        event = db.query(Event).first()
    
    if not event:
        return format_vapi_response("We don't have any hackathons currently scheduled.")
        
    date_str = event.start_date.strftime("%B %d, %Y") if event.start_date else "date TBD"
    return format_vapi_response(f"The hackathon is called {event.name}. The theme is {event.theme or 'General'}. It starts on {date_str}. Let me know if you want to register or find a team!")


def register_participant(args: dict, caller_phone: str, db: Session) -> str:
    name = args.get("name", "").strip()
    email = normalize_spoken_email(args.get("email", "").strip())
    skills = args.get("skills", "").strip()
    
    # Check by phone first if provided, else email
    repo = ParticipantRepository(db)
    
    if not name or not email:
        return format_vapi_response("I need your full name and email address to register you.")
        
    existing = repo.get_by_email(email)
    if existing:
        send_notification(
            db=db,
            participant_id=existing.id,
            template_key="registration_confirmed",
            context={"name": existing.full_name}
        )
        return format_vapi_response(f"{existing.full_name}, you are already registered! A reminder email has been sent.")
        
    participant = repo.create(
        full_name=name,
        email=email,
        phone=caller_phone if caller_phone else None,
        organization=None,
        raw_skills_text=skills
    )
    
    send_notification(
        db=db,
        participant_id=participant.id,
        template_key="registration_confirmed",
        context={"name": participant.full_name}
    )
    return format_vapi_response(f"Done! {name} is now registered. A confirmation email has been sent to {email}.")


def find_teams_by_skills(args: dict, db: Session) -> str:
    skill_query = args.get("skills", "").lower().strip()
    if not skill_query:
        return "Please tell me which skills you are looking for."

    teams = db.query(Team).all()
    matching = []

    for team in teams:
        members = (
            db.query(Participant)
            .join(TeamMember, TeamMember.participant_id == Participant.id)
            .filter(TeamMember.team_id == team.id)
            .all()
        )
        team_skills = " ".join((m.raw_skills_text or "") for m in members).lower()

        if skill_query in team_skills or any(skill_query in (m.raw_skills_text or "").lower() for m in members):
            member_names = ", ".join(m.full_name for m in members) or "no members yet"
            matching.append(f"{team.name} (members: {member_names})")

    if not matching:
        return format_vapi_response(f"No teams found with '{skill_query}' skills right now. You could start a new team!")

    return format_vapi_response(f"Teams matching '{skill_query}': " + "; ".join(matching[:5]))


def get_participant_status(args: dict, caller_phone: str, db: Session) -> str:
    email = normalize_spoken_email(args.get("email", "").strip())
    repo = ParticipantRepository(db)
    
    participant = None
    if caller_phone:
        participant = repo.get_by_phone(caller_phone)
    if not participant and email:
        participant = repo.get_by_email(email)
        
    if not participant:
        return format_vapi_response("I couldn't find a registration for that phone number or email. Would you like to register?")
        
    # Get team info
    team_member = db.query(TeamMember).filter(TeamMember.participant_id == participant.id).first()
    team_status = "You are not currently in a team."
    project_status = ""
    
    if team_member:
        team = db.query(Team).filter(Team.id == team_member.team_id).first()
        if team:
            team_status = f"You are on team '{team.name}'."
            # Get project info
            project = db.query(Project).filter(Project.team_id == team.id).first()
            if project:
                project_status = f"Your team has submitted a project called '{project.title}'."
            else:
                project_status = "Your team hasn't submitted a project yet."
                
    full_status = f"You are registered as {participant.full_name}. {team_status} {project_status}"
    
    send_notification(
        db=db,
        participant_id=participant.id,
        template_key="voice_participant_status",
        context={"name": participant.full_name, "status_text": full_status}
    )
    
    return format_vapi_response(full_status)


def request_team_join(args: dict, caller_phone: str, db: Session) -> str:
    team_name = args.get("team_name", "").strip()
    email = normalize_spoken_email(args.get("email", "").strip())
    
    if not team_name:
        return format_vapi_response("Please specify the name of the team you want to join.")
        
    repo = ParticipantRepository(db)
    participant = None
    if caller_phone:
        participant = repo.get_by_phone(caller_phone)
    if not participant and email:
        participant = repo.get_by_email(email)
        
    if not participant:
        return format_vapi_response("I need to know who you are first. Are you registered?")
        
    team = db.query(Team).filter(Team.name.ilike(f"%{team_name}%")).first()
    if not team:
        return format_vapi_response(f"I couldn't find a team named {team_name}.")
        
    team_members = db.query(Participant).join(TeamMember, TeamMember.participant_id == Participant.id).filter(TeamMember.team_id == team.id).all()
    
    if not team_members:
        return format_vapi_response(f"Team {team.name} doesn't have any members to email.")
        
    # Send email to the first team member (e.g. leader)
    leader = team_members[0]
    
    send_notification(
        db=db,
        participant_id=leader.id,
        template_key="voice_team_intro",
        context={
            "name": participant.full_name,
            "team_name": team.name,
            "skills": participant.raw_skills_text or "General skills"
        }
    )
    
    return format_vapi_response(f"I have sent an introduction email to the members of team {team.name}. They will be in touch!")


def get_reviewer_assignments(args: dict, caller_phone: str, db: Session) -> str:
    email = normalize_spoken_email(args.get("email", "").strip())
    repo = ParticipantRepository(db)
    
    reviewer = None
    if caller_phone:
        reviewer = repo.get_by_phone(caller_phone)
    if not reviewer and email:
        reviewer = repo.get_by_email(email)
        
    if not reviewer:
        return format_vapi_response("I couldn't find your reviewer profile.")
        
    if reviewer.role != "reviewer":
        return format_vapi_response("You are not registered as a reviewer.")
        
    assignments = db.query(ReviewerAssignment).filter(ReviewerAssignment.reviewer_id == reviewer.id).all()
    
    if not assignments:
        return format_vapi_response("You haven't been assigned any projects yet.")
        
    project_titles = []
    for a in assignments:
        p = db.query(Project).filter(Project.id == a.project_id).first()
        if p:
            project_titles.append(p.title)
            
    return format_vapi_response(f"You have {len(assignments)} projects assigned to review: " + ", ".join(project_titles))


def create_hackathon_event(args: dict, caller_phone: str, db: Session) -> str:
    name = args.get("name", "").strip()
    theme = args.get("theme", "").strip()
    email = normalize_spoken_email(args.get("email", "").strip())
    
    if not name:
        return format_vapi_response("Please provide a name for the hackathon.")
        
    repo = ParticipantRepository(db)
    host = None
    if caller_phone:
        host = repo.get_by_phone(caller_phone)
    if not host and email:
        host = repo.get_by_email(email)
        
    if not host:
        return format_vapi_response("I couldn't find your profile. Only registered hosts can create events.")
        
    event = Event(
        name=name,
        theme=theme,
        organizer_id=host.id,
        start_date=datetime.now(timezone.utc),
        status="upcoming"
    )
    db.add(event)
    db.commit()
    
    return format_vapi_response(f"Excellent! The hackathon '{name}' with the theme '{theme}' has been created.")
