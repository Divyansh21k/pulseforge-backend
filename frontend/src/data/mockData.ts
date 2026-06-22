import { Participant, Reviewer, Project, Evaluation, CommunicationLog, AuditTrail, BiasAlert } from '../types';

// Helper to generate IDs
const uuid = () => Math.random().toString(36).substr(2, 9);

export const INITIAL_PARTICIPANTS: Participant[] = [
  {
    id: 'p-1',
    name: 'Alice Vance',
    email: 'alice.vance@mit.edu',
    gender: 'Female',
    institution: 'MIT',
    country: 'USA',
    skills: ['React', 'TypeScript', 'Tailwind', 'UX/UI'],
    bio: 'Junior CS student passionate about building highly accessible frontend interfaces and web accessibility standards.',
    experienceLevel: 'Intermediate',
    registrationTime: '2026-06-18T10:15:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-2',
    name: 'Robert Chen',
    email: 'robert.chen@stanford.edu',
    gender: 'Male',
    institution: 'Stanford University',
    country: 'USA',
    skills: ['Python', 'PyTorch', 'FastAPI', 'AI/ML'],
    bio: 'AI major researching multi-modal Large Language Models. Experienced in training custom classifiers and embedding models.',
    experienceLevel: 'Advanced',
    registrationTime: '2026-06-18T10:30:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-3',
    name: 'Robert Chen',
    email: 'rob.chen@stanford.edu', // Similar email, same name - duplicate!
    gender: 'Male',
    institution: 'Stanford',
    country: 'USA',
    skills: ['Python', 'PyTorch', 'Data Science'],
    bio: 'Research intern working with vision models. Let\'s build AI hackathon solutions!',
    experienceLevel: 'Advanced',
    registrationTime: '2026-06-18T10:34:00-07:00',
    isDuplicateOf: 'p-2',
    similarityScore: 92,
    duplicateChecked: true,
  },
  {
    id: 'p-4',
    name: 'Devika Nair',
    email: 'devika.nair@iitd.ac.in',
    gender: 'Female',
    institution: 'IIT Delhi',
    country: 'India',
    skills: ['Flutter', 'Node.js', 'Express', 'Firebase'],
    bio: 'Mobile developer building secure, cross-platform apps. Prefers offline-first databases and local caching layers.',
    experienceLevel: 'Advanced',
    registrationTime: '2026-06-18T11:02:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-5',
    name: 'Carlos Mendez',
    email: 'mendez.carlos@uabc.mx',
    gender: 'Male',
    institution: 'UABC',
    country: 'Mexico',
    skills: ['React', 'Node.js', 'Tailwind CSS', 'Figma'],
    bio: 'Fullstack developer looking for a team to build education-tech or micro-SaaS integrations.',
    experienceLevel: 'Intermediate',
    registrationTime: '2026-06-18T11:45:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-6',
    name: 'Yuki Takahashi',
    email: 'yuki.takahashi@u-tokyo.ac.jp',
    gender: 'Non-binary',
    institution: 'University of Tokyo',
    country: 'Japan',
    skills: ['React Native', 'TypeScript', 'GraphQL', 'D3.js'],
    bio: 'Data visualization designer. Specialize in charting network trees, bias metrics, and timeline maps.',
    experienceLevel: 'Intermediate',
    registrationTime: '2026-06-18T12:12:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-7',
    name: 'Sarah Jenkins',
    email: 'sarah.j@mit.edu',
    gender: 'Female',
    institution: 'MIT',
    country: 'USA',
    skills: ['Go', 'Docker', 'Kubernetes', 'Backend'],
    bio: 'Distributed systems programmer. Fan of static compilation, RPC microservices, and extreme load balancing.',
    experienceLevel: 'Advanced',
    registrationTime: '2026-06-18T13:05:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-8',
    name: 'Aris Thorne',
    email: 'aris.t@berkeley.edu',
    gender: 'Male',
    institution: 'UC Berkeley',
    country: 'USA',
    skills: ['Svelte', 'FastAPI', 'PostgreSQL', 'Docker'],
    bio: 'Indie hacker. Build clean prototypes fast. Focused on user experience and light fluid styles.',
    experienceLevel: 'Intermediate',
    registrationTime: '2026-06-18T13:20:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-9',
    name: 'Fatima Al-Sudairy',
    email: 'fatima.as@kaust.edu.sa',
    gender: 'Female',
    institution: 'KAUST',
    country: 'Saudi Arabia',
    skills: ['Flask', 'SciKit-Learn', 'Pandas', 'Python'],
    bio: 'Bioinformatics analyst working with genomic datasets. I speak Python and enjoy tabular anomaly detection.',
    experienceLevel: 'Advanced',
    registrationTime: '2026-06-18T13:40:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-10',
    name: 'Liam O\'Connor',
    email: 'l.oconnor@tcd.ie',
    gender: 'Male',
    institution: 'Trinity College Dublin',
    country: 'Ireland',
    skills: ['Figma', 'UX/UI', 'CSS/HTML', 'Frontend'],
    bio: 'Design enthusiast who believes accessibility isn\'t a feature—it\'s the absolute core of software engineering.',
    experienceLevel: 'Beginner',
    registrationTime: '2026-06-18T14:15:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-11',
    name: 'Chen Wei-Ting',
    email: 'wt.chen@ntu.edu.tw',
    gender: 'Male',
    institution: 'National Taiwan University',
    country: 'Taiwan',
    skills: ['React', 'Next.js', 'Express', 'Tailwind'],
    bio: 'Self-taught coder with a background in business strategy. Wanting to design hackathon dashboards that sell metrics.',
    experienceLevel: 'Intermediate',
    registrationTime: '2026-06-18T14:48:00-07:00',
    duplicateChecked: true,
  },
  {
    id: 'p-12',
    name: 'Chen Wei-Ting',
    email: 'wt.chen.web@ntu.edu.tw', // Another email, same name, similar details - Duplicate!
    gender: 'Male',
    institution: 'National Taiwan University',
    country: 'Taiwan',
    skills: ['React', 'Express'],
    bio: 'Full-stack developer student NTU.',
    experienceLevel: 'Intermediate',
    registrationTime: '2026-06-18T14:55:00-07:00',
    isDuplicateOf: 'p-11',
    similarityScore: 88,
    duplicateChecked: true,
  }
];

