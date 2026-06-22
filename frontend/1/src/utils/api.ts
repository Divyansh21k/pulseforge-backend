/**
 * PulseForge Backend API — JWT-authenticated integration layer.
 */

import { authHeaders, clearAuth, getToken, setStoredUser, setToken, AuthUser } from './auth';

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

export async function testBackendHealth(): Promise<{ online: boolean; url: string }> {
  const url = getBackendUrl();
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2500);
    const res = await fetch(`${url}/health`, { method: 'GET', signal: controller.signal });
    clearTimeout(timeoutId);
    const online = res.ok;
    setBackendActiveState(online);
    return { online, url };
  } catch {
    setBackendActiveState(false);
    return { online: false, url };
  }
}

export const toBackendId = (id: string | number): number => {
  if (typeof id === 'number') return id;
  const match = id.replace(/^[a-zA-Z-]+/, '');
  const parsed = parseInt(match, 10);
  return isNaN(parsed) ? 1 : parsed;
};

export const toFrontendId = (prefix: string, id: number | string): string => {
  const s = id.toString();
  if (s.startsWith(prefix)) return s;
  return `${prefix}-${s}`;
};

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function apiFetch<T>(path: string, options?: RequestInit, requireAuth = true): Promise<T> {
  const url = `${getBackendUrl()}${path.startsWith('/') ? '' : '/'}${path}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(requireAuth ? authHeaders() : {}),
    ...(options?.headers as Record<string, string> || {}),
  };

  const res = await fetch(url, { ...options, headers });
  if (res.status === 401 && requireAuth) {
    clearAuth();
    throw new ApiError('Session expired — please log in again', 401);
  }
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch { /* ignore */ }
    throw new ApiError(String(detail), res.status);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/* ── Auth ── */
export interface TokenResponse {
  access_token: string;
  role: string;
  participant_id: number;
}

export async function login(email: string, password: string): Promise<AuthUser> {
  const data = await apiFetch<TokenResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }, false);
  setToken(data.access_token);
  const profile = await getMe();
  setStoredUser(profile);
  return profile;
}

export async function register(payload: {
  full_name: string;
  email: string;
  password: string;
  organization?: string;
  role: 'participant' | 'reviewer' | 'organizer';
  raw_skills_text?: string;
  expertise_text?: string;
  linkedinUrl?: string;
}): Promise<AuthUser> {
  const data = await apiFetch<TokenResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ ...payload, linkedin_url: payload.linkedinUrl }),
  }, false);
  setToken(data.access_token);
  const profile = await getMe();
  setStoredUser(profile);
  return profile;
}

export async function getMe(): Promise<AuthUser> {
  const profile = await apiFetch<AuthUser>('/api/auth/me');
  setStoredUser(profile);
  return profile;
}

export function logout(): void {
  clearAuth();
}

/* ── Demo ── */
export async function getDemoStatus(): Promise<{
  database_empty: boolean;
  participant_count: number;
  demo_credentials: Record<string, { email: string; password: string }>;
}> {
  return apiFetch('/api/demo/status', { method: 'GET' }, false);
}

export async function seedDemoDataset(): Promise<{ seeded: boolean; message: string; participant_count?: number }> {
  return apiFetch('/api/demo/seed', { method: 'POST' }, false);
}

/* ── Events ── */
export interface BackendEvent {
  id: number;
  name: string;
  theme?: string;
  status: string;
}

export async function listEvents(): Promise<BackendEvent[]> {
  return apiFetch('api/events/', { method: 'GET' });
}

export async function createEvent(payload: {
  name: string;
  theme?: string;
}): Promise<BackendEvent & { organizer_id: number }> {
  return apiFetch('api/events/', { method: 'POST', body: JSON.stringify(payload) });
}

export async function enrollInEvent(eventId: number | string): Promise<{ event_id: number; participant_id: number; enrolled_at: string }> {
  return apiFetch(`api/events/${toBackendId(eventId)}/enroll`, { method: 'POST' });
}

export async function getEnrolledEvents(): Promise<BackendEvent[]> {
  return apiFetch('api/events/enrolled/me', { method: 'GET' });
}

/* ── Participants ── */
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
}): Promise<BackendParticipant> {
  return apiFetch('api/participants/', { method: 'POST', body: JSON.stringify(payload) });
}

export async function listParticipants(): Promise<BackendParticipant[]> {
  return apiFetch('api/participants/', { method: 'GET' });
}

export async function getParticipant(participantId: string | number): Promise<BackendParticipant> {
  return apiFetch(`api/participants/${toBackendId(participantId)}`, { method: 'GET' });
}

/* ── Duplicates ── */
export async function checkDuplicates(participantId: string | number): Promise<{
  participant_id: number;
  matches_found: number;
  matches: Array<{ matched_participant_id: number; match_type: string; confidence_score: number }>;
}> {
  return apiFetch(`api/duplicates/check/${toBackendId(participantId)}`, { method: 'POST' });
}

export async function checkDuplicatesRaw(payload: {
  full_name: string;
  email: string;
  organization?: string;
}): Promise<{
  duplicateDetected: boolean;
  confidenceScore: number;
  matchedParticipantId: string | null;
  reason: string;
}> {
  return apiFetch('api/duplicates/check-raw', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function getExistingDuplicateFlags(participantId: string | number) {
  return apiFetch(`api/duplicates/flags/${toBackendId(participantId)}`, { method: 'GET' });
}

/* ── Skills ── */
export async function previewExtraction(rawText: string): Promise<{ normalized_skills: string[] }> {
  return apiFetch('api/skills/extract', {
    method: 'POST',
    body: JSON.stringify({ raw_text: rawText }),
  }, false);
}

export async function extractAndSaveSkills(participantId: string | number) {
  return apiFetch(`api/skills/extract/${toBackendId(participantId)}`, { method: 'POST' });
}

export async function getParticipantSkills(participantId: string | number) {
  return apiFetch(`api/skills/${toBackendId(participantId)}`, { method: 'GET' });
}

/* ── Teams ── */
export interface BackendTeam { id: number; name: string; member_count: number }
export interface BackendTeamComposition {
  team_id: number;
  skill_diversity_score: number;
  skill_coverage_pct: number;
  uniqueness_score: number;
  strength_assessment: string;
  coverage_gaps: string[];
}

export async function createTeam(name: string, memberIds: Array<string | number>) {
  return apiFetch('api/teams/', {
    method: 'POST',
    body: JSON.stringify({ name, member_ids: memberIds.map(toBackendId) }),
  });
}

export async function listTeams(): Promise<BackendTeam[]> {
  return apiFetch('api/teams/', { method: 'GET' });
}

export async function getTeam(teamId: string | number) {
  return apiFetch(`api/teams/${toBackendId(teamId)}`, { method: 'GET' });
}

export async function getTeamComposition(teamId: string | number): Promise<BackendTeamComposition> {
  return apiFetch(`api/teams/${toBackendId(teamId)}/composition`, { method: 'GET' });
}

export async function autoFormTeams(teamSize: number): Promise<{ teams_formed: number; teams: Array<{ name: string; member_ids: number[] }> }> {
  return apiFetch('api/teams/auto-form', {
    method: 'POST',
    body: JSON.stringify({ team_size: teamSize }),
  });
}

/* ── Evaluations ── */
export async function submitEvaluation(payload: {
  project_id: string | number;
  reviewer_id: string | number;
  innovation_score: number;
  technical_score: number;
  impact_score: number;
  presentation_score: number;
  feedback_text: string;
}) {
  return apiFetch('api/evaluations/', {
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
  });
}

export async function listEvaluationsForProject(projectId: string | number) {
  return apiFetch(`api/evaluations/project/${toBackendId(projectId)}`, { method: 'GET' });
}

export async function normalizeScores(): Promise<{ evaluations_normalized: number }> {
  return apiFetch('api/evaluations/normalize', { method: 'POST' });
}

export async function runBiasScan(): Promise<{ cohort_flags: unknown[]; reviewer_flags: unknown[]; total_flags: number }> {
  return apiFetch('api/evaluations/bias-scan', { method: 'POST' });
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

export async function listBiasFlags(statusFilter?: string): Promise<BackendBiasFlag[]> {
  const query = statusFilter ? `?status_filter=${statusFilter}` : '';
  return apiFetch(`api/evaluations/bias-flags${query}`, { method: 'GET' });
}

/* ── Results ── */
export interface BackendRankedProject {
  project_id: number;
  title: string;
  team_name: string;
  raw_mean: number;
  normalized_mean: number;
  confidence_score: number;
  rank: number;
}

export async function getRankings(): Promise<BackendRankedProject[]> {
  const data = await apiFetch<{ rankings: BackendRankedProject[] }>('api/results/rankings', { method: 'GET' });
  return data?.rankings || [];
}

export async function getProjectFeedback(projectId: string | number) {
  return apiFetch(`api/results/feedback/${toBackendId(projectId)}`, { method: 'GET' });
}

/* ── Projects ── */
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
}): Promise<BackendProject> {
  return apiFetch('api/projects/', {
    method: 'POST',
    body: JSON.stringify({ ...payload, team_id: toBackendId(payload.team_id) }),
  });
}

export async function listProjects(): Promise<BackendProject[]> {
  return apiFetch('api/projects/', { method: 'GET' });
}

export async function getProject(projectId: string | number): Promise<BackendProject> {
  return apiFetch(`api/projects/${toBackendId(projectId)}`, { method: 'GET' });
}

/* ── Reviewers ── */
export interface BackendReviewer {
  id: number;
  full_name: string;
  email: string;
  organization: string;
  expertise_text: string;
  max_workload: number;
  participant_id: number | null;
  linkedin_url?: string;
  status: string;
}

export interface BackendReviewerWorkload {
  reviewer_id: number;
  active_assignments: number;
  max_workload: number;
  utilization_pct: number;
}

export async function registerReviewer(payload: {
  full_name: string;
  email: string;
  organization: string;
  expertise_text: string;
  max_workload: number;
}) {
  return apiFetch('api/reviewers/', { method: 'POST', body: JSON.stringify(payload) });
}

export async function listReviewers(): Promise<BackendReviewer[]> {
  return apiFetch('api/reviewers/', { method: 'GET' });
}

export async function getReviewerWorkload(reviewerId: string | number): Promise<BackendReviewerWorkload> {
  return apiFetch(`api/reviewers/${toBackendId(reviewerId)}/workload`, { method: 'GET' });
}

export async function approveReviewer(reviewerId: string | number, status: string): Promise<BackendReviewer> {
  return apiFetch(`api/reviewers/${toBackendId(reviewerId)}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status })
  });
}

