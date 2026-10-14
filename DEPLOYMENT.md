# Deployment Guide: Ameerul Portfolio & "Ask Architecture AI"

This guide outlines how to deploy **amee.my** on **100% Free GitHub Pages** and connect the **"Ask Architecture AI"** Cloudflare Worker with key rotation and zero-cost failovers.

---

## Architecture Overview

```
                      ┌──────────────────────────────────────────┐
                      │    1. Static Portfolio (amee.my)         │
                      │    Hosted on: GitHub Pages (100% Free)   │
                      └────────────────────┬─────────────────────┘
                                           │
                                           │ POST /api/chat (or https://ai.amee.my/chat)
                                           ▼
                      ┌──────────────────────────────────────────┐
                      │    2. AI Router (Cloudflare Worker)      │
                      │    Free Tier: 100,000 req/day            │
                      └─────────────┬──────────────────┬─────────┘
                                    │                  │
                (Primary Key Pool)  │                  │ (Fallback)
                                    ▼                  ▼
              ┌───────────────────────────┐   ┌───────────────────────────┐
              │ Google Gemini 2.0 Flash   │   │ Cloudflare Workers AI     │
              │ Free Tier: 1,500 req/day  │   │ @cf/meta/llama-3.1-8b     │
              │ Multi-Key Auto-Rotation   │   │ 10,000 free neurons/day   │
              └───────────────────────────┘   └───────────────────────────┘
```

---

## 🚦 Deployment Decision Matrix: When to Deploy What?

| What Did You Change? | Files Involved | Where & How to Deploy |
| :--- | :--- | :--- |
| **Worker AI logic / Prompts** | `worker/index.js`, `worker/wrangler.toml` | **Deploy to Cloudflare:**<br>`cd worker && npx wrangler deploy` |
| **API Keys / Secrets** | `GEMINI_API_KEYS` in Cloudflare | **Update via Wrangler CLI:**<br>`cd worker && wrangler secret put GEMINI_API_KEYS` |
| **Portfolio Frontend / HTML / CSS** | `index.html`, `assets/`, `blog/`, `projects/` | **Deploy to GitHub Pages:**<br>`git add . && git commit -m "..." && git push origin main` |
| **Local dev server / Studio** | `server.py`, `editor/` | **Zero deploy needed:**<br>Restart your local `python3 server.py` process. |

> [!IMPORTANT]
> **Cloudflare Worker vs GitHub Pages separation:**
> GitHub Pages only hosts static client files (`index.html`, CSS, JS). It does **not** run or compile the Cloudflare Worker. Any changes to `worker/index.js` or system prompts must be deployed via `npx wrangler deploy` from inside the `worker` directory.

---

## 🛡️ Dynamic AI Guardrails Architecture

The AI guardrail architecture follows a **zero-hardcoding, closed-world principle**:

1. **Single Source of Truth (`data/ameerul-context.json`):**
   - Verified engineering systems, roles, certifications (CKA, MBOT), and spoken languages (Malay native, English professional).
   - Any updates in `ameerul-context.json` automatically inform both the local server and the edge router.
2. **Closed-World Grounding (Zero Hallucination):**
   - The model is instructed under a strict closed-world constraint. It cannot extrapolate, speculate, or draw from outside world trivia to fabricate personal details (no invented languages like Japanese/Arabic, no fictional hobbies, no fake SLAs or benchmarks).
   - Unverified attributes produce an honest acknowledgment:
     > *"That specific detail is not documented in my public portfolio notes. Feel free to connect with me on LinkedIn or email me at hey@amee.my."*
3. **Semantic Scope & Personal Privacy Boundary:**
   - The system is restricted strictly to Ameerul's professional software engineering, cloud architecture, and systems engineering career.
   - Non-technical questions and personal/family/romantic life inquiries are naturally rejected by the model rather than relying on brittle, hardcoded keyword blocklists.
4. **Input Length Bounding:**
   - User inputs are capped at 500 characters to prevent prompt stuffing and excess token consumption.

---

## Part 1: Deploy the Cloudflare Worker (AI Router)

The Cloudflare Worker safely holds your Google Gemini API key(s), rotates between them, handles automatic rollover on `429 (Rate Limit)` responses, and falls back to Cloudflare Workers AI if needed.

### 1. How to Get Your Free Google Gemini API Keys

Google gives developers **1,500 requests per day 100% free** for Gemini 2.0 Flash.

1. Go to **[Google AI Studio](https://aistudio.google.com/)** and sign in with your Google account.
2. In the left navigation menu or top bar, click the blue button **"Get API key"** (or visit direct URL: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)).
3. Click **"Create API key"**.
4. Choose either:
   - **"Create API key in new project"** (easiest, Google creates a default project for you).
   - Or select an existing Google Cloud project if you have one.
5. Copy the generated key (starts with `AIzaSy...`).
6. *(Optional for Rotation)*: If you want extra rate-limit headroom, you can create a 2nd or 3rd key across different projects. The worker will automatically load-balance and rotate between them!

---

