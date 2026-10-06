/**
 * Core Navigation & Documentation System
 * Ameerul Arif Portfolio
 */

document.addEventListener('DOMContentLoaded', () => {
    // Shared state or initialization if needed
});

/**
 * Loads shared partials (Navbar/Footer) into the page
 * @param {string} base - The relative or absolute base path to the root directory
 */
async function loadPartials(base = "/") {
    try {
        const fetchPartial = async (name) => {
            const res = await fetch(`${base}_partials/${name}.html`);
            if (!res.ok) throw new Error(`Partial ${name} not found`);
            return await res.text();
        };

        const [footerTxt, navbarTxt] = await Promise.all([
            fetchPartial('_footer'),
            fetchPartial('_navbar')
        ]);

        const updateEl = (id, html) => {
            const el = document.getElementById(id);
            if (el) {
                // Smart Path Correction: Skip absolute, protocol, or hash links
                el.innerHTML = html.replace(/href="(?!http|#|\/)/g, `href="${base}`);
                if (window.Alpine) {
                    window.Alpine.initTree(el);
                }
            }
        };

        updateEl('footer', footerTxt);
        updateEl('navbar', navbarTxt);
    } catch (e) {
        console.error("Infrastructure Error: Failed to load core components.", e);
    }
}

/**
 * Shared Blog Data System
 */
const BlogData = {
    async getPosts(base = "") {
        try {
            const res = await fetch(`${base}blog/posts/posts.json`);
            if (!res.ok) throw new Error("Manifest not accessible");
            const posts = await res.json();
            return posts.filter(post => post.draft !== true);
        } catch (e) {
            console.warn("Using system fallbacks for documentation feed.", e);
            return [];
        }
    },
    async loadSuggestedPosts(currentFolder = "", tags = [], containerId = "suggested-posts") {
        try {
            const container = document.getElementById(containerId);
            if (!container) return;

            const allPosts = await BlogData.getPosts("/");
            // Exclude current post
            const others = allPosts.filter(p => p.folder !== currentFolder);
            if (others.length === 0) {
                container.style.display = 'none';
                return;
            }

            // Score posts based on tag overlap
            const scored = others.map(post => {
                let score = 0;
                if (Array.isArray(post.tags) && Array.isArray(tags)) {
                    post.tags.forEach(t => {
                        if (tags.some(curr => curr.toLowerCase() === t.toLowerCase())) {
                            score += 1;
                        }
                    });
                }
                return { post, score };
            });

            // Sort: highest score first, then newest date
            scored.sort((a, b) => {
                if (b.score !== a.score) return b.score - a.score;
                return (b.post.date || '').localeCompare(a.post.date || '');
            });

            const suggestions = scored.slice(0, 2).map(s => s.post);
            if (suggestions.length === 0) {
                container.style.display = 'none';
                return;
            }

            const cardsHtml = suggestions.map(post => {
                const badge = post.type === 'case-study'
                    ? '<span class="mono text-[9px] uppercase font-bold bg-[#1f6feb]/20 text-[#58a6ff] border border-[#388bfd]/30 px-1.5 py-0.5 rounded">Case Study</span>'
                    : '<span class="mono text-[9px] uppercase font-bold bg-[#238636]/20 text-[#3fb950] border border-[#2ea043]/30 px-1.5 py-0.5 rounded">Snippet</span>';

                const metricHtml = post.metrics
                    ? `<div class="mono text-[10px] text-emerald-400 font-semibold mb-2">⚡ ${post.metrics}</div>`
                    : '';

                const tagsHtml = (post.tags || []).slice(0, 3).map(t =>
                    `<span class="mono text-[10px] bg-[#21262d] text-[#8b949e] px-1.5 py-0.5 rounded">${t}</span>`
                ).join(' ');

                return `
                <a href="/blog/posts/${post.folder}/" class="block p-4 sm:p-5 rounded-lg border border-[#30363d] bg-[#161b22] hover:border-[#58a6ff] transition-all group">
                    <div class="flex items-center justify-between gap-2 mb-2">
                        ${badge}
                        <span class="mono text-[10px] text-[#8b949e]">${post.date || ''}</span>
                    </div>
                    <h3 class="text-sm sm:text-base font-bold text-white group-hover:text-[#58a6ff] transition-colors mb-1.5 line-clamp-2">${post.title}</h3>
                    <p class="text-xs text-[#8b949e] line-clamp-2 mb-3 leading-relaxed">${post.excerpt || ''}</p>
                    ${metricHtml}
                    <div class="flex flex-wrap gap-1">${tagsHtml}</div>
                </a>
                `;
            }).join('');

            container.innerHTML = `
                <div class="mt-16 pt-8 border-t border-[#30363d]">
                    <div class="flex items-center justify-between mb-4">
                        <div class="mono text-xs uppercase font-bold text-white tracking-wider flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-[#58a6ff]"></span>
                            <span>Related Case Studies & Snippets</span>
                        </div>
                        <a href="/blog/" class="mono text-xs text-[#58a6ff] hover:underline">All Entries →</a>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        ${cardsHtml}
                    </div>
                </div>
            `;
        } catch (e) {
            console.warn("Failed to load suggested posts", e);
        }
    }
};

/**
 * Alpine.js Blog & Logs Component Factory
 */
function blogSystem(base = "") {
    return {
        posts: [],
        allTags: [],
        selectedTag: '',
        selectedType: 'all', // 'all', 'case-study', 'snippet', 'article'
        currentPage: 1,
        itemsPerPage: 15,
        async init() {
            this.posts = await BlogData.getPosts(base);
            const tagSet = new Set();
            this.posts.forEach(post => {
                if (Array.isArray(post.tags)) {
                    post.tags.forEach(tag => tagSet.add(tag));
                }
            });
            this.allTags = Array.from(tagSet).sort();
        },
        setType(type) {
            this.selectedType = type;
            this.currentPage = 1;
        },
        get filteredPosts() {
            return this.posts.filter(p => {
                const matchesTag = !this.selectedTag || (p.tags && p.tags.includes(this.selectedTag));
                const matchesType = this.selectedType === 'all' || p.type === this.selectedType;
                return matchesTag && matchesType;
            });
        },
        get totalPages() {
            return Math.ceil(this.filteredPosts.length / this.itemsPerPage) || 1;
        },
        get paginatedPosts() {
            const start = (this.currentPage - 1) * this.itemsPerPage;
            return this.filteredPosts.slice(start, start + this.itemsPerPage);
        }
    };
}
