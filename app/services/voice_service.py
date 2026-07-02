"""
HackBridge AI Voice Assistant — Service Layer
=============================================
Implements every tool function callable by the Vapi AI assistant.
Each function is thin by design: it reads from / writes to the DB
through the existing repository and service layer, then returns a
voice-friendly string that Vapi reads back to the caller.

Architecture contract:
  - Never duplicate business logic that already lives in a service/repo.
  - Use background_tasks for email (avoids blocking the Vapi webhook response).
  - All email sends pass db=None so send_notification opens its own session
    (the request-scoped session is closed before BackgroundTasks run).
"""

import json
import logging
import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.participant import Participant
from app.models.team import Team, TeamMember
from app.models.project import Project
from app.models.reviewer import Reviewer
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.reviewer_repository import ReviewerRepository, ReviewerAssignmentRepository
from app.repositories.event_repository import EventRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_repository import TeamRepository
from app.services.communication_service import send_notification
from app.services.results import ResultsService
from app.services.analytics import AnalyticsService
from app.services.team_composition import TeamCompositionService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_spoken_email(email: str) -> str:
    """Normalise spoken email addresses.
    e.g. 'john dot doe at gmail dot com' → 'john.doe@gmail.com'
    """
    if not email:
        return ""
    email = email.lower().strip()
    email = email.replace(" at ", "@")
    email = email.replace(" dot ", ".")
    email = re.sub(r"\s+", "", email)
    return email


def _voice(text: str) -> str:
    """Pass-through — returns the text Vapi will speak back to the caller.
    Kept as a named function so we can add post-processing (e.g. SSML) later.
    """
    return text


def _find_participant(db: Session, caller_phone: str, email: str = "") -> Optional[Participant]:
    """Look up a participant by phone (caller ID) or by spoken email."""
    repo = ParticipantRepository(db)
    if caller_phone:
        p = repo.get_by_phone(caller_phone)
        if p:
            return p
    if email:
        return repo.get_by_email(normalize_spoken_email(email))
    return None


def _find_reviewer(db: Session, caller_phone: str, email: str = "") -> Optional[Reviewer]:
    """Look up a reviewer by email (reviewers table, not participants)."""
    repo = ReviewerRepository(db)
    if email:
        r = repo.get_by_email(normalize_spoken_email(email))
        if r:
            return r
    # Reviewers may also be linked to a participant with a phone number.
    if caller_phone:
        p_repo = ParticipantRepository(db)
        participant = p_repo.get_by_phone(caller_phone)
        if participant:
            r = db.query(Reviewer).filter(Reviewer.participant_id == participant.id).first()
            if r:
                return r
    return None


# ---------------------------------------------------------------------------
# Tool: get_upcoming_events
# ---------------------------------------------------------------------------

def get_upcoming_events(db: Session) -> str:
    """Returns a voice-friendly list of all events (any status), not just 'upcoming'."""
    events = db.query(Event).limit(5).all()
    if not events:
        return _voice(
            "There are currently no hackathon events in the system. "
            "Please check back soon or contact the organizer."
        )

    lines = []
    for e in events:
        date_str = e.start_date.strftime("%B %d, %Y") if e.start_date else "date to be announced"
        status_label = {
            "upcoming": "coming up",
            "ongoing": "currently live",
            "completed": "completed",
        }.get(e.status or "upcoming", e.status or "upcoming")
        lines.append(f"{e.name} (theme: {e.theme or 'General'}, date: {date_str}, status: {status_label})")

    return _voice("Here are the hackathon events: " + ". Next: ".join(lines) + ".")


# ---------------------------------------------------------------------------
# Tool: get_hackathon_info
# ---------------------------------------------------------------------------

def get_hackathon_info(db: Session) -> str:
    """Gets rich information about the most relevant event."""
    # Prefer an ongoing or upcoming event; fall back to any event.
    event = (
        db.query(Event).filter(Event.status == "ongoing").first()
        or db.query(Event).filter(Event.status == "upcoming").first()
        or db.query(Event).first()
    )

    if not event:
        return _voice(
            "There are no hackathon events registered yet. "
            "Stay tuned or contact the organizer for details."
        )

    date_str = event.start_date.strftime("%B %d, %Y") if event.start_date else "date to be announced"
    end_str = event.end_date.strftime("%B %d, %Y") if event.end_date else "end date to be announced"
    return _voice(
        f"The hackathon is called {event.name}. "
        f"The theme is {event.theme or 'General'}. "
        f"It runs from {date_str} to {end_str}. "
        "Tell me if you'd like to register, find a team, or check your status!"
    )


