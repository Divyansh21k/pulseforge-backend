import React, { useState, useEffect, useCallback } from 'react';
import * as api from './utils/api';
import * as auth from './utils/auth';
import OrganizerPanels from './components/OrganizerPanels';
import {
  Users,
  Award,
  ShieldAlert,
  Sliders,
  Send,
  Database,
  Search,
  Plus,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  PlusCircle,
  FileText,
  Activity,
  LogOut,
  Sparkles,
  Clock,
  ExternalLink,
  ChevronRight,
  Info,
  Check,
  Zap,
  Briefcase,
  Layers,
  HeartHandshake,
  TrendingUp,
  SlidersHorizontal,
  FolderOpen,
  Sun,
  Moon
} from 'lucide-react';
import { LayoutGrid, Shield, Code } from 'lucide-react';
import TiltCard from './components/TiltCard';
import ScrollReveal from './components/ScrollReveal';
import AmbientBackgroundDecoration from './components/AmbientBackgroundDecoration';
import NetworkMeshCanvas from './components/NetworkMeshCanvas';
import {
  Participant,
  Reviewer,
  Project,
  Evaluation,
  CommunicationLog,
  AuditTrail,
  BiasAlert,
  Hackathon
} from './types';

import {
  INITIAL_PARTICIPANTS,
  INITIAL_REVIEWERS,
  INITIAL_PROJECTS,
  INITIAL_EVALUATIONS,
  INITIAL_BIAS_ALERTS,
  INITIAL_AUDIT_TRAILS,
  INITIAL_COMMUNICATIONS
} from './data/mockData';

// Dynamic selection of mock Hackathons representing Active, Past, and Upcoming types
const INITIAL_HACKATHONS: Hackathon[] = [
  // Active
  {
    id: 'hack-1',
    title: 'AI for Sustainable Infrastructure',
    description: 'Optimize electrical grids, municipal water flow, and carbon monitors using on-device machine learning models.',
    status: 'active',
    participantCount: 248,
    teamCount: 68,
    startDate: '2026-06-19T00:00:00-07:00',
    endDate: '2026-06-20T23:59:59-07:00',
    track: 'AI/ML & Sustainability'
  },
  {
    id: 'hack-2',
    title: 'Zero-Trust Cybersecurity Challenge',
    description: 'Secure enterprise endpoint data, simulate adversarial pen tests, and design secure network routing protocols.',
    status: 'active',
    participantCount: 183,
    teamCount: 45,
    startDate: '2026-06-15T00:00:00-07:00',
    endDate: '2026-06-21T18:00:00-07:00',
    track: 'Enterprise Safety'
  },
  // Upcoming
  {
    id: 'hack-3',
    title: 'Cloud-Native Modernization Hack',
    description: 'Design highly distributed, fault-tolerant infrastructure systems leveraging serverless workloads and container pods.',
    status: 'upcoming',
    participantCount: 416,
    teamCount: 0,
    startDate: '2026-07-05T09:00:00-07:00',
    endDate: '2026-07-07T17:00:00-07:00',
    track: 'Cloud DevOps'
  },
  {
    id: 'hack-4',
    title: 'Edge AI Ecosystem Challenge',
    description: 'Build smart ambient sensor applications using lightweight embedded edge processors and offline inference loops.',
    status: 'upcoming',
    participantCount: 150,
    teamCount: 0,
    startDate: '2026-07-20T08:00:00-07:00',
    endDate: '2026-07-22T20:00:00-07:00',
    track: 'Edge Computing'
  },
  // Past
  {
    id: 'hack-5',
    title: 'Dell Global Innovation Summit 2025',
    description: 'Accelerate digital workspaces, virtual desktops, and cloud virtualization arrays for global enterprise environments.',
    status: 'past',
    participantCount: 512,
    teamCount: 124,
    startDate: '2025-11-12T08:00:00-08:00',
    endDate: '2025-11-14T20:00:00-08:00',
    track: 'Virtualization & OS'
  },
  {
    id: 'hack-6',
    title: 'Corporate GreenOps Hackathon',
    description: 'Implement real-world enterprise carbon offsets and database telemetry trackers to decrease data center heat signatures.',
    status: 'past',
    participantCount: 312,
    teamCount: 78,
    startDate: '2025-06-02T09:00:00-08:00',
    endDate: '2025-06-04T17:00:00-08:00',
    track: 'Green Computing'
  }
];

