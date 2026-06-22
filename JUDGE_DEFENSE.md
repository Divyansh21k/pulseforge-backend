# PulseForge — Judge Defense Guide

Technical Q&A for skeptical SIH judges. Every answer maps to real code paths.

---

## Authentication & Authorization

### Q: Is login real or a UI fake?
**Answer:** Real JWT authentication via `/api/auth/login` and `/api/auth/register`.

**Technical Explanation:** Passwords are bcrypt-hashed (`app/utils/security.py`). Tokens are HS256 JWTs with `sub` (participant ID) and `role`. The frontend stores the token in `localStorage` and sends `Authorization: Bearer` on every protected request (`frontend/1/src/utils/auth.ts`, `frontend/1/src/utils/api.ts`). There is no role selector on login — role comes from the database record.

### Q: Can anyone become an organizer?
**Answer:** No. Self-registration allows `participant` and `reviewer` only.

**Technical Explanation:** `app/routers/v1/auth.py` rejects `organizer` in `RegisterRequest`. Organizer accounts are created in `scripts/seed_data.py` (`organizer@pulseforge.dev` / `demo1234`).

### Q: Are sensitive endpoints protected?
**Answer:** Yes — evaluations, assignments, normalization, bias scans, rankings, communications, and team auto-formation require JWT + role checks.

**Technical Explanation:** `app/utils/auth_deps.py` provides `require_organizer`, `require_reviewer`, `require_participant`. Routers in `app/routers/v1/` apply these dependencies. Evaluation submit additionally verifies the reviewer email matches the authenticated user (`app/routers/v1/evaluations.py`).

---

## Skill Extraction

### Q: Where are skills stored?
**Answer:** `participant_skills` and `skills` tables after extraction.

**Technical Explanation:** `POST /api/skills/extract/{participant_id}` runs `SkillExtractionService` which calls `extract_skills()` in `app/utils/gemini_client.py`. Normalized tags are persisted via `ParticipantSkillRepository`.

### Q: What if Gemini fails?
**Answer:** Keyword fallback extractor runs automatically.

**Technical Explanation:** If `GEMINI_API_KEY` is unset or the API errors, `_FALLBACK_KEYWORDS` in `gemini_client.py` maps text to taxonomy tags. Tests force this path via `GEMINI_API_KEY=""` in `tests/conftest.py`.

### Q: What if a participant submits duplicate skills?
**Answer:** Duplicate detection runs separately; skills dedupe at taxonomy level.

**Technical Explanation:** `DuplicateDetectionService` flags fuzzy name/email matches. Skill extraction normalizes synonyms to canonical skill IDs.

---

## Team Formation

### Q: How does auto team formation work?
**Answer:** Greedy skill-diversity clustering in `TeamFormationService`.

**Technical Explanation:** `POST /api/teams/auto-form` groups unassigned participants maximizing complementary skill coverage. UI: Organizer → Team Formation tab.

### Q: What is team composition analysis?
**Answer:** Coverage score against 10 core categories (backend, frontend, ML, devops, etc.).

**Technical Explanation:** `GET /api/teams/{id}/composition` returns `skill_diversity_score`, `categories_covered`, and `coverage_gaps`.

---

## Reviewer Assignment

### Q: What algorithm assigns reviewers?
**Answer:** Multi-objective greedy optimizer: expertise 40%, workload 30%, conflict 20%, diversity 10%.

**Technical Explanation:** `ReviewerAssignmentService` in `app/services/reviewer_assignment.py`. Same-org reviewers excluded. Breakdown stored in `reviewer_assignments`.

---

## Evaluations & Normalization

### Q: How are raw scores computed?
**Answer:** Weighted sum: innovation 30%, technical 30%, impact 25%, presentation 15%.

**Technical Explanation:** `EvaluationService` in `app/services/evaluation_service.py`.

### Q: What normalization algorithm is used?
**Answer:** Per-reviewer z-score normalization via `POST /api/evaluations/normalize`.

---

## Bias Detection

### Q: How does bias detection work?
**Answer:** Cohort statistical comparison + reviewer outlier detection.

**Technical Explanation:** `BiasDetectionService` in `app/services/bias_detection.py`. Flags persist in `bias_flags` table. Seed data embeds intentional bias patterns for demo.

---

## Rankings

### Q: Where are rankings generated?
**Answer:** Backend only — `GET /api/results/rankings` via `ResultsService`.

---

## Demo Reliability

### Q: What if the database is empty?
**Answer:** Auto-seed on startup + `POST /api/demo/seed`.

### Q: Demo credentials?
- `organizer@pulseforge.dev` / `demo1234`
- `reviewer@pulseforge.dev` / `demo1234`
- `participant@pulseforge.dev` / `demo1234`

---

## Recommended Demo Flow

1. Start backend (`uvicorn app.main:app --reload`) — auto-seeds if empty
2. Start frontend (`cd frontend/1 && npm run dev`)
3. Login as organizer → show KPIs, team formation, matcher, normalization, bias scan
4. Login as reviewer → submit evaluation
5. Login as participant → view workspace
