cat > seed_blog.sh << 'EOF'
#!/bin/bash
# seed_blog.sh
# Usage: bash seed_blog.sh

echo "Creating portfolio/blog structure with a shared navbar..."

# --- Define the Navbar HTML ---
# This is the single source of truth for the navigation.
# We create two versions to handle relative paths correctly.

# Navbar for pages in the root directory (index.html, about.html)
NAVBAR_ROOT='<nav>
  <ul><li><strong>My Portfolio</strong></li></ul>
  <ul>
    <li><a href="index.html">Home</a></li>
    <li><a href="blog/blog.html">Blog</a></li>
    <li><a href="about.html">About</a></li>
  </ul>
</nav>'

# Navbar for pages in the /blog/ directory (blog.html)
# Note the "../" to go up one directory level.
NAVBAR_BLOG='<nav>
  <ul><li><strong>My Portfolio</strong></li></ul>
  <ul>
    <li><a href="../index.html">Home</a></li>
    <li><a href="blog.html">Blog</a></li>
    <li><a href="../about.html">About</a></li>
  </ul>
</nav>'

# Root folders
mkdir -p blog posts styles

# Create index.html
# Notice we use "$NAVBAR_ROOT" to insert the navbar.
# The heredoc delimiter (HTML_EOF) is NOT quoted to allow variable expansion.
cat > index.html << HTML_EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Portfolio</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
<link rel="stylesheet" href="styles/style.css">
</head>
<body>
<header class="container">
 $NAVBAR_ROOT
</header>

<main class="container">
<h1>Welcome to My Portfolio</h1>
<p>This is a minimal static portfolio + blog built with Pico.css.</p>
</main>

<footer class="container">
<small>© 2025 Your Name</small>
</footer>
</body>
</html>
HTML_EOF

# Create about page
cat > about.html << HTML_EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>About | My Portfolio</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
<link rel="stylesheet" href="styles/style.css">
</head>
<body>
<header class="container">
 $NAVBAR_ROOT
</header>

<main class="container">
<h1>About Me</h1>
<p>Write something about yourself here.</p>
</main>

<footer class="container">
<small>© 2025 Your Name</small>
</footer>
</body>
</html>
HTML_EOF

