export interface Participant {
  id: string;
  name: string;
  email: string;
  gender: 'Male' | 'Female' | 'Non-binary' | 'Prefer not to say';
  institution: string;
  country: string;
  skills: string[];
  bio: string;
  experienceLevel: 'Beginner' | 'Intermediate' | 'Advanced';
  registrationTime: string;
  isDuplicateOf?: string; // ID of duplicate participant if detected
  similarityScore?: number;
  duplicateChecked?: boolean;
}

export interface Reviewer {
  id: string;
  name: string;
  email: string;
  institution: string;
  country: string;
  gender: 'Male' | 'Female' | 'Non-binary' | 'Prefer not to say';
  domainExpertise: string[]; // e.g. ["Frontend", "AI/ML", "Backend", "UX/UI"]
  assignedProjects: string[]; // array of projectIds
}

export interface Project {
  id: string;
  title: string;
  tagline: string;
  description: string;
  techStack: string[];
  institution: string;
  teamMembers: string[]; // array of participant names or IDs
  submittedBy: string; // participant ID
  githubUrl?: string;
  videoUrl?: string;
}

export interface EvaluationCriteria {
  innovation: number; // 1-10
  execution: number; // 1-10
  impact: number;      // 1-10
  design: number;      // 1-10
}

export interface Evaluation {
  id: string;
  projectId: string;
  reviewerId: string;
  scores: EvaluationCriteria;
  feedback: string;
  timestamp: string;
  isNormalized?: boolean;
  originalAverage?: number;
  normalizedScore?: number; // Normalized weighted index
}

export interface CommunicationLog {
  id: string;
  recipientEmail: string;
  subject: string;
  content: string;
  channel: 'Email' | 'Slack' | 'Twitter' | 'LinkedIn';
  timestamp: string;
  engagementOpened: boolean;
  engagementClicked: boolean;
  abTestSegment: 'A' | 'B';
}

export interface AuditTrail {
  id: string;
  timestamp: string;
  action: string;
  userRole: string;
  details: string;
  category: 'Registration' | 'Matching' | 'Evaluation' | 'Promotion';
}

export interface BiasAlert {
  id: string;
  timestamp: string;
  reviewerId: string;
  reviewerName: string;
  dimension: 'Gender' | 'Institution' | 'Tech Stack' | 'Geography';
  description: string;
  severity: 'low' | 'medium' | 'high';
  audited: boolean;
}

export interface LiveStats {
  registrationConversionRate: number; // e.g. percentage 84%
  participantEngagementScore: number; // 1-100 score
  evaluationCompletionRate: number; // e.g. 75%
  reviewerSatisfactionScore: number; // 1-5 score
}

export interface Hackathon {
  id: string;
  title: string;
  description: string;
  status: 'active' | 'past' | 'upcoming';
  participantCount: number;
  teamCount: number;
  startDate: string;
  endDate: string;
  track: string;
}

