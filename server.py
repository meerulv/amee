#!/usr/bin/env python3
"""
Local Post & Snippet Manager Server for Ameerul Arif's Portfolio.
Provides:
- Web-based Visual Editor (UI/UX) at http://localhost:8000/editor/
- Automatic generation of clean, styled index.html based on scaffolding
- Real-time updates to blog/posts/posts.json
- Static file serving for the portfolio
"""

import http.server
import socketserver
import json
import os
import re
import shutil
from urllib.parse import urlparse

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_JSON_PATH = os.path.join(BASE_DIR, "blog", "posts", "posts.json")
SHOWCASES_JSON_PATH = os.path.join(BASE_DIR, "projects", "showcases.json")
POSTS_DIR = os.path.join(BASE_DIR, "blog", "posts")
SCAFFOLDING_PATH = os.path.join(BASE_DIR, "blog", "scaffolding-template.html")

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def generate_seo_assets():
    """Generates sitemap.xml and robots.txt dynamically with all published posts."""
    try:
        with open(POSTS_JSON_PATH, "r", encoding="utf-8") as f:
            posts = json.load(f)
    except Exception:
        posts = []

    # 1. Generate sitemap.xml
    urls = [
        ("https://amee.my/", "1.0", "weekly"),
    ]
    for p in posts:
        if not p.get("draft", False) and not p.get("hidden", False) and not p.get("hide", False):
            folder = p.get("folder", "")
            date = p.get("date", "")
            if folder:
                urls.append((f"https://amee.my/blog/posts/{folder}/", "0.8", "monthly", date))

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for item in urls:
        loc = item[0]
        priority = item[1]
        changefreq = item[2]
        lastmod = item[3] if len(item) > 3 and item[3] else None
        
        sitemap_lines.append("  <url>")
        sitemap_lines.append(f"    <loc>{loc}</loc>")
        if lastmod:
            sitemap_lines.append(f"    <lastmod>{lastmod}</lastmod>")
        sitemap_lines.append(f"    <changefreq>{changefreq}</changefreq>")
        sitemap_lines.append(f"    <priority>{priority}</priority>")
        sitemap_lines.append("  </url>")
    sitemap_lines.append("</urlset>")

    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_lines) + "\n")

    # 2. Generate robots.txt with AI bot declarations
    robots_content = """# robots.txt for amee.my
User-agent: *
Allow: /
Disallow: /editor/
Disallow: /_backups/

# Allow & welcome AI Search & Answer Engines
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Applebot
Allow: /

Sitemap: https://amee.my/sitemap.xml
"""
    robots_path = os.path.join(BASE_DIR, "robots.txt")
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(robots_content)


