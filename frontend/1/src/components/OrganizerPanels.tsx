import React, { useState } from 'react';
import * as api from '../utils/api';
import { RefreshCw, Users, ShieldAlert, Send, Award } from 'lucide-react';

interface Props {
  onAudit: (action: string, actor: string, detail: string, category: string) => void;
  onRefresh: () => Promise<void>;
}

export default function OrganizerPanels({ onAudit, onRefresh }: Props) {
  const [tab, setTab] = useState<'teams' | 'matcher' | 'bias' | 'promo'>('teams');
  const [teamSize, setTeamSize] = useState(2);
  const [teamResult, setTeamResult] = useState<string>('');
  const [composition, setComposition] = useState<api.BackendTeamComposition | null>(null);
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [teams, setTeams] = useState<api.BackendTeam[]>([]);
  const [workloads, setWorkloads] = useState<api.BackendReviewerWorkload[]>([]);
  const [biasFlags, setBiasFlags] = useState<api.BackendBiasFlag[]>([]);
  const [assignResult, setAssignResult] = useState<string>('');
  const [promoTemplate, setPromoTemplate] = useState('submission_reminder');
  const [promoParticipantId, setPromoParticipantId] = useState('1');
  const [loading, setLoading] = useState(false);

  const loadTeams = async () => {
    const t = await api.listTeams();
    setTeams(t);
  };

  const loadWorkloads = async () => {
    const reviewers = await api.listReviewers();
    const wls = await Promise.all(reviewers.map(r => api.getReviewerWorkload(r.id)));
    setWorkloads(wls);
  };

  const loadBias = async () => {
    const flags = await api.listBiasFlags();
    setBiasFlags(flags);
  };

  const handleAutoForm = async () => {
    setLoading(true);
    try {
      const result = await api.autoFormTeams(teamSize);
      setTeamResult(`Formed ${result.teams_formed} teams (size ${teamSize}). Algorithm: skill-diversity greedy clustering with complementary coverage optimization.`);
      onAudit('Team Auto-Formation', 'Organizer', `${result.teams_formed} teams created via backend optimizer`, 'Registration');
      await loadTeams();
      await onRefresh();
    } catch (e: unknown) {
      setTeamResult(`Error: ${e instanceof Error ? e.message : 'Failed'}`);
    }
    setLoading(false);
  };

  const handleComposition = async (teamId: number) => {
    setSelectedTeamId(teamId);
    try {
      const c = await api.getTeamComposition(teamId);
      setComposition(c);
    } catch {
      setComposition(null);
    }
  };

  const handleAssign = async () => {
    setLoading(true);
    try {
      const r = await api.runReviewerAssignments(2);
      setAssignResult(`Created ${r.assignments_created} assignments. Weights: expertise 40%, workload 30%, conflict 20%, diversity 10%.`);
      onAudit('Reviewer Assignment Run', 'Organizer', assignResult, 'Evaluation');
      await loadWorkloads();
    } catch (e: unknown) {
      setAssignResult(`Error: ${e instanceof Error ? e.message : 'Failed'}`);
    }
    setLoading(false);
  };

  const handleBiasScan = async () => {
    setLoading(true);
    try {
      await api.normalizeScores();
      const scan = await api.runBiasScan();
      await loadBias();
      onAudit('Bias Scan', 'Organizer', `${scan.total_flags} flags detected`, 'Evaluation');
    } catch (e: unknown) {
      onAudit('Bias Scan Failed', 'System', String(e), 'Evaluation');
    }
    setLoading(false);
  };

  const handlePromo = async () => {
    setLoading(true);
    try {
      const r = await api.sendNotification({
        participant_id: promoParticipantId,
        template_key: promoTemplate,
        context: { event_name: 'PulseForge Demo Hackathon' },
      });
      onAudit('Notification Sent', 'Organizer', r.subject, 'Promotion');
      await onRefresh();
    } catch (e: unknown) {
      onAudit('Notification Failed', 'Organizer', String(e), 'Promotion');
    }
    setLoading(false);
  };

  React.useEffect(() => {
    if (tab === 'teams') loadTeams();
    if (tab === 'matcher') loadWorkloads();
    if (tab === 'bias') loadBias();
  }, [tab]);

  const tabs = [
    { id: 'teams' as const, label: 'Team Formation', icon: Users },
    { id: 'matcher' as const, label: 'Reviewer Matcher', icon: Award },
    { id: 'bias' as const, label: 'Bias Dashboard', icon: ShieldAlert },
    { id: 'promo' as const, label: 'Communications', icon: Send },
  ];

  return (
    <div className="p-5 border border-slate-200 rounded bg-white space-y-4">
      <div className="flex flex-wrap gap-2 border-b border-slate-100 pb-3">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-3 py-1.5 text-xs font-bold rounded-sm flex items-center gap-1.5 cursor-pointer ${
              tab === t.id ? 'bg-[#0B1E36] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <t.icon className="h-3.5 w-3.5" />
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'teams' && (
        <div className="space-y-4">
          <p className="text-xs text-slate-500">Auto-form teams using backend skill-diversity algorithm. Each team is built to maximize complementary skill coverage.</p>
          <div className="flex items-center gap-3">
            <label className="text-xs font-bold text-slate-600">Team size:</label>
            <input type="number" min={2} max={5} value={teamSize} onChange={e => setTeamSize(parseInt(e.target.value) || 2)} className="w-16 px-2 py-1 border rounded text-xs" />
            <button onClick={handleAutoForm} disabled={loading} className="px-4 py-1.5 bg-[#0B1E36] text-white text-xs font-bold rounded cursor-pointer flex items-center gap-1">
              {loading ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : null}
              Run Auto-Formation
            </button>
          </div>
          {teamResult && <p className="text-xs text-slate-700 bg-[#F5F2EB] p-3 rounded border border-[#DFD7C7]">{teamResult}</p>}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {teams.map(t => (
              <button key={t.id} onClick={() => handleComposition(t.id)} className={`p-3 border rounded text-left text-xs cursor-pointer ${selectedTeamId === t.id ? 'border-[#0076ce] bg-blue-50' : 'border-slate-200'}`}>
                <strong>{t.name}</strong>
                <span className="block text-slate-500 mt-1">{t.member_count} members</span>
              </button>
            ))}
          </div>
          {composition && (
            <div className="p-4 bg-slate-50 border rounded space-y-2 text-xs">
              <strong>Team #{composition.team_id} Composition Analysis</strong>
              <p>Diversity score: <strong>{composition.skill_diversity_score}%</strong></p>
              <p>Coverage gaps: {composition.coverage_gaps?.length ? composition.coverage_gaps.join(', ') : 'None detected'}</p>
              <p>AI Reasoning: <strong>{composition.strength_assessment}</strong></p>
              <p className="text-slate-500">Computed live from participant skill taxonomy in PostgreSQL/SQLite.</p>
            </div>
          )}
        </div>
      )}

      {tab === 'matcher' && (
        <div className="space-y-4">
          <p className="text-xs text-slate-500">Multi-objective reviewer↔project assignment with explainable score breakdown per pairing.</p>
          <button onClick={handleAssign} disabled={loading} className="px-4 py-1.5 bg-[#0076ce] text-white text-xs font-bold rounded cursor-pointer">
            Run Assignment Optimizer
          </button>
          {assignResult && <p className="text-xs bg-blue-50 p-3 rounded border border-blue-100">{assignResult}</p>}
          <div className="space-y-2">
            <span className="text-[10px] font-bold uppercase text-slate-500">Reviewer Workload (live from DB)</span>
            {workloads.map(w => (
              <div key={w.reviewer_id} className="flex justify-between items-center p-2 border rounded text-xs">
                <span>Reviewer #{w.reviewer_id}</span>
                <span>{w.active_assignments}/{w.max_workload} projects ({w.utilization_pct}%)</span>
                <div className="w-24 bg-slate-100 h-1.5 rounded overflow-hidden">
                  <div className="bg-[#0076ce] h-full" style={{ width: `${Math.min(100, w.utilization_pct)}%` }} />
                </div>
              </div>
            ))}
            {workloads.length === 0 && <p className="text-xs text-slate-400">No reviewers loaded. Run assignment after seeding data.</p>}
          </div>
        </div>
      )}

      {tab === 'bias' && (
        <div className="space-y-4">
          <button onClick={handleBiasScan} disabled={loading} className="px-4 py-1.5 bg-amber-600 text-white text-xs font-bold rounded cursor-pointer">
            Normalize Scores + Run Bias Scan
          </button>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {biasFlags.map(f => (
              <div key={f.id} className={`p-3 border rounded text-xs ${f.severity === 'high' ? 'border-red-300 bg-red-50' : 'border-slate-200'}`}>
                <div className="flex justify-between">
                  <strong>{f.dimension} — {f.scope}</strong>
                  <span className="font-mono text-[10px] uppercase">{f.severity}</span>
                </div>
                <p className="mt-1 text-slate-600">{f.description}</p>
                <p className="mt-1 font-mono text-[10px] text-slate-400">stat={f.statistic} conf={f.confidence} status={f.status}</p>
              </div>
            ))}
            {biasFlags.length === 0 && <p className="text-xs text-slate-400">No bias flags yet. Submit evaluations and run scan.</p>}
          </div>
        </div>
      )}

      {tab === 'promo' && (
        <div className="space-y-4">
          <p className="text-xs text-slate-500">Send templated notifications (logged to DB — delivery is simulated for demo).</p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] font-bold uppercase text-slate-500 block mb-1">Template</label>
              <select value={promoTemplate} onChange={e => setPromoTemplate(e.target.value)} className="w-full px-2 py-1.5 border rounded text-xs">
                <option value="welcome">welcome</option>
                <option value="submission_reminder">submission_reminder</option>
                <option value="evaluation_complete">evaluation_complete</option>
                <option value="team_formed">team_formed</option>
              </select>
            </div>
            <div>
              <label className="text-[10px] font-bold uppercase text-slate-500 block mb-1">Participant ID</label>
              <input value={promoParticipantId} onChange={e => setPromoParticipantId(e.target.value)} className="w-full px-2 py-1.5 border rounded text-xs" />
            </div>
          </div>
          <button onClick={handlePromo} disabled={loading} className="px-4 py-1.5 bg-[#0B1E36] text-white text-xs font-bold rounded cursor-pointer">
            Send Notification
          </button>
        </div>
      )}
    </div>
  );
}