export async function runReviewerAssignments(reviewersPerProject: number): Promise<{ assignments_created: number; assignments: unknown[] }> {
  return apiFetch('api/reviewers/assign', {
    method: 'POST',
    body: JSON.stringify({ reviewers_per_project: reviewersPerProject }),
  });
}

export async function getAssignmentsForProject(projectId: string | number) {
  return apiFetch(`api/reviewers/assignments/${toBackendId(projectId)}`, { method: 'GET' });
}

/* ── Communications ── */
export async function sendNotification(payload: {
  participant_id: string | number;
  template_key: string;
  context?: Record<string, unknown>;
}): Promise<{ id: number; status: string; subject: string }> {
  return apiFetch('api/communications/send', {
    method: 'POST',
    body: JSON.stringify({
      participant_id: toBackendId(payload.participant_id),
      template_key: payload.template_key,
      context: payload.context || {},
    }),
  });
}

export async function getAllNotifications(limit = 100): Promise<Array<{ id: number; participant_id: number; subject: string; template_key: string; sent_at: string }>> {
  return apiFetch(`api/communications/all?limit=${limit}`, { method: 'GET' });
}

export async function getParticipantNotifications(participantId: string | number) {
  return apiFetch(`api/communications/participant/${toBackendId(participantId)}`, { method: 'GET' });
}

