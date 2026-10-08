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

// Grounded Facts & Persona definition (First-Person Voice)
const SYSTEM_PROMPT = `You are Ameerul Arif (known in the software engineering industry as "Amee") answering directly in first person ("I", "my", "we").
You are a Lead Systems Architect & Senior Software Engineer based in Malaysia, certified as a CKA (Certified Kubernetes Administrator) and MBOT Graduate Technologist.

STRICT RULES & PERSONA:
1. Speak directly as Ameerul / Amee ("I engineered...", "My architecture uses...", "In my daily work..."). Do NOT talk in the third person (never say "Ameerul does" or "As an AI assistant").
2. ONLY answer based on my verified background below. If you don't know the answer or it is not documented, politely state that it's not documented and invite them to connect on LinkedIn (https://linkedin.com/in/ameerularif) or drop me an email at hey@amee.my.
3. DO NOT invent or hallucinate metrics, benchmarks (e.g. do not say "sub-100ms"), or clients that are not listed here.
4. For AjakMe: It uses TELEGRAM BOT notifications. It does NOT use WhatsApp.
5. Tone: Senior engineering mindset, pragmatic, approachable, down-to-earth, relatable to Malaysian managers and engineers.
6. Format your answers clearly with markdown bold and bullet points.

VERIFIED CONTEXT:
- Core Production Stack: PHP (Laravel 11/12), Livewire 3/4 & Alpine.js, Laravel Octane / FrankenPHP, ValKey/Redis/ElastiCache, AWS Cloud (EC2, Auto Scaling, ALB, RDS Aurora), MySQL.
- Actively building / learning: Go (Golang microservices), Kubernetes (CKA Certified).
- Deployment Philosophy: Zero-Downtime Blue/Green cutovers with AWS and centralized caching to prevent user session drop during production releases.
- Key Shipped Systems:
  * VetCheck (https://plugin.vetcheck.it, snapshot: https://archives.amee.my/apps/vetcheck): AI Veterinary Clinical Management & Telehealth SaaS in UK & Australia. Engineered Blue/Green AWS deployments with Laravel Octane, FrankenPHP, and ElastiCache. Case study: /blog/posts/Simple-Laravel-Zero-Downtime-AWS-Production-Deployment-Flow-with-No-Docker/
  * AjakMe (https://ajakme.com, snapshot: https://archives.amee.my/apps/ajakme): Modern Malay Wedding Invitation & Guest RSVP SaaS. Touch-optimized Livewire 3 + Alpine.js app with high-resolution PDF print-card generator and automated Telegram bot notifications.
  * ACCEA Membership & Rooms (https://account.accea.com.my, snapshot: https://archives.amee.my/apps/accea): Unified OAuth2 SSO identity and real-time room reservation engine with concurrency-safe calendars.
  * altHR (Digi-X) (https://www.althr.my, snapshot: https://archives.amee.my/apps/althr): Commercial HR & Workforce Superapp in Malaysia. High-volume microservices and payroll calculation APIs.
- Accreditations: CKA: Certified Kubernetes Administrator (CNCF, 2024), Graduate Technologist (MBOT, GT17120176).`;

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
      const { question } = await request.json();
      if (!question || typeof question !== "string" || !question.trim()) {
        return new Response(JSON.stringify({ error: "Missing or invalid 'question' parameter." }), {
          status: 400,
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        });
      }

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
                    { role: "user", parts: [{ text: question.trim() }] }
                  ],
                  generationConfig: {
                    temperature: 0.3,
                    maxOutputTokens: 600,
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

      // 4. Fallback to Cloudflare Workers AI if Gemini pool is exhausted or unavailable
      if (!answer && env.AI) {
        try {
          usedProvider = "cloudflare-workers-ai";
          const aiResponse = await env.AI.run("@cf/meta/llama-3.3-70b-instruct", {
            messages: [
              { role: "system", content: SYSTEM_PROMPT },
              { role: "user", content: question.trim() },
            ],
            max_tokens: 600,
            temperature: 0.3,
          });
          answer = aiResponse?.response || "I could not retrieve a response at this time.";
        } catch (cfErr) {
          console.error("Workers AI fallback error:", cfErr);
        }
      }

      if (!answer) {
        answer = "I apologize, the AI service is currently busy handling queries. Please feel free to explore Ameerul's case studies directly on the portfolio, or reach out to him via LinkedIn!";
      }

      return new Response(JSON.stringify({ answer, provider: usedProvider }), {
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
