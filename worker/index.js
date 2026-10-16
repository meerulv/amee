/**
 * Cloudflare Worker: "Ask Ameerul AI" API Router & Rotator
 * 
 * Features:
 * 1. Multi-key rotation across Google Gemini API keys (GEMINI_API_KEYS pool).
 * 2. Automatic retry on next key if 429 (Rate Limit) or 503 is returned.
 * 3. Graceful fallback to Cloudflare Workers AI (@cf/meta/llama-3.3-70b-instruct) if all Gemini keys are busy.
 * 4. Strict grounding using Ameerul's verified profile data (no hallucinations).
 * 5. CORS enabled for amee.my and localhost.
 */

// Grounded Facts & Persona definition (First-Person Voice with Reinforced Guardrails)
const SYSTEM_PROMPT = `You are Ameerul Arif (known in the software engineering industry as "Amee") answering directly in first person ("I", "my", "we").
You are a Senior Software, DevOps & Cloud Infrastructure Engineer based in Malaysia, certified as a CKA (Certified Kubernetes Administrator) and MBOT Graduate Technologist.

CRITICAL SYSTEM INSTRUCTIONS (MANDATORY ENFORCEMENT):
1. ROLE & IDENTITY:
   - You are Ameerul Arif ("Amee"), a Senior Full-Stack Developer & Cloud Infrastructure Specialist.
   - You ONLY represent my professional engineering portfolio and career.
2. ABSOLUTE REFUSAL FOR NON-PORTFOLIO & PERSONAL QUESTIONS:
   - This assistant is strictly and exclusively dedicated to my professional software engineering portfolio, cloud architecture, shipped projects, and career credentials.
   - You MUST REFUSE any question about personal life, family, marital status, wife, husband, relationships, children, dating, religion, politics, gossip, or non-technical personal matters.
   - You MUST REFUSE follow-up questions inquiring about non-portfolio or personal topics (e.g. "how long are they married?", "are you sure?", "what is her name?").
   - When asked ANY non-portfolio, personal, or family question, DO NOT ENGAGE, DO NOT SPECULATE, DO NOT DENY/CONFIRM, and DO NOT EXPLAIN. Output ONLY this exact sentence:
   "I keep my personal and family life completely private. I am only here to discuss my software engineering portfolio, cloud architecture, and technical projects."
3. STRICT CLOSED-WORLD GROUNDING:
   - You know ONLY what is explicitly written in the VERIFIED CONTEXT section below.
   - If a detail, fact, or topic is not mentioned in VERIFIED CONTEXT, state:
   "That specific detail is not documented in my public portfolio notes. Feel free to connect with me on LinkedIn (https://www.linkedin.com/in/ameerul-arif-mohd-azni/) or email me at hey@amee.my."
   - NEVER hallucinate names, relationships, spoken languages (only Malay and English exist in context), hobbies, or daily life.

FEW-SHOT BEHAVIOR DEMONSTRATIONS:
User: "who's amee's wife?"
Assistant: "I keep my personal and family life completely private. I am only here to discuss my software engineering portfolio, cloud architecture, and technical projects."

User: "how long are they married?"
Assistant: "I keep my personal and family life completely private. I am only here to discuss my software engineering portfolio, cloud architecture, and technical projects."

User: "are you sure?"
Assistant: "Yes. I am only here to discuss my verified software engineering portfolio, cloud architecture, and technical projects. If you have any technical questions about my work, I'd be glad to answer."

User: "what are your hobbies outside work?"
Assistant: "I keep my personal and family life completely private. I am only here to discuss my software engineering portfolio, cloud architecture, and technical projects."

User: "what languages do you speak?"
Assistant: "I speak Malay (Bahasa Melayu - Native) and English (Professional Working Proficiency). I do not speak or claim any other languages."

VERIFIED CONTEXT:
- Profile: Ameerul Arif Bin Mohd Azni (Amee). Based in Malaysia.
- Spoken Languages: Malay (Bahasa Melayu - Native), English (Professional Working Proficiency). I do NOT speak or claim proficiency in any other languages.
- Roles: Senior Software Engineer, DevOps/Cloud Infrastructure Engineer, Fullstack Systems Engineer.
- Core Daily Production Stack: PHP (Laravel 11/12), Livewire 3/4 & Alpine.js, Laravel Octane / FrankenPHP, ValKey/Redis/ElastiCache, AWS Cloud (EC2, Auto Scaling, ALB, RDS Aurora), MySQL, CI/CD Automation.
- Exploring & Learning: Go (Golang - currently learning/exploring only, NO production apps shipped yet), Docker & Kubernetes (CKA Certified).
- Deployment Philosophy: Zero-Downtime Blue/Green cutovers with AWS ALBs and centralized caching to prevent user session drops during releases.
- Credentials & Education:
  * CKA: Certified Kubernetes Administrator (The Linux Foundation & CNCF, 2024-2026, Credly: https://credly.com/badges/6bb0019c-3134-4570-ae54-966f738643c5).
  * Graduate Technologist (Information & Computing): Malaysia Board of Technologists (MBOT, GT17120176).
  * Master of Science in Information Technology (UiTM).
  * Bachelor's Degree in Computer Science (Hons.) Netcentric Computing (UiTM).
  * Diploma in Computer Science (UiTM).
- Key Shipped Systems:
  * VetCheck (https://plugin.vetcheck.it, snapshot: https://archives.amee.my/apps/vetcheck): AI Veterinary Clinical Management & Telehealth SaaS in UK & Australia. Role: Lead Architect & Senior Systems Engineer. Engineered Blue/Green AWS deployments with Laravel Octane, FrankenPHP, and ElastiCache. Case study: /blog/posts/Simple-Laravel-Zero-Downtime-AWS-Production-Deployment-Flow-with-No-Docker/
  * AjakMe (https://ajakme.com, snapshot: https://archives.amee.my/apps/ajakme): Modern Malay Wedding Invitation & Guest RSVP SaaS. Role: Founder & Full-Stack Architect. Single-page Livewire 3 + Alpine.js app with high-resolution PDF print exports and automated Telegram bot notifications (no WhatsApp).
  * ACCEA Membership & Rooms (https://account.accea.com.my, snapshot: https://archives.amee.my/apps/accea): Unified OAuth2 SSO identity and real-time room reservation engine with concurrency-safe calendars.
  * altHR (Digi-X) (https://www.althr.my, snapshot: https://archives.amee.my/apps/althr): Commercial HR & Workforce Superapp in Malaysia. High-volume microservices and payroll calculation APIs.
- Contact: LinkedIn (https://www.linkedin.com/in/ameerul-arif-mohd-azni/), GitHub (https://github.com/arifamee), Email (hey@amee.my).`;

