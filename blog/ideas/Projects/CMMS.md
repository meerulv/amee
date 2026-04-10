ACCEA Centralized SSO & Campaign Management Platform

🔗 https://account.accea.com.my/

Summary
Architected and led development of a centralized identity and shared services platform, providing Single Sign-On (SSO) and unified customer data across multiple ACCEA applications. The platform also functions as a cross-product campaign and coupon engine, enabling consistent promotion management and real-time validation at scale.

Key Contributions:

Architected and owned a centralized SSO platform, serving as the single source of truth for authentication and customer identity across 5+ integrated applications.
Designed and implemented a modular, API-driven campaign & coupon engine supporting rule-based validation, usage limits, expiry logic, and user-level eligibility.
Defined scalable backend architecture patterns (stateless APIs, shared services, async processing) to support multi-system integrations and future extensibility.
Built high-performance services in Laravel 12 handling authentication and real-time coupon validation with low-latency response times (<100ms typical).
Implemented Redis caching for sessions and high-frequency operations, reducing database load by ~40–60% under peak traffic.
Engineered asynchronous job pipelines using Laravel queues (supervisord), processing thousands of background jobs daily with idempotent design for fault tolerance.
Designed optimized MySQL schemas supporting both identity management and high-volume transactional coupon usage.
Collaborated with multiple teams to onboard systems into the SSO ecosystem, defining API contracts and integration standards.
Enforced security best practices including encrypted credentials, CSRF protection, and role-based access control for admin and campaign operations.

Tech Stack:

Backend: Laravel 12 (PHP)
Frontend: Livewire 3, Alpine.js, Tailwind CSS
Database: MySQL
Caching & Queue: Redis, Laravel Queues (supervisord)
Architecture: Centralized identity platform + shared services (SSO & campaign engine), API-first integrations

Impact:

Unified authentication across multiple products, eliminating duplicated login systems and reducing development overhead.
Enabled centralized campaign management powering cross-platform promotions and consistent coupon validation.
Improved system scalability and responsiveness, supporting growing user base and concurrent authentication requests.
Reduced operational complexity by consolidating identity and promotion logic into a single, maintainable platform.
Established a scalable foundation for onboarding new products with minimal integration effort.





GENERAL

==============


Here are a few strong 2–3 line resume bullet versions you can choose from depending on tone:

Option 1 (balanced & solid):

Built a centralized SSO platform using Laravel 12, enabling seamless authentication and unified customer identity across multiple ACCEA applications.
Developed an integrated campaign and coupon management system with shared APIs for cross-platform promotions and validation.
Improved performance and scalability using Redis caching and asynchronous job processing (queues + supervisord).

Option 2 (more impact-focused):

Engineered a centralized SSO system to unify authentication and customer data across multiple products, reducing duplication and improving maintainability.
Designed and implemented a full-featured campaign & coupon engine supporting cross-application promotions via shared APIs.
Optimized system performance with Redis caching and background job processing.

Option 3 (more technical depth):

Architected and developed a Laravel 12-based SSO platform with unified identity management and secure cross-application authentication.
Implemented a scalable coupon and campaign module with rule-based validation, API integrations, and centralized control.
Leveraged Redis and queue workers (supervisord) for caching and asynchronous processing.

Option 4 (shortest, punchy):

Built a centralized SSO and customer platform (Laravel 12) powering authentication across multiple applications.
Developed a shared campaign & coupon system with real-time validation APIs.
Enhanced performance using Redis caching and queue-based background processing.


LEAD

===============

Senior/Lead Full Stack + DevOps Focus (Recommended):

Architected and delivered a centralized SSO platform (Laravel 12) unifying authentication and customer identity across multiple products, reducing system duplication and improving scalability.
Designed a shared campaign & coupon engine with rule-based validation and API integrations, enabling cross-application promotions from a single platform.
Implemented Redis caching and queue-based background processing (supervisord), optimizing performance, reliability, and operational efficiency in production.

Slightly more DevOps-heavy version:

Led development of a centralized SSO and customer platform, enabling secure cross-application authentication and unified identity management.
Built a scalable campaign & coupon service with shared APIs, supporting real-time validation across multiple systems.
Improved system performance and reliability through Redis caching, queue workers, and production process management (supervisord).

If you want it to hit even harder (top-tier senior roles):

Architected a centralized SSO platform and shared services layer, unifying authentication and customer data across multiple applications.
Designed and deployed a cross-platform campaign & coupon system with rule-based logic and API-driven integrations.
Owned performance and reliability improvements via Redis caching, asynchronous job processing, and production workload management.



STAFF/LEAD

================


Here’s a staff/lead-level version—this emphasizes architecture ownership, scalability thinking, and DevOps maturity. These are the kinds of bullets that get attention for senior/lead roles:

Staff / Lead Full Stack + DevOps (High-Impact Version):

Architected and owned a centralized SSO platform and shared services layer (Laravel 12), unifying authentication and customer identity across multiple applications, eliminating duplication and improving system cohesion.
Designed and implemented a scalable, API-driven campaign & coupon system with rule-based validation, supporting cross-platform promotions with consistency and extensibility.
Drove performance and reliability improvements through Redis caching, idempotent job processing, and queue-based architectures (supervisord), ensuring fault tolerance under load.
Established backend patterns for scalability (API standardization, caching strategies, async workflows) and collaborated across teams to integrate multiple products into a single authentication ecosystem.

Even stronger (if you want to signal system design depth):

Led architecture and development of a centralized SSO and identity platform, serving as the single source of truth for authentication and customer data across distributed applications.
Built a modular campaign & coupon engine with rule-based logic, real-time validation APIs, and support for high-volume transactional use cases.
Optimized system throughput and resilience using Redis caching, queue workers, and idempotent processing patterns; reduced bottlenecks in authentication and promotion flows.
Introduced scalable design practices (stateless APIs, background processing, caching layers) to support growing product integrations and traffic demands.

Optional “spicy” version (for top-tier companies):

Architected a centralized identity and SSO platform, enabling secure, seamless authentication across multiple applications and establishing a unified customer data layer.
Designed a distributed-ready campaign & coupon service with rule engines and API-first integration, supporting cross-system consistency and extensibility.
Improved reliability and scalability via caching strategies, idempotent async processing, and workload orchestration (Redis + queue workers).
Influenced system design standards across teams, driving adoption of scalable backend patterns and integration best practices.