# ---------------------------------------------------------------------------
# Tool: register_participant
# ---------------------------------------------------------------------------

def register_participant(args: dict, caller_phone: str, background_tasks: BackgroundTasks, db: Session) -> str:
    name = args.get("name", "").strip()
    email = normalize_spoken_email(args.get("email", "").strip())
    skills = args.get("skills", "").strip()

    if not name or not email:
        return _voice("I need your full name and email address to register you. Could you please provide both?")

    repo = ParticipantRepository(db)
    existing = repo.get_by_email(email)
    if existing:
        background_tasks.add_task(
            send_notification,
            db=None,
            participant_id=existing.id,
            template_key="registration_confirmed",
            context={"name": existing.full_name},
        )
        return _voice(
            f"Great news! {existing.full_name}, you are already registered. "
            "I've just sent you a reminder email with all the details."
        )

    participant = repo.create(
        full_name=name,
        email=email,
        phone=caller_phone if caller_phone else None,
        organization=None,
        raw_skills_text=skills,
    )

    background_tasks.add_task(
        send_notification,
        db=None,
        participant_id=participant.id,
        template_key="registration_confirmed",
        context={"name": participant.full_name},
    )
    return _voice(
        f"You're all set, {name}! Registration is confirmed. "
        f"I've sent a confirmation email to {email}. "
        "Would you like me to help you find a team next?"
    )


# ---------------------------------------------------------------------------
# Tool: find_teams_by_skills
# ---------------------------------------------------------------------------

def find_teams_by_skills(args: dict, db: Session) -> str:
    skill_query = args.get("skills", "").lower().strip()
    if not skill_query:
        return _voice("Which skills are you looking for in a team? Please tell me, for example, Python, machine learning, or mobile development.")

    teams = db.query(Team).all()
    matching = []

    for team in teams:
        members = (
            db.query(Participant)
            .join(TeamMember, TeamMember.participant_id == Participant.id)
            .filter(TeamMember.team_id == team.id)
            .all()
        )
        team_skills_text = " ".join((m.raw_skills_text or "") for m in members).lower()
        has_skill = skill_query in team_skills_text or any(
            skill_query in (m.raw_skills_text or "").lower() for m in members
        )
        if has_skill:
            member_names = ", ".join(m.full_name for m in members) or "no members yet"
            matching.append(
                f"{team.name} with {len(members)} member(s): {member_names}"
            )

    if not matching:
        return _voice(
            f"I couldn't find any teams with '{skill_query}' skills right now. "
            "You could start your own team, or I can help you find a team that needs those skills."
        )

    return _voice(
        f"I found {len(matching)} team(s) with '{skill_query}' skills: "
        + "; ".join(matching[:5])
        + ". Would you like to request an introduction to any of them?"
    )


# ---------------------------------------------------------------------------
# Tool: get_participant_status
# ---------------------------------------------------------------------------

def get_participant_status(args: dict, caller_phone: str, background_tasks: BackgroundTasks, db: Session) -> str:
    email = args.get("email", "").strip()
    participant = _find_participant(db, caller_phone, email)

    if not participant:
        return _voice(
            "I couldn't find a registration for that phone number or email. "
            "Would you like to register for the hackathon?"
        )

    team_member = db.query(TeamMember).filter(TeamMember.participant_id == participant.id).first()
    team_status = "You are not currently in a team."
    project_status = ""

    if team_member:
        team = db.query(Team).filter(Team.id == team_member.team_id).first()
        if team:
            team_status = f"You are on team '{team.name}'."
            project = db.query(Project).filter(Project.team_id == team.id).first()
            if project:
                project_status = f"Your team has submitted a project called '{project.title}'."
            else:
                project_status = "Your team hasn't submitted a project yet."

    full_status = f"You are registered as {participant.full_name}. {team_status} {project_status}".strip()

    background_tasks.add_task(
        send_notification,
        db=None,
        participant_id=participant.id,
        template_key="voice_participant_status",
        context={"name": participant.full_name, "status_text": full_status},
    )
    return _voice(full_status + " I've also emailed you a copy of this status update.")


# ---------------------------------------------------------------------------
# Tool: request_team_join
# ---------------------------------------------------------------------------