export const INITIAL_REVIEWERS: Reviewer[] = [
  {
    id: 'r-1',
    name: 'Dr. Helen Vance',
    email: 'h.vance@mit.edu',
    institution: 'MIT',
    country: 'USA',
    gender: 'Female',
    domainExpertise: ['UX/UI', 'Frontend', 'Accessibility'],
    assignedProjects: []
  },
  {
    id: 'r-2',
    name: 'Prof. David Kael',
    email: 'kael@stanford.edu',
    institution: 'Stanford University',
    country: 'USA',
    gender: 'Male',
    domainExpertise: ['AI/ML', 'Python', 'Backend'],
    assignedProjects: []
  },
  {
    id: 'r-3',
    name: 'Siddharth Rao',
    email: 'sid.rao@techinvest.in',
    institution: 'IIT Delhi Alumni Association',
    country: 'India',
    gender: 'Male',
    domainExpertise: ['Backend', 'Mobile', 'Figma'],
    assignedProjects: []
  },
  {
    id: 'r-4',
    name: 'Dr. Clara Montero',
    email: 'c.montero@uabc.mx',
    institution: 'UABC',
    country: 'Mexico',
    gender: 'Female',
    domainExpertise: ['React', 'Full Stack', 'Cloud Architecture'],
    assignedProjects: []
  }
];

