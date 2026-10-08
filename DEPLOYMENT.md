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
                                           │ POST /api/chat
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
              │ Free Tier: 1,500 req/day  │   │ @cf/meta/llama-3.3-70b    │
              │ Multi-Key Auto-Rotation   │   │ 10,000 free neurons/day   │
              └───────────────────────────┘   └───────────────────────────┘
```

---

## Part 1: Deploy the Cloudflare Worker (AI Router)

The Cloudflare Worker safely holds your Google Gemini API key(s), rotates between them, handles automatic rollover on `429 (Rate Limit)` responses, and falls back to Cloudflare Workers AI if needed.

### 1. Prerequisites
- A free [Cloudflare](https://dash.cloudflare.com/) account.
- One or more free Google Gemini API Keys from [Google AI Studio](https://aistudio.google.com/).

### 2. Install Wrangler & Log In
From the root of your project directory, open your terminal:

```bash
cd worker
npm install -g wrangler   # or use npx wrangler
wrangler login
```
*(This opens a browser window for a one-click authorization into your Cloudflare account).*

### 3. Configure API Keys with Rotation
You can provide a single key or multiple keys separated by commas. The worker automatically rotates through them:

```bash
wrangler secret put GEMINI_API_KEYS
```
When prompted, paste your key(s):
```text
AIzaSyKeyOne...,AIzaSyKeyTwo...,AIzaSyKeyThree...
```

### 4. Deploy the Worker
Run the deployment command:

```bash
wrangler deploy
```

Once deployed, Cloudflare will output your public endpoint URL:
```text
Published amee-ai-router (1.23 sec)
  https://amee-ai-router.<your-subdomain>.workers.dev
```

### 5. Link Custom Domain (Optional)
If you manage `amee.my` in Cloudflare:
1. Go to **Cloudflare Dashboard** > **Workers & Pages** > **amee-ai-router** > **Settings** > **Triggers**.
2. Click **Add Custom Domain** and enter `ai.amee.my`.

---

## Part 2: Connect Frontend to Your Deployed Worker

In `assets/js/app.js` (or in `index.html`), configure the AI endpoint to point to your live Cloudflare Worker URL when running in production:

```javascript
// In index.html (askAi method):
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const aiEndpoint = isLocal 
  ? '/api/chat' 
  : 'https://amee-ai-router.<your-subdomain>.workers.dev'; // or https://ai.amee.my
```

*(Note: If the network request ever fails or is blocked, the frontend automatically falls back to clean, client-side grounded facts, ensuring the UI never breaks).*

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