export async function listNotificationTemplates() {
  return apiFetch('api/communications/templates', { method: 'GET' });
}

/* ── Analytics ── */
export interface BackendAnalyticsOverview {
  participants: { total: number; organizations_represented?: number };
  teams: { total: number };
  projects: { total: number; evaluation_completion_rate_pct?: number };
  evaluations: { total: number; avg_normalized_score?: number | null };
  reviewers: { total: number; active_assignments?: number; workload_balance_variance?: number };
  fairness: { open_bias_flags: number; by_severity?: Record<string, number> };
}

export async function getAnalyticsOverview(): Promise<BackendAnalyticsOverview> {
  return apiFetch('api/analytics/overview', { method: 'GET' }, false);
}

export async function getBiasStreamSummary() {
  return apiFetch('api/bias-stream/summary', { method: 'GET' });
}

export async function getBiasStreamFlags() {
  return apiFetch<{ flags: BackendBiasFlag[]; total: number }>('api/bias-stream/flags/live', { method: 'GET' });
}

/* ── Sync helper: load all backend data after login ── */
export async function syncAllBackendData(): Promise<{
  participants: BackendParticipant[];
  projects: BackendProject[];
  reviewers: BackendReviewer[];
  overview: BackendAnalyticsOverview | null;
  events: BackendEvent[];
  notifications: Array<{ id: number; participant_id: number; subject: string; template_key: string; sent_at: string }>;
  biasFlags: BackendBiasFlag[];
}> {
  const [participants, projects, reviewers, overview, events, notifications, biasFlags] = await Promise.all([
    listParticipants().catch(() => []),
    listProjects().catch(() => []),
    listReviewers().catch(() => []),
    getAnalyticsOverview().catch(() => null),
    listEvents().catch(() => []),
    getAllNotifications().catch(() => []),
    listBiasFlags().catch(() => []),
  ]);
  return { participants, projects, reviewers, overview, events, notifications, biasFlags };
}

/* ── Audit Trails ── */
export interface BackendAuditTrail {
  id: number;
  timestamp: string;
  action: string;
  userRole: string;
  details: string;
  category: string;
}

export async function listAuditTrails(): Promise<BackendAuditTrail[]> {
  return apiFetch('api/audit/', { method: 'GET' });
}

export async function createAuditRecord(payload: {
  action: string;
  user_role: string;
  details: string;
  category: string;
}) {
  return apiFetch('api/audit/', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}
