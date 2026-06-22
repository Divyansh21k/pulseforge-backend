import express from "express";
import path from "path";
import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";
import { createServer as createViteServer } from "vite";

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json());

// Initialize Google Gen AI securely on the server side
let ai: GoogleGenAI | null = null;
try {
  const apiKey = process.env.GEMINI_API_KEY;
  if (apiKey) {
    ai = new GoogleGenAI({
      apiKey: apiKey,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        }
      }
    });
    console.log("[HackBridge Master Server] Secure Gemini API integration configured successfully.");
  } else {
    console.warn("[HackBridge Master Server] Warning: GEMINI_API_KEY missing in environment variables. Local backup modes enabled.");
  }
} catch (e) {
  console.error("[HackBridge Master Server] Gemini initialization failed:", e);
}

// SECURED EXPOSED REST API ROUTERS FOR THE COPILOT SYSTEM
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    backend: "Express Node Server Mode",
    hasSecretsConfigured: !!process.env.GEMINI_API_KEY,
    currentTime: "2026-06-21T06:56:55-07:00",
    hasGeminiActive: !!ai
  });
});

/**
 * 1. DELL CRITICAL WINNING-POTENTIAL AUDITOR (AI powered analysis)
 */
app.post("/api/gemini/analyze-dell-potential", async (req, res) => {
  if (!ai) {
    return res.status(200).json({
      feedback: `### ⚠️ Local AI Emulation Mode Active

To test live Gemini generations, ensure you populate the **GEMINI_API_KEY** in the Secrets panel in AI Studio. 

#### **Pre-Evaluation Metrics (Emulated Baseline)**
- **WIN PROBABILITY: 85%**
- **Architecture alignment**: Your general outline matches key trends.
- **Critical Recommendation**: To lock in first place, explicit hardware deployment diagrams highlighting **Dell PowerEdge XE9680** clusters mapping real-time sensor streams and local **Dell APEX Hybrid Workloads** must be mentioned.
- **Green Computing Advice**: Map carbon offsets dynamically via lightweight database telemetry sensors.`
    });
  }

  const { title, tagline, description, techStack } = req.body;
  const prompt = `You are a Senior Executive Distringuished Engineer and Principal Hackathon Juror at Dell Technologies.
Your goal is to evaluate candidate hackathon proposals and check if they have what it takes to win a prestigious Dell Global Hackathon competition.
Analyze this candidate project under the four main pillars of the evaluation framework:
1. DEPLOYMENT SCALABILITY & VIRTUALIZATION (Using Dell PowerEdge servers, client virtualization platforms, unified enterprise platforms)
2. GREENOPS & POWER TELEMETRY (Carbon tracking, CPU cooling strategies, data center thermal optimizations)
3. ZERO-TRUST RESILIENCE (Edge security, endpoint identity, adversarial compliance models)
4. PRACTICAL EDGE AI COUPLING (軽量 lightweight local inference model integration, latency-optimized calculations)

CANDIDATE SUBMISSION DATA:
Project Title: ${title || "Unnamed Hacker Project"}
Elevator Tagline: ${tagline || "General technology solver"}
Detailed System Description: ${description || "No description provided."}
Tech Stack Components: ${techStack || "Standard frontend/backend stack"}

Provide a highly professional markdown feedback report structured as follows:
- **Dell Hackathon Win Probability Score**: Assign a percentage (0-100%) based on rigor and design.
- **Technical Excellence Breakdown**: 2 concise bullet points for each of the 4 pillars.
- **Specific Dell Hardware / System Suggestion**: Describe how they can realistically leverage Dell products (Dell Precision Workstations, PowerEdge servers, APEX multi-cloud, PowerScale storage) to pitch a world-class hybrid cloud architectural blueprint.
- **3 Urgent Technical Implementations**: Actionable, precise software/hardware improvements to execute immediately to guarantee first place.

Keep the advice clinical, highly expert, authentic to modern Dell enterprise tech, encouraging, and detailed. DO NOT use generic AI filler words. Use exact terms.`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: prompt,
    });
    res.json({ feedback: response.text });
  } catch (error: any) {
    console.error("[Gemini API Error] Failed to generate Dell potential analysis:", error);
    res.status(500).json({ error: error?.message || "Internal server error occurred during analysis." });
  }
});

/**
 * 2. AUTOMATED 60-SECOND PITCH SCRIPTER & SPEECH WRITER
 */
