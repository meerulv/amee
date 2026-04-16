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
            // Filter out posts marked as drafts
            return posts.filter(post => post.draft !== true);
        } catch (e) {
            console.warn("Using system fallbacks for documentation feed.");
            return [
                { 
                    folder: "multi-file-uploads", 
                    title: "Multi-File Uploads in Laravel Vapor", 
                    date: "2026-04-10", 
                    excerpt: "Implementation patterns for scalable S3 streaming directly from the frontend to bypass Lambda payload limits.", 
                    tags: ["Laravel", "AWS Vapor"] 
                },
                { 
                    folder: "upgrading-ajakme", 
                    title: "Upgrading AjakMe Architecture", 
                    date: "2026-03-28", 
                    excerpt: "Transitioning AjakMe from a monolithic system to a modular, distributed architecture for improved scalability.", 
                    tags: ["Infrastructure", "Refactoring"] 
                }
            ];
        }
    }
};

/**
 * Alpine.js Blog Component Factory
 */
function blogSystem(base = "") {
    return {
        posts: [],
        allTags: [],
        selectedTag: '',
        currentPage: 1,
        itemsPerPage: 30,
        async init() {
            this.posts = await BlogData.getPosts(base);
            const tagSet = new Set();
            this.posts.forEach(post => post.tags.forEach(tag => tagSet.add(tag)));
            this.allTags = Array.from(tagSet).sort();
        },
        get filteredPosts() {
            if (!this.selectedTag) return this.posts;
            return this.posts.filter(p => p.tags.includes(this.selectedTag));
        },
        get totalPages() {
            return Math.ceil(this.filteredPosts.length / this.itemsPerPage);
        },
        get paginatedPosts() {
            const start = (this.currentPage - 1) * this.itemsPerPage;
            return this.filteredPosts.slice(start, start + this.itemsPerPage);
        }
    }
}

/**
 * DevOps Pulse Indicator - Proof of Concept for Seniority Signal
 */
function initSystemPulse() {
    const statusText = document.querySelector('.status-text');
    if (statusText) {
        const regions = ['MY-KUL', 'AWS-SG', 'GC-SH'];
        let idx = 0;
        setInterval(() => {
            statusText.setAttribute('title', `Primary substrate: ${regions[idx]}`);
            idx = (idx + 1) % regions.length;
        }, 10000);
    }
}