# Create styles/style.css
cat > styles/style.css << 'CSS_EOF'
body {
  transition: background-color 0.3s, color 0.3s;
}
body.dark-mode {
  background-color: #121212;
  color: #eee;
}
body.dark-mode a { color: #90caf9; }
body.dark-mode .post-card { border-color: #333; background: #1e1e1e; }
CSS_EOF

# Create blog/blog.html
# Here we use "$NAVBAR_BLOG" for the correct relative links.
mkdir -p blog
cat > blog/blog.html << HTML_EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blog | My Portfolio</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
<link rel="stylesheet" href="../styles/style.css">
<style>
#tagFilter { margin-bottom: 1rem; }
.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
.post-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
  background: #fff;
}
.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.post-cover {
  width: 100%;
  height: 180px;
  object-fit: cover;
}
.post-content {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.post-content h2 { margin: 0 0 0.5rem 0; font-size: 1.25rem; }
.post-content .secondary { font-size: 0.85rem; color: #666; margin-bottom: 0.5rem; }
.tags span {
  background: #eee;
  border-radius: 4px;
  padding: 0.2rem 0.5rem;
  margin-right: 0.3rem;
  font-size: 0.75rem;
}
.post-excerpt { margin-top: auto; font-size: 0.95rem; color: #333; }
#darkToggle { margin-left:1rem; }
</style>
</head>

<body>
<header class="container">
 $NAVBAR_BLOG
<li><button id="darkToggle">🌓 Dark Mode</button></li>
</ul>
</nav>
</header>

<main class="container">
<h1>Blog Posts</h1>
<select id="tagFilter"><option value="">Filter by tag</option></select>
<div id="posts-list" class="posts-grid"><p>Loading posts...</p></div>

<nav id="pagination" style="display:flex; justify-content:center; margin-top:2rem;">
<button id="prevPage" disabled>← Prev</button>
<span id="pageIndicator" style="margin: 0 1rem;"></span>
<button id="nextPage" disabled>Next →</button>
</nav>
</main>

<footer class="container">
<small>© 2025 Your Name</small>
</footer>

<script>
const POSTS_PER_PAGE = 6;
const STORAGE_KEY = "blog_page";

document.getElementById("darkToggle").addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
});

async function loadPosts() {
try {
  const res = await fetch("../posts/");
  const txt = await res.text();
  const parser = new DOMParser();
  const html = parser.parseFromString(txt,"text/html");
  const links = Array.from(html.querySelectorAll("a"))
    .map(a=>a.getAttribute("href"))
    .filter(h=>h && h.endsWith("/") && h!="../");

  const posts = [], allTags = new Set();
  for(const folder of links){
    const r = await fetch(`../posts/${folder}index.html`);
    const t = await r.text();
    const d = parser.parseFromString(t,"text/html");
    const title=d.querySelector("h1")?.textContent?.trim()||folder.replace("/","");
    const date=d.querySelector(".secondary")?.textContent?.trim()||"Unknown date";
    const excerpt=d.querySelector("p:not(.secondary)")?.textContent?.trim()||"";
    const tagDiv=d.querySelector(".tags");
    const tags=tagDiv?Array.from(tagDiv.querySelectorAll("span")).map(s=>s.textContent.trim()):[];
    tags.forEach(t=>allTags.add(t));
    const coverUrl=`../posts/${folder}cover.jpg`;
    posts.push({folder,title,date,excerpt,tags,coverUrl});
  }

  posts.sort((a,b)=>new Date(b.date)-new Date(a.date));

  let currentPage = parseInt(localStorage.getItem(STORAGE_KEY)||"1",10);
  const postContainer = document.getElementById("posts-list");
  const pagination = document.getElementById("pagination");
  const prevBtn = document.getElementById("prevPage");
  const nextBtn = document.getElementById("nextPage");
  const pageIndicator = document.getElementById("pageIndicator");
  const tagFilter = document.getElementById("tagFilter");

  allTags.forEach(t=>{
    const option=document.createElement("option");
    option.value=t;
    option.textContent=t;
    tagFilter.appendChild(option);
  });

  function renderPage(page,filterTag=""){
    postContainer.innerHTML="";
    const filtered=filterTag?posts.filter(p=>p.tags.includes(filterTag)):posts;
    const totalPages=Math.ceil(filtered.length/POSTS_PER_PAGE);
    if(page>totalPages) page=totalPages||1;
    const start=(page-1)*POSTS_PER_PAGE;
    const visible=filtered.slice(start,start+POSTS_PER_PAGE);

    if(!visible.length){
      postContainer.innerHTML="<p>No posts found.</p>";
      pagination.style.display="none";
      return;
    }

    visible.forEach(p=>{
      postContainer.innerHTML+=\`
      <div class="post-card">
        \${p.coverUrl?`<img src="\${p.coverUrl}" class="post-cover" alt="Cover image" loading="lazy">`:""}
        <div class="post-content">
          <h2><a href="../posts/\${p.folder}">\${p.title}</a></h2>
          <p class="secondary">\${p.date}</p>
          \${p.tags.length?`<div class="tags">\${p.tags.map(t=>\`<span>\${t}</span>\`).join(" ")}</div>`:""}
          <p class="post-excerpt">\${p.excerpt}</p>
        </div>
      </div>
      \`;
    });

    pagination.style.display="flex";
    pageIndicator.textContent=\`Page \${page} of \${totalPages}\`;
    prevBtn.disabled=page===1;
    nextBtn.disabled=page>=totalPages;
    localStorage.setItem(STORAGE_KEY,page);
    window.scrollTo({top:0,behavior:"smooth"});
  }

  prevBtn.addEventListener("click",()=>{currentPage--;renderPage(currentPage,tagFilter.value);});
  nextBtn.addEventListener("click",()=>{currentPage++;renderPage(currentPage,tagFilter.value);});
  tagFilter.addEventListener("change",()=>{currentPage=1;renderPage(currentPage,tagFilter.value);});

  renderPage(currentPage);
}catch(e){console.error(e); postContainer.innerHTML="<p>Error loading posts</p>";}
}

loadPosts();
</script>
</body>
</html>
HTML_EOF

# Create sample post
mkdir -p posts/first-post
cat > posts/first-post/index.html << 'HTML_EOF'
<article>
<h1>My First Post</h1>
<p class="secondary">2025-11-11</p>
<div class="tags"><span>intro</span><span>hello</span></div>
<p>Welcome to my first post. This is an excerpt showing how the post will look on the blog page.</p>
</article>
HTML_EOF

echo "Blog skeleton created with a shared navbar!"
echo "To add a new link, edit the NAVBAR variables in this script and re-run it."
EOF