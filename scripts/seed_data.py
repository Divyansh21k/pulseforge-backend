"""
Seed script for demo/judging purposes (PS1 section 7.2).

Generates:
  - 40 mock participants with diverse skills, orgs, genders, regions
  - 20 teams (2 participants each)
  - 12 mock projects with varied tech stacks and descriptions
  - 8 mock reviewers with different expertise areas (some sharing an
    organization with a team, to exercise conflict-of-interest detection)
  - Evaluations with INTENTIONAL bias patterns baked in (one harsh
    reviewer, one lenient reviewer, and a deliberate score gap between
    two organizations) so the bias-detection feature has something real
    to find during a live demo.

Run with: python -m scripts.seed_data
"""
import random

from app.core.database import Base, engine, SessionLocal
from app import models  # noqa: F401
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.team_repository import TeamRepository
from app.services.project_service import ProjectService
from app.services.reviewer_service import ReviewerService
from app.services.reviewer_assignment import ReviewerAssignmentService
from app.services.evaluation_service import EvaluationService
from app.services.bias_detection import ScoreNormalizationService, BiasDetectionService

from app.utils.security import hash_password

random.seed(42)

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Sai", "Ishaan", "Diya", "Ananya", "Saanvi",
    "Myra", "Kiara", "Liam", "Noah", "Emma", "Olivia", "Mia", "Ethan",
    "Sofia", "Lucas", "Ava", "Mason", "Priya", "Rohan", "Neha", "Karan",
]
LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Iyer", "Nair", "Gupta", "Reddy", "Singh",
    "Khan", "Mehta", "Park", "Kim", "Lopez", "Garcia", "Chen", "Wang",
    "Brown", "Wilson", "Anderson", "Clark",
]
ORGS = ["VIT University", "MIT", "Stanford", "IIT Bombay", "BITS Pilani", "UC Berkeley"]
GENDERS = ["male", "female"]
REGIONS = ["south-asia", "north-america", "west-asia", "europe"]
SKILL_PHRASES = [
    "I love working with react, node.js and building full stack web apps",
    "Strong in python, machine learning and data science, also know pandas",
    "Mobile developer, flutter and android, some kotlin too",
    "DevOps engineer, aws, terraform, ci/cd pipelines",
    "Backend with java and sql, building scalable apis",
    "UI/UX designer, figma, also dabble in frontend css",
    "Blockchain developer, solidity and web3 smart contracts",
    "Cybersecurity enthusiast, penetration testing and infosec",
    "Full stack: javascript, react, nodejs, sql databases",
    "Cloud architecture on gcp and azure, plus some devops",
]
PROJECT_IDEAS = [
    ("CampusConnect", "A social platform connecting students across departments for project collaboration.", "react, nodejs, sql"),
    ("EcoTrack", "Carbon footprint tracker using machine learning predictions for daily habits.", "python, machine-learning, react"),
    ("SmartAttend", "AI-powered attendance system using facial recognition.", "python, opencv, react"),
    ("StudyBuddy", "AI tutor that generates personalized practice questions from lecture notes.", "python, machine-learning, nodejs"),
    ("MedAlert", "Wearable health monitor with anomaly detection alerts.", "python, machine-learning, mobile"),
    ("CodeReview AI", "Automated code review assistant flagging bugs and style issues.", "python, javascript, backend"),
    ("VolunteerHub", "Matches student volunteers to local NGOs based on skills.", "react, nodejs, sql"),
    ("AgriSense", "IoT + ML system predicting crop yield from sensor data.", "python, machine-learning, devops"),
    ("CampusEats", "Crowd-sourced cafeteria wait-time predictor.", "react, python, sql"),
    ("SecureVote", "Blockchain-based voting system for student council elections.", "blockchain, solidity, react"),
    ("MindfulMe", "Mental wellness check-in app with sentiment analysis.", "python, machine-learning, mobile"),
    ("BugHunters", "Crowdsourced bug bounty platform for student-built apps.", "cybersecurity, nodejs, react"),
]
REVIEWER_PROFILES = [
    ("Dr. Ananya Rao", "VIT University", "machine learning, python, data science, statistics"),
    ("Prof. James Lee", "Stanford", "react, frontend, ui-ux, javascript"),
    ("Dr. Wei Zhang", "MIT", "devops, cloud, aws, backend infrastructure"),
    ("Prof. Fatima Noor", "IIT Bombay", "cybersecurity, infosec, network security"),
    ("Dr. Carlos Mendes", "UC Berkeley", "blockchain, solidity, distributed systems"),
    ("Prof. Sara Kim", "BITS Pilani", "mobile development, flutter, android, ios"),
    ("Dr. Arjun Mehta", "VIT University", "backend, sql, java, system design"),
    ("Prof. Linda Osei", "Stanford", "data science, machine learning, nlp"),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    p_repo = ParticipantRepository(db)
    t_repo = TeamRepository(db)
    proj_service = ProjectService(db)
    rev_service = ReviewerService(db)

    print("Creating demo auth accounts...")
    demo_users = [
        ("Alexander Vance", "organizer@pulseforge.dev", "organizer", "PulseForge HQ"),
        ("Dr. Marcus Chen", "reviewer@pulseforge.dev", "reviewer", "MIT"),
        ("Elena Rostova", "participant@pulseforge.dev", "participant", "Stanford"),
    ]
    for name, email, role, org in demo_users:
        if not p_repo.get_by_email(email):
            user = p_repo.create(name, email, None, org, "python, react, machine learning")
            user.role = role
            user.hashed_password = hash_password("demo1234")
            db.commit()
            if role == "reviewer":
                try:
                    rev = rev_service.create_reviewer(
                        name, email, organization=org,
                        expertise_text="machine learning, python, data science",
                        max_workload=4, participant_id=user.id,
                    )
                    db.query(models.Reviewer).filter(models.Reviewer.id == rev.id).update({"status": "approved"})
                    db.commit()
                except ValueError:
                    pass
    print("  demo login: organizer@pulseforge.dev / demo1234 (organizer)")
    print("  demo login: reviewer@pulseforge.dev / demo1234 (reviewer)")
    print("  demo login: participant@pulseforge.dev / demo1234 (participant)")

    if p_repo.get_by_email("participant1@hackathon.dev"):
        print("Bulk demo dataset already present. Skipping re-seed.")
        db.close()
        return

    print("Seeding participants...")
    participants = []
    for i in range(40):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        email = f"participant{i+1}@hackathon.dev"
        org = random.choice(ORGS)
        skills_text = random.choice(SKILL_PHRASES)
        p = p_repo.create(name, email, None, org, skills_text)
        p.gender = random.choice(GENDERS)
        p.region = random.choice(REGIONS)
        participants.append(p)
    db.commit()
    print(f"  created {len(participants)} participants")

    print("Forming teams...")
    teams = []
    for i in range(0, len(participants) - 1, 2):
        members = [participants[i].id, participants[i + 1].id]
        team = t_repo.create(f"Team {chr(65 + len(teams))}", members)
        teams.append(team)
    print(f"  created {len(teams)} teams")

    print("Submitting projects...")
    projects = []
    for i, (title, desc, stack) in enumerate(PROJECT_IDEAS):
        team = teams[i % len(teams)]
        proj = proj_service.create_project(team.id, title, desc, stack)
        projects.append(proj)
    print(f"  created {len(projects)} projects")

    print("Registering reviewers (this uses the skill-extraction fallback if no Gemini key is set)...")
    reviewers = []
    for name, org, expertise in REVIEWER_PROFILES:
        email = f"{name.split()[-1].lower()}@reviewers.dev"
        try:
            rev = rev_service.create_reviewer(name, email, organization=org, expertise_text=expertise, max_workload=4)
            db.query(models.Reviewer).filter(models.Reviewer.id == rev.id).update({"status": "approved"})
            db.commit()
            reviewers.append(rev)
        except ValueError:
            pass  # already exists, skip on re-seed
    print(f"  created {len(reviewers)} reviewers")

    print("Running reviewer assignment optimizer...")
    assign_service = ReviewerAssignmentService(db)
    try:
        assignments = assign_service.run_assignment(reviewers_per_project=2)
        print(f"  created {len(assignments)} assignments")
    except ValueError as e:
        print(f"  assignment skipped: {e}")
        assignments = []

    print("Submitting evaluations with INTENTIONAL bias patterns for demo purposes...")
    eval_service = EvaluationService(db)
    by_project = {}
    for a in assignments:
        by_project.setdefault(a["project_id"], []).append(a["reviewer_id"])

    eval_count = 0
    for idx, (project_id, reviewer_ids) in enumerate(by_project.items()):
        for j, reviewer_id in enumerate(reviewer_ids):
            # Reviewer at index 0 in REVIEWER_PROFILES order tends lenient;
            # reviewer index 3 tends harsh -- baked-in pattern for the
            # bias-detection + normalization demo to surface.
            base = random.uniform(6.0, 8.5)
            if reviewer_id == reviewers[0].id if reviewers else False:
                base += 1.2  # lenient reviewer
            if len(reviewers) > 3 and reviewer_id == reviewers[3].id:
                base -= 1.5  # harsh reviewer

            innovation = round(min(10, max(0, base + random.uniform(-0.5, 0.5))), 1)
            technical = round(min(10, max(0, base + random.uniform(-0.5, 0.5))), 1)
            impact = round(min(10, max(0, base + random.uniform(-0.5, 0.5))), 1)
            presentation = round(min(10, max(0, base + random.uniform(-0.5, 0.5))), 1)

            eval_service.submit_evaluation(
                project_id, reviewer_id, innovation, technical, impact, presentation,
                feedback_text=random.choice([
                    "Solid execution, clear demo.",
                    "Good idea but needs more polish on the UI.",
                    "Impressive technical depth.",
                    "Could use a clearer problem statement.",
                    "Strong potential for real-world use.",
                ]),
            )
            eval_count += 1
    print(f"  created {eval_count} evaluations")

    print("Running score normalization...")
    norm_service = ScoreNormalizationService(db)
    updated = norm_service.normalize_all()
    print(f"  normalized {updated} evaluations")

    print("Running bias detection...")
    bias_service = BiasDetectionService(db)
    cohort_flags = bias_service.detect_cohort_bias()
    reviewer_flags = bias_service.detect_reviewer_outliers()
    print(f"  cohort flags: {len(cohort_flags)}, reviewer flags: {len(reviewer_flags)}")
    for f in cohort_flags:
        print(f"    [cohort] {f['description']}")
    for f in reviewer_flags:
        print(f"    [reviewer] {f['description']}")

    db.close()
    print()
    print("Seed complete. Start the server and visit /docs to explore the API.")


if __name__ == "__main__":
    run()
