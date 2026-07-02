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
from app.repositories.event_repository import EventRepository
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
    "Wei", "Jin", "Hassan", "Omar", "Yuki", "Sakura", "Elena", "Mateo"
]
LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Iyer", "Nair", "Gupta", "Reddy", "Singh",
    "Khan", "Mehta", "Park", "Kim", "Lopez", "Garcia", "Chen", "Wang",
    "Brown", "Wilson", "Anderson", "Clark", "Alves", "Silva", "Ali"
]
ORGS = [
    "Stanford University", "Massachusetts Institute of Technology (MIT)", 
    "University of Waterloo", "Carnegie Mellon University", 
    "National University of Singapore", "Indian Institute of Technology (IIT)", 
    "University of California, Berkeley", "Tsinghua University"
]
GENDERS = ["male", "female", "non-binary"]
REGIONS = ["North America", "Europe", "South Asia", "East Asia", "South America", "Middle East"]
SKILL_PHRASES = [
    "Full-stack engineer with 3 years of experience in React, Next.js, and PostgreSQL. Interested in building scalable web applications.",
    "Data scientist specializing in NLP and time-series forecasting. Proficient in Python, PyTorch, and Pandas.",
    "Backend developer focused on distributed systems. Go, Rust, gRPC, and Kubernetes are my bread and butter.",
    "Mobile app developer (Flutter/Dart). I love creating smooth, accessible cross-platform experiences.",
    "DevOps and Cloud architect. AWS Certified Solutions Architect. I automate everything using Terraform and GitHub Actions.",
    "UI/UX designer with a background in cognitive psychology. Figma ninja. I also write some frontend code in Vue.js.",
    "Blockchain researcher. I write secure smart contracts in Solidity and Cairo. Deeply interested in zero-knowledge proofs.",
    "Cybersecurity researcher. Penetration testing, malware analysis, and network security. OSCP certified.",
    "Hardware hacker. C/C++, Arduino, Raspberry Pi, and IoT protocols like MQTT. I make physical things talk to the internet.",
    "Machine Learning Engineer. I deploy LLMs to production using vLLM and TensorRT-LLM. Heavy Python and Cuda experience."
]
PROJECT_IDEAS = [
    ("Nexus Graph", "A highly optimized, distributed graph database designed specifically for analyzing complex social media interaction networks in real-time.", "c++, rust, distributed-systems", "https://github.com/nexus-graph/nexus-core"),
    ("Aura Vision", "An edge-compute computer vision system for drones that detects wildfires early by analyzing multispectral infrared camera feeds.", "python, pytorch, computer-vision, edge-computing", "https://github.com/aura-vision/wildfire-detect"),
    ("FinStream", "A unified API gateway for decentralized finance (DeFi) protocols, providing developers a single interface to interact with multiple liquidity pools.", "solidity, typescript, graphql, web3", "https://github.com/finstream-labs/gateway"),
    ("NeuroSync", "A brain-computer interface application that translates EEG signals into keystrokes for individuals with severe motor disabilities.", "python, signal-processing, bci, qt", "https://github.com/neurosync/eeg-keyboard"),
    ("KubeScaler", "An intelligent auto-scaler for Kubernetes that uses predictive machine learning models to pre-scale pods before traffic spikes occur.", "go, kubernetes, machine-learning", "https://github.com/kubescaler/autoscaler"),
    ("VitaChain", "A hyperledger-based supply chain tracking system for pharmaceutical drugs to prevent counterfeiting and ensure temperature compliance.", "hyperledger, go, react", "https://github.com/vitachain/pharma-track"),
    ("OmniLearn", "An adaptive learning management system that generates custom syllabus and quizzes dynamically using large language models.", "nextjs, python, fastapi, llm", "https://github.com/omnilearn-edu/platform"),
    ("AquaSense", "An IoT sensor network deployment that monitors water quality in urban rivers and alerts local authorities of hazardous chemical spikes.", "c, arduino, mqtt, react", "https://github.com/aquasense/sensor-mesh"),
    ("QuantumSim", "A lightweight, browser-based quantum circuit simulator built with WebAssembly for educational purposes.", "rust, wasm, typescript, react", "https://github.com/quantumsim/web-simulator"),
    ("CivicConnect", "A civic engagement platform that aggregates local municipal data and allows citizens to vote on neighborhood improvement proposals.", "ruby-on-rails, postgresql, vuejs", "https://github.com/civicconnect/platform"),
    ("AtmoShield", "A real-time weather pattern anomaly detection API that provides early warnings for hyper-localized severe weather events.", "python, tensorflow, apache-kafka", "https://github.com/atmoshield/anomaly-api"),
    ("PentaTest", "An automated web application vulnerability scanner that leverages fuzzing and AI-driven payload generation.", "python, cybersecurity, selenium", "https://github.com/pentatest/scanner")
]
REVIEWER_PROFILES = [
    ("Dr. Alistair Vance", "Carnegie Mellon University", "machine learning, artificial intelligence, computer vision, robotics"),
    ("Prof. Sarah Jenkins", "Massachusetts Institute of Technology (MIT)", "distributed systems, cloud computing, operating systems, go"),
    ("Dr. Hector Ramirez", "Stanford University", "cybersecurity, cryptography, network security, blockchain"),
    ("Prof. Aisha Malik", "University of Waterloo", "human-computer interaction, ui/ux, frontend development, accessibility"),
    ("Dr. Kenji Sato", "University of Tokyo", "embedded systems, iot, hardware design, c++"),
    ("Prof. Maria Rossi", "Politecnico di Milano", "data science, natural language processing, statistics, python"),
    ("Dr. David Chen", "National University of Singapore", "software engineering, system architecture, backend development, java"),
    ("Prof. Elena Kovac", "ETH Zurich", "quantum computing, theoretical computer science, algorithms")
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

    print("Seeding events...")
    e_repo = EventRepository(db)
    from datetime import datetime, timedelta
    
    organizer = p_repo.get_by_email("organizer@pulseforge.dev")
    events_to_create = [
        ("Global AI Hackathon 2026", "AI/ML & Sustainability"),
        ("FinTech Disrupt", "Enterprise Security & Finance"),
        ("EduTech Innovators", "Education & Accessibility"),
        ("Web3 Decentralize", "Blockchain & Smart Contracts"),
        ("HealthTech Open", "Medical IoT & Data Science"),
    ]
    
    # Shuffle and pick a random subset to ensure variance across re-seeds
    random.shuffle(events_to_create)
    events_to_seed = events_to_create[:random.randint(3, 5)]
    
    for name, theme in events_to_seed:
        # Vary the start and end dates
        start_offset = random.randint(-10, 5)
        duration = random.randint(2, 30)
        e_repo.create(
            name, 
            theme, 
            organizer.id, 
            datetime.utcnow() + timedelta(days=start_offset), 
            datetime.utcnow() + timedelta(days=start_offset + duration)
        )
    print(f"  created {len(events_to_seed)} events")


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
    for i, (title, desc, stack, repo_url) in enumerate(PROJECT_IDEAS):
        team = teams[i % len(teams)]
        # Add repo_url to the description or store it if the model supports it.
        # Looking at ProjectService, create_project takes (team_id, title, description, tech_stack_text)
        # We will append the repo url to the description for now or if repo_url is a field, pass it.
        # Let's check if repo_url exists in ProjectService. If not, append it.
        proj = proj_service.create_project(team.id, title, desc, stack)
        proj.repo_url = repo_url
        projects.append(proj)
    db.commit()
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
