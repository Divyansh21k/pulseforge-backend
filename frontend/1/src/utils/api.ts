/**
 * PulseForge Backend API Core Integration Bridge
 * Connects the React client to Divyansh21k/pulseforge-backend.
 * Includes complete fallback patterns to local mock/simulated states
 * with string-to-integer ID wrappers.
 */

export const getBackendUrl = (): string => {
  return localStorage.getItem('PULSEFORGE_BACKEND_URL') || 'http://localhost:8000';
};

export const setBackendUrl = (url: string) => {
  localStorage.setItem('PULSEFORGE_BACKEND_URL', url);
};

export const isBackendActive = (): boolean => {
  return localStorage.getItem('PULSEFORGE_BACKEND_ACTIVE') === 'true';
};

export const setBackendActiveState = (active: boolean) => {
  localStorage.setItem('PULSEFORGE_BACKEND_ACTIVE', active ? 'true' : 'false');
};

/**
 * Checks if the backend FastAPI server is online on the chosen URL.
 */
export async function testBackendHealth(): Promise<{ online: boolean; url: string }> {
  const url = getBackendUrl();
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000); // 2 second timeout
    const res = await fetch(`${url}/api/analytics/overview`, {
      method: 'GET',
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    const online = res.status < 500;
    setBackendActiveState(online);
    return { online, url };
  } catch (err) {
    try {
      // Fallback ping to root / docs
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(url, { method: 'GET', signal: controller.signal });
      clearTimeout(timeoutId);
      const online = res.status < 500;
      setBackendActiveState(online);
      return { online, url };
    } catch (_) {
      setBackendActiveState(false);
      return { online: false, url };
    }
  }
}

/**
 * Standard utility to parse string-based IDs (like 'p-1' or 'proj-12') into backend integers.
 */
export const toBackendId = (id: string | number): number => {
  if (typeof id === 'number') return id;
  const match = id.replace(/^[a-zA-Z-]+/, '');
  const parsed = parseInt(match, 10);
  return isNaN(parsed) ? 1 : parsed;
};

/**
 * Standard utility to wrap backend integers back to standard frontend styled string IDs.
 */
export const toFrontendId = (prefix: string, id: number | string): string => {
  const s = id.toString();
  if (s.startsWith(prefix)) return s;
  return `${prefix}-${s}`;
};

/**
 * Helper to perform fetch requests that automatically fall back or throw based on active state.
 */
