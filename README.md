# HackBridge — AI-Enabled Hackathon Management Dashboard

PulseForge is an AI-powered backend platform that automates the
hackathon lifecycle end to end: registration → team formation →
project submission → reviewer assignment → bias-aware evaluation →
results & analytics. Built for the **AI-Enabled Hackathon Management
Dashboard** problem statement (PS1).

## Why this exists

Hackathon organizers currently juggle 5-7 disconnected tools, spend
20-30 hours per event on manual coordination, and 35% report fairness
concerns in evaluation. PulseForge replaces that fragmented workflow
with a single API surface backed by real, auditable AI/statistical
methods — not black-box ML, but transparent algorithms whose scoring
breakdown is always inspectable.

## The 3 differentiating AI features

1. **Multi-objective reviewer assignment** (`/api/reviewers/assign`) —
   greedy optimizer balancing expertise match (40%), workload balance
   (30%), conflict-of-interest avoidance (20%), and diversity (10%),
   exactly matching the weights specified in the problem statement.
   Conflicts (shared organization between reviewer and submitting team)
   are a **hard exclusion**, not just a penalty.

2. **Statistical bias detection + score normalization**
   (`/api/evaluations/normalize`, `/api/evaluations/bias-scan`) —
   per-reviewer z-score normalization corrects for harsh/lenient
   scoring tendencies before ranking. A second pass flags statistically
   significant score gaps across gender, geography, institution, and
   tech-stack groups, plus reviewer-level outliers. Every flag carries
   a confidence score and the exact z-statistic behind it — fully
   auditable, no opaque model.

3. **AI-assisted duplicate detection + skill extraction**
   (`/api/duplicates/check/*`, `/api/skills/extract`) — exact-email,
   fuzzy-name (token-sort-ratio), and organization-based duplicate
   matching; free-text skill extraction normalized into a shared
   taxonomy via Gemini, with a **fully offline keyword-based fallback**
   so the feature never breaks if the API key is missing or the
   network call fails during a live demo.

## Architecture

```
app/
  core/        # settings, DB engine/session
  models/      # SQLAlchemy ORM models
  schemas/     # Pydantic request/response models
  repositories/# data-access layer (no business logic)
  services/    # business logic + AI/statistical algorithms
  routers/v1/  # FastAPI route handlers (thin — delegate to services)
  utils/       # fuzzy matching, Gemini client + fallback
scripts/
  seed_data.py # generates realistic mock data (PS1 section 7.2)
tests/         # pytest suite, isolated in-memory DB per test
```

Layering is strict: **router → service → repository → model**. Routers
never touch the DB directly; services hold all business/AI logic;
repositories are the only layer that runs queries. This keeps each
piece independently testable and easy to extend.

### Data model

| Entity | Purpose |
|---|---|
| `Participant` | Registrants; includes `gender`/`region` used *only* in aggregate bias statistics |
| `Skill` / `ParticipantSkill` | Normalized skill taxonomy, AI-extracted or manual |
| `DuplicateFlag` | Stored duplicate-detection results, auditable |
| `Team` / `TeamMember` | Team formation |
| `TeamCompositionScore` | Skill-diversity score + coverage gaps per team |
| `Project` | Hackathon submissions — the entity everything else hangs off of |
| `Reviewer` / `ReviewerExpertise` | Reviewer profiles + normalized expertise tags |
| `ReviewerAssignment` | Reviewer↔project pairing with full score breakdown |
| `Evaluation` | Per-reviewer scores + raw/normalized composite |
| `BiasFlag` | Statistically-detected bias signal (cohort or reviewer-level) |

## API surface

Full interactive docs at `/docs` once running. Grouped by lifecycle stage:

| Stage | Endpoints |
|---|---|
| Registration | `POST /api/participants/`, `GET /api/participants/` |
| Duplicate detection | `POST /api/duplicates/check/{id}`, `GET /api/duplicates/flags/{id}` |
| Skill extraction | `POST /api/skills/extract`, `POST /api/skills/extract/{participant_id}` |
| Team formation | `POST /api/teams/`, `GET /api/teams/{id}/composition` |
| Project submission | `POST /api/projects/`, `GET /api/projects/` |
| Reviewer intelligence | `POST /api/reviewers/`, `POST /api/reviewers/assign`, `POST /api/reviewers/reassign/{project_id}/{reviewer_id}` |
| Evaluation & fairness | `POST /api/evaluations/`, `POST /api/evaluations/normalize`, `POST /api/evaluations/bias-scan`, `GET /api/evaluations/bias-flags` |
| Results | `GET /api/results/rankings`, `GET /api/results/feedback/{project_id}` |
| Analytics | `GET /api/analytics/overview` |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: enables live Gemini-based skill extraction.
# Without it, the app automatically uses an offline keyword-based
# fallback extractor -- nothing breaks, nothing requires a key to run.
echo "GEMINI_API_KEY=your-key-here" > .env

uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API explorer.

### Seed realistic demo data

```bash
python -m scripts.seed_data
```

Generates 40 participants, 20 teams, 12 projects, 8 reviewers, runs the
assignment optimizer, submits evaluations with **intentionally baked-in
bias patterns** (one lenient reviewer, one harsh reviewer), then runs
normalization and bias detection so the fairness features have real
signal to show during judging — not an empty dashboard.

### Run tests

```bash
pytest tests/ -v
```

23 tests covering registration, duplicate detection, skill extraction
(including the offline fallback path), reviewer assignment and
conflict-of-interest exclusion, evaluation scoring, normalization, bias
detection, and results ranking. All tests run against an isolated
in-memory SQLite database — no shared state, no network calls.

## Design decisions & trade-offs

- **Greedy assignment, not a global solver.** A Hungarian-algorithm
  style optimal assignment would maximize *total* expertise match, but
  for a 24-48h build the greedy multi-objective approach is fully
  explainable (every assignment stores its score breakdown), fast
  (O(projects × reviewers)), and comfortably clears the "<60s for 100+
  projects" target. Upgrading to a global solver (e.g. `scipy.optimize.
  linear_sum_assignment`) is a natural next step.
- **Statistical bias detection over a trained classifier.** Z-score
  group comparisons require no training data, are instantly auditable
  (judges can verify the math by hand), and directly match the "90%
  bias detection accuracy" framing in the problem statement without
  needing a labeled bias dataset that doesn't exist for a brand-new
  hackathon.
- **Gemini with deterministic fallback.** Live demos should never fail
  because of an external API hiccup. The fallback extractor uses the
  same skill vocabulary, so behavior is consistent whether or not a key
  is configured.
- **SQLite for the demo, swappable via `DATABASE_URL`.** `app/core/
  config.py` reads `database_url` from the environment; pointing it at
  Postgres for a production deployment requires no code changes.

## What's next (scaling roadmap)

- Swap the greedy assignment for `scipy.optimize.linear_sum_assignment`
  for a globally optimal match.
- Add a notification/communication service (email/SMS mocked per
  problem-statement constraints) for personalized participant updates.
- Add JWT-based auth and role-based permissions (participant / reviewer
  / admin) — the `Participant.role` field already exists as the hook.
- Move skill extraction to a background task queue for true 1000+
  registrations/minute throughput.
