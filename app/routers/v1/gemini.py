from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.gemini_client import _model

router = APIRouter(prefix="/api/gemini", tags=["Gemini AI Copilot"])


class AnalyzePayload(BaseModel):
    title: str
    tagline: str
    description: str
    techStack: str


class PitchPayload(BaseModel):
    title: str
    tagline: str
    description: str
    techStack: str
    targetAudience: str


@router.post("/analyze-dell-potential")
def analyze_dell_potential(payload: AnalyzePayload):
    if not _model:
        return {
            "feedback": "### ⚠️ Local AI Emulation Mode Active\n\nTo test live Gemini generations, ensure you populate the **GEMINI_API_KEY**.\n\n#### **Pre-Evaluation Metrics (Emulated Baseline)**\n- **WIN PROBABILITY: 85%**\n- **Architecture alignment**: Your general outline matches key trends.\n- **Critical Recommendation**: To lock in first place, explicit hardware deployment diagrams highlighting **Dell PowerEdge XE9680** clusters mapping real-time sensor streams and local **Dell APEX Hybrid Workloads** must be mentioned.\n- **Green Computing Advice**: Map carbon offsets dynamically via lightweight database telemetry sensors."
        }

    prompt = f"""You are a Senior Executive Distringuished Engineer and Principal Hackathon Juror at Dell Technologies.
Your goal is to evaluate candidate hackathon proposals and check if they have what it takes to win a prestigious Dell Global Hackathon competition.
Analyze this candidate project under the four main pillars of the evaluation framework:
1. DEPLOYMENT SCALABILITY & VIRTUALIZATION (Using Dell PowerEdge servers, client virtualization platforms, unified enterprise platforms)
2. GREENOPS & POWER TELEMETRY (Carbon tracking, CPU cooling strategies, data center thermal optimizations)
3. ZERO-TRUST RESILIENCE (Edge security, endpoint identity, adversarial compliance models)
4. PRACTICAL EDGE AI COUPLING (軽量 lightweight local inference model integration, latency-optimized calculations)

CANDIDATE SUBMISSION DATA:
Project Title: {payload.title or "Unnamed Hacker Project"}
Elevator Tagline: {payload.tagline or "General technology solver"}
Detailed System Description: {payload.description or "No description provided."}
Tech Stack Components: {payload.techStack or "Standard frontend/backend stack"}

Provide a highly professional markdown feedback report structured as follows:
- **Dell Hackathon Win Probability Score**: Assign a percentage (0-100%) based on rigor and design.
- **Technical Excellence Breakdown**: 2 concise bullet points for each of the 4 pillars.
- **Specific Dell Hardware / System Suggestion**: Describe how they can realistically leverage Dell products (Dell Precision Workstations, PowerEdge servers, APEX multi-cloud, PowerScale storage) to pitch a world-class hybrid cloud architectural blueprint.
- **3 Urgent Technical Implementations**: Actionable, precise software/hardware improvements to execute immediately to guarantee first place.

Keep the advice clinical, highly expert, authentic to modern Dell enterprise tech, encouraging, and detailed. DO NOT use generic AI filler words. Use exact terms."""

    try:
        response = _model.generate_content(prompt)
        return {"feedback": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-pitch")
def generate_pitch(payload: PitchPayload):
    if not _model:
        return {
            "script": "## 🎙️ Emulated Elevator Pitch & Cue Card\n\n**[00:00 - 00:15] Open with a visual punch**\n- *Visual*: Stand tall, screen shared with an elegant flow diagram of telemetry streams. \n- *Audio*: Hello, judges! We created a dynamic workspace resolving the core operational bottlenecks of enterprise telemetry.\n\n**[00:15 - 00:45] The Technical Deep-dive**\n- *Visual*: Switch to the Live Dashboard highlighting z-score normalized evaluations and secure endpoint routes.\n- *Audio*: Running on local edge instances, our solution couples low-latency inference loops with real-time analytics, scaling securely across enterprise servers.\n\n**[00:45 - 01:00] The Ask & Integration**\n- *Visual*: Show the Dell APEX workflow integration slide.\n- *Audio*: By bridging the gaps between co-founder capabilities and expert jury allocations, we guarantee 100% operational fairness. That is how we power edge workspaces with Dell! Thank you."
        }

    prompt = f"""Write a high-impact, professional 60-second video elevator pitch or live demonstration script for the following competitor hackathon project.
Target Audience for Pitch: {payload.targetAudience or "General Venture Judges and Technical Faculty Directors"}

PROJECT DETAILS:
Title: {payload.title}
Tagline: {payload.tagline}
Description: {payload.description}
Tech Stack: {payload.techStack}

Please format the response as a professional cue performance sheet containing:
- [Visual / Slide Cue] notation telling them what they should display on screen.
- [Spoken script] text containing the highly precise words they should execute under exact time allocations ([00:00-00:15], [00:15-00:45], [00:45-01:00]).
Include professional hooks emphasizing scaling parameters, business metrics, and structural integration with Dell enterprise technology."""

    try:
        response = _model.generate_content(prompt)
        return {"script": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