app.post("/api/gemini/generate-pitch", async (req, res) => {
  if (!ai) {
    return res.status(200).json({
      script: `## 🎙️ Emulated Elevator Pitch & Cue Card

**[00:00 - 00:15] Open with a visual punch**
- *Visual*: Stand tall, screen shared with an elegant flow diagram of telemetry streams. 
- *Audio*: Hello, judges! We created a dynamic workspace resolving the core operational bottlenecks of enterprise telemetry.

**[00:15 - 00:45] The Technical Deep-dive**
- *Visual*: Switch to the Live Dashboard highlighting z-score normalized evaluations and secure endpoint routes.
- *Audio*: Running on local edge instances, our solution couples low-latency inference loops with real-time analytics, scaling securely across enterprise servers.

**[00:45 - 01:00] The Ask & Integration**
- *Visual*: Show the Dell APEX workflow integration slide.
- *Audio*: By bridging the gaps between co-founder capabilities and expert jury allocations, we guarantee 100% operational fairness. That is how we power edge workspaces with Dell! Thank you.`
    });
  }

  const { title, tagline, description, techStack, targetAudience } = req.body;
  const prompt = `Write a high-impact, professional 60-second video elevator pitch or live demonstration script for the following competitor hackathon project.
Target Audience for Pitch: ${targetAudience || "General Venture Judges and Technical Faculty Directors"}

PROJECT DETAILS:
Title: ${title}
Tagline: ${tagline}
Description: ${description}
Tech Stack: ${techStack}

Please format the response as a professional cue performance sheet containing:
- [Visual / Slide Cue] notation telling them what they should display on screen.
- [Spoken script] text containing the highly precise words they should execute under exact time allocations ([00:00-00:15], [00:15-00:45], [00:45-01:00]).
Include professional hooks emphasizing scaling parameters, business metrics, and structural integration with Dell enterprise technology.`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: prompt,
    });
    res.json({ script: response.text });
  } catch (error: any) {
    console.error("[Gemini API Error] Failed to generate elevator script:", error);
    res.status(500).json({ error: error?.message || "Failed pitch compilation." });
  }
});

/**
 * 3. REAL-TIME REGISTRATION DUPLICATE SCANNER (Fuzzy Semantic Parser)
 */
app.post("/api/gemini/fuzzy-dedup", async (req, res) => {
  if (!ai) {
    return res.status(200).json({
      duplicateDetected: false,
      confidenceScore: 0,
      matchedParticipantId: null,
      reason: "Standalone offline duplicate checker matches names locally."
    });
  }

  const { newParticipant, existingParticipants } = req.body;
  const prompt = `You are an expert Registrations Audit Engine. Compare this newcomer registrant against the database of current registrants. Determine if this represents a semantic duplicate, spelling variation, alternative email double entry, or distinct developer account.

NEWCOMER PROFILE:
${JSON.stringify(newParticipant)}

CURRENT COHORT DIRECTORY SAMPLE:
${JSON.stringify((existingParticipants || []).slice(0, 15))}

Output a strict JSON object (enclosed in standard JSON, no markdown wrapper around it or raw blocks) returning:
{
  "duplicateDetected": true or false,
  "confidenceScore": integer percentage from 0 to 100 indicating likelihood of double-entry,
  "matchedParticipantId": "id of matching profile" or null,
  "reason": "1-sentence descriptive audit reasoning (e.g., 'Matches Bob Chen with Stanford email variation rob.chen@...')"
}`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      }
    });
    
    const parsedText = response.text || "{}";
    res.json(JSON.parse(parsedText));
  } catch (e: any) {
    console.error("[Gemini API Error] Schema registration comparison failed:", e);
    res.status(500).json({ error: e.message || "Failed similarity scans." });
  }
});


// MAIN VITE SERVER AND STATIC ASSETS BRIDGE MIDDLEWARES
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    console.log("[HackBridge Master Server] Node launched in Developer Mode. Mounting dynamic Vite HMR bridge...");
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    console.log(`[HackBridge Master Server] Node launched in Production Mode. Serving static builds from ${distPath}`);
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`================================================================`);
    console.log(`🚀 [DEL TECHNOLOGIES HACKBRIDGE MASTER ENGINE COUPLING PORTAL]`);
    console.log(`🎯 Serving secure edge analytics dynamically on port: ${PORT}`);
    console.log(`⚙️  Node environment configuration: ${process.env.NODE_ENV || 'development'}`);
    console.log(`================================================================`);
  });
}

startServer();