### 2. Prerequisites & Accounts
- A free [Cloudflare](https://dash.cloudflare.com/) account (Free plan includes 100,000 worker requests/day).
- The Gemini API Key(s) obtained from the steps above.

### 3. Install Wrangler & Log In
From the root of your project directory, open your terminal:

```bash
cd worker
npm install -g wrangler   # or use npx wrangler
wrangler login
```
*(This opens a browser window for a one-click authorization into your Cloudflare account).*

### 4. Configure API Keys with Rotation in Cloudflare Secrets
You can provide a single key or multiple keys separated by commas. The worker automatically rotates through them:

```bash
wrangler secret put GEMINI_API_KEYS
```
When prompted, paste your key(s):
```text
AIzaSyKeyOne...,AIzaSyKeyTwo...,AIzaSyKeyThree...
```

### 5. Deploy the Worker
Run the deployment command:

```bash
cd worker
npx wrangler deploy
```

> [!IMPORTANT]
> Make sure you are inside the **`worker`** directory (`cd worker`). If you run `wrangler deploy` from the root directory, Wrangler won't find `wrangler.toml` and will mistakenly prompt you with interactive questions (framework, project name, etc.).

Once deployed, Cloudflare will output your public endpoint URL:
```text
Published amee-ai-router (1.23 sec)
  https://amee-ai-router.<your-subdomain>.workers.dev
```

### 6. Connecting Your Worker to Frontend: Two Options

After running `wrangler deploy`, you can connect your frontend using either **Option A** or **Option B**:

---

#### 🅰️ Option A: Free `*.workers.dev` Subdomain (Easiest — Zero DNS setup)
Cloudflare automatically gives every worker a free public URL on deploy:
```text
https://amee-ai-router.<your-cloudflare-subdomain>.workers.dev
```
- **How to use**: No DNS or domain verification needed. Works immediately.
- **In [index.html](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/index.html)**: Simply update your endpoint:
  ```javascript
  const endpoint = isLocal 
    ? '/api/chat' 
    : 'https://amee-ai-router.<your-cloudflare-subdomain>.workers.dev';
  ```

---

#### 🅱️ Option B: Clean Custom Domain `ai.amee.my` (Recommended & Professional)
If your root domain `amee.my` is already added to Cloudflare (or nameservers pointed to Cloudflare):

1. Open your [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Navigate to: **Workers & Pages** ➔ **`amee-ai-router`** ➔ **Settings** ➔ **Domains & Routes** (or **Triggers**).
3. Click **Add** ➔ Select **Custom Domain**.
4. Type:
   ```text
   ai.amee.my
   ```
5. Click **Add Custom Domain**.
   - Cloudflare automatically provisions a free SSL/TLS certificate and creates the DNS record for you.
6. **In [index.html](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/index.html)**:
   The code is already pre-configured to hit `https://ai.amee.my/chat`:
   ```javascript
   const endpoint = isLocal ? '/api/chat' : 'https://ai.amee.my/chat';
   ```

---

## Part 2: Connect Frontend to Your Deployed Worker

In [index.html](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/index.html) (inside the `askAi` method):

```javascript
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// Switch between Option A or Option B:
const endpoint = isLocal 
  ? '/api/chat' 
  : 'https://ai.amee.my/chat'; // Option B (or use https://amee-ai-router.<subdomain>.workers.dev for Option A)
```

> [!NOTE]
> **Built-in Offline Fallback:** If the network request ever fails or the worker is temporarily unreachable, the frontend automatically falls back to client-side grounded answers so the UI never shows an error to your guests.

---

## Part 3: Deploy Portfolio to GitHub Pages

Because **amee.my** is a clean, static site (HTML, Vanilla CSS, Alpine.js), it deploys directly onto GitHub Pages for free.

### 1. Repository Setup
1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: add project showcases and Ask Architecture AI system"
   git push origin main
   ```

### 2. Enable GitHub Pages
1. In your GitHub repository, navigate to **Settings** > **Pages**.
2. Under **Build and deployment**:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main` / folder: `/ (root)`
3. Under **Custom domain**:
   - Enter `amee.my`.
   - Ensure **Enforce HTTPS** is checked.

### 3. Verify DNS Records (Cloudflare / Registrar)
Ensure your DNS records point to GitHub Pages:
- **Apex domain (`amee.my`)**:
  - `185.199.108.153` (A)
  - `185.199.109.153` (A)
  - `185.199.110.153` (A)
  - `185.199.111.153` (A)
- **CNAME (`www.amee.my`)**:
  - `<your-username>.github.io`

---

## Part 4: Local Development & Studio Testing

When running locally on your machine:
```bash
python3 server.py
```
- Portfolio UI: `http://localhost:8000/`
- Visual Studio Editor: `http://localhost:8000/editor/`
- Local AI Endpoint: `http://localhost:8000/api/chat` (Supported directly by `server.py` with multi-key rotation).

To test local Gemini queries without Cloudflare, simply export your key before running:
```bash
export GEMINI_API_KEYS="AIzaSyKey1...,AIzaSyKey2..."
python3 server.py
```

---

## Summary of Costs

| Service | Component | Monthly Cost |
| :--- | :--- | :--- |
| **GitHub Pages** | Static Website Hosting & CDN | **RM 0.00** |
| **Cloudflare Workers** | Reverse Proxy & AI Router (100k req/day) | **RM 0.00** |
| **Google AI Studio** | Gemini 2.0 Flash (1,500 req/day per key) | **RM 0.00** |
| **Cloudflare Workers AI** | Llama 3.3 70B Fallback (10k neurons/day) | **RM 0.00** |
| **Total Operating Cost** | | **RM 0.00 / month** |