export const INITIAL_PROJECTS: Project[] = [
  {
    id: 'proj-1',
    title: 'EduCare Dashboard',
    tagline: 'An accessible, dynamic, web companion supporting dyslexic students with adaptive reading styles.',
    description: 'We built a functional dashboard that analyzes student reading parameters and dynamically tweaks contrast, font-tracking (using OpenDyslexic), and visual spacing in response to micro-comprehension checks.',
    techStack: ['React', 'TypeScript', 'Tailwind', 'UX/UI'],
    institution: 'MIT',
    teamMembers: ['Alice Vance', 'Sarah Jenkins'],
    submittedBy: 'p-1',
    githubUrl: 'https://github.com/mit-student/educare',
    videoUrl: 'https://youtube.com/watch?v=demo1'
  },
  {
    id: 'proj-2',
    title: 'AuraClassifier ML',
    tagline: 'Automated anomaly verification on genomics metadata using isolated Forest networks.',
    description: 'Processes thousands of sequencing columns, validates metadata and outputs structural clusters. Solves traditional data noise through optimized random embeddings.',
    techStack: ['Python', 'PyTorch', 'FastAPI', 'AI/ML'],
    institution: 'Stanford University',
    teamMembers: ['Robert Chen', 'Fatima Al-Sudairy'],
    submittedBy: 'p-2',
    githubUrl: 'https://github.com/stanford-ai/aura-ml',
    videoUrl: 'https://youtube.com/watch?v=demo2'
  },
  {
    id: 'proj-3',
    title: 'EcoRoute Planner',
    tagline: 'Optimizing logistics mileage using localized street grid statistics for zero-emission delivery.',
    description: 'An interactive map overlay charting carbon density index pathways. Integrates mobile native caching to run fully offline on delivery tablets.',
    techStack: ['React Native', 'TypeScript', 'D3.js', 'Tailwind CSS'],
    institution: 'University of Tokyo',
    teamMembers: ['Yuki Takahashi', 'Carlos Mendez'],
    submittedBy: 'p-6',
    githubUrl: 'https://github.com/utokyo/ecoroute',
    videoUrl: 'https://youtube.com/watch?v=demo3'
  },
  {
    id: 'proj-4',
    title: 'TaskMesh Peer-to-Peer',
    tagline: 'Decentralized local-network team matching utility running over Wi-Fi broadcast protocol.',
    description: 'No internet required. Allows developers, designers, and domain experts to broadcast metadata payloads locally and pair based on reciprocal skill gaps.',
    techStack: ['Svelte', 'FastAPI', 'PostgreSQL', 'Docker'],
    institution: 'UC Berkeley',
    teamMembers: ['Aris Thorne', 'Liam O\'Connor'],
    submittedBy: 'p-8',
    githubUrl: 'https://github.com/berkeley/taskmesh',
    videoUrl: 'https://youtube.com/watch?v=demo4'
  }
];

export const INITIAL_EVALUATIONS: Evaluation[] = [
  // Reviewer Helen Vance evaluations - she tends to praise UX/UI projects but gives extremely high scores to MIT (her own institution - potential bias!)
  {
    id: 'e-1',
    projectId: 'proj-1', // EduCare (MIT)
    reviewerId: 'r-1', // Dr. Helen Vance (MIT)
    scores: {
      innovation: 10,
      execution: 10,
      impact: 9,
      design: 10
    },
    feedback: 'Visual design is absolutely exemplary. Brilliant utility that should be immediately deployed. Outstanding contribution from MIT!',
    timestamp: '2026-06-19T02:10:00-07:00'
  },
  {
    id: 'e-2',
    projectId: 'proj-3', // EcoRoute (U Tokyo)
    reviewerId: 'r-1', // Dr. Helen Vance (MIT)
    scores: {
      innovation: 6,
      execution: 5,
      impact: 6,
      design: 6
    },
    feedback: 'Interesting charting but the mobile controls are somewhat clunky. Needs higher emphasis on accessible typography layout.',
    timestamp: '2026-06-19T02:25:00-07:00'
  },
  // Reviewer David Kael evaluations - Stanford Prof, gives very high scores to Python AI/ML and projects highlighting Stanford (AuraClassifier)
  {
    id: 'e-3',
    projectId: 'proj-2', // AuraClassifier (Stanford)
    reviewerId: 'r-2', // Prof. David Kael (Stanford)
    scores: {
      innovation: 10,
      execution: 10,
      impact: 10,
      design: 6
    },
    feedback: 'Deep ML modeling. Excellent usage of forest isolation. Representing Stanford extremely well.',
    timestamp: '2026-06-19T03:05:00-07:00'
  },
  {
    id: 'e-4',
    projectId: 'proj-1', // EduCare (MIT)
    reviewerId: 'r-2', // David Kael (Stanford)
    scores: {
      innovation: 7,
      execution: 6,
      impact: 7,
      design: 8
    },
    feedback: 'Good frontend application, but lacks robust machine learning analytics to identify progression trends.',
    timestamp: '2026-06-19T03:15:00-07:00'
  },
  // Reviewer Siddharth Rao (Neutral/Strict reviewer with high standards)
  {
    id: 'e-5',
    projectId: 'proj-1',
    reviewerId: 'r-3',
    scores: {
      innovation: 8,
      execution: 7,
      impact: 8,
      design: 8
    },
    feedback: 'Solid implementation of OpenDyslexic font support and responsive layout. Good documentation.',
    timestamp: '2026-06-19T04:12:00-07:00'
  },
  {
    id: 'e-6',
    projectId: 'proj-2',
    reviewerId: 'r-3',
    scores: {
      innovation: 8,
      execution: 7,
      impact: 8,
      design: 5
    },
    feedback: 'The backend model works, but the CLI dashboard makes it hard for common developers to interface with.',
    timestamp: '2026-06-19T04:30:00-07:00'
  },
  {
    id: 'e-7',
    projectId: 'proj-4', // TaskMesh (UC Berkeley)
    reviewerId: 'r-3',
    scores: {
      innovation: 9,
      execution: 8,
      impact: 9,
      design: 8
    },
    feedback: 'Decentralized local Wi-Fi sharing works correctly. Exceptionally useful and aligns with practical scenarios.',
    timestamp: '2026-06-19T04:50:00-07:00'
  }
];