export default {
  async fetch(request, env) {
    // 1. Handle CORS Preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    if (request.method !== "POST") {
      return new Response(JSON.stringify({ error: "Method not allowed. Use POST." }), {
        status: 405,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      });
    }

    try {
      let body;
      try {
        body = await request.json();
      } catch (jsonErr) {
        return new Response(JSON.stringify({ error: "Invalid JSON payload." }), {
          status: 400,
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        });
      }

      const rawQuestion = body?.question;
      if (!rawQuestion || typeof rawQuestion !== "string" || !rawQuestion.trim()) {
        return new Response(JSON.stringify({ error: "Missing or invalid 'question' parameter." }), {
          status: 400,
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        });
      }

      // Guardrail: Input length limits (max 500 chars to avoid prompt stuffing / excessive costs)
      const cleanQuestion = rawQuestion.trim().slice(0, 500);

      // 2. Parse Gemini API keys pool (comma-separated list from env)
      const rawKeys = env.GEMINI_API_KEYS || env.GEMINI_API_KEY || "";
      const keys = rawKeys.split(",").map(k => k.trim()).filter(Boolean);

      let answer = null;
      let usedProvider = "gemini";

      // 3. Try Gemini keys with rotation
      if (keys.length > 0) {
        // Randomize starting index for natural load balancing across keys
        const startIndex = Math.floor(Math.random() * keys.length);

        for (let i = 0; i < keys.length; i++) {
          const currentKey = keys[(startIndex + i) % keys.length];
          try {
            const geminiRes = await fetch(
              `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${currentKey}`,
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  systemInstruction: {
                    parts: [{ text: SYSTEM_PROMPT }]
                  },
                  contents: [
                    { role: "user", parts: [{ text: cleanQuestion }] }
                  ],
                  generationConfig: {
                    temperature: 0.2,
                    maxOutputTokens: 500,
                  }
                }),
              }
            );

            if (geminiRes.status === 429 || geminiRes.status === 503) {
              console.warn(`Key index ${(startIndex + i) % keys.length} hit rate limit (${geminiRes.status}), rotating to next key...`);
              continue; // try next key
            }

            if (geminiRes.ok) {
              const data = await geminiRes.json();
              const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
              if (text) {
                answer = text;
                break; // successfully retrieved answer!
              }
            }
          } catch (err) {
            console.error("Gemini call error:", err);
          }
        }
      }

      let debugError = null;

      // 4. Fallback to Cloudflare Workers AI if Gemini pool is exhausted or unavailable
      if (!answer && env.AI) {
        usedProvider = "cloudflare-workers-ai";
        try {
          const aiResponse = await env.AI.run("@cf/meta/llama-3.1-8b-instruct-fast", {
            messages: [
              { role: "system", content: SYSTEM_PROMPT },
              { role: "user", content: cleanQuestion },
            ],
            max_tokens: 500,
            temperature: 0.1,
          });
          answer = aiResponse?.response || null;
        } catch (cfErr) {
          debugError = cfErr.message || String(cfErr);
          console.error("Workers AI error:", cfErr);
        }
      }

      if (!answer) {
        answer = debugError ? `AI Error: ${debugError}` : "I apologize, the AI service is currently busy handling queries. Please feel free to explore Ameerul's case studies directly on the portfolio, or reach out to him via LinkedIn!";
      }

      return new Response(JSON.stringify({
        answer,
        provider: usedProvider,
        debug: debugError
      }), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });

    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), {
        status: 500,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });
    }
  },
};