def build_post_html(data):
    """Generates the static index.html using the scaffolding template."""
    with open(SCAFFOLDING_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    is_case_study = data.get('type') == 'case-study'
    type_label = "Case Study" if is_case_study else ("Code Snippet" if data.get('type') == 'snippet' else "Technical Article")
    badge_class = "bg-[#1f6feb]/20 text-[#58a6ff] border border-[#388bfd]/30" if is_case_study else "bg-[#238636]/20 text-[#3fb950] border border-[#2ea043]/30"

    # Tags HTML
    tags = data.get('tags', [])
    tags_html = " ".join([
        f'<span class="mono text-[11px] bg-[#161b22] border border-[#30363d] text-[#8b949e] px-2 py-0.5 rounded">{tag}</span>'
        for tag in tags
    ])

    # Metric bar
    metrics = data.get('metrics', '')
    metric_bar = ""
    if metrics:
        metric_bar = f"""
      <div class="p-3 bg-[#161b22] border border-emerald-500/30 rounded mb-6">
        <div class="mono text-[10px] text-emerald-400 font-bold uppercase tracking-wider mb-1">Key Impact Verified</div>
        <div class="mono text-xs sm:text-sm text-emerald-300 font-semibold">{metrics}</div>
      </div>
        """

    # Mermaid check
    mermaid_script = ""
    if "<pre class=\"mermaid\"" in data.get('content_html', '') or "graph " in data.get('content_html', ''):
        mermaid_script = """  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>\n  <script>mermaid.initialize({ startOnLoad: true, theme: 'dark' });</script>"""

    # Replace placeholders
    html = template
    html = html.replace("{{TITLE}}", data.get('title', 'Untitled'))
    html = html.replace("{{TYPE_LABEL}}", type_label)
    html = html.replace("{{BADGE_CLASS}}", badge_class)
    html = html.replace("{{CATEGORY}}", data.get('category', 'Engineering Blueprint & Architecture'))
    html = html.replace("{{METRIC_BAR}}", metric_bar)
    html = html.replace("{{DATE}}", data.get('date', ''))
    html = html.replace("{{TAGS_HTML}}", tags_html)
    html = html.replace("{{TAGS_JSON}}", json.dumps(tags))
    html = html.replace("{{FOLDER}}", data.get('folder', ''))
    html = html.replace("{{EXCERPT}}", data.get('excerpt', 'Technical architecture and engineering notes.'))
    html = html.replace("{{CONTENT_HTML}}", data.get('content_html', ''))
    html = html.replace("{{MERMAID_SCRIPT}}", mermaid_script)

    return html

class PortfolioRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Disable browser caching for live editing
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/editor" or parsed.path == "/editor/":
            self.path = "/editor/index.html"
            return super().do_GET()
        
        if parsed.path == "/api/posts":
            try:
                with open(POSTS_JSON_PATH, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if parsed.path == "/api/showcases":
            try:
                with open(SHOWCASES_JSON_PATH, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if parsed.path.startswith("/api/post/"):
            folder = parsed.path.replace("/api/post/", "").strip("/")
            file_path = os.path.join(POSTS_DIR, folder, "index.html")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_html = f.read()
                # Extract article content
                match = re.search(r'<article class="prose max-w-none text-\[#c9d1d9\] leading-relaxed">(.*?)</article>', raw_html, re.DOTALL)
                content_html = match.group(1).strip() if match else ""
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"folder": folder, "content_html": content_html}).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Post not found"}).encode("utf-8"))
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/save-post":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_body)
                title = (data.get('title') or '').strip()
                folder = (data.get('folder') or '').strip() or slugify(title)
                post_type = data.get('type') or 'case-study'
                date_str = (data.get('date') or '').strip()
                excerpt = (data.get('excerpt') or '').strip()
                metrics = (data.get('metrics') or '').strip()
                tags = [str(t).strip() for t in (data.get('tags') or []) if str(t).strip()]
                draft = bool(data.get('draft', False))
                content_html = data.get('content_html') or ''

                # 1. Update/Add entry in posts.json
                with open(POSTS_JSON_PATH, "r", encoding="utf-8") as f:
                    posts = json.load(f)

                post_entry = {
                    "folder": folder,
                    "title": title,
                    "type": post_type,
                    "date": date_str,
                    "category": (data.get('category') or '').strip(),
                    "excerpt": excerpt,
                    "metrics": metrics,
                    "tags": tags,
                    "draft": draft,
                    "hidden": bool(data.get('hidden', False))
                }

                existing_idx = next((i for i, p in enumerate(posts) if p.get('folder') == folder), None)
                if existing_idx is not None:
                    posts[existing_idx] = post_entry
                else:
                    posts.insert(0, post_entry)

                with open(POSTS_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(posts, f, indent=2)

                # 2. Create folder and generate index.html
                target_folder = os.path.join(POSTS_DIR, folder)
                os.makedirs(target_folder, exist_ok=True)
                full_html = build_post_html(data)
                
                with open(os.path.join(target_folder, "index.html"), "w", encoding="utf-8") as f:
                    f.write(full_html)

                # 3. Regenerate sitemap.xml and robots.txt
                generate_seo_assets()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "folder": folder,
                    "url": f"/blog/posts/{folder}/",
                    "message": f"Successfully created/updated post in {folder}/"
                }).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            return

        if parsed.path == "/api/delete-post":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_body)
                folder = data.get('folder', '').strip()
                if not folder:
                    raise ValueError("Post folder is required to delete.")

                # 1. Remove from posts.json
                with open(POSTS_JSON_PATH, "r", encoding="utf-8") as f:
                    posts = json.load(f)

                posts = [p for p in posts if p.get('folder') != folder]

                with open(POSTS_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(posts, f, indent=2)

                # 2. Delete post directory
                target_folder = os.path.join(POSTS_DIR, folder)
                if os.path.exists(target_folder):
                    shutil.rmtree(target_folder)

                # 3. Regenerate sitemap.xml and robots.txt
                generate_seo_assets()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "folder": folder,
                    "message": f"Successfully deleted post {folder}"
                }).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            return

        if parsed.path == "/api/save-showcase":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_body)
                showcase_id = (data.get('id') or '').strip() or slugify(data.get('name') or 'project')
                name = (data.get('name') or '').strip()
                tagline = (data.get('tagline') or '').strip()
                category = (data.get('category') or '').strip()
                role = (data.get('role') or '').strip()
                badge = (data.get('badge') or 'Active Production').strip()
                badgeColor = (data.get('badgeColor') or 'emerald').strip()
                image = (data.get('image') or '').strip()
                problem = (data.get('problem') or '').strip()
                solution = (data.get('solution') or '').strip()
                metrics = (data.get('metrics') or '').strip()
                stack = [str(s).strip() for s in (data.get('stack') or []) if str(s).strip()]
                liveUrl = (data.get('liveUrl') or '').strip()
                snapshotUrl = (data.get('snapshotUrl') or '').strip()
                relatedPost = (data.get('relatedPost') or '').strip()

                try:
                    with open(SHOWCASES_JSON_PATH, "r", encoding="utf-8") as f:
                        showcases = json.load(f)
                except Exception:
                    showcases = []

                entry = {
                    "id": showcase_id,
                    "name": name,
                    "tagline": tagline,
                    "category": category,
                    "role": role,
                    "badge": badge,
                    "badgeColor": badgeColor,
                    "image": image,
                    "problem": problem,
                    "solution": solution,
                    "metrics": metrics,
                    "stack": stack,
                    "liveUrl": liveUrl,
                    "snapshotUrl": snapshotUrl,
                    "relatedPost": relatedPost,
                    "hidden": bool(data.get('hidden', False))
                }

                existing_idx = next((i for i, s in enumerate(showcases) if s.get('id') == showcase_id), None)
                if existing_idx is not None:
                    showcases[existing_idx] = entry
                else:
                    showcases.append(entry)

                with open(SHOWCASES_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(showcases, f, indent=2)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "id": showcase_id,
                    "message": f"Successfully saved showcase for {name}"
                }).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            return

        if parsed.path == "/api/delete-showcase":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_body)
                showcase_id = data.get('id', '').strip()
                if not showcase_id:
                    raise ValueError("Showcase ID is required.")

                try:
                    with open(SHOWCASES_JSON_PATH, "r", encoding="utf-8") as f:
                        showcases = json.load(f)
                except Exception:
                    showcases = []

                showcases = [s for s in showcases if s.get('id') != showcase_id]

                with open(SHOWCASES_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(showcases, f, indent=2)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "id": showcase_id,
                    "message": f"Successfully deleted showcase {showcase_id}"
                }).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            return

        if parsed.path == "/api/chat":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length).decode('utf-8')
            try:
                import urllib.request
                import random
                req_data = json.loads(post_body)
                question = req_data.get('question', '').strip()

                if not question:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Empty question"}).encode("utf-8"))
                    return

                # Load context facts
                context_path = os.path.join(BASE_DIR, "data", "ameerul-context.json")
                facts_text = ""
                if os.path.exists(context_path):
                    with open(context_path, "r", encoding="utf-8") as f:
                        facts_text = f.read()

                system_prompt = f"""You are Ameerul Arif (known as "Amee" in the software engineering industry) responding directly in first person ("I", "my", "we").
You are a Lead Systems Architect & Senior Software Engineer based in Malaysia, certified as CKA (Certified Kubernetes Administrator) and MBOT Graduate Technologist.

STRICT RULES & PERSONA:
1. Speak directly as Ameerul / Amee ("I engineered...", "My architecture uses...", "In my daily work..."). Do NOT talk in the third person (never say "Ameerul does" or "As an AI assistant").
2. ONLY answer using my verified facts below. If something is not covered, politely state that it's not documented here and invite them to connect with me on LinkedIn (https://www.linkedin.com/in/ameerul-arif-mohd-azni/) or drop me an email at hey@amee.my.
3. DO NOT invent or hallucinate metrics or benchmarks (e.g., do not claim sub-100ms unless verified).
4. AjakMe uses TELEGRAM BOT notifications. It does NOT use WhatsApp.
5. Tone: Pragmatic, direct, approachable, senior engineering mindset, grounded in real production systems.

VERIFIED FACTS:
{facts_text}"""

                # Check for Gemini API keys in environment
                gemini_keys_env = os.environ.get("GEMINI_API_KEYS", os.environ.get("GEMINI_API_KEY", ""))
                keys = [k.strip() for k in gemini_keys_env.split(",") if k.strip()]

                answer = None
                used_provider = "gemini"

                if keys:
                    start_idx = random.randint(0, len(keys) - 1)
                    for i in range(len(keys)):
                        current_key = keys[(start_idx + i) % len(keys)]
                        try:
                            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={current_key}"
                            payload = json.dumps({
                                "systemInstruction": {"parts": [{"text": system_prompt}]},
                                "contents": [{"role": "user", "parts": [{"text": question}]}],
                                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600}
                            }).encode("utf-8")

                            req = urllib.request.Request(gemini_url, data=payload, headers={"Content-Type": "application/json"})
                            with urllib.request.urlopen(req, timeout=10) as resp:
                                resp_data = json.loads(resp.read().decode("utf-8"))
                                text = resp_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
                                if text:
                                    answer = text
                                    break
                        except Exception as gemini_err:
                            continue

                if not answer:
                    # Grounded local fallback matching queries if no external key is active yet (First-Person)
                    q_lower = question.lower()
                    if "vetcheck" in q_lower or "veterinary" in q_lower:
                        answer = "I serve as **Lead Architect & Senior Systems Engineer** for **VetCheck**, an AI Veterinary Clinical Management & Telehealth SaaS in the UK & Australia.\n\nI engineered an automated **Blue/Green deployment pipeline on AWS** using Laravel Octane, FrankenPHP, and centralized ElastiCache (Redis/ValKey), ensuring continuous uptime and seamless cutovers during busy clinic consultation hours without disrupting appointments."
                    elif "ajakme" in q_lower or "wedding" in q_lower or "telegram" in q_lower:
                        answer = "I founded and architected **AjakMe**, a modern digital wedding invitation and guest RSVP SaaS tailored for the Malaysian market.\n\nKey highlights:\n- Touch-optimized single-page architecture built with **Livewire 3.7 + Alpine.js**\n- Automated high-resolution **PDF print-card generator**\n- Real-time guest RSVP tracking\n- **Automated Telegram Bot notifications** (I chose Telegram for speed and reliability, avoiding WhatsApp API overhead)."
                    elif "zero" in q_lower or "downtime" in q_lower or "aws" in q_lower or "deploy" in q_lower:
                        answer = "In my infrastructure designs, I specialize in **Zero-Downtime Blue/Green Deployments** on AWS without Docker complexity.\n\nMy approach uses AWS Application Load Balancers, Target Group weight shifting, Laravel Octane/FrankenPHP workers, and centralized ElastiCache to ensure 100% traffic cutover safety and instant rollback without dropping active sessions.\n\nYou can read my complete breakdown in the **Case Studies** tab: *Zero-Downtime Blue/Green Deployments Explained Simply*."
                    elif "cka" in q_lower or "cert" in q_lower or "k8s" in q_lower or "kubernetes" in q_lower:
                        answer = "I hold the **CKA: Certified Kubernetes Administrator** certification from The Linux Foundation & CNCF (issued 2024, verified on Credly).\n\nAdditionally, I am accredited as a **Graduate Technologist (Information & Computing)** by the Malaysia Board of Technologists (MBOT)."
                    elif "stack" in q_lower or "laravel" in q_lower or "php" in q_lower:
                        answer = "My daily production stack centers on:\n- **Backend:** PHP (Laravel 11 / 12), Laravel Octane / FrankenPHP\n- **Frontend & Interaction:** Livewire 3 / 4, Alpine.js, Tailwind CSS\n- **Data & Caching:** MySQL, Redis / ValKey, AWS ElastiCache\n- **Cloud & DevOps:** AWS (EC2, Auto Scaling, ALB, RDS Aurora), CI/CD Automation\n- **Current Focus:** Concurrency in Go (Golang) and Kubernetes (CKA)."
                    elif "name" in q_lower or "who" in q_lower or "amee" in q_lower:
                        answer = "My full name is **Ameerul Arif Bin Mohd Azni**, though friends and colleagues across the tech community call me **Amee**.\n\nI'm a Malaysia-based Lead Systems Architect and Senior Software Engineer specializing in cloud infrastructure, zero-downtime AWS deployments, and scalable Laravel + Go architectures. I hold both the **CKA (Certified Kubernetes Administrator)** and **Graduate Technologist (MBOT)** credentials.\n\nFeel free to ask about any of my setups or code architectures!"
                    else:
                        answer = "Hi! I'm **Ameerul Arif** (known as **Amee**). I specialize in high-density cloud infrastructure, zero-downtime AWS deployments, and scalable Laravel + Go architectures.\n\nYou can explore my case studies and live project showcases directly in the tabs above, or feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/ameerul-arif-mohd-azni/) or drop me an email at hey@amee.my!"

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"answer": answer, "provider": used_provider}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    generate_seo_assets()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortfolioRequestHandler) as httpd:
        print(f"🚀 Ameerul Portfolio & Visual Post Editor running at http://localhost:{PORT}")
        print(f"👉 Visual Post Editor UI: http://localhost:{PORT}/editor/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
