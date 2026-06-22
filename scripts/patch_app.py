import os
import re

app_path = '/Users/divyanshkharnal/pulseforge-backend/frontend/1/src/App.tsx'

with open(app_path, 'r') as f:
    content = f.read()

# 1. Add CreatableSelect import
if "import CreatableSelect from 'react-select/creatable';" not in content:
    content = content.replace("import React, { useState, useEffect, useCallback } from 'react';", "import React, { useState, useEffect, useCallback } from 'react';\nimport CreatableSelect from 'react-select/creatable';")

# 2. Add enrolledHackathons state
if "const [enrolledHackathons, setEnrolledHackathons]" not in content:
    content = content.replace("const [hackathons, setHackathons] = useState<Hackathon[]>(INITIAL_HACKATHONS);", "const [hackathons, setHackathons] = useState<Hackathon[]>(INITIAL_HACKATHONS);\n  const [enrolledHackathons, setEnrolledHackathons] = useState<api.BackendEvent[]>([]);")

# 3. Add getEnrolledEvents to refreshBackendData
if "setEnrolledHackathons(enrolled);" not in content:
    content = content.replace("const data = await api.syncAllBackendData();", "const data = await api.syncAllBackendData();\n      const enrolled = await api.getEnrolledEvents().catch(() => []);\n      setEnrolledHackathons(enrolled);")

# 4. Replace techSkills input with CreatableSelect
tech_skills_block = """<input
                            type="text"
                            placeholder="e.g. React, Python, PyTorch, Docker, PostgreSQL"
                            value={registerForm.techSkills}
                            onChange={(e) => setRegisterForm({ ...registerForm, techSkills: e.target.value })}
                            className="w-full px-2.5 py-1.5 border border-slate-300 text-xs rounded-sm outline-none bg-white font-mono"
                          />"""
creatable_select_block = """<CreatableSelect
                              isMulti
                              value={registerForm.techSkills.split(',').map(s => s.trim()).filter(Boolean).map(s => ({ label: s, value: s }))}
                              onChange={(newValues) => setRegisterForm({ ...registerForm, techSkills: newValues.map(v => v.value).join(', ') })}
                              options={[
                                { label: 'React', value: 'React' },
                                { label: 'Python', value: 'Python' },
                                { label: 'Machine Learning', value: 'Machine Learning' },
                                { label: 'TypeScript', value: 'TypeScript' },
                                { label: 'Node.js', value: 'Node.js' }
                              ]}
                              className="text-xs font-mono"
                              styles={{
                                control: (baseStyles) => ({
                                  ...baseStyles,
                                  borderColor: '#cbd5e1',
                                  borderRadius: '0.125rem',
                                  minHeight: '34px',
                                  backgroundColor: '#ffffff'
                                }),
                              }}
                              placeholder="Type skills here..."
                            />"""
content = content.replace(tech_skills_block, creatable_select_block)

# 5. Add Enrollment box to Participant Dashboard
participant_enrollment_box = """
              {/* AVAILABLE EVENTS ENROLLMENT */}
              <div className="p-5 border border-slate-200 bg-white rounded-sm space-y-4">
                <div className="border-b border-slate-100 pb-2">
                  <h3 className="text-sm font-extrabold text-[#0c2340] uppercase tracking-wide">Available Hackathons</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Enroll to participate in ongoing and upcoming events.</p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {hackathons.filter(h => h.status !== 'past').map(h => {
                    const hackIdInt = parseInt(h.id.replace('hack-', ''), 10) || 1;
                    const isEnrolled = enrolledHackathons.some(e => e.id === hackIdInt);
                    return (
                      <div key={h.id} className="p-3 border border-slate-200 rounded-sm bg-slate-50 flex flex-col justify-between">
                        <div>
                          <h4 className="font-bold text-sm text-slate-900">{h.title}</h4>
                          <span className="text-[10px] uppercase font-mono text-slate-500 mb-2 inline-block">{h.status} | {h.track}</span>
                        </div>
                        <button
                          onClick={async () => {
                            try {
                              await api.enrollInEvent(hackIdInt);
                              const enrolled = await api.getEnrolledEvents().catch(() => []);
                              setEnrolledHackathons(enrolled);
                            } catch (e: any) {
                              alert('Failed to enroll: ' + e.message);
                            }
                          }}
                          disabled={isEnrolled}
                          className={`mt-2 py-1.5 px-3 text-xs font-bold uppercase rounded-sm transition-colors ${isEnrolled ? 'bg-slate-200 text-slate-500 cursor-not-allowed' : 'bg-[#0076ce] text-white hover:bg-[#005a9e]'}`}
                        >
                          {isEnrolled ? 'Enrolled' : 'Enroll Now'}
                        </button>
                      </div>
                    );
                  })}
                  {hackathons.filter(h => h.status !== 'past').length === 0 && (
                    <p className="text-xs text-slate-500">No active or upcoming events at this time.</p>
                  )}
                </div>
              </div>

"""
if "{/* AVAILABLE EVENTS ENROLLMENT */}" not in content:
    content = content.replace("{/* PROJECT PORTFOLIO ENROLLMENT VIEWPORTS */}", participant_enrollment_box + "              {/* PROJECT PORTFOLIO ENROLLMENT VIEWPORTS */}")

with open(app_path, 'w') as f:
    f.write(content)

print("Patch applied.")