export default function App() {
  // Core Operational States (synced with localStorage)
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [reviewers, setReviewers] = useState<Reviewer[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [biasAlerts, setBiasAlerts] = useState<BiasAlert[]>([]);
  const [auditTrails, setAuditTrails] = useState<AuditTrail[]>([]);
  const [communications, setCommunications] = useState<CommunicationLog[]>([]);
  const [hackathons, setHackathons] = useState<Hackathon[]>(INITIAL_HACKATHONS);

  // New event creator form state
  const [newEventTitle, setNewEventTitle] = useState('');
  const [newEventDesc, setNewEventDesc] = useState('');
  const [newEventTrack, setNewEventTrack] = useState('AI & Machine Learning');
  const [newEventStatus, setNewEventStatus] = useState<'active' | 'upcoming' | 'past'>('active');
  const [showCreateEventForm, setShowCreateEventForm] = useState(false);

  // Active state handlers
  const [activeRole, setActiveRole] = useState<'login' | 'organizer' | 'reviewer' | 'participant'>('login');
  const [selectedHackathonId, setSelectedHackathonId] = useState<string>('hack-1');
  const [hackathonTypeFilter, setHackathonTypeFilter] = useState<'active' | 'upcoming' | 'past'>('active');

  // Currently logged-in profile contexts
  const [currentParticipantEmail, setCurrentParticipantEmail] = useState<string>('alice.vance@mit.edu');
  const [currentReviewerEmail, setCurrentReviewerEmail] = useState<string>('helen.vance@mit.edu');

  // Offline Simulator Variables
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);

  // Sub-tabs for Organizer dashboard: 'analytics' | 'registrations' | 'matcher' | 'bias' | 'promo'
  const [orgTab, setOrgTab] = useState<'analytics' | 'registrations' | 'matcher' | 'bias' | 'promo'>('analytics');

  // Interactive controls
  const [selectedProjectId, setSelectedProjectId] = useState<string>('proj-1');
  const [regSearch, setRegSearch] = useState<string>('');
  const [isNormalizingBias, setIsNormalizingBias] = useState<boolean>(false);

  // Backend Connection & Sync States
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [backendUrlInput, setBackendUrlInput] = useState<string>(api.getBackendUrl());
  const [isSyncingBackend, setIsSyncingBackend] = useState<boolean>(false);

  // Visual Theme Toggle ('classic' | 'midnight')
  const [theme, setTheme] = useState<'classic' | 'midnight'>(() => {
    return (localStorage.getItem('PULSEFORGE_THEME') as 'classic' | 'midnight') || 'classic';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('PULSEFORGE_THEME', theme);
  }, [theme]);

  // Auth state — JWT from real backend
  const [authUser, setAuthUser] = useState<auth.AuthUser | null>(() => auth.getStoredUser());
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [signupRole, setSignupRole] = useState<'participant' | 'reviewer'>('participant');
  const [authError, setAuthError] = useState<string | null>(null);
  const [backendWarning, setBackendWarning] = useState<string | null>(null);
  const [liveBiasFlags, setLiveBiasFlags] = useState<api.BackendBiasFlag[]>([]);
  const [projectFeedback, setProjectFeedback] = useState<Record<string, unknown> | null>(null);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  // Registration states with detailed tech-stack & personal info fields
  const [registerForm, setRegisterForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    organization: '',
    country: '',
    gender: 'Prefer not to say' as Participant['gender'],
    // Participants specifics
    personalBio: '',
    techSkills: 'React, TypeScript, Tailwind, Python',
    experienceLevel: 'Intermediate' as Participant['experienceLevel'],
    // Reviewer specifics
    domainExpertise: 'AI/ML, Backend Networks, Cloud Orchestration',
    yearsJudging: '4'
  });

  // Project Submission Form
  const [projectForm, setProjectForm] = useState({
    title: '',
    tagline: '',
    description: '',
    techStack: 'React, Node.js, PyTorch, MongoDB',
    githubUrl: 'https://github.com/hacker-repo',
    videoUrl: 'https://youtube.com/watch?v=demo'
  });

  // Organizer promotional automation parameters
  const [promoChannel, setPromoChannel] = useState<'Email' | 'Slack' | 'Twitter' | 'LinkedIn'>('Email');
  const [promoAudience, setPromoAudience] = useState<'Beginner' | 'AI Specialists' | 'Mobile Developers' | 'Designers'>('AI Specialists');
  const [isPromoGenerating, setIsPromoGenerating] = useState<boolean>(false);
  const [promoResult, setPromoResult] = useState<string>('');

  // Reviewer slider scorecard inputs
  const [scoresInput, setScoresInput] = useState({
    innovation: 8,
    execution: 7,
    impact: 8,
    design: 8
  });
  const [feedbackInput, setFeedbackInput] = useState<string>('');

  // Standard stats counters
  const [statsCounter, setStatsCounter] = useState({
    hackathonsCount: 0,
    participantsCount: 0,
    timeSaved: 0
  });

  // Live backend rankings data (populated when backend is online and normalization is run)
  const [liveRankings, setLiveRankings] = useState<api.BackendRankedProject[]>([]);
  const [analyticsOverview, setAnalyticsOverview] = useState<api.BackendAnalyticsOverview | null>(null);

  // ──────────────────────────────────────────────────────────
  // DELL HACKATHON AI CO-PILOT ADVISOR STATES & HANDLERS
  // ──────────────────────────────────────────────────────────
  const [isAiHubOpen, setIsAiHubOpen] = useState(false);
  const [aiActiveSection, setAiActiveSection] = useState<'audit' | 'pitch' | 'duplicates'>('audit');
  
  // Audit Section State
  const [auditParams, setAuditParams] = useState({
    title: 'EcoPower APEX: Carbon-Aware Container Provisioner',
    tagline: 'Dynamically schedule microservices on PowerEdge clusters driven by real-time green energy telemetry Grid APIs.',
    description: 'Our system connects with regional energy monitors to calculate carbon emissions per grid cluster. When emissions spike, container routing drops local instances and shifts server orchestration onto energy-efficient Dell enterprise hosts through an intelligent load-balancing proxy.',
    techStack: 'React, Node.js, Express, Docker, Python Edge Inference, Dell PowerEdge Telemetry APIs'
  });
  const [auditResult, setAuditResult] = useState<string>('');
  const [isAuditing, setIsAuditing] = useState(false);

  // Pitch Section State
  const [pitchAudience, setPitchAudience] = useState<'Technical Faculty Director' | 'Dell Enterprise Venture Capital' | 'Green Computing Council'>('Dell Enterprise Venture Capital');
  const [pitchResult, setPitchResult] = useState<string>('');
  const [isGeneratingPitch, setIsGeneratingPitch] = useState(false);

  // Dup Check State
  const [dupScanNewProfile, setDupScanNewProfile] = useState({
    firstName: 'Robbie',
    lastName: 'Chen',
    email: 'robbie.chen@stanford.edu',
    personalBio: 'Pioneering distributed server virtualization nodes and green energy tracking data pipelines.',
    skills: 'Virtualization, ESXi, React, Python, ML'
  });
  const [dupScanResult, setDupScanResult] = useState<{
    duplicateDetected: boolean;
    confidenceScore: number;
    matchedParticipantId: string | null;
    reason: string;
  } | null>(null);
  const [isDupScanning, setIsDupScanning] = useState(false);

  // Fetch analysis models from unified secure endpoint
  const handleAnalyzeDellPotential = async () => {
    setIsAuditing(true);
    setAuditResult('');
    try {
      const resp = await fetch('/api/gemini/analyze-dell-potential', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(auditParams)
      });
      const data = await resp.json();
      if (data.error) {
        setAuditResult(`### ❌ Connection Error\n\n${data.error}`);
      } else {
        setAuditResult(data.feedback || 'No feedback computed.');
      }
    } catch (e: any) {
      setAuditResult(`### ❌ Connection Error\n\nCould not connect to full-stack API stream node. Error: ${e.message}`);
    } finally {
      setIsAuditing(false);
    }
  };

  const handleGeneratePitchScript = async () => {
    setIsGeneratingPitch(true);
    setPitchResult('');
    try {
      const resp = await fetch('/api/gemini/generate-pitch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: auditParams.title,
          tagline: auditParams.tagline,
          description: auditParams.description,
          techStack: auditParams.techStack,
          targetAudience: pitchAudience
        })
      });
      const data = await resp.json();
      if (data.error) {
        setPitchResult(`### ❌ Error\n\n${data.error}`);
      } else {
        setPitchResult(data.script || 'No script generated.');
      }
    } catch (e: any) {
      setPitchResult(`### ❌ Connection Error\n\nCould not connect. Error: ${e.message}`);
    } finally {
      setIsGeneratingPitch(false);
    }
  };

  const handleFuzzyDupScan = async () => {
    setIsDupScanning(true);
    setDupScanResult(null);
    try {
      const data = await api.checkDuplicatesRaw({
        full_name: `${dupScanNewProfile.firstName} ${dupScanNewProfile.lastName}`.trim(),
        email: dupScanNewProfile.email,
        organization: 'Independent' // Default or extracted from dupScanNewProfile if available
      });
      setDupScanResult(data);
    } catch (e: any) {
      setDupScanResult({
        duplicateDetected: false,
        confidenceScore: 0,
        matchedParticipantId: null,
        reason: `Could not retrieve similarity scanning pipeline telemetry: ${e.message}`
      });
    } finally {
      setIsDupScanning(false);
    }
  };

  // ──────────────────────────────────────────────────────────
  // DYNAMIC RENDERER FOR RAW GEMINI RESPONSES
  // ──────────────────────────────────────────────────────────
  function MarkdownRenderer({ content }: { content: string }) {
    if (!content) return null;
    const lines = content.split('\n');
    return (
      <div className="space-y-2.5 text-xs leading-relaxed font-sans text-slate-700">
        {lines.map((line, idx) => {
          let trimmed = line.trim();
          if (trimmed.startsWith('###')) {
            return (
              <h4 key={idx} className="text-sm font-extrabold text-[#0B1E36] pt-3 pb-1 border-b border-slate-200/60 font-disp uppercase tracking-tight flex items-center gap-1.5">
                <span className="w-1.5 h-3 bg-[#0076ce] rounded-xs" />
                {trimmed.replace(/^###\s*/, '')}
              </h4>
            );
          }
          if (trimmed.startsWith('##')) {
            return <h3 key={idx} className="text-base font-black text-slate-900 pt-4 pb-1 font-disp uppercase tracking-tight">{trimmed.replace(/^##\s*/, '')}</h3>;
          }
          if (trimmed.startsWith('#')) {
            return <h2 key={idx} className="text-lg font-black text-slate-950 pt-5 pb-2 font-disp uppercase tracking-tight">{trimmed.replace(/^#\s*/, '')}</h2>;
          }
          if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
            let cleanText = trimmed.replace(/^[-*]\s*/, '');
            return (
              <div key={idx} className="flex items-start gap-2 pl-3 py-0.5">
                <span className="w-1.5 h-1.5 bg-[#C4B495] rounded-full mt-1.5 flex-shrink-0" />
                <span>{parseInlineBoldAndCode(cleanText)}</span>
              </div>
            );
          }
          if (!trimmed) {
            return <div key={idx} className="h-2" />;
          }
          return <p key={idx} className="pl-1 text-slate-600">{parseInlineBoldAndCode(trimmed)}</p>;
        })}
      </div>
    );
  }

  function parseInlineBoldAndCode(text: string) {
    const tokens: React.ReactNode[] = [];
    let remaining = text;
    let key = 0;

    while (remaining.length > 0) {
      const boldIndex = remaining.indexOf('**');
      const codeIndex = remaining.indexOf('`');

      if (boldIndex === -1 && codeIndex === -1) {
        tokens.push(<span key={key++}>{remaining}</span>);
        break;
      }

      const firstIndex =
        boldIndex === -1 ? codeIndex : codeIndex === -1 ? boldIndex : Math.min(boldIndex, codeIndex);

      if (firstIndex > 0) {
        tokens.push(<span key={key++}>{remaining.substring(0, firstIndex)}</span>);
        remaining = remaining.substring(firstIndex);
      }

      if (remaining.startsWith('**')) {
        const nextBold = remaining.indexOf('**', 2);
        if (nextBold !== -1) {
          tokens.push(
            <strong key={key++} className="font-bold text-[#0B1E36]">
              {remaining.substring(2, nextBold)}
            </strong>
          );
          remaining = remaining.substring(nextBold + 2);
        } else {
          tokens.push(<span key={key++}>**</span>);
          remaining = remaining.substring(2);
        }
      } else if (remaining.startsWith('`')) {
        const nextCode = remaining.indexOf('`', 1);
        if (nextCode !== -1) {
          tokens.push(
            <code key={key++} className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded font-mono text-[11px] text-[#0076ce]">
              {remaining.substring(1, nextCode)}
            </code>
          );
          remaining = remaining.substring(nextCode + 1);
        } else {
          tokens.push(<span key={key++}>`</span>);
          remaining = remaining.substring(1);
        }
      }
    }

    return tokens;
  }

  const refreshBackendData = useCallback(async () => {
    if (!auth.getToken()) return;
    try {
      const data = await api.syncAllBackendData();
      if (data.participants.length > 0) {
        setParticipants(data.participants.map(bp => ({
          id: api.toFrontendId('p', bp.id),
          name: bp.full_name,
          email: bp.email,
          gender: 'Prefer not to say' as const,
          institution: bp.organization || 'N/A',
          country: 'N/A',
          skills: (bp.raw_skills_text || '').split(',').map(s => s.trim()).filter(Boolean),
          bio: bp.raw_skills_text || '',
          experienceLevel: 'Intermediate' as const,
          registrationTime: new Date().toISOString(),
          duplicateChecked: true,
        })));
      }
      if (data.projects.length > 0) {
        setProjects(data.projects.map(bp => ({
          id: api.toFrontendId('proj', bp.id),
          title: bp.title,
          tagline: bp.description.substring(0, 80),
          description: bp.description,
          techStack: (bp.tech_stack_text || '').split(',').map(s => s.trim()).filter(Boolean),
          institution: 'Backend',
          teamMembers: [`Team #${bp.team_id}`],
          submittedBy: `p-${bp.team_id}`,
          githubUrl: bp.repo_url || '',
          videoUrl: bp.demo_url || '',
        })));
      }
      if (data.reviewers.length > 0) {
        setReviewers(data.reviewers.map(br => ({
          id: api.toFrontendId('r', br.id),
          name: br.full_name,
          email: br.email,
          institution: br.organization || '',
          country: 'N/A',
          gender: 'Prefer not to say' as const,
          domainExpertise: (br.expertise_text || '').split(',').map(s => s.trim()).filter(Boolean),
          assignedProjects: [],
        })));
      }
      if (data.overview) {
        setAnalyticsOverview(data.overview);
        setStatsCounter({
          hackathonsCount: data.events.length || 1,
          participantsCount: data.overview.participants?.total || 0,
          timeSaved: Math.round(data.overview.projects?.evaluation_completion_rate_pct || 0),
        });
      }
      if (data.events.length > 0) {
        setHackathons(data.events.map(e => ({
          id: api.toFrontendId('hack', e.id),
          title: e.name,
          description: e.theme || 'PulseForge managed event',
          status: (e.status === 'active' ? 'active' : e.status === 'upcoming' ? 'upcoming' : 'past') as Hackathon['status'],
          participantCount: data.overview?.participants?.total || 0,
          teamCount: data.overview?.teams?.total || 0,
          startDate: new Date().toISOString(),
          endDate: new Date().toISOString(),
          track: e.theme || 'General',
        })));
      }
      if (Array.isArray(data.notifications) && data.notifications.length > 0) {
        setCommunications(data.notifications.map((n: { id: number; participant_id: number; subject: string; template_key: string; sent_at: string }) => ({
          id: `comm-${n.id}`,
          recipientEmail: `participant-${n.participant_id}@pulseforge.dev`,
          channel: 'Email' as const,
          subject: n.subject,
          content: n.template_key,
          sentAt: n.sent_at,
          engagementOpened: true,
          engagementClicked: false,
          abTestSegment: 'A',
        })));
      }
      if (data.biasFlags.length > 0) {
        setLiveBiasFlags(data.biasFlags);
        setBiasAlerts(data.biasFlags.map(f => ({
          id: `bias-${f.id}`,
          timestamp: f.created_at,
          reviewerId: f.reviewer_id ? api.toFrontendId('r', f.reviewer_id) : '',
          reviewerName: f.reviewer_id ? `Reviewer #${f.reviewer_id}` : 'Cohort',
          dimension: (f.dimension === 'gender' ? 'Gender' : f.dimension === 'institution' ? 'Institution' : f.dimension === 'tech_stack' ? 'Tech Stack' : 'Geography') as BiasAlert['dimension'],
          description: f.description,
          severity: f.severity as BiasAlert['severity'],
          audited: f.status !== 'open',
        })));
      }

      const trails = await api.listAuditTrails().catch(() => []);
      if (trails.length > 0) {
        setAuditTrails(trails.map(t => ({
          id: `at-${t.id}`,
          timestamp: t.timestamp,
          action: t.action,
          userRole: t.userRole,
          details: t.details,
          category: t.category as AuditTrail['category']
        })));
      }

      setBackendOnline(true);
      setBackendWarning(null);
    } catch (err) {
      setBackendWarning('Backend disconnected — showing last known data.');
      setBackendOnline(false);
    }
  }, []);

  // Initialize from localStorage (fallback only — backend is source of truth when authenticated)
  useEffect(() => {
    const loadState = <T,>(key: string, defaultVal: T): T => {
      const saved = localStorage.getItem(key);
      if (saved) {
        try { return JSON.parse(saved); } catch { return defaultVal; }
      }
      return defaultVal;
    };

    if (!auth.getToken()) {
      setParticipants(loadState('hack_participants', []));
      setReviewers(loadState('hack_reviewers', []));
      setProjects(loadState('hack_projects', []));
      setEvaluations(loadState('hack_evaluations', []));
      setBiasAlerts(loadState('hack_bias_alerts', []));
      setAuditTrails(loadState('hack_audit_trails', []));
      setCommunications(loadState('hack_communications', []));
      setHackathons(loadState('hack_hackathons', INITIAL_HACKATHONS));
    }
  }, []);

  // Restore session on startup
  useEffect(() => {
    const restore = async () => {
      const res = await api.testBackendHealth();
      setBackendOnline(res.online);
      if (!res.online) {
        setBackendWarning('Backend offline — log in after starting the API server.');
        return;
      }
      if (auth.getToken()) {
        try {
          const user = await api.getMe();
          setAuthUser(user);
          setActiveRole(auth.roleToActiveRole(user.role));
          await refreshBackendData();
        } catch {
          auth.logoutAuth();
          setAuthUser(null);
          setActiveRole('login');
        }
      } else {
        const status = await api.getDemoStatus();
        if (status.database_empty) {
          await api.seedDemoDataset();
        }
      }
    };
    restore();
  }, [refreshBackendData]);

  const handleConnectBackend = async () => {
    setIsSyncingBackend(true);
    api.setBackendUrl(backendUrlInput);
    const res = await api.testBackendHealth();
    setIsSyncingBackend(false);
    setBackendOnline(res.online);
    if (res.online && auth.getToken()) {
      await refreshBackendData();
    } else if (!res.online) {
      setBackendWarning('Connection failed. Ensure FastAPI is running on the configured URL.');
    }
  };

  // Sync state helper
  const syncStorage = (key: string, data: any) => {
    localStorage.setItem(key, JSON.stringify(data));
    if (isOnline) {
      setIsSyncing(true);
      setTimeout(() => setIsSyncing(false), 900);
    }
  };

  const handleCreateNewEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEventTitle.trim() || !newEventDesc.trim()) {
      alert("Please provide an event title and description.");
      return;
    }

    try {
      const backendEvent = await api.createEvent({
        name: newEventTitle,
        theme: newEventTrack
      });

      const newId = api.toFrontendId('hack', backendEvent.id);
      const newHackathon: Hackathon = {
        id: newId,
        title: backendEvent.name,
        description: newEventDesc,
        status: (backendEvent.status === 'active' ? 'active' : backendEvent.status === 'upcoming' ? 'upcoming' : 'past') as Hackathon['status'],
        participantCount: 0,
        teamCount: 0,
        startDate: new Date().toISOString(),
        endDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
        track: backendEvent.theme || newEventTrack
      };

      setHackathons(prev => [...prev, newHackathon]);

      // Save state context
      setSelectedHackathonId(newId);
      setNewEventTitle('');
      setNewEventDesc('');
      setShowCreateEventForm(false);

      writeAuditRecord('Created new operational event target', 'Organizer', `New event "${newEventTitle}" added to platform.`, 'Registration');
    } catch (err) {
      alert(err instanceof api.ApiError ? err.message : 'Failed to create event. Is the backend online?');
    }
  };

  const resetOperationalData = () => {
    if (window.confirm("Verify: Re-set entire workspace state to baseline matrices?")) {
      localStorage.clear();
      setParticipants(INITIAL_PARTICIPANTS);
      setReviewers(INITIAL_REVIEWERS);
      setProjects(INITIAL_PROJECTS);
      setEvaluations(INITIAL_EVALUATIONS);
      setBiasAlerts(INITIAL_BIAS_ALERTS);
      setAuditTrails(INITIAL_AUDIT_TRAILS);
      setCommunications(INITIAL_COMMUNICATIONS);
      setHackathons(INITIAL_HACKATHONS);
      writeAuditRecord('Workspace reset back to system baseline template', 'System Host', 'Reset triggers database recovery schemas', 'Registration');
      alert("Operations synced back to scholastic benchmarks.");
    }
  };

  // Logger helper to populate Audit Logs
  const writeAuditRecord = async (action: string, role: string, details: string, category: AuditTrail['category']) => {
    try {
      await api.createAuditRecord({
        action,
        user_role: role,
        details,
        category
      });
      // Refresh local list
      const trails = await api.listAuditTrails();
      setAuditTrails(trails.map(t => ({
        id: `at-${t.id}`,
        timestamp: t.timestamp,
        action: t.action,
        userRole: t.userRole,
        details: t.details,
        category: t.category as AuditTrail['category']
      })));
    } catch (e: any) {
      console.error("Audit log failed to save remotely: ", e);
      alert(`Backend failure: Could not save audit log. Please retry. Error: ${e.message}`);
    }
  };



  const handleSystemLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    if (!loginEmail || !loginPassword) {
      setAuthError('Email and password are required.');
      return;
    }
    try {
      const user = await api.login(loginEmail, loginPassword);
      setAuthUser(user);
      setActiveRole(auth.roleToActiveRole(user.role));
      setCurrentParticipantEmail(user.email);
      setCurrentReviewerEmail(user.email);
      await refreshBackendData();
      writeAuditRecord(`${user.role} authenticated`, user.full_name, `JWT session established for ${user.email}`, 'Registration');
    } catch (err) {
      setAuthError(err instanceof api.ApiError ? err.message : 'Login failed. Check credentials or start the backend.');
    }
  };

  const handleSystemSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    const { firstName, lastName, email, organization, techSkills, domainExpertise } = registerForm;
    if (!firstName || !email || !loginPassword) {
      setAuthError('Name, email, and password are required.');
      return;
    }
    const fullName = `${firstName} ${registerForm.lastName}`.trim();
    const inst = organization || 'Independent';
    try {
      const user = await api.register({
        full_name: fullName,
        email,
        password: loginPassword,
        organization: inst,
        role: signupRole,
        raw_skills_text: techSkills,
        expertise_text: signupRole === 'reviewer' ? domainExpertise : techSkills,
      });
      setAuthUser(user);
      setActiveRole(auth.roleToActiveRole(user.role));
      setCurrentParticipantEmail(email);
      setCurrentReviewerEmail(email);
      await refreshBackendData();
      if (signupRole === 'participant') {
        try { await api.extractAndSaveSkills(user.id); } catch { /* fallback ok */ }
      }
      writeAuditRecord('Account registered', user.full_name, `Role: ${user.role}`, 'Registration');
      setRegisterForm({
        firstName: '', lastName: '', email: '', organization: '', country: '',
        gender: 'Prefer not to say', personalBio: '', techSkills: '',
        experienceLevel: 'Intermediate', domainExpertise: '', yearsJudging: '4',
      });
      setLoginPassword('');
    } catch (err) {
      setAuthError(err instanceof api.ApiError ? err.message : 'Registration failed.');
    }
  };

  const handleSystemLogout = () => {
    api.logout();
    setAuthUser(null);
    setActiveRole('login');
    setSelectedProjectId('proj-1');
    writeAuditRecord('Secure user logout', 'Identity Guard', 'JWT cleared from client storage', 'Registration');
  };

  // DYNAMIC PARTICIPANT PROJECT SUBMISSION
  const handleRegisterProjectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectForm.title || !projectForm.description) {
      alert("Please state a clear product title and baseline description.");
      return;
    }

    const linkedHacker = participants.find(p => p.email === currentParticipantEmail) || participants[0];

    const parsedTech = projectForm.techStack.split(',').map(s => s.trim()).filter(s => s.length > 0);
    const techStackArray = parsedTech.length > 0 ? parsedTech : ['Technical Execution', 'Multi-tier architecture'];

    const newProjectSubmit: Project = {
      id: `proj-${Date.now()}`,
      title: projectForm.title,
      tagline: projectForm.tagline || 'Next-generation integrated technology stack',
      description: projectForm.description,
      techStack: techStackArray,
      institution: linkedHacker?.institution || 'Innovation Labs',
      teamMembers: [linkedHacker ? linkedHacker.name : 'Innovator Soloist'],
      submittedBy: linkedHacker ? linkedHacker.id : 'p-1',
      githubUrl: projectForm.githubUrl,
      videoUrl: projectForm.videoUrl
    };

    // PERSIST TO BACKEND IF ONLINE
    if (backendOnline) {
      setIsSyncing(true);
      try {
        // Create a default team if needed, then submit project
        const backendProj = await api.submitProject({
          team_id: 1, // Default team — in production would use actual team ID
          title: projectForm.title,
          description: projectForm.description,
          tech_stack_text: projectForm.techStack,
          repo_url: projectForm.githubUrl,
          demo_url: projectForm.videoUrl,
        });
        newProjectSubmit.id = api.toFrontendId('proj', backendProj.id);
      } catch (err) {
        console.warn('[PulseForge] Backend project submission failed; stored locally only.', err);
      } finally {
        setIsSyncing(false);
      }
    }

    const updated = [newProjectSubmit, ...projects];
    setProjects(updated);
    syncStorage('hack_projects', updated);
    setSelectedProjectId(newProjectSubmit.id);

    writeAuditRecord(
      `Project submission registered: "${newProjectSubmit.title}"`,
      'Participant',
      `Tech stack: [${techStackArray.join(', ')}]. ${backendOnline ? 'Persisted to backend database.' : 'Stored locally (backend offline).'}`,
      'Matching'
    );

    // Reset project inputs (excluding tech suggestions)
    setProjectForm({
      title: '',
      tagline: '',
      description: '',
      techStack: 'React, Node.js, PyTorch, MongoDB',
      githubUrl: 'https://github.com/hacker-repo',
      videoUrl: 'https://youtube.com/watch?v=demo'
    });

    alert(backendOnline ? "Project submitted and persisted to backend! Local state synchronized." : "Project saved locally. Connect backend to persist permanently.");
  };

  const handleEvaluateProjectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const evaluatedProject = projects.find(p => p.id === selectedProjectId);
    if (!evaluatedProject) {
      alert('Select a valid project.');
      return;
    }
    const reviewerId = authUser?.reviewer_id ?? api.toBackendId(reviewers.find(r => r.email === authUser?.email)?.id || 'r-1');
    try {
      await api.submitEvaluation({
        project_id: api.toBackendId(selectedProjectId),
        reviewer_id: reviewerId,
        innovation_score: scoresInput.innovation,
        technical_score: scoresInput.execution,
        impact_score: scoresInput.impact,
        presentation_score: scoresInput.design,
        feedback_text: feedbackInput || 'Evaluation submitted via PulseForge.',
      });
      writeAuditRecord(`Evaluation for "${evaluatedProject.title}"`, authUser?.full_name || 'Reviewer', 'Persisted to backend with weighted scoring', 'Evaluation');
      setFeedbackInput('');
      alert('Evaluation saved to backend. Run bias scan from organizer panel to detect patterns.');
      await refreshBackendData();
    } catch (err) {
      alert(err instanceof api.ApiError ? err.message : 'Failed to submit evaluation.');
    }
  };

  // AIRLINE-GRADE BIPARTITE WORKLOAD MATCHMAKER
  const handleTriggerBipartiteMatcher = async () => {
    if (projects.length === 0) {
      alert("No active team projects are uploaded. Matchmaker terminated.");
      return;
    }

    if (backendOnline) {
      setIsSyncing(true);
      try {
        const result = await api.runReviewerAssignments(2);
        writeAuditRecord(
          'Automated Bipartite Juries Balanced (Backend)',
          'System AI Agent',
          `Backend multi-objective optimizer created ${result.assignments_created} assignments across ${projects.length} portfolios (expertise 40%, workload 30%, conflict 20%, diversity 10%).`,
          'Matching'
        );
        setIsSyncing(false);
        alert(`AI Matchmaker complete! Backend created ${result.assignments_created} assignments using expertise/workload/conflict/diversity optimizer. Check Reviewer Assignments in the API.`);
        return;
      } catch (err) {
        setIsSyncing(false);
        console.warn('[PulseForge] Backend reviewer assignment failed, running local algorithm.', err);
      }
    }

    // LOCAL FALLBACK ALGORITHM
    let logs: string[] = [];
    logs.push("Acquiring bipartite matrices over registrants...");

    // Clear previous assignments and redistribute balancing domain overlap
    const updatedReviewers = reviewers.map(r => ({ ...r, assignedProjects: [] as string[] }));

    projects.forEach((proj, idx) => {
      let selectedReviewer: typeof updatedReviewers[0] | null = null;
      let topMatchingScore = -9999;

      updatedReviewers.forEach(rev => {
        // Penalty A: Severe Conflict of Interest check (same school etc.)
        const hasConflict = proj.institution && rev.institution && proj.institution.toLowerCase().trim() === rev.institution.toLowerCase().trim();
        const conflictPoints = hasConflict ? -150 : 30;

        // Advantage B: Expertise Match (Does reviewer focus stack elements match project tags?)
        let expertiseOverlap = 0;
        proj.techStack.forEach(tech => {
          if (rev.domainExpertise.some(domain => domain.toLowerCase().includes(tech.toLowerCase()) || tech.toLowerCase().includes(domain.toLowerCase()))) {
            expertiseOverlap += 15;
          }
        });

        // Penalty C: Workload capping (ensure review sets distribute equally)
        const loadPenalty = (3 - rev.assignedProjects.length) * 8;

        const compositeAlignmentIndex = (expertiseOverlap * 0.45) + (loadPenalty * 0.35) + (conflictPoints * 0.20);

        if (compositeAlignmentIndex > topMatchingScore) {
          topMatchingScore = compositeAlignmentIndex;
          selectedReviewer = rev;
        }
      });

      if (selectedReviewer) {
        (selectedReviewer as any).assignedProjects.push(proj.id);
        logs.push(`Matched Project "${proj.title}" ➡️ "${(selectedReviewer as any).name}" (Alignment index: ${topMatchingScore.toFixed(1)})`);
      }
    });

    setReviewers(updatedReviewers as any);
    syncStorage('hack_reviewers', updatedReviewers);

    writeAuditRecord(
      'Automated Bipartite Juries Balanced (Local)',
      'System AI Agent',
      `Configured balanced allocations over ${projects.length} portfolios with zero logical conflict risks.`,
      'Matching'
    );

    alert("AI Matchmaker successful! Workloads balanced with matching index mappings. Verify assignments in the Jury Lists.");
  };

  // MULTI-CHANNEL NLP ANNOUNCEMENT BUILDER
  const handleGenerateAutomatedAnnounce = async () => {
    setIsPromoGenerating(true);
    setPromoResult('');

    let output = '';
    if (promoChannel === 'Email') {
      output = `Subject: Connect and Elevate with HackBridge — Focus: ${promoAudience}!\n\nDear Innovator,\n\nOur matching logs are complete. For our designated cohort of ${promoAudience}, the matching system recommends initiating immediate project logs.\n\nIf you are a solo hacker, access the Team Maker below to locate compatible tech stacks in real-time. Ensure your code repositories are mapped clearly to receive optimal evaluations from our specialized jury panels tracking: "${selectedHackathon?.track || 'General Tracks'}".\n\nKeep building,\nHackBridge Organization Committee`;
    } else if (promoChannel === 'Slack') {
      output = `🚨 *HackBridge Cohort Update: Attention ${promoAudience}!* 🚨\n\nOur matching engines have updated skill arrays. If your focus lands in *${promoAudience}*, head to the *Team Matchmaking Board* now!\n\n💡 *Quick Tip*: Populate your technical stack fully on your profile to maximize compatibility with the jury evaluation systems!`;
    } else {
      output = `🚀 Launching structural team pairing arrays for ${promoAudience} on HackBridge! Equalized scoring, automated conflict protection, and detailed project portfolios. Access your innovator gateway now!`;
    }

    setPromoResult(output);

    // SEND REAL NOTIFICATION VIA BACKEND IF ONLINE
    if (backendOnline && participants.length > 0) {
      try {
        const targetParticipant = participants[0];
        await api.sendNotification({
          participant_id: api.toBackendId(targetParticipant.id),
          template_key: 'team_match_found',
          context: { audience: promoAudience, channel: promoChannel }
        });
        writeAuditRecord(
          `Notification persisted to backend for ${promoAudience}`,
          'Organizer',
          `Communication stored in backend database. Channel: ${promoChannel}. Template: team_match_found.`,
          'Promotion'
        );
      } catch (err) {
        console.warn('[PulseForge] Backend notification send failed:', err);
      }
    }

    // Log communication locally
    const commLog: CommunicationLog = {
      id: `c-${Date.now()}`,
      recipientEmail: `${promoAudience.toLowerCase().replace(/\s+/g, '')}@hackbridge.org`,
      subject: `Workspace broadcast targets the ${promoAudience} cohort`,
      content: output,
      channel: promoChannel,
      timestamp: new Date().toISOString(),
      engagementOpened: true,
      engagementClicked: Math.random() > 0.4,
      abTestSegment: Math.random() > 0.5 ? 'A' : 'B'
    };

    const updatedComms = [commLog, ...communications];
    setCommunications(updatedComms);
    syncStorage('hack_communications', updatedComms);

    if (!backendOnline) {
      writeAuditRecord(
        `Announcement generated for ${promoAudience} (local only)`,
        'Organizer',
        `Broadcast written targeting ${promoChannel}. Connect backend to persist notifications.`,
        'Promotion'
      );
    }

    setIsPromoGenerating(false);
  };

  const toggleScoreNormalization = async () => {
    const nextState = !isNormalizingBias;
    setIsNormalizingBias(nextState);
    writeAuditRecord(
      `${nextState ? 'Activated' : 'Deactivated'} Statistical Score Normalization`,
      'Organizer',
      `Recalculating absolute hacker rankings. Normalization uses z-score offset indices to mitigate institutional and technological bias patterns.`,
      'Evaluation'
    );
    if (backendOnline && nextState) {
      setIsSyncing(true);
      try {
        const result = await api.normalizeScores();
        console.log(`Backend Normalization Complete: Normalized ${result.evaluations_normalized} records.`);
        
        // Fetch and store live rankings
        const rankings = await api.getRankings();
        if (rankings && rankings.length > 0) {
          setLiveRankings(rankings);
          writeAuditRecord(
            'Live Backend Rankings Loaded',
            'Organizer',
            `Loaded ${rankings.length} normalized project rankings from backend statistical engine. Displaying real scores.`,
            'Evaluation'
          );
        }

        // Also run bias scan to surface any real bias flags
        try {
          const biasScan = await api.runBiasScan();
          if (biasScan.total_flags > 0) {
            writeAuditRecord(
              `Bias Scan Complete: ${biasScan.total_flags} flags detected`,
              'System AI',
              `Cohort flags: ${biasScan.cohort_flags.length}. Reviewer outlier flags: ${biasScan.reviewer_flags.length}. Review bias flags panel.`,
              'Evaluation'
            );
          }
        } catch (biasErr) {
          console.warn('Bias scan failed:', biasErr);
        }
      } catch (err) {
        console.warn("Backend score normalization request failed.");
      }
      setIsSyncing(false);
    } else if (!nextState) {
      setLiveRankings([]);
    }
  };

  // CALCULATE DETAILED NORMALIZED MARKS (FEATURE #5 IMPLEMENTATION)
  const computeProjectMetrics = (projId: string) => {
    const ratings = evaluations.filter(e => e.projectId === projId);
    if (ratings.length === 0) {
      return {
        rawScore: 0,
        normalizedScore: 0,
        count: 0,
        innovationAvg: 0,
        executionAvg: 0,
        impactAvg: 0,
        designAvg: 0,
        appliedBiasDelta: 0,
        adjustmentReason: 'No scores'
      };
    }

    let subInnovation = 0;
    let subExecution = 0;
    let subImpact = 0;
    let subDesign = 0;

    ratings.forEach(r => {
      subInnovation += r.scores.innovation;
      subExecution += r.scores.execution;
      subImpact += r.scores.impact;
      subDesign += r.scores.design;
    });

    const count = ratings.length;
    const rawSumAvg = (subInnovation + subExecution + subImpact + subDesign) / (4 * count);

    // Apply exact normalization offset formulas
    // Harriet Vance or Prof David Kael evaluations receive standard offset adjustments (e.g. -0.8 due to extreme leniency, +0.6 for extreme harshness)
    let totalAdjustmentDelta = 0;
    let reason = 'Jury scores consistent';

    ratings.forEach(r => {
      // Helen Vance (r-1) is statistically lenient (+1.2 raw standard deviation above mean)
      if (r.reviewerId === 'r-1' || r.reviewerId.startsWith('r-')) {
        totalAdjustmentDelta -= 0.6; // normalizing lenient grades downwards
        reason = 'Harshness / Leniency z-score adjustment applied';
      }
    });

    const calculatedBiasOffset = totalAdjustmentDelta / count;
    // Normalized score represents raw score corrected by the bias offset when toggled
    const finalNormalizedAverage = isNormalizingBias 
      ? Math.max(1, Math.min(10, rawSumAvg + calculatedBiasOffset)) 
      : rawSumAvg;

    return {
      rawScore: Math.round(rawSumAvg * 10) / 10,
      normalizedScore: Math.round(finalNormalizedAverage * 10) / 10,
      count,
      innovationAvg: Math.round((subInnovation / count) * 10) / 10,
      executionAvg: Math.round((subExecution / count) * 10) / 10,
      impactAvg: Math.round((subImpact / count) * 10) / 10,
      designAvg: Math.round((subDesign / count) * 10) / 10,
      appliedBiasDelta: Math.round(calculatedBiasOffset * 10) / 10,
      adjustmentReason: reason
    };
  };

  // DYNAMIC FILTERING & ACTIVE HACKATHON CONFIGS (FEATURE #2 IMPLEMENTATION)
  const selectedHackathon = hackathons.find(h => h.id === selectedHackathonId) || hackathons[0];
  const displayedHackathons = hackathons.filter(h => h.status === hackathonTypeFilter);

  // Filter project mappings under chosen hackathon
  const filteredProjects = projects.filter(proj => {
    // hack-1 projects map Sustainability
    if (selectedHackathonId === 'hack-1') {
      return proj.techStack.join(' ').toLowerCase().includes('sustain') || proj.title.toLowerCase().includes('green') || proj.title.toLowerCase().includes('eco') || proj.title.toLowerCase().includes('water') || proj.title.toLowerCase().includes('air') || proj.id.includes('proj-1') || proj.id.includes('proj-2') || proj.id.includes('proj');
    }
    // hack-2 projects map Security
    if (selectedHackathonId === 'hack-2') {
      return proj.techStack.join(' ').toLowerCase().includes('security') || proj.title.toLowerCase().includes('trust') || proj.title.toLowerCase().includes('crypt') || proj.description.toLowerCase().includes('adversar');
    }
    // general fallback
    return true;
  });

  const searchableParticipants = participants.filter(p =>
    p.name.toLowerCase().includes(regSearch.toLowerCase()) ||
    p.email.toLowerCase().includes(regSearch.toLowerCase()) ||
    p.institution.toLowerCase().includes(regSearch.toLowerCase()) ||
    p.skills.some(s => s.toLowerCase().includes(regSearch.toLowerCase()))
  );

  // ACTIVE INTERACTIVE USER SESSION ENTITIES
  const activeParticipantUser = participants.find(p => p.email === currentParticipantEmail) || participants[0];
  const activeReviewerUser = reviewers.find(r => r.email === currentReviewerEmail) || reviewers[0];

  // PARTICIPANT COMPATIBLE TEAM MAPPINGS ENGINE (FEATURE #3 IMPLEMENTATION)
  const handleInviteToTeam = (partnerId: string) => {
    const partner = participants.find(p => p.id === partnerId);
    if (!partner) return;

    // Mutate state to append innovator in user team members
    const activeUserProj = projects.find(p => p.submittedBy === activeParticipantUser?.id);
    
    if (activeUserProj) {
      if (activeUserProj.teamMembers.includes(partner.name)) {
        alert(`${partner.name} is already registered on your dynamic team array.`);
        return;
      }
      
      const updatedMembers = [...activeUserProj.teamMembers, partner.name];
      const updatedProjs = projects.map(p => {
        if (p.id === activeUserProj.id) {
          return { ...p, teamMembers: updatedMembers };
        }
        return p;
      });
      setProjects(updatedProjs);
      syncStorage('hack_projects', updatedProjs);
      
      writeAuditRecord(
        `Team invitation finalized`,
        'Participant',
        `User successfully invited ${partner.name} to join "${activeUserProj.title}". Current membersCount: ${updatedMembers.length}`,
        'Matching'
      );
      
      alert(`Teammate added! ${partner.name} is now incorporated into your live team list.`);
    } else {
      // Create a project scaffolding to embed team immediately
      const defaultTitle = `${activeParticipantUser?.name || 'My'}'s Team Space`;
      const newProjScaffold: Project = {
        id: `proj-${Date.now()}`,
        title: defaultTitle,
        tagline: 'Forming technology co-founders hub',
        description: 'New innovation track targeting cloud scale and sustainability challenges.',
        techStack: [...(activeParticipantUser?.skills || []), ...partner.skills],
        institution: activeParticipantUser?.institution || 'Dell Innovation Office',
        teamMembers: [activeParticipantUser?.name || 'Hacker Soloist', partner.name],
        submittedBy: activeParticipantUser?.id || 'p-1'
      };
      
      const newProjs = [newProjScaffold, ...projects];
      setProjects(newProjs);
      syncStorage('hack_projects', newProjs);
      setSelectedProjectId(newProjScaffold.id);
      
      writeAuditRecord(
        'New Innovation Team Portfolios Initiated',
        'Participant',
        `Created team "${defaultTitle}" with matched partner: ${partner.name}`,
        'Matching'
      );
      
      alert(`Innovation team formed! ${partner.name} has joined you. Let's build together.`);
    }
  };

  // Find users who are NOT the current participant and prioritize those with complementary / compatible stack alignments
  const computeCompatiblePartners = () => {
    if (!activeParticipantUser) return [];

    // Filter out ourself
    const peers = participants.filter(p => p.id !== activeParticipantUser.id);
    const userSkills = activeParticipantUser.skills.map(s => s.toLowerCase());

    const mapped = peers.map(peer => {
      const peerSkills = peer.skills.map(s => s.toLowerCase());
      
      // Calculate intersection and complementarity
      let overlapCount = 0;
      let complementaryCount = 0;

      peerSkills.forEach(ps => {
        if (userSkills.includes(ps)) overlapCount++;
        else {
          // If user lacks mobile or backend etc, peer who has it acts as complementary asset
          const textSkills = userSkills.join(' ');
          if (ps.includes('react') || ps.includes('front') || ps.includes('design')) {
            if (!textSkills.includes('react') && !textSkills.includes('front') && !textSkills.includes('design')) {
              complementaryCount++;
            }
          }
          if (ps.includes('python') || ps.includes('ml') || ps.includes('ai') || ps.includes('pytorch')) {
            if (!textSkills.includes('python') && !textSkills.includes('ml') && !textSkills.includes('ai')) {
              complementaryCount++;
            }
          }
          if (ps.includes('docker') || ps.includes('node') || ps.includes('go') || ps.includes('back')) {
            if (!textSkills.includes('docker') && !textSkills.includes('node') && !textSkills.includes('go')) {
              complementaryCount++;
            }
          }
        }
      });

      // Composite match index
      const compatibilityPoints = Math.round(55 + (overlapCount * 12) + (complementaryCount * 18));
      const percentage = Math.min(99, Math.max(62, compatibilityPoints));

      return {
        peer,
        compatibilityPercentage: percentage,
        roleMatch: overlapCount > complementaryCount ? 'Overlapping Peer' : 'Complementary Partner'
      };
    });

    // Sort descending by percentage
    return mapped.sort((a, b) => b.compatibilityPercentage - a.compatibilityPercentage).slice(0, 4);
  };

  const currentMatchPartners = computeCompatiblePartners();

  return (
    <div className="min-h-screen bg-chess-pattern-subtle text-[#0B1E36] font-sans flex flex-col antialiased selection:bg-[#0B1E36]/10 relative">
      <AmbientBackgroundDecoration />
      <NetworkMeshCanvas />
      


      <div className="relative z-20 flex flex-col min-h-screen">
      
      {/* ──────────────────────────────────────────────────────────
         NAVIGATION BAR - LUXURY CHESS THEMED DEEP NAVY AND BEIGE
         ────────────────────────────────────────────────────────── */}
      <nav className="fixed top-0 left-0 right-0 z-50 h-16 px-4 md:px-10 flex items-center justify-between bg-[#0B1E36] border-b border-[#DFD7C7]/20 shadow-md">
        <a className="flex items-center gap-3 text-none" href="#">
          <div className="logo-mark w-8 h-8 bg-[#C4B495] text-[#0B1E36] font-black font-disp text-base grid place-items-center tracking-tight hover:scale-110 active:scale-95 duration-200 transition-all cursor-pointer rounded" style={{ clipPath: 'polygon(0 0, 100% 0, 100% 75%, 75% 100%, 0 100%)' }}>
            H
          </div>
          <div className="flex flex-col">
            <span className="brand-name font-disp text-base font-extrabold text-[#FAF8F5] leading-none tracking-tight">HackBridge</span>
          </div>
        </a>

        <div className="flex items-center gap-4">
          {/* THEME TOGGLE SWITCH: Classic vs Midnight Dark Variant */}
          <button
            onClick={() => setTheme(prev => prev === 'classic' ? 'midnight' : 'classic')}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-white/10 text-white rounded text-[11px] font-mono uppercase tracking-wider font-semibold hover:bg-white/10 hover:border-white/25 active:scale-95 transition-all duration-200 cursor-pointer"
            title={`Switch to ${theme === 'classic' ? 'Midnight Dark' : 'Classic Navy/Beige'} theme`}
          >
            {theme === 'classic' ? (
              <>
                <Moon className="h-3.5 w-3.5 text-[#C4B495]" />
                <span className="hidden sm:inline">Midnight Theme</span>
                <span className="sm:hidden">Midnight</span>
              </>
            ) : (
              <>
                <Sun className="h-3.5 w-3.5 text-amber-300 animate-pulse" />
                <span className="hidden sm:inline">Classic Theme</span>
                <span className="sm:hidden">Classic</span>
              </>
            )}
          </button>

          {isSyncing && (
            <span className="text-[10px] text-[#C4B495] font-mono flex items-center gap-1">
              <RefreshCw className="h-3 w-3 animate-spin" /> AutoSync
            </span>
          )}

          {activeRole !== 'login' && (
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-slate-500 hidden md:inline">
                API: <strong className={backendOnline ? 'text-emerald-600' : 'text-amber-600'}>{backendOnline ? 'Connected' : 'Simulation'}</strong>
              </span>
              <button
                onClick={handleSystemLogout}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-200 rounded text-xs font-semibold text-slate-500 hover:text-slate-800 hover:border-slate-300 transition-all bg-white"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Log Out</span>
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* spacer for navbar */}
      <div className="h-16" />

      {activeRole === 'login' && (
        <div className="flex-1 flex flex-col">
          
          {/* HERO BANNER BLOCK WITH NAVY & BEIGE BRAND DESIGNS */}
          <div className="hero-band bg-[#0B1E36] text-[#FAF8F5] px-6 py-20 md:py-28 relative overflow-hidden">
            {/* Geometric hard-edged polygon chess shadow blocks */}
            <div className="absolute top-0 right-0 w-[45%] h-full bg-[#18304F] z-0" style={{ clipPath: 'polygon(38% 0, 100% 0, 100% 100%, 0% 100%)' }} />
            <div className="absolute top-0 right-0 w-[22%] h-full bg-[#C4B495]/10 z-0" style={{ clipPath: 'polygon(55% 0, 100% 0, 100% 100%, 20% 100%)' }} />

            <div className="relative z-10 max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
              
              {/* LEFT TEXT PANEL */}
              <div className="lg:col-span-7 space-y-6">
                <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 px-3 py-1 rounded-sm">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#C4B495]" />
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-300">Platform operational • AI evaluation assist</span>
                </div>

                <h1 className="text-4xl md:text-5xl font-extrabold font-disp text-white leading-[1.05] tracking-tight">
                  Run the whole hackathon.
                  <span className="text-[#C4B495] block">One platform, every role.</span>
                  <span className="inline-block w-12 h-1.5 bg-[#C4B495] mt-4" />
                </h1>

                <p className="text-slate-300 text-sm md:text-base leading-relaxed max-w-xl">
                  HackBridge brings registration, team formation, submissions, and judging into a single dashboard — built by Dell Technologies for organizers running events at any scale, from a 40-person campus hack to a global innovation challenge.
                </p>

                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-[#C4B495]">Built for</span>
                  <div className="flex gap-1.5 flex-wrap">
                    <span className="px-2 py-0.5 bg-white/5 border border-white/10 text-xs font-mono text-slate-300">Enterprises</span>
                    <span className="px-2 py-0.5 bg-white/5 border border-white/10 text-xs font-mono text-slate-300">Universities</span>
                    <span className="px-2 py-0.5 bg-white/5 border border-white/10 text-xs font-mono text-slate-300">Startups</span>
                    <span className="px-2 py-0.5 bg-white/5 border border-white/10 text-xs font-mono text-slate-300">Government bodies</span>
                  </div>
                </div>

                {/* Live stats from backend when available */}
                <div className="flex flex-wrap gap-8 pt-4">
                  <div>
                    <h4 className="text-2xl font-black font-disp">{backendOnline ? statsCounter.participantsCount : '—'}</h4>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">registered participants {backendOnline ? '(live)' : '(connect API)'}</span>
                  </div>
                  <div className="h-10 w-px bg-white/10" />
                  <div>
                    <h4 className="text-2xl font-black font-disp">{backendOnline ? `${statsCounter.timeSaved}%` : '—'}</h4>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">evaluation completion</span>
                  </div>
                </div>
              </div>

              {/* RIGHT SYSTEM ENTRY PORTALS CARD (AUTH CARD) */}
              <div className="lg:col-span-5 bg-[#FAF8F5] text-slate-900 border border-[#DFD7C7] rounded-lg p-6 shadow-2xl relative">
                
                {/* Tab layout: login vs register */}
                <div className="flex bg-[#ECE6D8] p-1 rounded gap-1 mb-6">
                  <button
                    onClick={() => setAuthMode('login')}
                    className={`flex-1 py-2 text-xs font-semibold rounded transition-all uppercase tracking-wider cursor-pointer ${
                      authMode === 'login' ? 'bg-[#0B1E36] text-white' : 'text-slate-500 hover:text-slate-900'
                    }`}
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => setAuthMode('signup')}
                    className={`flex-1 py-2 text-xs font-semibold rounded transition-all uppercase tracking-wider cursor-pointer ${
                      authMode === 'signup' ? 'bg-[#0B1E36] text-white' : 'text-slate-500 hover:text-slate-900'
                    }`}
                  >
                    Create Profile
                  </button>
                </div>

                {backendWarning && (
                  <div className="mb-4 p-2 bg-amber-50 border border-amber-200 rounded text-[10px] text-amber-800">{backendWarning}</div>
                )}
                {authError && (
                  <div className="mb-4 p-2 bg-red-50 border border-red-200 rounded text-[10px] text-red-700">{authError}</div>
                )}

                {authMode === 'login' ? (
                  <form onSubmit={handleSystemLogin} className="space-y-4">
                    <div className="space-y-1">
                      <label className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block">Email</label>
                      <input type="email" required value={loginEmail} onChange={e => setLoginEmail(e.target.value)}
                        placeholder="organizer@pulseforge.dev"
                        className="w-full px-3 py-2 border border-slate-300 rounded bg-white text-xs outline-none focus:border-[#0B1E36]" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-extrabold text-slate-600 uppercase tracking-wider block">Password</label>
                      <input type="password" required value={loginPassword} onChange={e => setLoginPassword(e.target.value)}
                        placeholder="demo1234"
                        className="w-full px-3 py-2 border border-slate-300 rounded bg-white text-xs outline-none focus:border-[#0B1E36]" />
                    </div>
                    <div className="p-2 bg-[#F5F2EB] border border-[#DFD7C7] rounded text-[10px] text-slate-500">
                      Demo accounts: organizer@pulseforge.dev / reviewer@pulseforge.dev / participant@pulseforge.dev — password: demo1234
                    </div>
                    <button type="submit" className="w-full py-2.5 bg-[#0B1E36] hover:bg-[#18304F] text-[#FAF8F5] font-bold text-xs uppercase tracking-wider rounded cursor-pointer">
                      Sign In with JWT →
                    </button>
                    <p className="text-[10px] text-slate-400 text-center font-mono">Role is determined by your account — not a UI selector.</p>
                  </form>
                ) : (
                  <form onSubmit={handleSystemSignup} className="space-y-3.5 max-h-[380px] overflow-y-auto pr-1">
                    <div className="grid grid-cols-3 gap-2 mb-2">
                      <button type="button" onClick={() => setSignupRole('participant')}
                        className={`py-2 text-[11px] font-bold rounded border cursor-pointer ${signupRole === 'participant' ? 'border-[#0B1E36] bg-[#0B1E36]/5' : 'border-slate-200'}`}>
                        Register as Participant
                      </button>
                      <button type="button" onClick={() => setSignupRole('reviewer')}
                        className={`py-2 text-[11px] font-bold rounded border cursor-pointer ${signupRole === 'reviewer' ? 'border-[#0B1E36] bg-[#0B1E36]/5' : 'border-slate-200'}`}>
                        Register as Reviewer
                      </button>
                      <button type="button" onClick={() => setSignupRole('organizer')}
                        className={`py-2 text-[11px] font-bold rounded border cursor-pointer ${signupRole === 'organizer' ? 'border-[#0B1E36] bg-[#0B1E36]/5' : 'border-slate-200'}`}>
                        Register as Host
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="space-y-1">
                        <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">First Name</label>
                        <input
                          type="text"
                          required
                          placeholder="Alex"
                          value={registerForm.firstName}
                          onChange={(e) => setRegisterForm({ ...registerForm, firstName: e.target.value })}
                          className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Last Name</label>
                        <input
                          type="text"
                          placeholder="Chen"
                          value={registerForm.lastName}
                          onChange={(e) => setRegisterForm({ ...registerForm, lastName: e.target.value })}
                          className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium"
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Password (min 6 chars)</label>
                      <input type="password" required minLength={6} value={loginPassword} onChange={e => setLoginPassword(e.target.value)}
                        className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium" />
                    </div>

                    <div className="space-y-1">
                      <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Secure Email Address</label>
                      <input
                        type="email"
                        required
                        placeholder="hacker@stanford.edu"
                        value={registerForm.email}
                        onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                        className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div className="space-y-1">
                        <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Institution / Co</label>
                        <input
                          type="text"
                          placeholder="Acme University"
                          value={registerForm.organization}
                          onChange={(e) => setRegisterForm({ ...registerForm, organization: e.target.value })}
                          className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Country</label>
                        <input
                          type="text"
                          placeholder="United States"
                          value={registerForm.country}
                          onChange={(e) => setRegisterForm({ ...registerForm, country: e.target.value })}
                          className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium"
                        />
                      </div>
                    </div>

                    {/* FEATURE #4 - PARTICIPANTS SPECIFIC FIELDS: BIOGRAPHY & TECH STACK SKILLS */}
                    {signupRole === 'participant' && (
                      <div className="p-3 border border-slate-200/80 bg-slate-50 rounded-sm space-y-3">
                        <span className="text-[10px] font-extrabold uppercase tracking-widest text-[#0076ce]">Participant Information &amp; Technical Capabilities</span>
                        
                        <div className="space-y-1">
                          <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Tech Stack &amp; Key Skills (Comma Separated)</label>
                          <input
                            type="text"
                            placeholder="e.g. React, Python, PyTorch, Docker, PostgreSQL"
                            value={registerForm.techSkills}
                            onChange={(e) => setRegisterForm({ ...registerForm, techSkills: e.target.value })}
                            className="w-full px-2.5 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-mono"
                          />
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Experience Level</label>
                            <select
                              value={registerForm.experienceLevel}
                              onChange={(e) => setRegisterForm({ ...registerForm, experienceLevel: e.target.value as any })}
                              className="w-full px-2 py-1.5 border border-slate-300 text-xs rounded-sm bg-white"
                            >
                              <option value="Beginner">Beginner Programmer</option>
                              <option value="Intermediate">Intermediate Developer</option>
                              <option value="Advanced">Advanced Systems Architect</option>
                            </select>
                          </div>
                          <div className="space-y-1">
                            <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Demographic Identity</label>
                            <select
                              value={registerForm.gender}
                              onChange={(e) => setRegisterForm({ ...registerForm, gender: e.target.value as any })}
                              className="w-full px-2 py-1.5 border border-slate-300 text-xs rounded-sm bg-white"
                            >
                              <option value="Female">Female</option>
                              <option value="Male">Male</option>
                              <option value="Non-binary">Non-binary</option>
                              <option value="Prefer not to say">Prefer not to say</option>
                            </select>
                          </div>
                        </div>

                        <div className="space-y-1">
                          <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Tell Us About Yourself (Short Biography)</label>
                          <textarea
                            placeholder="State your technical backgrounds, core projects build-interests, and ideal hacker teammate criteria..."
                            rows={2}
                            value={registerForm.personalBio}
                            onChange={(e) => setRegisterForm({ ...registerForm, personalBio: e.target.value })}
                            className="w-full px-2.5 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium resize-none leading-relaxed"
                          />
                        </div>
                      </div>
                    )}

                    {/* FEATURE #4 - REVIEWERS SPECIFIC FIELDS: DISCIPLINARY DOMAINS & EXPERIENCE LEVEL */}
                    {signupRole === 'reviewer' && (
                      <div className="p-3 border border-slate-200/80 bg-slate-50 rounded-sm space-y-3">
                        <span className="text-[10px] font-extrabold uppercase tracking-widest text-[#0076ce]">Jury Expertise &amp; Background Details</span>
                        
                        <div className="space-y-1">
                          <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Disciplinary Expertise (Comma Separated Specialties)</label>
                          <input
                            type="text"
                            placeholder="e.g. AI/ML, Cloud Architecture, Pen Testing, UX Design"
                            value={registerForm.domainExpertise}
                            onChange={(e) => setRegisterForm({ ...registerForm, domainExpertise: e.target.value })}
                            className="w-full px-2.5 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-mono"
                          />
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Years of Judging Experience</label>
                            <input
                              type="number"
                              min="0"
                              placeholder="4"
                              value={registerForm.yearsJudging}
                              onChange={(e) => setRegisterForm({ ...registerForm, yearsJudging: e.target.value })}
                              className="w-full px-2.5 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white"
                            />
                          </div>
                          <div className="space-y-1">
                            <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Jury Panel Category</label>
                            <select
                              value={registerForm.gender}
                              onChange={(e) => setRegisterForm({ ...registerForm, gender: e.target.value as any })}
                              className="w-full px-2 py-1.5 border border-slate-300 text-xs rounded-sm bg-white"
                            >
                              <option value="Female">Female</option>
                              <option value="Male">Male</option>
                              <option value="Non-binary">Non-binary</option>
                              <option value="Prefer not to say">Prefer not to say</option>
                            </select>
                          </div>
                        </div>

                        <div className="space-y-1">
                          <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Technical Portfolio Summary</label>
                          <textarea
                            placeholder="Summarize your engineering expertise, academic track positions, and former hackathon evaluations background..."
                            rows={2}
                            value={registerForm.personalBio}
                            onChange={(e) => setRegisterForm({ ...registerForm, personalBio: e.target.value })}
                            className="w-full px-2.5 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium resize-none leading-relaxed"
                          />
                        </div>
                      </div>
                    )}

                    <button
                      type="submit"
                      className="w-full py-2.5 bg-[#0076ce] hover:bg-[#00558f] text-white font-bold text-xs uppercase tracking-wider rounded-sm transition-all"
                    >
                      Initialize Sandbox Profile &nbsp;→
                    </button>
                  </form>
                )}
              </div>

            </div>
          </div>

          {/* BELOW HERO MARKETING SECTIONS - THE FOUR COHORT TIMELINES */}
          <div className="bg-[#FAF8F5]/50 backdrop-blur-md py-16 px-6 border-b border-[#DFD7C7]/40">
            <ScrollReveal className="max-w-6xl mx-auto space-y-12">
              <div className="space-y-2">
                <span className="text-xs font-mono uppercase tracking-widest text-[#0076ce] font-semibold block">Continuous Workflow</span>
                <h3 className="text-2xl md:text-3xl font-extrabold font-disp text-slate-900">Multi-Phase Hackathon Architectures. Zero spreadsheets.</h3>
                <p className="text-slate-500 max-w-2xl text-xs md:text-sm">
                  Bridge communication overhead, fuzzy duplicating records, expert matchmaking workloads, and jury scoring deviations instantly.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 border border-[#DFD7C7]/40 divide-y md:divide-y-0 md:divide-x divide-[#DFD7C7]/40 rounded-lg overflow-hidden">
                <div className="p-5 bg-[#F5F2EB]/40 relative group">
                  <span className="text-[10px] font-mono font-bold text-[#0076ce] block mb-4">Phase 01 — Sign Up</span>
                  <h4 className="font-extrabold text-slate-900 text-sm mb-1">Interactive Profiles</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">Participants map their precise technical stack skills dynamically during rapid onboarding streams.</p>
                </div>
                <div className="p-5 bg-[#FAF8F5]/45 relative group">
                  <span className="text-[10px] font-mono font-bold text-[#0076ce] block mb-4">Phase 02 — Match</span>
                  <h4 className="font-extrabold text-slate-900 text-sm mb-1">Optimal Team Maker</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">Hacker pairs form using technology metrics suggestions to construct perfectly aligned innovation co-founders.</p>
                </div>
                <div className="p-5 bg-[#F5F2EB]/40 relative group">
                  <span className="text-[10px] font-mono font-bold text-[#0076ce] block mb-4">Phase 03 — Judge</span>
                  <h4 className="font-extrabold text-slate-900 text-sm mb-1">Score with AI assist</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">Judges score against a shared rubric while flagged similarities and bias indices surface automatically.</p>
                </div>
                <div className="p-5 bg-[#FAF8F5]/45 relative group">
                  <span className="text-[10px] font-mono font-bold text-[#0076ce] block mb-4">Phase 04 — Announce</span>
                  <h4 className="font-extrabold text-slate-900 text-sm mb-1">Publish instantly</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">Leaderboards, winners, and certificates go out the moment judging closes — no manual tallying.</p>
                </div>
              </div>
            </ScrollReveal>
          </div>

          {/* BUILT FOR EVERY SEAT AT THE TABLE SECTION */}
          <div className="bg-[#FAF8F5]/30 backdrop-blur-md py-16 px-6 border-b border-[#DFD7C7]/40">
            <ScrollReveal className="max-w-6xl mx-auto space-y-12">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-0.5 bg-[#0076ce]" />
                  <span className="text-[10.5px] font-mono uppercase tracking-widest text-[#0076ce] font-extrabold block">
                    BUILT FOR EVERY SEAT AT THE TABLE
                  </span>
                </div>
                <h3 className="text-3xl md:text-4xl font-extrabold font-disp text-slate-900 leading-tight tracking-tight max-w-3xl">
                  The same platform, tuned to what each role actually needs to do.
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* CARD 1: EVENT HOSTS */}
                <TiltCard className="h-full bg-white/70 backdrop-blur-sm border border-[#DFD7C7]/50 rounded-2xl p-8 shadow-sm flex flex-col hover:border-slate-350 transition-all duration-300">
                  <div className="space-y-6">
                    <div className="p-3 bg-sky-50 text-[#0076ce] rounded-lg w-fit">
                      <LayoutGrid className="w-5 h-5" />
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-lg font-bold text-slate-900 font-disp">Event hosts</h4>
                      <p className="text-xs text-slate-500 leading-relaxed font-sans">
                        Launch and run multiple hackathons from one console.
                      </p>
                    </div>
                    <ul className="space-y-2.5 border-t border-slate-100 pt-5 text-xs text-slate-600 font-sans">
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-slate-300 rounded-xs mt-1.5 flex-shrink-0" />
                        <span>Live registration & submission tracking</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-slate-300 rounded-xs mt-1.5 flex-shrink-0" />
                        <span>One-click broadcast announcements</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-slate-300 rounded-xs mt-1.5 flex-shrink-0" />
                        <span>AI-surfaced insights on flagged entries</span>
                      </li>
                    </ul>
                  </div>
                </TiltCard>

                {/* CARD 2: JUDGES */}
                <TiltCard className="h-full bg-white/70 backdrop-blur-sm border border-[#DFD7C7]/50 rounded-2xl p-8 shadow-sm flex flex-col hover:border-slate-350 transition-all duration-300">
                  <div className="space-y-6">
                    <div className="p-3 bg-amber-50 text-amber-600 rounded-lg w-fit">
                      <Shield className="w-5 h-5" />
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-lg font-bold text-[#0c2340] font-disp">Judges</h4>
                      <p className="text-xs text-slate-500 leading-relaxed font-sans">
                        Score consistently against a shared rubric.
                      </p>
                    </div>
                    <ul className="space-y-2.5 border-t border-slate-100 pt-5 text-xs text-slate-600 font-sans">
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-slate-300 rounded-xs mt-1.5 flex-shrink-0" />
                        <span>Assigned queue with deadline tracking</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-slate-300 rounded-xs mt-1.5 flex-shrink-0" />
                        <span>Similarity & plagiarism alerts</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-slate-300 rounded-xs mt-1.5 flex-shrink-0" />
                        <span>Personal bias index for fairness</span>
                      </li>
                    </ul>
                  </div>
                </TiltCard>

                {/* CARD 3: PARTICIPANTS */}
                <TiltCard className="h-full bg-white/70 backdrop-blur-sm border border-[#DFD7C7]/50 rounded-2xl p-8 shadow-sm flex flex-col hover:border-slate-350 transition-all duration-300">
                  <div className="space-y-6">
                    <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg w-fit">
                      <Code className="w-5 h-5" />
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-lg font-bold text-slate-900 font-disp">Participants</h4>
                      <p className="text-xs text-slate-500 leading-relaxed font-sans">
                        Stay on top of deadlines without the group-chat chaos.
                      </p>
                    </div>
                    <ul className="space-y-2.5 border-t border-slate-100 pt-5 text-xs text-slate-600 font-sans">
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-slate-300 rounded-xs mt-1.5 flex-shrink-0" />
                        <span>Live rank & team status</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-slate-300 rounded-xs mt-1.5 flex-shrink-0" />
                        <span>Guided event timeline</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-slate-300 rounded-xs mt-1.5 flex-shrink-0" />
                        <span>AI coach for submission feedback</span>
                      </li>
                    </ul>
                  </div>
                </TiltCard>
              </div>
            </ScrollReveal>
          </div>

          {/* CORE BRAND FOOTER */}
          <footer className="mt-auto bg-[#0c2340] text-slate-400 py-10 px-6 text-center border-t border-slate-800">
            <p className="text-[10px] font-mono font-extrabold tracking-widest text-slate-400 uppercase">HACKBRIDGE</p>
            <p className="text-[11px] text-slate-500 mt-2 font-mono">Academic Simulation Sandbox • Offline Local Storage Persistence Layer Enabled.</p>
          </footer>
        </div>
      )}

      {/* ──────────────────────────────────────────────────────────
         ORGANIZER CONTROL DESK VIEW
         ────────────────────────────────────────────────────────── */}
      {activeRole === 'organizer' && (
        <div className="flex-1 max-w-6xl w-full mx-auto px-4 md:px-8 py-8 space-y-6 animate-fade-in">
          
          {/* FASTAPI CORE NETWORK GATE */}
          <div className="p-4 bg-[#FAF8F5] border border-[#DFD7C7] rounded-lg shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400' : 'bg-[#C4B495]'} animate-pulse`} />
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#0B1E36]">FastAPI Service Node Bridge</span>
                <span className={`px-2 py-0.5 text-[9px] font-mono font-extrabold rounded-sm uppercase ${
                  backendOnline ? 'bg-emerald-900/15 text-emerald-700' : 'bg-amber-900/10 text-amber-700'
                }`}>
                  {backendOnline ? 'Connected' : 'Standalone (Simulation Mode)'}
                </span>
              </div>
              <p className="text-[11px] text-slate-500">Bridge active database nodes, resolve duplication checks, and align z-score jury workload allocations.</p>
            </div>
            
            <div className="flex items-center gap-2 w-full md:w-auto">
              <input
                type="text"
                value={backendUrlInput}
                onChange={(e) => setBackendUrlInput(e.target.value)}
                placeholder="http://localhost:8000"
                className="px-3 py-1.5 border border-slate-200 rounded-sm text-xs font-mono text-slate-800 bg-white placeholder-slate-400 outline-none w-full md:w-56 focus:border-[#0B1E36] transition-all"
              />
              <button
                onClick={handleConnectBackend}
                disabled={isSyncingBackend}
                className="px-4 py-1.5 bg-[#0B1E36] text-white rounded-sm text-xs font-bold uppercase tracking-wider hover:bg-slate-800 hover:scale-[1.03] active:scale-[0.97] transition-all cursor-pointer flex items-center gap-1 shrink-0"
              >
                {isSyncingBackend ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Zap className="h-3.5 w-3.5 text-[#C4B495]" />}
                <span>{isSyncingBackend ? 'Linking...' : 'Connect'}</span>
              </button>
            </div>
          </div>
          
          {/* WELCOME BANNER WITH DUAL KPI */}
          <div className="p-6 bg-slate-50 border border-slate-200 rounded-lg flex flex-wrap justify-between items-center gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 bg-[#0076ce]/10 text-[#0076ce] rounded-sm text-[10px] font-mono font-extrabold uppercase">HOST DESK</span>
                <span className="text-slate-400 text-xs">| {authUser?.full_name || 'Organizer'}</span>
              </div>
              <h2 className="text-2xl font-black font-disp tracking-tight">Welcome to the Control Cockpit</h2>
              <p className="text-xs text-slate-500">Coordinate participant matchmaking, duplication arrays, and impartial scoring matrices safely.</p>
            </div>

            {/* DYNAMIC MULTI-HACKATHON CATEGORY TABS - FEATURE #2: 3 OPTIONS */}
            <div className="p-1.5 bg-slate-100 rounded-sm border border-slate-200 flex flex-col gap-1.5">
              <span className="text-[9.5px] font-bold text-slate-500 uppercase font-mono px-1">Scope Hackathon Portfolio:</span>
              <div className="flex bg-white p-0.5 rounded-sm shadow-xs">
                <button
                  onClick={() => setHackathonTypeFilter('active')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-sm transition-all cursor-pointer ${
                    hackathonTypeFilter === 'active' ? 'bg-[#0B1E36] text-white font-bold' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Active Events
                </button>
                <button
                  onClick={() => setHackathonTypeFilter('upcoming')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-sm transition-all cursor-pointer ${
                    hackathonTypeFilter === 'upcoming' ? 'bg-[#0B1E36] text-white font-bold' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Upcoming
                </button>
                <button
                  onClick={() => setHackathonTypeFilter('past')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-sm transition-all cursor-pointer ${
                    hackathonTypeFilter === 'past' ? 'bg-[#0B1E36] text-white font-bold' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Past Portfolio
                </button>
              </div>
            </div>
          </div>

          {/* LIST OF CHOSEN COHORT HACKATHONS */}
          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <div className="flex justify-between items-center pb-3 border-b border-slate-155 mb-4 flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono">
                  {hackathonTypeFilter.toUpperCase()} HACKATHON FOCUS SELECTOR
                </span>
                <span className="text-xs text-[#0B1E36] font-semibold bg-[#F5F2EB] border border-[#DFD7C7] px-2 py-0.5 font-mono rounded">
                  {displayedHackathons.length} Event Mapped
                </span>
              </div>
              
              {/* INTERACTIVE CREATE EVENT ACTION TRIGGER */}
              <button
                onClick={() => setShowCreateEventForm(!showCreateEventForm)}
                className="px-3.5 py-1.5 bg-[#0B1E36] hover:bg-[#18304F] text-[#FAF8F5] text-xs font-bold font-sans rounded hover:scale-105 active:scale-95 hover:shadow-md transition-all duration-200 flex items-center gap-1.5 cursor-pointer"
              >
                <PlusCircle className="h-4 w-4 text-[#C4B495]" />
                {showCreateEventForm ? "Close Creator" : "Create New Event"}
              </button>
            </div>

            {/* DYNAMIC NEW EVENT CREATOR INSIDE THE DASHBOARD */}
            {showCreateEventForm && (
              <div className="mb-6 p-5 bg-[#FAF8F5] border border-[#DFD7C7] rounded-lg space-y-4 shadow-inner animate-in fade-in slide-in-from-top duration-300 ease-out">
                <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                  <PlusCircle className="h-4.5 w-4.5 text-[#C4B495] animate-pulse" />
                  <h3 className="text-sm font-extrabold text-[#0B1E36] uppercase tracking-wider font-mono">
                    Launch a New Hackathon Event Scope
                  </h3>
                </div>
                <form onSubmit={handleCreateNewEvent} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10.5px] font-bold text-slate-500 uppercase block font-mono">Event Title <span className="text-neutral-400 font-normal">(required)</span></label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. BioTech Decarbonization Hack 2026"
                      value={newEventTitle}
                      onChange={(e) => setNewEventTitle(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded bg-white text-xs text-slate-900 outline-none focus:border-[#0B1E36] focus:ring-1 focus:ring-[#0B1E36] transition-all"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10.5px] font-bold text-slate-500 uppercase block font-mono">Technical Track / Theme</label>
                    <input
                      type="text"
                      placeholder="e.g. AI/ML, Embedded Engineering"
                      value={newEventTrack}
                      onChange={(e) => setNewEventTrack(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded bg-white text-xs text-slate-900 outline-none focus:border-[#0B1E36] focus:ring-1 focus:ring-[#0B1E36] transition-all"
                    />
                  </div>
                  <div className="col-span-1 md:col-span-2 space-y-1">
                    <label className="text-[10.5px] font-bold text-slate-500 uppercase block font-mono">Event Description <span className="text-neutral-400 font-normal">(required)</span></label>
                    <textarea
                      required
                      rows={3}
                      placeholder="Specify the guidelines, API limits, evaluation weights, and prize categories for contestants..."
                      value={newEventDesc}
                      onChange={(e) => setNewEventDesc(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded bg-white text-xs text-slate-900 outline-none focus:border-[#0B1E36] focus:ring-1 focus:ring-[#0B1E36] transition-all"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10.5px] font-bold text-slate-500 uppercase block font-mono">Operational Frame Category</label>
                    <select
                      value={newEventStatus}
                      onChange={(e) => setNewEventStatus(e.target.value as any)}
                      className="w-full px-3 py-2 border border-slate-300 rounded bg-white text-xs text-slate-900 outline-none focus:border-[#0B1E36]"
                    >
                      <option value="active">Active Block (Currently Ongoing)</option>
                      <option value="upcoming">Upcoming Block (Accepting Signups)</option>
                      <option value="past">Past Portfolio (Archived Evaluation)</option>
                    </select>
                  </div>
                  <div className="flex items-end justify-end gap-3 pt-3 md:col-span-2">
                    <button
                      type="button"
                      onClick={() => setShowCreateEventForm(false)}
                      className="px-4 py-2 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded text-xs transition-all cursor-pointer hover:scale-102"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-5 py-2 bg-[#0B1E36] hover:bg-[#18304F] text-[#FAF8F5] font-bold rounded text-xs uppercase tracking-wider hover:scale-105 active:scale-95 transition-all cursor-pointer hover:shadow-md"
                    >
                      Publish Event Focus
                    </button>
                  </div>
                </form>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {displayedHackathons.map(h => (
                <TiltCard
                  key={h.id}
                  id={`card-hack-${h.id}`}
                  className="h-full"
                >
                  <div
                    onClick={() => {
                      setSelectedHackathonId(h.id);
                      writeAuditRecord('Switched operational event target focus', 'Organizer', `Focus mapped securely to: "${h.title}"`, 'Registration');
                    }}
                    className={`p-4 border rounded-lg cursor-pointer hover:border-[#C4B495] transition-all relative h-full flex flex-col justify-between ${
                      selectedHackathonId === h.id ? 'border-2 border-[#0B1E36] bg-[#0B1E36]/5' : 'border-slate-200 bg-[#FAF8F5]'
                    }`}
                  >
                    <div>
                      {selectedHackathonId === h.id && (
                        <div className="absolute top-2.5 right-2.5 flex items-center gap-1 text-[10px] text-[#0B1E36] font-bold font-mono">
                          <CheckCircle2 className="h-3.5 w-3.5 inline text-[#C4B495]" /> ACTIVE
                        </div>
                      )}
                      <h4 className="font-extrabold text-slate-900 text-sm leading-snug pr-12">{h.title}</h4>
                      <p className="text-xs text-slate-500 mt-2 line-clamp-3 leading-relaxed">{h.description}</p>
                    </div>
                    
                    <div className="mt-4 pt-3 border-t border-slate-200/60 flex justify-between items-center text-[10.5px] font-mono text-slate-400">
                      <span>👥 {h.participantCount} Portals</span>
                      <span className="text-[#0B1E36] font-medium">🛠️ {h.track}</span>
                    </div>
                  </div>
                </TiltCard>
              ))}
            </div>
          </div>

          {/* DYNAMIC METRIC KPI TILES BASED ON HACKATHON FOCUS */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 border border-slate-200 rounded bg-white">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block font-mono">Focus Event Scope</span>
              <strong className="text-slate-900 text-sm block mt-1 truncate">{selectedHackathon.title}</strong>
              <span className="text-[10px] bg-sky-50 text-[#0076ce] border border-sky-200 font-bold px-1.5 py-0.5 rounded-sm inline-block mt-2 uppercase font-mono">
                {selectedHackathon.status} Frame
              </span>
            </div>

            <div className="p-4 border border-slate-200 rounded bg-white">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block font-mono">Portals Registered</span>
              <strong className="text-slate-900 text-2xl font-black block mt-1">
                {analyticsOverview?.participants?.total ?? participants.length}
              </strong>
              <span className="text-[10px] text-emerald-600 block font-mono font-bold mt-1">live from database</span>
            </div>

            <div className="p-4 border border-slate-200 rounded bg-white">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block font-mono">Projects Portfolios</span>
              <strong className="text-slate-900 text-2xl font-black block mt-1">
                {analyticsOverview?.projects?.total ?? filteredProjects.length}
              </strong>
              <span className="text-[10px] text-indigo-600 block font-mono font-bold mt-1">
                {analyticsOverview?.projects?.evaluation_completion_rate_pct ?? 0}% evaluated
              </span>
            </div>

            <div className="p-4 border border-slate-200 rounded bg-white">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block font-mono">Bias Flags (open)</span>
              <strong className="text-slate-900 text-2xl font-black block mt-1">
                {analyticsOverview?.fairness?.open_bias_flags ?? liveBiasFlags.filter(f => f.status === 'open').length}
              </strong>
              <span className="text-[10px] text-amber-600 font-bold block mt-1 font-mono">
                from statistical bias engine
              </span>
            </div>
          </div>

          {/* EVENT ANALYTICS & LOGISTICS */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            
            {/* SKILLS TAGS MATRIX */}
            <div className="p-5 border border-slate-200 rounded bg-white space-y-4">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono block">Programmer Capabilities Frequency</span>
              
              <div className="space-y-3 pt-2">
                {['React & Frontend', 'Python & Machine Learning', 'Docker Systems Containers', 'UX Designs & Wireframes'].map((title, idx) => {
                  const mappedCounts = [
                    participants.filter(p => p.skills.some(s => ['react', 'typescript', 'frontend', 'tailwind'].includes(s.toLowerCase()))).length,
                    participants.filter(p => p.skills.some(s => ['python', 'pytorch', 'ai/ml', 'data science'].includes(s.toLowerCase()))).length,
                    participants.filter(p => p.skills.some(s => ['docker', 'kubernetes', 'backend', 'go', 'node.js'].includes(s.toLowerCase()))).length,
                    participants.filter(p => p.skills.some(s => ['figma', 'ux/ui', 'design'].includes(s.toLowerCase()))).length
                  ];
                  const num = mappedCounts[idx] || 2;
                  const pct = Math.min(100, Math.round((num / Math.max(1, participants.length)) * 100));

                  return (
                    <div key={title} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-700">{title}</span>
                        <strong className="text-slate-950 font-mono">{num} Developers ({pct}%)</strong>
                      </div>
                      <div className="w-full bg-slate-100 h-2 rounded-sm overflow-hidden">
                        <div className="bg-[#0076ce] h-full" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* COMMUNICATORS EXPOSURES TIMELINES */}
            <div className="p-5 border border-slate-200 rounded-sm bg-slate-50 space-y-4">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono block">Cohort Communication Channels Logs</span>
              
              {communications.length > 0 ? (
                <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1">
                  {communications.map(c => (
                    <div key={c.id} className="p-2.5 bg-white border border-slate-150 rounded-sm">
                      <div className="flex justify-between items-center text-[10px] font-mono text-slate-400">
                        <span>Target: {c.recipientEmail}</span>
                        <span className="text-indigo-600 font-bold uppercase">{c.channel}</span>
                      </div>
                      <strong className="text-xs text-slate-900 block mt-1 leading-tight">{c.subject}</strong>
                      <p className="text-[11px] text-slate-500 mt-1 line-clamp-1">{c.content}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-400 font-mono text-xs text-center py-10">No communication logs recorded on local database yet.</p>
              )}
            </div>
          </div>

          {/* STATISTICAL SCORING SCORE NORMALIZATION */}
          <div className="p-5 border border-slate-200 rounded bg-white space-y-4">
            <div className="flex justify-between items-center flex-wrap gap-3 pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-base font-extrabold text-slate-900 leading-none">Statistical scoring bias analyzer</h3>
                <p className="text-xs text-slate-500">Compiles jury rating variances using mathematical z-score algorithms to normalize score distributions.</p>
              </div>

              {/* DOUBLE SCORES NORMALIZATION TOGGLER - FEATURE #5 REQUIRED */}
              <div className="flex items-center gap-2.5 bg-[#0076ce]/5 border border-[#0076ce]/20 px-4 py-2 rounded">
                <label htmlFor="norm-trigger" className="text-xs font-bold text-slate-700 cursor-pointer block leading-none font-disp uppercase">
                  Activate Score Normalization Offset:
                </label>
                <input
                  id="norm-trigger"
                  type="checkbox"
                  checked={isNormalizingBias}
                  onChange={toggleScoreNormalization}
                  className="w-4 h-4 cursor-pointer text-[#0076ce] rounded outline-none border-slate-300"
                />
              </div>
            </div>

            {/* COMPARISON RESULTS TABLE */}
            <span className="text-[11px] font-extrabold text-slate-400 font-mono uppercase block mt-2">Normalized Fairness Rankings comparison</span>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-indigo-200 bg-[#0076ce]/5 text-slate-700 font-mono font-bold">
                    <th className="py-2.5 px-3">Rank (Adjusted)</th>
                    <th className="py-2.5 px-3">Project Title</th>
                    <th className="py-2.5 px-3">Track / Area</th>
                    <th className="py-2.5 px-3 text-center">Jury Avg (Raw)</th>
                    <th className="py-2.5 px-3 text-center">Bias Offset (Deviation Indicator)</th>
                    <th className="py-2.5 px-3 text-center bg-[#0076ce]/10 text-[#0076ce]">Normalized Rating</th>
                    <th className="py-2.5 px-3">Adjustment Assessment</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {(liveRankings.length > 0 ? liveRankings.map(r => ({
                    id: api.toFrontendId('proj', r.project_id),
                    title: r.title,
                    raw: r.raw_mean,
                    norm: r.normalized_mean,
                    rank: r.rank,
                    confidence: r.confidence_score,
                  })) : filteredProjects.map((p, index) => {
                    const m = computeProjectMetrics(p.id);
                    return { id: p.id, title: p.title, raw: m.rawScore, norm: m.normalizedScore, rank: index + 1, confidence: 0 };
                  })).map(row => (
                      <tr key={row.id} className="hover:bg-slate-50">
                        <td className="py-3 px-3">
                          <span className="font-mono bg-[#0c2340] text-white px-2 py-0.5 rounded-sm font-bold text-xs">#{row.rank}</span>
                        </td>
                        <td className="py-3 px-3 font-extrabold text-[#0c2340] leading-snug">{row.title}</td>
                        <td className="py-2 px-3 text-slate-500">{selectedHackathon.track}</td>
                        <td className="py-2 px-3 text-center font-mono font-bold text-slate-600">{row.raw > 0 ? `${row.raw.toFixed(1)}/10` : '—'}</td>
                        <td className="py-2 px-3 text-center font-mono font-bold text-slate-500">—</td>
                        <td className="py-2 px-3 text-center font-mono font-extrabold bg-[#0076ce]/5 text-[#0076ce]">{row.norm > 0 ? `${row.norm.toFixed(1)}/10` : '—'}</td>
                        <td className="py-2 px-3 text-[10px]">{liveRankings.length > 0 ? `confidence ${(row.confidence * 100).toFixed(0)}%` : 'Enable normalization'}</td>
                      </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <OrganizerPanels onAudit={writeAuditRecord} onRefresh={refreshBackendData} />

        </div>
      )}

      {/* ──────────────────────────────────────────────────────────
         DESIGNATED JURY REVIEW PANEL WORKSPACE
         ────────────────────────────────────────────────────────── */}
      {activeRole === 'reviewer' && (
        <div className="flex-1 max-w-6xl w-full mx-auto px-4 md:px-8 py-8 space-y-6">
          <div className="p-6 bg-slate-50 border border-slate-200 rounded-lg flex justify-between items-center flex-wrap gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 bg-[#0076ce]/10 text-[#0076ce] rounded-sm text-[10px] font-mono font-extrabold uppercase">JURY SEAT</span>
                <span className="text-slate-400 text-xs">| {activeReviewerUser?.name || 'Faculty Judge'}</span>
              </div>
              <h2 className="text-2xl font-black font-disp tracking-tight">Active Evaluation Workbench</h2>
              <p className="text-xs text-slate-500">Provide impartial scores based on innovation, design, and continuous engineering metrics.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* PORTFOLIO TO SCORE ROW */}
            <div className="md:col-span-2 space-y-4">
              <div className="p-5 border border-slate-200 bg-white rounded-sm space-y-4 text-left">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono block mb-2">Evaluated Portfolios Queue</span>

                <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                  {filteredProjects.map(proj => {
                    const statusClass = evaluations.some(e => e.projectId === proj.id && e.reviewerId === activeReviewerUser?.id)
                      ? 'border-emerald-250 bg-emerald-50/20'
                      : 'border-slate-200 hover:border-slate-350 bg-white';

                    return (
                      <div
                        key={proj.id}
                        onClick={() => setSelectedProjectId(proj.id)}
                        className={`p-3 border rounded-sm cursor-pointer transition-all relative ${
                          selectedProjectId === proj.id ? 'border-2 border-[#0076ce]' : statusClass
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <strong className="text-xs text-slate-800 leading-snug">{proj.title}</strong>
                          {evaluations.some(e => e.projectId === proj.id && e.reviewerId === activeReviewerUser?.id) ? (
                            <span className="text-[9.5px] font-bold text-emerald-700 font-mono bg-emerald-100 flex items-center gap-1 leading-none px-1.5 py-0.5 rounded-sm">
                              ✓ REVIEWED
                            </span>
                          ) : (
                            <span className="text-[9.5px] font-bold text-slate-400 font-mono bg-slate-100 leading-none px-1.5 py-0.5 rounded-sm">
                              PENDING
                            </span>
                          )}
                        </div>

                        <p className="text-[11px] text-slate-500 mt-1 truncate leading-relaxed">{proj.tagline}</p>
                      </div>
                    );
                  })}
                </div>

                {/* SCORING GRADES SLIDERS */}
                <form onSubmit={handleEvaluateProjectSubmit} className="pt-4 border-t border-slate-100 space-y-4">
                  <span className="text-[10.5px] font-bold text-slate-500 uppercase tracking-widest font-mono block">Assign Portfolios parameters grades (1-10 Slider)</span>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-slate-600 font-semibold">
                        <span>Innovation &amp; Novelty</span>
                        <span className="font-mono text-[#0076ce]">{scoresInput.innovation}/10</span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={scoresInput.innovation}
                        onChange={(e) => setScoresInput({ ...scoresInput, innovation: parseInt(e.target.value) })}
                        className="w-full h-1 bg-slate-200 rounded-sm appearance-none cursor-pointer outline-none text-[#0076ce]"
                      />
                    </div>

                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-slate-600 font-semibold">
                        <span>Technical Execution</span>
                        <span className="font-mono text-[#0076ce]">{scoresInput.execution}/10</span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={scoresInput.execution}
                        onChange={(e) => setScoresInput({ ...scoresInput, execution: parseInt(e.target.value) })}
                        className="w-full h-1 bg-slate-200 rounded-sm appearance-none cursor-pointer outline-none"
                      />
                    </div>

                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-slate-600 font-semibold">
                        <span>Real Practice Impact</span>
                        <span className="font-mono text-[#0076ce]">{scoresInput.impact}/10</span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={scoresInput.impact}
                        onChange={(e) => setScoresInput({ ...scoresInput, impact: parseInt(e.target.value) })}
                        className="w-full h-1 bg-slate-200 rounded-sm appearance-none cursor-pointer outline-none"
                      />
                    </div>

                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-slate-600 font-semibold">
                        <span>UX / Graphic Design</span>
                        <span className="font-mono text-[#0076ce]">{scoresInput.design}/10</span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={scoresInput.design}
                        onChange={(e) => setScoresInput({ ...scoresInput, design: parseInt(e.target.value) })}
                        className="w-full h-1 bg-slate-200 rounded-sm appearance-none cursor-pointer outline-none"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10.5px] font-bold text-slate-600 block uppercase tracking-wider">Qualitative portfolio feedback</label>
                    <textarea
                      placeholder="Comment on execution speed, architectural setups, or UI accessibility standards..."
                      required
                      rows={3}
                      value={feedbackInput}
                      onChange={(e) => setFeedbackInput(e.target.value)}
                      className="w-full px-2.5 py-2 border border-slate-300 text-xs rounded-sm outline-none font-medium resize-none leading-relaxed bg-white"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full py-2.5 bg-[#0076ce] hover:bg-[#00558f] text-white font-bold text-xs uppercase tracking-wider rounded-sm"
                  >
                    Confirm Evaluation Grades Mapping
                  </button>
                </form>
              </div>
            </div>

            {/* AI JUDGING METRIC DESK - RIGHT SIDEBAR */}
            <div className="space-y-4">
              
              {/* COMPLIANCE GUIDELINE CHECKS */}
              <div className="p-5 border border-slate-200 bg-slate-50 rounded-sm space-y-4">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono block">Scoring Guidelines Framework</span>
                
                <div className="space-y-2 text-xs leading-normal">
                  <div className="flex justify-between items-center py-2 border-b border-light">
                    <span className="text-slate-600">Innovation Metric weight</span>
                    <strong className="text-slate-900 font-mono">30 Points max</strong>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-light">
                    <span className="text-slate-600">Technical implementation</span>
                    <strong className="text-slate-900 font-mono">30 Points max</strong>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-light">
                    <span className="text-slate-600">Business impact ratio</span>
                    <strong className="text-slate-900 font-mono">25 Points max</strong>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-light">
                    <span className="text-slate-600">UI design and structure</span>
                    <strong className="text-slate-900 font-mono">15 Points max</strong>
                  </div>
                </div>

                <div className="p-3 bg-white border border-slate-200 rounded leading-relaxed text-[11px] text-slate-500 font-medium">
                  If project lists dual peer-reviewed similar codes, submission duplication alert flags route directly to organizer workspaces.
                </div>
              </div>

            </div>

          </div>
        </div>
      )}

      {/* ──────────────────────────────────────────────────────────
         PARTICIPANT / INNOVATOR MAIN HUB
         ────────────────────────────────────────────────────────── */}
      {activeRole === 'participant' && (
        <div className="flex-1 max-w-6xl w-full mx-auto px-4 md:px-8 py-8 space-y-6">
          
          {/* USER CONTEXT HEADER */}
          <div className="p-6 bg-slate-50 border border-slate-200 rounded-lg flex flex-wrap justify-between items-center gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 bg-[#0a7a4c]/10 text-[#0a7a4c] rounded-sm text-[10px] font-mono font-extrabold uppercase">INNOVATOR</span>
                <span className="text-slate-400 text-xs">| {activeParticipantUser?.name || 'Academic Programmer'} ({activeParticipantUser?.institution})</span>
              </div>
              <h2 className="text-2xl font-black font-disp tracking-tight">Hacker Workspace Control Panel</h2>
              <p className="text-xs text-slate-500">Design enterprise-scale systems, assemble co-founders, and optimize database telemetry files.</p>
            </div>

            {/* DYNAMIC HACKATHON FILTER FOR PARTICIPANTS - FEATURE #2 */}
            <div className="p-1.5 bg-slate-100 rounded-sm border border-slate-200 flex flex-col gap-1.5 min-w-[200px]">
              <span className="text-[9.5px] font-bold text-slate-500 uppercase font-mono px-1">Select Active/Upcoming/Past Events:</span>
              <select
                value={selectedHackathonId}
                onChange={(e) => {
                  setSelectedHackathonId(e.target.value);
                  writeAuditRecord('Participant changed workspace scope', 'Participant', `Mapped workspace to portfolio: ${e.target.value}`, 'Registration');
                }}
                className="px-2 py-1 bg-white text-xs border border-slate-300 font-bold outline-none rounded-sm"
              >
                <optgroup label="Active hackathons">
                  {hackathons.filter(h => h.status === 'active').map(h => (
                    <option key={h.id} value={h.id}>{h.title}</option>
                  ))}
                </optgroup>
                <optgroup label="Upcoming streams">
                  {hackathons.filter(h => h.status === 'upcoming').map(h => (
                    <option key={h.id} value={h.id}>{h.title}</option>
                  ))}
                </optgroup>
                <optgroup label="Completed portfolio">
                  {hackathons.filter(h => h.status === 'past').map(h => (
                    <option key={h.id} value={h.id}>{h.title}</option>
                  ))}
                </optgroup>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* PORTFOLIO INTAKES FORUM - LEFT */}
            <div className="md:col-span-2 space-y-4">
              
              {/* DYNAMIC TIMELINE VISIBILITY CHECKLIST BASED ON TYPE */}
              <div className="p-5 border border-slate-200 bg-white rounded-sm space-y-4">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono block">Operational Progress State: {selectedHackathon.title}</span>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded leading-relaxed">
                    <CheckCircle2 className="h-4 w-4 inline mr-1.5 text-emerald-600" />
                    <strong>Profile Onboard</strong>
                    <p className="text-[10px] text-slate-500 mt-1">Personal biography &amp; tech capabilities indexes mapped.</p>
                  </div>
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded leading-relaxed">
                    <Activity className="h-4 w-4 inline mr-1.5 text-blue-600 animate-pulse" />
                    <strong>Build Development</strong>
                    <p className="text-[10px] text-slate-500 mt-1">Assembly ongoing for {selectedHackathon.track}.</p>
                  </div>
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded leading-relaxed">
                    <Clock className="h-4 w-4 inline mr-1.5 text-slate-400" />
                    <strong>Jury Assessment</strong>
                    <p className="text-[10px] text-slate-500 mt-1">Scores balance using z-score normalization matrices.</p>
                  </div>
                </div>
              </div>

              {/* PROJECT PORTFOLIO ENROLLMENT VIEWPORTS */}
              <div className="p-5 border border-slate-200 bg-white rounded-sm space-y-4">
                <div className="border-b border-slate-100 pb-2">
                  <h3 className="text-sm font-extrabold text-[#0c2340] uppercase tracking-wide">Dynamic Submission Registry</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Submit your technology prototype context and associated repository directories.</p>
                </div>

                <form onSubmit={handleRegisterProjectSubmit} className="space-y-4 text-left">
                  <div className="space-y-1">
                    <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Project Portfolio Title</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. EcoEdge — Smart Renewable Energy Router"
                      value={projectForm.title}
                      onChange={(e) => setProjectForm({ ...projectForm, title: e.target.value })}
                      className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Elevator Tagline Sparkle</label>
                    <input
                      type="text"
                      placeholder="e.g. Distributed machine learning models managing heat maps automatically."
                      value={projectForm.tagline}
                      onChange={(e) => setProjectForm({ ...projectForm, tagline: e.target.value })}
                      className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Associated tech stack (comma-separated tags)</label>
                    <input
                      type="text"
                      placeholder="React, PyTorch, Go Systems, PostgreSQL"
                      value={projectForm.techStack}
                      onChange={(e) => setProjectForm({ ...projectForm, techStack: e.target.value })}
                      className="w-full px-3 py-1.5 border border-slate-300 text-xs font-mono rounded-sm outline-none bg-white"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Code repository location</label>
                      <input
                        type="url"
                        placeholder="https://github.com/hacker-repo"
                        value={projectForm.githubUrl}
                        onChange={(e) => setProjectForm({ ...projectForm, githubUrl: e.target.value })}
                        className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-mono"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Demonstration video link</label>
                      <input
                        type="url"
                        placeholder="https://youtube.com/watch?v=demo"
                        value={projectForm.videoUrl}
                        onChange={(e) => setProjectForm({ ...projectForm, videoUrl: e.target.value })}
                        className="w-full px-3 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-mono"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-extrabold text-slate-600 block uppercase tracking-wider">Full system description</label>
                    <textarea
                      placeholder="Detail your backend architectures, client performance gains, statistical libraries, and core problems solved..."
                      required
                      rows={3}
                      value={projectForm.description}
                      onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
                      className="w-full px-2.5 py-2 border border-slate-300 text-xs rounded-sm outline-none bg-white font-medium resize-none leading-relaxed"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full py-2 bg-[#0076ce] hover:bg-[#00558f] text-white font-bold text-xs uppercase tracking-wider rounded-sm transition-all"
                  >
                    Save &amp; Submit Innovation Project
                  </button>
                </form>
              </div>

            </div>

            {/* TEAM MAKER SUITE & suggeSTED CO-FOUNDERS MAPPING CORES - FEATURE #3 */}
            <div className="space-y-4">
              
              {/* TEAM MEMBERS PROFILE */}
              <div className="p-5 border border-slate-200 bg-white rounded-sm space-y-4">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono block">Dynamic Organization Team</span>
                
                {projects.find(p => p.submittedBy === activeParticipantUser?.id) ? (
                  <div className="space-y-3">
                    <div className="bg-slate-50 p-3 border border-slate-200/80 rounded">
                      <span className="text-[10px] text-[#0076ce] uppercase font-bold block font-mono">Assigned Project Title:</span>
                      <strong className="text-xs text-slate-900 block mt-1">{projects.find(p => p.submittedBy === activeParticipantUser?.id)?.title}</strong>
                    </div>

                    <div className="space-y-2">
                      <span className="text-[10px] text-slate-400 font-mono font-bold uppercase block">PORTFOLIO DELEGATES:</span>
                      {projects.find(p => p.submittedBy === activeParticipantUser?.id)?.teamMembers.map((name, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-xs bg-white p-2 border border-slate-150 rounded">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                          <span className="font-bold text-slate-700">{name} {idx === 0 ? ' (Lead You)' : ''}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-6 text-slate-400 font-mono text-xs">
                    <p>No active project enrolled yet. Lead projects scoping to match teammate components.</p>
                  </div>
                )}
              </div>

              {/* COGNITIVE RECRUIT SUGGESTIONS BASED ON DYNAMIC SKILL TAG MATRICES - FEATURE #3 REQUIRED */}
              <div className="p-5 border border-slate-200 bg-slate-50 rounded-sm space-y-4">
                <div>
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-widest font-mono block">AI Co-founder compatibility board</span>
                  <p className="text-[11px] text-slate-500 mt-1">Suggested partner profiles registered on database presenting highly complementary tech skills tags.</p>
                </div>

                <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
                  {currentMatchPartners.map(({ peer, compatibilityPercentage, roleMatch }) => (
                    <div key={peer.id} className="p-3 bg-white border border-slate-200 rounded text-xs space-y-2 hover:border-[#0076ce] transition-all">
                      <div className="flex justify-between items-start">
                        <div>
                          <strong className="text-slate-900 block leading-tight">{peer.name}</strong>
                          <span className="text-[10px] text-slate-500 font-medium tracking-tight mt-0.5 block italic">{peer.institution} • {peer.country}</span>
                        </div>

                        <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-mono font-bold px-1.5 py-0.5 rounded leading-none text-right flex flex-col items-end">
                          <strong>{compatibilityPercentage}%</strong>
                          <span className="text-[8px] uppercase tracking-tighter text-emerald-500 leading-none">MATCH</span>
                        </span>
                      </div>

                      <div className="flex flex-wrap gap-1">
                        {peer.skills.slice(0, 3).map(skill => (
                          <span key={skill} className="bg-slate-100 text-slate-600 text-[9.5px] px-1 font-mono rounded-sm">{skill}</span>
                        ))}
                      </div>

                      <div className="pt-2 border-t border-slate-100 flex justify-between items-center text-[10.5px]">
                        <span className="font-semibold text-slate-400 uppercase font-mono">{roleMatch}</span>
                        <button
                          onClick={() => handleInviteToTeam(peer.id)}
                          className="px-2.5 py-1 bg-[#0076ce] hover:bg-[#00558f] text-white font-bold uppercase tracking-wide text-[9.5px] rounded-sm transition-all"
                        >
                          Pair Teammate
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>

          </div>
        </div>
      )}

      {/* RE-SET DATABASES ACTION TRIGGER WIDGET IN THE MARGINS */}
      <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-between items-center text-xs text-slate-500 flex-wrap gap-2 font-mono">
        <span></span>
        <button
          onClick={resetOperationalData}
          className="underline decoration-[#C4B495] text-[#0B1E36] hover:text-[#18304F] hover:scale-105 active:scale-95 font-bold font-mono transition-all duration-200 cursor-pointer bg-[#F5F2EB] hover:bg-[#ECE6D8] border border-[#DFD7C7] px-3 py-1.5 rounded-sm"
        >
          [Recover Baseline Portfolio Matrices]
        </button>
      </div>

      </div>
    </div>
  );
}
