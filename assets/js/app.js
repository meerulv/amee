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