async function apiFetch<T>(path: string, options?: RequestInit, fallbackValue?: T): Promise<T> {
  const url = `${getBackendUrl()}${path.startsWith('/') ? '' : '/'}${path}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });
    if (!res.ok) {
      throw new Error(`API returned HTTP ${res.status}`);
    }
    return await res.json() as T;
  } catch (err) {
    if (fallbackValue !== undefined) {
      console.warn(`[PulseForge Core] Failed connecting to ${url}. Falling back to client-side simulator.`);
      return fallbackValue;
    }
    throw err;
  }
}

/* ──────────────────────────────────────────────────────────
   0. PARTICIPANTS API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendParticipant {
  id: number;
  full_name: string;
  email: string;
  phone?: string;
  organization: string;
  raw_skills_text: string;
}

export async function createParticipant(payload: {
  full_name: string;
  email: string;
  phone?: string;
  organization: string;
  raw_skills_text: string;
}, fallback?: BackendParticipant): Promise<BackendParticipant> {
  return apiFetch(
    'api/participants/',
    {
      method: 'POST',
      body: JSON.stringify({
        full_name: payload.full_name,
        email: payload.email,
        phone: payload.phone || '',
        organization: payload.organization,
        raw_skills_text: payload.raw_skills_text
      }),
    },
    fallback
  );
}

export async function listParticipants(fallback?: BackendParticipant[]): Promise<BackendParticipant[]> {
  return apiFetch('api/participants/', { method: 'GET' }, fallback);
}

export async function getParticipant(participantId: string | number, fallback?: BackendParticipant): Promise<BackendParticipant> {
  return apiFetch(`api/participants/${toBackendId(participantId)}`, { method: 'GET' }, fallback);
}

/* ──────────────────────────────────────────────────────────
   1. DUPLICATE DETECTION API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendDuplicateMatch {
  matched_participant_id: number;
  match_type: string;
  confidence_score: number;
}

export interface BackendDuplicateFlag {
  id: number;
  matched_participant_id: number;
  match_type: string;
  confidence_score: number;
  status: string;
  created_at: string;
}

export async function checkDuplicates(participantId: string | number, fallback?: any): Promise<{
  participant_id: number;
  matches_found: number;
  matches: BackendDuplicateMatch[];
}> {
  return apiFetch(
    `api/duplicates/check/${toBackendId(participantId)}`,
    { method: 'POST' },
    fallback
  );
}

export async function getExistingDuplicateFlags(participantId: string | number, fallback?: any): Promise<BackendDuplicateFlag[]> {
  return apiFetch(
    `api/duplicates/flags/${toBackendId(participantId)}`,
    { method: 'GET' },
    fallback
  );
}

/* ──────────────────────────────────────────────────────────
   2. SKILLS EXTRACTION API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendSkillLink {
  skill_id: number;
  skill_name: string;
  source: string;
  confidence: number;
}

export async function previewExtraction(rawText: string, fallback?: string[]): Promise<{ normalized_skills: string[] }> {
  return apiFetch(
    'api/skills/extract',
    {
      method: 'POST',
      body: JSON.stringify({ raw_text: rawText }),
    },
    fallback ? { normalized_skills: fallback } : undefined
  );
}

export async function extractAndSaveSkills(participantId: string | number, fallback?: string[]): Promise<{
  participant_id: number;
  normalized_skills: string[];
}> {
  return apiFetch(
    `api/skills/extract/${toBackendId(participantId)}`,
    { method: 'POST' },
    fallback ? { participant_id: toBackendId(participantId), normalized_skills: fallback } : undefined
  );
}

export async function getParticipantSkills(participantId: string | number, fallback?: BackendSkillLink[]): Promise<BackendSkillLink[]> {
  return apiFetch(
    `api/skills/${toBackendId(participantId)}`,
    { method: 'GET' },
    fallback
  );
}

/* ──────────────────────────────────────────────────────────
   3. TEAM MAPPING & AUTO FORMATION API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendTeam {
  id: number;
  name: string;
  member_count: number;
}

export interface BackendTeamDetails {
  id: number;
  name: string;
  members: Array<{
    participant_id: number;
    full_name: string;
    role: string;
  }>;
  created_at: string;
}

export interface BackendTeamComposition {
  team_id: number;
  diversity_index: number;
  skill_coverage_pct: number;
  uniqueness_score: number;
  strength_assessment: string;
  gaps_detected: string[];
}

export async function createTeam(name: string, memberIds: Array<string | number>, fallback?: any): Promise<BackendTeamDetails> {
  const ids = memberIds.map(toBackendId);
  return apiFetch(
    'api/teams/',
    {
      method: 'POST',
      body: JSON.stringify({ name, member_ids: ids }),
    },
    fallback
  );
}

export async function listTeams(fallback?: BackendTeam[]): Promise<BackendTeam[]> {
  return apiFetch('api/teams/', { method: 'GET' }, fallback);
}

export async function getTeam(teamId: string | number, fallback?: BackendTeamDetails): Promise<BackendTeamDetails> {
  return apiFetch(`api/teams/${toBackendId(teamId)}`, { method: 'GET' }, fallback);
}

export async function getTeamComposition(teamId: string | number, fallback?: BackendTeamComposition): Promise<BackendTeamComposition> {
  return apiFetch(`api/teams/${toBackendId(teamId)}/composition`, { method: 'GET' }, fallback);
}

export async function autoFormTeams(teamSize: number, fallback?: any): Promise<{
  teams_formed: number;
  teams: Array<{
    name: string;
    member_ids: number[];
  }>;
}> {
  return apiFetch(
    'api/teams/auto-form',
    {
      method: 'POST',
      body: JSON.stringify({ team_size: teamSize }),
    },
    fallback
  );
}

/* ──────────────────────────────────────────────────────────
   4. EVALUATION WORKFLOW API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendEvaluation {
  id: number;
  project_id: number;
  reviewer_id: number;
  raw_score: number;
  created_at: string;
}

export interface BackendEvaluationDetails {
  id: number;
  reviewer_id: number;
  innovation_score: number;
  technical_score: number;
  impact_score: number;
  presentation_score: number;
  raw_score: number;
  normalized_score: number;
  feedback_text: string;
}

export interface BackendBiasFlag {
  id: number;
  dimension: string;
  scope: string;
  reviewer_id: number | null;
  description: string;
  severity: string;
  statistic: number;
  confidence: number;
  status: string;
  created_at: string;
}

export async function submitEvaluation(payload: {
  project_id: string | number;
  reviewer_id: string | number;
  innovation_score: number;
  technical_score: number;
  impact_score: number;
  presentation_score: number;
  feedback_text: string;
}, fallback?: any): Promise<BackendEvaluation> {
  return apiFetch(
    'api/evaluations/',
    {
      method: 'POST',
      body: JSON.stringify({
        project_id: toBackendId(payload.project_id),
        reviewer_id: toBackendId(payload.reviewer_id),
        innovation_score: payload.innovation_score,
        technical_score: payload.technical_score,
        impact_score: payload.impact_score,
        presentation_score: payload.presentation_score,
        feedback_text: payload.feedback_text,
      }),
    },
    fallback
  );
}

export async function listEvaluationsForProject(projectId: string | number, fallback?: BackendEvaluationDetails[]): Promise<BackendEvaluationDetails[]> {
  return apiFetch(`api/evaluations/project/${toBackendId(projectId)}`, { method: 'GET' }, fallback);
}

export async function normalizeScores(fallback?: any): Promise<{ evaluations_normalized: number }> {
  return apiFetch('api/evaluations/normalize', { method: 'POST' }, fallback);
}

export async function runBiasScan(fallback?: any): Promise<{
  cohort_flags: any[];
  reviewer_flags: any[];
  total_flags: number;
}> {
  return apiFetch('api/evaluations/bias-scan', { method: 'POST' }, fallback);
}

export async function listBiasFlags(statusFilter?: string, fallback?: BackendBiasFlag[]): Promise<BackendBiasFlag[]> {
  const query = statusFilter ? `?status_filter=${statusFilter}` : '';
  return apiFetch(`api/evaluations/bias-flags${query}`, { method: 'GET' }, fallback);
}

/* ──────────────────────────────────────────────────────────
   5. RESULTS PROCESSING API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendRankedProject {
  project_id: number;
  title: string;
  team_name: string;
  raw_mean: number;
  normalized_mean: number;
  confidence_score: number;
  rank: number;
}

export async function getRankings(fallback?: BackendRankedProject[]): Promise<BackendRankedProject[]> {
  const data = await apiFetch<{ rankings: BackendRankedProject[] }>(
    'api/results/rankings',
    { method: 'GET' },
    fallback ? { rankings: fallback } : undefined
  );
  return data?.rankings || [];
}

export async function getProjectFeedback(projectId: string | number, fallback?: any): Promise<{
  project_id: number;
  innovation: { average: number; comments: string[] };
  technical: { average: number; comments: string[] };
  impact: { average: number; comments: string[] };
  presentation: { average: number; comments: string[] };
  overall_feedback: string[];
}> {
  return apiFetch(`api/results/feedback/${toBackendId(projectId)}`, { method: 'GET' }, fallback);
}

/* ──────────────────────────────────────────────────────────
   6. PROJECTS API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendProject {
  id: number;
  team_id: number;
  title: string;
  description: string;
  tech_stack_text: string;
  repo_url: string;
  demo_url: string;
  created_at: string;
}

export async function submitProject(payload: {
  team_id: string | number;
  title: string;
  description: string;
  tech_stack_text: string;
  repo_url: string;
  demo_url: string;
}, fallback?: BackendProject): Promise<BackendProject> {
  return apiFetch(
    'api/projects/',
    {
      method: 'POST',
      body: JSON.stringify({
        team_id: toBackendId(payload.team_id),
        title: payload.title,
        description: payload.description,
        tech_stack_text: payload.tech_stack_text,
        repo_url: payload.repo_url,
        demo_url: payload.demo_url,
      }),
    },
    fallback
  );
}

export async function listProjects(fallback?: BackendProject[]): Promise<BackendProject[]> {
  return apiFetch('api/projects/', { method: 'GET' }, fallback);
}

export async function getProject(projectId: string | number, fallback?: BackendProject): Promise<BackendProject> {
  return apiFetch(`api/projects/${toBackendId(projectId)}`, { method: 'GET' }, fallback);
}

/* ──────────────────────────────────────────────────────────
   7. REVIEWER INTELLIGENCE API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendReviewer {
  id: number;
  full_name: string;
  email: string;
  organization: string;
  expertise_text: string;
  max_workload: number;
  participant_id: number | null;
}

export interface BackendReviewerWorkload {
  reviewer_id: number;
  active_assignments: number;
  max_workload: number;
  utilization_pct: number;
}

export interface BackendReviewerAssignment {
  id: number;
  reviewer_id: number;
  reviewer_name: string;
  expertise_score: number;
  workload_score: number;
  conflict_score: number;
  diversity_score: number;
  total_score: number;
  status: string;
}

export async function registerReviewer(payload: {
  full_name: string;
  email: string;
  organization: string;
  expertise_text: string;
  max_workload: number;
  participant_id?: string | number | null;
}, fallback?: BackendReviewer): Promise<BackendReviewer> {
  return apiFetch(
    'api/reviewers/',
    {
      method: 'POST',
      body: JSON.stringify({
        full_name: payload.full_name,
        email: payload.email,
        organization: payload.organization,
        expertise_text: payload.expertise_text,
        max_workload: payload.max_workload,
        participant_id: payload.participant_id ? toBackendId(payload.participant_id) : null,
      }),
    },
    fallback
  );
}

export async function listReviewers(fallback?: BackendReviewer[]): Promise<BackendReviewer[]> {
  return apiFetch('api/reviewers/', { method: 'GET' }, fallback);
}

export async function getReviewer(reviewerId: string | number, fallback?: BackendReviewer): Promise<BackendReviewer> {
  return apiFetch(`api/reviewers/${toBackendId(reviewerId)}`, { method: 'GET' }, fallback);
}

export async function getReviewerWorkload(reviewerId: string | number, fallback?: BackendReviewerWorkload): Promise<BackendReviewerWorkload> {
  return apiFetch(`api/reviewers/${toBackendId(reviewerId)}/workload`, { method: 'GET' }, fallback);
}

export async function runReviewerAssignments(reviewersPerProject: number, fallback?: any): Promise<{
  assignments_created: number;
  assignments: any[];
}> {
  return apiFetch(
    'api/reviewers/assign',
    {
      method: 'POST',
      body: JSON.stringify({ reviewers_per_project: reviewersPerProject }),
    },
    fallback
  );
}

export async function reassignNoShowReviewer(projectId: string | number, noShowReviewerId: string | number, fallback?: any): Promise<any> {
  return apiFetch(
    `api/reviewers/reassign/${toBackendId(projectId)}/${toBackendId(noShowReviewerId)}`,
    { method: 'POST' },
    fallback
  );
}

export async function getAssignmentsForProject(projectId: string | number, fallback?: BackendReviewerAssignment[]): Promise<BackendReviewerAssignment[]> {
  return apiFetch(`api/reviewers/assignments/${toBackendId(projectId)}`, { method: 'GET' }, fallback);
}

/* ──────────────────────────────────────────────────────────
   8. COMMUNICATIONS API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendNotification {
  id: number;
  participant_id: number;
  template_key: string;
  subject: string;
  status: string;
  sent_at: string;
}

export async function sendNotification(payload: {
  participant_id: string | number;
  template_key: string;
  context?: any;
}, fallback?: any): Promise<{ id: number; status: string; subject: string }> {
  return apiFetch(
    'api/communications/send',
    {
      method: 'POST',
      body: JSON.stringify({
        participant_id: toBackendId(payload.participant_id),
        template_key: payload.template_key,
        context: payload.context || {},
      }),
    },
    fallback
  );
}

export async function getParticipantNotifications(participantId: string | number, fallback?: any[]): Promise<any[]> {
  return apiFetch(`api/communications/participant/${toBackendId(participantId)}`, { method: 'GET' }, fallback);
}

export async function getAllNotifications(limit = 100, fallback?: any[]): Promise<any[]> {
  return apiFetch(`api/communications/all?limit=${limit}`, { method: 'GET' }, fallback);
}

export async function listNotificationTemplates(fallback?: string[]): Promise<string[]> {
  return apiFetch('api/communications/templates', { method: 'GET' }, fallback);
}

/* ──────────────────────────────────────────────────────────
   9. OVERVIEW ANALYTICS API WRAPPERS
   ────────────────────────────────────────────────────────── */
export interface BackendAnalyticsOverview {
  participant_count: number;
  team_count: number;
  project_count: number;
  evaluations_completed: number;
  evaluations_completion_pct: number;
  reviewer_count: number;
  reviewer_workload_variance: number;
  bias_flags_count: number;
  bias_flags_critical: number;
  average_raw_score: number;
  average_normalized_score: number;
}

export async function getAnalyticsOverview(fallback?: BackendAnalyticsOverview): Promise<BackendAnalyticsOverview> {
  return apiFetch('api/analytics/overview', { method: 'GET' }, fallback);
}