def request_team_join(args: dict, caller_phone: str, background_tasks: BackgroundTasks, db: Session) -> str:
    team_name = args.get("team_name", "").strip()
    email = args.get("email", "").strip()

    if not team_name:
        return _voice("Which team would you like to join? Please tell me the team name.")

    participant = _find_participant(db, caller_phone, email)
    if not participant:
        return _voice(
            "I need to verify your identity first. Are you registered? "
            "If so, please provide your email address."
        )

    team = db.query(Team).filter(Team.name.ilike(f"%{team_name}%")).first()
    if not team:
        return _voice(f"I couldn't find a team called '{team_name}'. Could you double-check the name?")

    team_members = (
        db.query(Participant)
        .join(TeamMember, TeamMember.participant_id == Participant.id)
        .filter(TeamMember.team_id == team.id)
        .all()
    )

    if not team_members:
        return _voice(f"Team '{team.name}' doesn't have any members to contact yet.")

    # Send introduction email to all current team members
    for member in team_members:
        background_tasks.add_task(
            send_notification,
            db=None,
            participant_id=member.id,
            template_key="voice_team_intro",
            context={
                "name": participant.full_name,
                "team_name": team.name,
                "skills": participant.raw_skills_text or "General skills",
            },
        )

    return _voice(
        f"Done! I've sent your introduction to all {len(team_members)} member(s) of team '{team.name}'. "
        "They'll reach out to you via the email they registered with. Good luck!"
    )


# ---------------------------------------------------------------------------
# Tool: get_reviewer_assignments
# ---------------------------------------------------------------------------

def get_reviewer_assignments(args: dict, caller_phone: str, db: Session) -> str:
    """FIXED: looks in the reviewers table, not participants."""
    email = args.get("email", "").strip()
    reviewer = _find_reviewer(db, caller_phone, email)

    if not reviewer:
        return _voice(
            "I couldn't find a reviewer profile for that email or phone number. "
            "Are you sure you're registered as a reviewer?"
        )

    assignment_repo = ReviewerAssignmentRepository(db)
    assignments = assignment_repo.list_for_reviewer(reviewer.id)

    if not assignments:
        return _voice(
            f"Hi {reviewer.full_name}, you don't have any project assignments yet. "
            "Assignments will appear here once the organizer runs the matching algorithm."
        )

    project_repo = ProjectRepository(db)
    titles = []
    for a in assignments:
        project = project_repo.get_by_id(a.project_id)
        if project:
            titles.append(f"'{project.title}' (status: {a.status})")

    return _voice(
        f"Hi {reviewer.full_name}, you have {len(assignments)} project(s) assigned: "
        + ", ".join(titles)
        + ". Would you like me to email you the full details?"
    )


# ---------------------------------------------------------------------------
# Tool: create_hackathon_event
# ---------------------------------------------------------------------------

def create_hackathon_event(args: dict, caller_phone: str, background_tasks: BackgroundTasks, db: Session) -> str:
    """FIXED: uses EventRepository and looks up the host properly."""
    name = args.get("name", "").strip()
    theme = args.get("theme", "").strip()
    email = args.get("email", "").strip()

    if not name:
        return _voice("What would you like to name the hackathon?")

    participant = _find_participant(db, caller_phone, email)
    if not participant:
        return _voice("I couldn't find your profile. Only registered organizers can create events via this line.")

    event_repo = EventRepository(db)
    from datetime import timedelta
    event = event_repo.create(
        name=name,
        theme=theme or "General",
        organizer_id=participant.id,
        start_date=datetime.now(timezone.utc) + timedelta(days=7),
        end_date=datetime.now(timezone.utc) + timedelta(days=9),
    )

    return _voice(
        f"Excellent! The hackathon '{event.name}' with the theme '{event.theme}' has been created "
        f"and is scheduled for one week from today. "
        "You can update the exact dates from the web dashboard."
    )


# ---------------------------------------------------------------------------
# Tool: get_project_rankings  (NEW)
# ---------------------------------------------------------------------------

def get_project_rankings(db: Session) -> str:
    """Returns the top projects on the live leaderboard."""
    try:
        service = ResultsService(db)
        rankings = service.generate_rankings()
        ranked = [r for r in rankings if r.get("status") == "ranked"]

        if not ranked:
            return _voice(
                "The leaderboard isn't ready yet. "
                "Evaluations may still be in progress or scores haven't been normalized. Check back soon!"
            )

        top3 = ranked[:3]
        lines = []
        for r in top3:
            lines.append(
                f"#{r['rank']}: {r['title']} "
                f"with a score of {r['mean_score']} "
                f"and {r['reviewer_count']} reviewer(s)"
            )

        suffix = ""
        if len(ranked) > 3:
            suffix = f" There are {len(ranked)} teams ranked in total."

        return _voice(
            f"Here are the top {len(top3)} projects right now: "
            + ". ".join(lines)
            + "."
            + suffix
        )
    except Exception as e:
        logger.error(f"[VoiceService] get_project_rankings error: {e}")
        return _voice("I couldn't retrieve the rankings right now. Please try again shortly.")