export const INITIAL_BIAS_ALERTS: BiasAlert[] = [
  {
    id: 'ba-1',
    timestamp: '2026-06-19T05:00:00-07:00',
    reviewerId: 'r-1',
    reviewerName: 'Dr. Helen Vance',
    dimension: 'Institution',
    description: 'Significantly higher scores are assigned exclusively to projects from MIT (+2.83 std deviation compared to normal score distribution).',
    severity: 'high',
    audited: false
  },
  {
    id: 'ba-2',
    timestamp: '2026-06-19T05:12:00-07:00',
    reviewerId: 'r-2',
    reviewerName: 'Prof. David Kael',
    dimension: 'Tech Stack',
    description: 'Systemic bias detected in favor of the Python/PyTorch technology stack (+2.10 score boost compared to Javascript stacks).',
    severity: 'medium',
    audited: false
  }
];

export const INITIAL_AUDIT_TRAILS: AuditTrail[] = [
  {
    id: 'at-1',
    timestamp: '2026-06-18T10:00:00-07:00',
    action: 'Database Initialized',
    userRole: 'Organizer Dev',
    details: 'System loaded default templates and initialized 12 participant accounts.',
    category: 'Registration'
  },
  {
    id: 'at-2',
    timestamp: '2026-06-18T15:00:00-07:00',
    action: 'Duplicate Guard Enabled',
    userRole: 'Organizer',
    details: 'Intelligent registration duplicate detector completed fuzzy evaluation across 12 items. Flagged 2 items with similarity > 85%.',
    category: 'Registration'
  },
  {
    id: 'at-3',
    timestamp: '2026-06-19T01:00:00-07:00',
    action: 'Reviewer Assignment Set',
    userRole: 'Organizer',
    details: 'Assigned 4 active multi-disciplinary reviewers based on expertise matching: UX/UI to Dr. Helen Vance, AI/ML to Prof. David Kael.',
    category: 'Matching'
  },
  {
    id: 'at-4',
    timestamp: '2026-06-19T05:15:00-07:00',
    action: 'Real-time Bias Audit',
    userRole: 'System',
    details: 'Statistical scan flags potential Institutional Bias on Dr. Helen Vance rating of MIT.',
    category: 'Evaluation'
  }
];

export const INITIAL_COMMUNICATIONS: CommunicationLog[] = [
  {
    id: 'c-1',
    recipientEmail: 'p-1', // Reference to Alice Vance
    subject: 'Aura Hackathon: Next Steps for Team Matching',
    content: 'Hi Alice, our AI team matchmaking assistant noticed a strong alignment between your Frontend skills and Sarah\'s docker skills. We suggest connecting on our Discord channel #team-pairing-6.',
    channel: 'Email',
    timestamp: '2026-06-18T16:00:00-07:00',
    engagementOpened: true,
    engagementClicked: true,
    abTestSegment: 'A'
  },
  {
    id: 'c-2',
    recipientEmail: 'p-4',
    subject: 'Welcome to AI Hackathon! 🚀 Unleash your Flutter Potential',
    content: 'Hey Devika, as a mobile specialist, check out the specialized React Native, Flutter API widgets hosted on our dev-portal to accelerate your offline architecture.',
    channel: 'Email',
    timestamp: '2026-06-18T16:15:00-07:00',
    engagementOpened: true,
    engagementClicked: false,
    abTestSegment: 'B'
  }
];
