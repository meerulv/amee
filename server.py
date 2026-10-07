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
POSTS_DIR = os.path.join(BASE_DIR, "blog", "posts")
SCAFFOLDING_PATH = os.path.join(BASE_DIR, "blog", "scaffolding-template.html")

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

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
                title = data.get('title', '').strip()
                folder = data.get('folder', '').strip() or slugify(title)
                post_type = data.get('type', 'case-study')
                date_str = data.get('date', '')
                excerpt = data.get('excerpt', '')
                metrics = data.get('metrics', '')
                tags = [t.strip() for t in data.get('tags', []) if t.strip()]
                draft = bool(data.get('draft', False))
                content_html = data.get('content_html', '')

                # 1. Update/Add entry in posts.json
                with open(POSTS_JSON_PATH, "r", encoding="utf-8") as f:
                    posts = json.load(f)

                post_entry = {
                    "folder": folder,
                    "title": title,
                    "type": post_type,
                    "date": date_str,
                    "category": data.get('category', '').strip(),
                    "excerpt": excerpt,
                    "metrics": metrics,
                    "tags": tags,
                    "draft": draft
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

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortfolioRequestHandler) as httpd:
        print(f"🚀 Ameerul Portfolio & Visual Post Editor running at http://localhost:{PORT}")
        print(f"👉 Visual Post Editor UI: http://localhost:{PORT}/editor/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