# ---------------------------------------------------------------------------
# Tool: get_project_feedback  (NEW)
# ---------------------------------------------------------------------------

def get_project_feedback(args: dict, db: Session) -> str:
    """Returns reviewer feedback for a named project."""
    project_name = args.get("project_name", "").strip()
    if not project_name:
        return _voice("Which project would you like feedback for? Please tell me the project name.")

    project_repo = ProjectRepository(db)
    all_projects = project_repo.list_all()
    project = next(
        (p for p in all_projects if project_name.lower() in p.title.lower()),
        None
    )

    if not project:
        return _voice(f"I couldn't find a project named '{project_name}'. Could you double-check the name?")

    try:
        service = ResultsService(db)
        feedback = service.generate_feedback(project.id)

        if not feedback.get("criteria_breakdown"):
            return _voice(f"No evaluations have been submitted for '{project.title}' yet.")

        cb = feedback["criteria_breakdown"]
        reviewer_count = feedback.get("reviewer_count", 0)
        comments = feedback.get("reviewer_comments", [])

        text = (
            f"Feedback for '{project.title}' based on {reviewer_count} reviewer(s): "
            f"Innovation scored {cb.get('innovation', 'N/A')} out of 10, "
            f"Technical execution scored {cb.get('technical', 'N/A')}, "
            f"Impact scored {cb.get('impact', 'N/A')}, "
            f"and Presentation scored {cb.get('presentation', 'N/A')}. "
        )
        if comments:
            text += f"A reviewer noted: '{comments[0]}'."

        return _voice(text)
    except Exception as e:
        logger.error(f"[VoiceService] get_project_feedback error: {e}")
        return _voice("I couldn't retrieve the feedback right now. Please try again shortly.")


# ---------------------------------------------------------------------------
# Tool: get_team_details  (NEW)
# ---------------------------------------------------------------------------

def get_team_details(args: dict, db: Session) -> str:
    """Returns details about a named team including members and skills."""
    team_name = args.get("team_name", "").strip()
    if not team_name:
        return _voice("Which team would you like to know about? Please tell me the team name.")

    team = db.query(Team).filter(Team.name.ilike(f"%{team_name}%")).first()
    if not team:
        return _voice(f"I couldn't find a team named '{team_name}'.")

    members = (
        db.query(Participant)
        .join(TeamMember, TeamMember.participant_id == Participant.id)
        .filter(TeamMember.team_id == team.id)
        .all()
    )

    if not members:
        return _voice(f"Team '{team.name}' exists but has no members yet.")

    member_text = ", ".join(
        f"{m.full_name}" + (f" ({m.raw_skills_text[:40]})" if m.raw_skills_text else "")
        for m in members
    )

    project = db.query(Project).filter(Project.team_id == team.id).first()
    project_text = f"Their project is '{project.title}'." if project else "They haven't submitted a project yet."

    try:
        comp_service = TeamCompositionService(db)
        comp = comp_service.analyze_team(team.id)
        score_text = f"Their skill diversity score is {comp.get('skill_diversity_score', 'N/A')} out of 1.0."
    except Exception:
        score_text = ""

    return _voice(
        f"Team '{team.name}' has {len(members)} member(s): {member_text}. "
        f"{project_text} {score_text}"
    )


# ---------------------------------------------------------------------------
# Tool: find_team_for_me  (NEW — AI-powered matchmaking)
# ---------------------------------------------------------------------------

