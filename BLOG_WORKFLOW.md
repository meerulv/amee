# Blog Posts & Snippets Architecture & Workflow Guide

This document outlines how blog posts, case studies, and snippets are structured, edited, and published to GitHub Pages on [amee.my](https://amee.my).

---

## 1. Core Architecture Overview

Your portfolio is hosted on **GitHub Pages** as a static website. 

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Hosting** | GitHub Pages (`amee.my`) | Serves static HTML, CSS, JS from the `main` branch |
| **Manifest** | [`blog/posts/posts.json`](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/blog/posts/posts.json) | Registry of all active posts shown in the homepage workspace (starts clean as `[]`) |
| **Scaffolding** | [`blog/scaffolding-template.html`](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/blog/scaffolding-template.html) | Standard production-grade HTML layout for all new articles & snippets |
| **Visual Studio** | [`editor/index.html`](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/editor/index.html) | Local browser-based UI to draft, preview, and build files |
| **Local Backend** | [`server.py`](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/server.py) | Python daemon that handles file writing and manifest updates |
| **Historical Backups** | `_backups/` | Full backups of past legacy posts and data |

---

## 2. Directory Structure

```text
amee/
├── blog/
│   ├── index.html                 # Archive page
│   ├── scaffolding-template.html  # Base skeleton used to generate new posts
│   └── posts/
│       ├── posts.json             # Manifest loaded dynamically by Alpine.js
│       └── <your-post-slug>/      # Generated when you create a post in Studio
│           └── index.html         # Generated post using scaffolding-template
├── editor/
│   └── index.html                 # Visual Studio UI (http://localhost:8000/editor/)
├── _backups/                      # Safe archives of legacy posts and data
│   └── blog_20261003_191703/      # Preserved legacy case studies & snippets
├── index.html                     # Main interactive portfolio workspace
├── server.py                      # Local development & studio server
└── BLOG_WORKFLOW.md               # This documentation
```

---

## 3. How to Create Posts (Clean Slate Workflow)

### Step 1: Start the Local Studio Server
Run the local Python server manually in your terminal:
```bash
python3 server.py
```
Open your browser to:
👉 **[http://localhost:8000/editor/](http://localhost:8000/editor/)** (or click the **"Studio"** button in the top bar of the portfolio)

### Step 2: Write & Customize in the Studio
- **Set Metadata:**
  - **Type:** `case-study` (Architecture / Production Deep Dive) or `snippet` (Code Pattern / Quick Solution)
  - **Date:** `YYYY-MM-DD`
  - **Title & Slug:** Title will automatically generate the directory slug (e.g. `vetcheck-multiregion-cloud`)
  - **Impact Metrics:** Highlights shown in the verified metrics box (e.g. `Multi-Region AU & UK • ARM64 FrankenPHP • Sub-100ms Latency`)
  - **Excerpt:** Short 1–2 sentence description for the homepage feed
  - **Tags:** Comma-separated (e.g. `Laravel Octane, AWS, Redis, FrankenPHP`)
- **Format Content:**
  - Use the quick toolbar buttons:
    - `+ Section` — Generates a new `<h2>` and paragraph.
    - `+ Code Block` — Insets a syntax-highlighted dark container.
    - `+ Diagram` — Inserts a Mermaid.js diagram.
    - `+ Image` — Inserts responsive `<figure>` with `<img>` and `<figcaption>`.
    - `+ Video` — Inserts a responsive 16:9 `.video-container` (YouTube/Vimeo embed or `<video>` tag).
    - `+ URL Link` — Inserts styled outbound links with external arrows (`↗`).
  - Preview renders in real-time on the right column with exact production styling.

### Step 3: Save & Build Files
Click **"Save & Build File"**:
- Automatically creates `blog/posts/<slug>/index.html` based on `blog/scaffolding-template.html`.
- Automatically inserts or updates the post entry in `blog/posts/posts.json`.
- Automatically opens a full post preview modal for instant review.

### Step 4: Generate Threads Social Chain (1, 2, or 3-Part Engagement Posts)
Click the purple **`🧵 Threads`** button in the Studio top bar:
- **Choose Tone:**
  - **🇲🇾 Santai Tech BM (Default):** Natural Malaysian developer tone (*"Korang pernah tak deploy production pastu seram sejuk takut downtime atau queue stuck? 😅"*, *"Benda ni straight forward je sebenarnya, tak perlu over-engineer..."*, *"Jom sembang santai kat bawah 👇"*). Extremely relatable to Malaysian dev communities on Threads, inviting open comments, questions, and networking.
  - **🌐 English Tech:** Professional developer tone for international or corporate technical audiences.
- **Choose Chain Length:**
  - **1 Post:** Punchy single-post overview + open-ended discussion question + canonical link.
  - **2 Posts:** Part 1 (Hook & problem statement) → Part 2 (Simplified fix, complete link & Q&A prompt).
  - **3 Posts (Recommended):** Part 1 (The Problem & verified metrics) → Part 2 (Key technical decisions) → Part 3 (Link to full blueprint & interactive follower discussion starter).
- **Designed for Presence & Interaction:**
  - Concludes with real questions (*"Stack korang kat company biasa buat deployment macam mana? CI/CD tool apa korang pakai sekarang? Drop je kat replies!"*).
- **Per-Post Controls:**
  - Individual **`Copy`** button and **`Open in Threads ↗`** for each node in the chain.
  - One-click **`Copy Entire Chain`** to copy all formatted posts at once.
  - **`↻ Re-roll Style`** to alternate phrasing.

### Step 5: Preview in Homepage Workspace
Visit [http://localhost:8000/](http://localhost:8000/) to see your newly drafted post appear immediately in the main portfolio workspace and detail drawer.

---

## 4. How to Delete a Post

### Option A: From the Studio UI (Recommended)
1. In the Studio ([http://localhost:8000/editor/](http://localhost:8000/editor/)), select the post you want to remove from the **"Existing Entries"** sidebar on the left.
2. Click the red **"Delete Post"** button in the top bar.
3. Confirm the browser prompt.
4. The server automatically:
   - Removes the entry from [blog/posts/posts.json](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/blog/posts/posts.json).
   - Deletes the `blog/posts/<slug>/` folder.

### Option B: Manually
1. Remove the JSON block from [blog/posts/posts.json](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/blog/posts/posts.json).
2. Delete the directory: `rm -rf blog/posts/<slug>/`.

---

## 4. Deploying to GitHub Pages

GitHub Pages automatically builds and deploys whenever you push commits to the `main` branch.

```bash
# Check status of generated posts
git status

# Stage the new post folder and updated posts.json
git add blog/posts/

# Commit changes
git commit -m "feat(blog): add accurate case study for <project>"

# Push to your feature branch first to review:
git push origin feature/revamp

# Or when ready to go live on amee.my:
# git checkout main
# git merge feature/revamp
# git push origin main
```

> [!NOTE]
> Because GitHub Pages is purely static, `server.py` and the save API only run on your local machine. In production, only the generated static HTML files and `posts.json` are served.

---

## 5. Restoring or Referencing Backups

If you ever need to inspect or recover details from the old case studies or snippets:
- Look in [`_backups/blog_20261003_191703/posts/`](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/_backups/blog_20261003_191703/posts/)
- Available archived items:
  - `vetcheck-aws-multiregion-modernization/`
  - `accea-centralized-sso-platform/`
  - `ajakme-high-traffic-rsvp-architecture/`
  - `multi-file-uploads/`
  - `upgrading-ajakme/`
  - `posts.json`

---

## 6. Manual Scaffolding (Without Server)

If you ever want to create a post manually without running `server.py`:
1. Duplicate `blog/scaffolding-template.html` into a new folder:
   ```bash
   mkdir -p blog/posts/my-new-post
   cp blog/scaffolding-template.html blog/posts/my-new-post/index.html
   ```
2. Replace the template tokens:
   - `{{TITLE}}`, `{{CATEGORY}}`, `{{DATE}}`
   - `{{TYPE_LABEL}}` (`Case Study` or `Code Snippet`)
   - `{{BADGE_CLASS}}` (`bg-[#1f6feb]/20 text-[#58a6ff] border border-[#388bfd]/30`)
   - `{{CONTENT_HTML}}` (Your article content)
3. Add the entry to [`blog/posts/posts.json`](file:///Users/amee/Documents/Projects/Apps/Laravels/amee/blog/posts/posts.json):
   ```json
   {
     "folder": "my-new-post",
     "title": "My New Post Title",
     "type": "case-study",
     "date": "2026-10-03",
     "excerpt": "Brief summary of the architecture and outcomes...",
     "metrics": "Verified Impact • Key Results",
     "tags": ["Laravel", "AWS", "DevOps"],
     "draft": false
   }
   ```