def find_team_for_me(args: dict, caller_phone: str, background_tasks: BackgroundTasks, db: Session) -> str:
    """Uses TeamCompositionService to find teams whose skill gaps best match the caller's skills."""
    email = args.get("email", "").strip()
    skills_override = args.get("skills", "").strip()

    participant = _find_participant(db, caller_phone, email)

    # Determine the caller's skills
    caller_skills_text = skills_override
    if not caller_skills_text and participant:
        caller_skills_text = participant.raw_skills_text or ""

    if not caller_skills_text:
        return _voice(
            "To find the best team for you, I need to know your skills. "
            "What are your main technical skills or areas of expertise?"
        )

    caller_skills_lower = caller_skills_text.lower()
    teams = db.query(Team).all()

    best_team = None
    best_match_score = -1

    comp_service = TeamCompositionService(db)

    for team in teams:
        # Skip teams where this participant is already a member
        if participant:
            membership = db.query(TeamMember).filter(
                TeamMember.team_id == team.id,
                TeamMember.participant_id == participant.id
            ).first()
            if membership:
                continue

        try:
            comp = comp_service.analyze_team(team.id)
            gaps = comp.get("coverage_gaps", [])
            # Score = how many of the caller's skills fill the team's gaps
            match_score = sum(
                1 for gap in gaps if gap.lower() in caller_skills_lower
            )
            if match_score > best_match_score:
                best_match_score = match_score
                best_team = (team, comp, gaps)
        except Exception:
            continue

    if not best_team:
        return _voice(
            "I wasn't able to find a suitable team match right now. "
            "There may be no open teams, or you might already be on a team."
        )

    team, comp, gaps = best_team
    members = (
        db.query(Participant)
        .join(TeamMember, TeamMember.participant_id == Participant.id)
        .filter(TeamMember.team_id == team.id)
        .all()
    )
    member_names = ", ".join(m.full_name for m in members) if members else "no members yet"
    gap_text = f"This team needs help with: {', '.join(gaps[:3])}." if gaps else ""

    # Optionally send a matchmaking email if we know the participant
    if participant:
        background_tasks.add_task(
            send_notification,
            db=None,
            participant_id=participant.id,
            template_key="voice_team_match",
            context={
                "name": participant.full_name,
                "team_name": team.name,
                "member_names": member_names,
                "skills": caller_skills_text,
                "gaps": ", ".join(gaps[:3]) if gaps else "various areas",
            },
        )
        email_note = " I've also emailed you the match details."
    else:
        email_note = ""

    return _voice(
        f"Great news! The best team match for your skills is '{team.name}' "
        f"with {len(members)} member(s): {member_names}. "
        f"{gap_text}"
        f"Would you like me to send them an introduction?{email_note}"
    )


# ---------------------------------------------------------------------------
# Tool: get_analytics_overview  (NEW)
# ---------------------------------------------------------------------------

def get_analytics_overview(db: Session) -> str:
    """Returns a voice-friendly summary of the hackathon analytics dashboard."""
    try:
        service = AnalyticsService(db)
        overview = service.overview()

        participants_total = overview["participants"]["total"]
        teams_total = overview["teams"]["total"]
        projects_total = overview["projects"]["total"]
        eval_rate = overview["projects"]["evaluation_completion_rate_pct"]
        reviewers_total = overview["reviewers"]["total"]
        open_flags = overview["fairness"]["open_bias_flags"]

        return _voice(
            f"Here's the live hackathon overview: "
            f"{participants_total} participants registered, "
            f"{teams_total} teams formed, "
            f"{projects_total} projects submitted. "
            f"Evaluation completion is at {eval_rate} percent, "
            f"with {reviewers_total} active reviewers. "
            f"The fairness monitor has {open_flags} open bias flag(s). "
            "For the full detailed dashboard, please visit the web interface."
        )
    except Exception as e:
        logger.error(f"[VoiceService] get_analytics_overview error: {e}")
        return _voice("I couldn't retrieve the analytics right now. Please try again shortly.")


# ---------------------------------------------------------------------------
# Tool: handle_call_end  (NEW — called on end-of-call-report)
# ---------------------------------------------------------------------------

def handle_call_end(
    call_id: str,
    transcript: str,
    summary: str,
    caller_phone: str,
    background_tasks: BackgroundTasks,
    db: Session,
) -> None:
    """
    Called when Vapi fires the 'end-of-call-report' event.
    Sends a post-call summary email to the caller if they are a registered participant.
    Does NOT return a voice response (call has ended).
    """
    logger.info(f"[VoiceService] Call ended. call_id={call_id}, caller={caller_phone}")

    participant = None
    if caller_phone:
        repo = ParticipantRepository(db)
        participant = repo.get_by_phone(caller_phone)

    if not participant:
        logger.info(f"[VoiceService] Call ended for unknown caller {caller_phone} — no summary email sent.")
        return

    # Build a readable summary
    call_summary_text = summary if summary else "Your call with the HackBridge AI Assistant has ended."
    transcript_snippet = (transcript[:500] + "...") if len(transcript) > 500 else transcript

    background_tasks.add_task(
        send_notification,
        db=None,
        participant_id=participant.id,
        template_key="voice_call_summary",
        context={
            "name": participant.full_name,
            "summary": call_summary_text,
            "transcript": transcript_snippet or "Transcript not available.",
        },
    )
    logger.info(f"[VoiceService] Post-call summary email queued for participant_id={participant.id}")
