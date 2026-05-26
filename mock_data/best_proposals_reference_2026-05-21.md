# Best Proposals Reference - 2026-05-21

Curated library of recent high-quality proposal drafts. Each entry includes the original Upwork job context (title, full brief, mandatory skills) and the proposal we sent or queued. Use this as pattern-mining reference for future drafting.

**Source:** drafts from session of 2026-05-19 to 2026-05-21 where full job context was preserved. Style follows `stylistic_requirements/PROPOSAL_PLAYBOOK.md`.

---

## 1. Next.js + Supabase Developer: Community Platform MVP

**Freelancer:** Yevhen Omelianenko
**Rate:** $40/hr
**Format:** Separate-blocks (5 questions in apply form)

### Job text

Seeking a mid-senior developer to build a tightly-scoped MVP web app for a curated creative-industry community platform on Next.js + Supabase. The build covers profiles, members directory, home feed, real-time messaging, casting calls with apply flow, and a project setup flow with document upload, role selection, and direct invites. A separate technical lead is providing the architecture spec and PR review. 8-9 weeks, hourly contract, milestone-based payment. Fluent English and 4+ hour overlap with European working hours required.

Apply questions:
1. Share 1-3 live URLs of Next.js + Supabase apps you have built and worked on personally.
2. How would you handle realtime 1:1 messaging in Supabase — postgres_changes vs broadcast channels?
3. Estimated total hours for the main scope (one number).
4. Riskiest technical part and how you'd mitigate it (one sentence).
5. Timezone, hours per week, vacation between today and end of July 2026.

### Mandatory skills

JavaScript, HTML5

### Our proposal

**Cover letter:**

Hi Jamie,

Read the brief. The execute-against-spec model with a separate tech lead handling architecture and PR review is a clean way to ship this scope in 8-9 weeks. Real-time messaging, the casting apply flow, and project setup with document upload all map cleanly to Supabase primitives (postgres_changes, RLS-scoped tables, Storage buckets), so the spec should be straightforward to execute against.

One honest note on the URLs below: I have one Next.js + Supabase app of my own deployed (library-management), where I worked through auth, RLS, and real-time row updates via postgres_changes. My larger production Next.js delivery has been on other backends. Baas (baasverpakkingen.nl) is Next.js + headless Shopify, not Supabase. Saying that upfront rather than padding the list with apps that don't actually use Supabase on the backend.

Rate: $40/hr. Fixed-bid total against the hours estimate below: $10,400.

Yevhen
Senior React / Next.js Developer

**Q1 (URLs):**
- https://library-management-ruby-nine.vercel.app/ — Next.js + Supabase + shadcn + Tailwind. Auth, RLS-scoped tables, real-time row updates via postgres_changes, Storage for book covers.
- https://baasverpakkingen.nl/ — Next.js production B2B e-commerce. Note: Next.js + headless Shopify, not Supabase.

**Q2 (postgres_changes vs broadcast):**
postgres_changes is the right primitive when messages have to be durable and conversation history is the source of truth: the realtime feed ties to the actual INSERT on the messages table, so a late refresh sees the same state. Broadcast is faster and lighter (no DB round-trip), useful for ephemeral signals like typing indicators, presence, and read receipts. For this build I'd persist messages via postgres_changes on a per-conversation channel with RLS, and layer broadcast on the same channel for typing and presence only.

**Q3 (Hours):** 260

**Q4 (Riskiest part):**
Realtime messaging at the RLS boundary — making sure postgres_changes only delivers rows to actual conversation participants without leaking to outside listeners; I'd mitigate by writing policy-tested fixtures (insert as user A, assert no realtime payload reaches user B's channel) before wiring UI.

**Q5 (Timezone/hours/vacation):**
(a) Ukraine (EET / EEST), 4-7 hour overlap with European working hours.
(b) Up to 30 hrs/week, matching the "Less than 30 hrs/week" cap.
(c) No vacation planned between today and end of July 2026.

---

## 2. Agentic AI Architect - AI Coaching & Engagement Platform

**Freelancer:** Dmitriy Melnichenko
**Rate:** $75/hr
**Format:** Single block

### Job text

We are seeking an experienced Agentic AI Architect to help build and deploy an AI-powered coaching and engagement ecosystem for a fast-growing consumer platform focused on financial empowerment, education, community engagement, and personalized user experiences.

Role focus: personalized coaching and recommendations, workflow automation, behavioral engagement, gamification systems, community interaction support, dashboard and data integrations, AI-powered communications, contextual memory and personalization.

Responsibilities: architect and deploy agentic AI workflows and multi-agent systems; build AI copilots and personalized AI assistants; integrate AI with dashboards, CRM systems, operational platforms; develop intelligent automation systems for engagement and retention; create AI-driven gamification; implement scalable cloud-based AI infrastructure.

Required: proven experience with agentic AI systems and autonomous workflows; LLM orchestration and AI automation; LangChain, LangGraph, CrewAI, AutoGen, or similar; API/dashboard/database integration; contextual memory, RAG, AI personalization; cloud (AWS, GCP, Azure).

Apply with: examples of AI systems / automations built, frameworks and tools, GitHub/portfolio/case studies, availability and timezone.

### Mandatory skills

Artificial Intelligence

### Our proposal

Hi Alex,

Read the brief. Strongest match on my end is a multi-agent AI operating system I'm currently architecting for a mid-size services business: sales, marketing, HR/recruiting, software-delivery estimation, and an AI-augmented programming methodology each shipped as separate LangGraph workflows behind a unified FastAPI surface. The estimation module took proposal-prep from 4 hours to 10 minutes per artifact (~95% senior-time reduction) with higher consistency and an explicit risk and open-question audit trail the manual process never produced. The pattern you describe (personalized coaching, behavioral engagement, contextual memory, gamification, multi-agent orchestration) maps onto the same primitives.

Architecture under the hood: LangGraph for orchestration with explicit state machines and checkpointer-backed persistence (PostgresSaver) for safe retries; Pydantic structured outputs at every agent boundary so the LLM never returns free-form JSON downstream code has to parse defensively; evaluator-optimizer loops where one agent produces an artifact and another scores it against a rubric until a quality threshold is hit; manager HITL gates at the points where the cost of a wrong decision is high; async job model so long-running agent chains don't block user-facing API; RAG with versioned source documents and per-tenant memory isolation for personalization.

Engineering reference: OPSY (https://opsyguard.com/), operations platform for security teams I led at CTO level. Python/FastAPI, Node/NestJS, PostgreSQL, React, Angular, Ionic mobile guard apps, white-label deployment. The same scale-and-reliability discipline an AI engagement platform needs once it leaves prototype.

Frameworks day-to-day: LangGraph, LangChain, FastAPI, Pydantic, PostgreSQL, OpenAI API, Anthropic API, Redis. Honest gap to flag: hands-on cloud is GCP and AWS general services. If you're standardizing on Bedrock specifically, the architecture is platform-agnostic but the Bedrock SDK is something I'd come up the curve on in the first sprint.

Case study walk-through with PRODUCT, ARCHITECTURE, API, DATA_CONTRACT, and ROADMAP documents available on a kickoff call.

Availability: 25-30 hrs/week. Timezone: Ukraine (EET / EEST), 4-7 hour overlap with US Eastern.

Dmitriy
AI Architect

---

## 3. Senior AI/LLM Application Engineer (Claude Code, MCP, RAG)

**Freelancer:** Dmytro Mamaiev
**Rate:** $110/hr
**Format:** Separate-blocks (4 questions)
**Client identified:** Remone Randolph / TruMotiv (CRE proptech, MOTIV-1 seller motivation scoring)

### Job text

Building a proprietary AI-driven intelligence platform on top of a 26-year commercial real estate brokerage. Target exit: $90M+ in 3-5 years. The platform combines a behavioral database of commercial property owners, an autonomous deal origination engine, multi-channel campaign automation, and AI-driven matching between verified buyers and motivated sellers.

Current stack: GoHighLevel, N8N, CallRail, OpenAI API. Looking for a senior engineer to work alongside a fractional CTO to start building the proprietary application layer. Execute architecture decisions, not strategic decisions alone.

First 30 days: complete technical inventory of current stack; build proprietary PostgreSQL schema (owners, properties, behavioral events, motivation scores, conversation history); build initial ingestion from GHL and CallRail (read-only first); document everything.

Following 60-90 days: motivation scoring engine as queryable service; buyer-seller matching engine with ranked output; Claude API integration for message generation, transcript analysis, intelligence synthesis; infrastructure (auth, logging, monitoring, deployment automation); IP assignment and code ownership controls.

Required: production LLM API integration (Claude, OpenAI), PostgreSQL schema design for behavioral/event data, vector databases and RAG at production scale (pgvector, Pinecone, Weaviate), Python or TypeScript, no-code platform API integration (GHL, Airtable), Claude Code + MCP familiarity a major plus.

No agencies. Long-term 12-24 month build.

Apply questions:
1. Production LLM application you've built. What it did, your role, one technical decision you'd do differently today.
2. First 3 days extracting GHL + CallRail data into a proprietary database.
3. Honest opinion on Claude Code and MCP.
4. Timezone and realistic hours per week for next 30 days.

### Mandatory skills

OpenAI API, Claude, PostgreSQL, Database, Python, TypeScript

### Our proposal

**Cover letter slot:**
Per your instructions: no cover letter. Answers to the four questions below.

Dmytro
Senior AI Engineer (Claude Code primary, OpenAI Assistants production)

**Q1 - Production LLM app + decision I'd do differently:**
DevMatch (https://github.com/dima-mamaev/devMatch_frontend and https://github.com/dima-mamaev/devMatch_backend). TikTok-style video profiles for developers with an AI matching agent for recruiters and founders. NestJS GraphQL API + Next.js frontend, OpenAI Assistants with tool handlers querying the talent graph, GraphQL subscriptions for streamed agent events, BullMQ async pipeline for video conversion with FFmpeg, retries and dead-letter handling, per-user AI rate limits in Redis.

My role: full-stack from scratch. Designed Postgres schema (PostgreSQL 17 + TypeORM), built NestJS microservices (API gateway, video-converter worker, AI agent service), wired the OpenAI Assistant tool handlers and streamed events, built the frontend GraphQL subscriptions for match-chat.

Technical decision I'd do differently: I leaned on OpenAI Assistants (managed thread/state API) for the agent layer. In hindsight I'd move to a self-managed agent loop with explicit state checkpoints in Postgres. Assistants is convenient but state lives behind OpenAI's API: limited inspection during failures, harder provider migration (Claude, Bedrock), tool retries constrained to OpenAI's semantics. A self-managed loop with structured outputs and Postgres-backed state gives audit trails for free and makes provider migration a one-week swap rather than a rewrite. For a build like yours where every line of code belongs to the company and provider portability matters for the exit story, this is the version I'd start with.

**Q2 - GHL + CallRail extraction, first three days:**

Day 1: Read-only inventory specific to your CRE data shapes. Pull GHL: contacts and the custom fields you've built around them (owner-side fields like property_address, zoning, deal stage, last contact date; campaign and tag taxonomy), opportunities and pipeline stages, conversations (SMS, email, voice), calendar if showings are booked through it. Pull CallRail: calls with their full metadata (campaign source, tracking number, ring duration, recording URL), transcripts where present, source-tracking that ties calls to specific outreach campaigns. Dump raw paginated JSON to a staging bucket (S3 or GCS) with timestamps. Goal of day 1 is to know exactly what data lives in your tenant versus what the platforms claim to support, because GHL especially has wide variation in custom-field usage across accounts.

Day 2: Canonical schema first pass. Postgres tables: owners (canonical natural-person or LLC record with dedupe keys against phone, email, mailing address), properties (one-to-many under owners, with address, zoning, lease history, source-of-truth field), behavioral_events (one row per touchpoint with a source enum and timestamp, ties to owner_id, holds the raw GHL/CallRail event id for traceability), conversations (CallRail transcripts and GHL SMS/email threads, linked to owner_id with full content available for later embedding), motivation_score_history (computed score over time, with the input features used and the version of the scoring model that produced it). Keep source JSON columns alongside the canonical fields for the first month so a misinterpreted GHL custom field is recoverable without re-ingesting. Idempotency keys on every event row so re-runs are safe.

Day 3: Read-only ingestion pipeline. Python or TypeScript worker polling the two APIs on a schedule, deduplicating against the idempotency key, writing to staging tables, then a transform step materializing canonical rows. Logging at every step. Reconciliation script comparing row counts between GHL/CallRail and the proprietary DB nightly, because silent drift is the most common ingestion bug at this stage. No write-back to GHL until the read path has been stable for at least two weeks.

**Q3 - Honest opinion on Claude Code and MCP:**

Useful, with caveats.

Claude Code is my main engineering agent day-to-day. The win is multi-file context: it reads the project, follows imports, and edits across files without me copy-pasting context into a chat window. Where it earns its keep is repetitive structural work (porting patterns, refactoring, documentation) and exploration of unfamiliar codebases. Where it falls down is anything requiring real architectural judgment under genuine constraints. It can produce a plausible plan but won't push back when the plan is wrong, so the human has to keep the bar.

MCP is the more interesting bet long-term. Right now the value is real but narrow: connecting Claude (or any MCP-capable client) to your actual systems via a standardized server interface so the agent can read your data, call your tools, and edit your state without bespoke per-tool integration code. For this build specifically, MCP is the right way to expose your GHL data, your CallRail transcripts, and your Postgres queries to the AI layer. One MCP server per data source, one client config, the agent gets typed tool access without me writing brittle per-prompt scaffolding. The hype is around what MCP enables in agentic workflows; the substance is the protocol replacing a lot of glue code. I'd push for MCP servers as part of the proprietary stack early, not late.

On the retrieval side, pgvector on top of the canonical Postgres is what I'd architect for transcript embedding and intelligence-synthesis queries. Concrete example for your build: every CallRail transcript chunked, embedded, and stored in pgvector with foreign keys back to owner_id and the behavioral_events row, so a query like "show me owners whose recent calls discuss redevelopment plans, refinancing pressure, or distress signals" becomes a semantic search + structured join rather than per-prompt keyword scraping or LLM context-stuffing. Honest note on fit: my production retrieval pattern in DevMatch is tool handlers + structured Postgres queries rather than embedding-based RAG at scale, so the pgvector layer at this build's volume is something I'd want to validate with you on real data before making throughput commitments.

**Q4 - Timezone and hours:**
Ukraine (EET / EEST), 4-7 hour overlap with US Eastern. Realistically 25-30 hrs/week in the next 30 days during the inventory + schema + ingestion sprint. Can taper to the 10-20 hrs/week steady-state once that's in place, scaling alongside the architecture decisions from the fractional CTO.

---

## 4. Real Estate Document Management Platform

**Freelancer:** Dmytro Mamaiev
**Rate:** $35/hr
**Format:** Single block
**Pitch angle:** Custom Twenty CRM app build (rather than from-scratch)

### Job text

I have a Figma mock-up for a real estate investments holding platform. I need a freelancer to develop a platform that can manage all relevant files across different lifecycles of real estate investments. The platform should be user-friendly and efficient in handling document management tasks.

I also need a non-live landing page to access the tool.

Less than 30 hrs/week, Hourly, 1-3 months. Intermediate.

### Mandatory skills

Administrative Support, Microsoft Word (mis-tagged by Upwork template)

### Our proposal

Hi,

Real estate investment file management is the kind of build where the from-scratch route burns the budget on auth, permissions, file storage, custom views, and audit trails before anyone touches the actual domain logic. There's a faster path: I'd build it as a custom Twenty CRM app. Twenty is open-source (MIT licensed, self-hostable) and gives you all of that out of the box. I'd configure custom objects for your domain (deals/holdings, properties, document categories, parties, lifecycle stages), match your Figma in the custom views, and ship the non-live landing page as a separate static page. You own the database, the code, and the deployment from day one. No SaaS lock-in, no per-seat fees as the team grows.

What this looks like in practice: custom objects in Twenty for the entities you actually have, custom fields and relations that mirror your real estate workflow rather than a generic CRM, file uploads scoped to deals and lifecycle stage with audit trail and per-user permissions, custom views matching your Figma layout (kanban for deal stages, list for documents, detail panes for each entity), plus the separate static landing page deployed alongside.

Why I'm credible for this stack:

DevMatch (https://github.com/dima-mamaev/devMatch_frontend and https://github.com/dima-mamaev/devMatch_backend). NestJS GraphQL + PostgreSQL + React, the exact stack Twenty is built on. TypeScript end-to-end, custom GraphQL schemas, real-time subscriptions, file uploads, permissions. Public GitHub.

Revvedup (https://revvedup.ai/). Workflow automation for sales and marketing teams. Task queues, event-triggered actions, dashboard for tracking progress, tight external-system integration. Same pattern as your real estate lifecycle workflow with documents instead of leads.

CVMaker (https://www.cvmaker.uk/). 1M+ user product I contributed to. Infrastructure that holds up under real consumer volume.

Stepler (https://www.steplerapp.com/). 10M+ user fitness platform with behavioral event tracking and AI microservices. PostgreSQL, MongoDB, Python FastAPI under heavy load.

I'm also currently contributing to a multi-agent AI operating system build (LangGraph + FastAPI + PostgreSQL, modular workflows for sales, marketing, HR, and software-delivery estimation). When the next phase of your platform wants AI on top of the document store (extract lease terms automatically, summarize a deal's document state, flag missing artifacts per lifecycle stage), those patterns are already familiar.

Process: week 1 inventory of your Figma against Twenty's primitives (which screens map to built-in views, which need custom builds). Weeks 2-3 custom objects, fields, relations, file handling, and permissions tied to the lifecycle. Week 4 custom views matching the Figma pixel-close where Twenty allows, with honest flagging where it doesn't. Landing page deployed in parallel.

Dmytro
Senior TypeScript / Full-Stack Developer

---

## 5. Mobile App Developer for Consumer App (Household/Family Organization)

**Freelancer:** Dmytro Mamaiev
**Rate:** $30/hr (top of $15-30 range)
**Format:** Single block

### Job text

Early-stage consumer mobile app focused on household/family organization. Looking for a skilled mobile app developer to create user-friendly and efficient apps for consumer use. Responsibilities include developing core features, ensuring smooth user experience, and collaborating with the team.

Interest in working with someone who has experience with consumer app monetization, user engagement, and long-term app growth. Experience with subscription models, user retention, or strategies for generating revenue from mobile apps is a plus.

Less than 30 hrs/week, Hourly, 1-3 months. Intermediate.

### Mandatory skills

Mobile App Development, Android App Development (iOS nice-to-have)

### Our proposal

Hi,

Household and family organization is a strong consumer-app shape. Daily habit, real value, lots of natural retention surfaces (shared lists, reminders, role-based access for kids vs parents, family calendar). The harder part is what you flagged at the end: making the monetization, retention, and growth actually work without breaking the early-stage user experience.

I've been on a consumer app that lived through exactly that problem. Stepler (https://www.steplerapp.com/) is Sweden's #1 fitness app, 10M+ users. Users walk to earn points, optionally watch ads for extra points, then spend points in a marketplace of partner offers. Three monetization channels (ads, marketplace partner revenue, premium tiers) layered on a daily-habit core. React Native + Flutter clients, Node/NestJS GraphQL backend, Python (FastAPI) AI microservices for personalization, MongoDB. The MongoDB layer was optimized with input from the MongoDB core team after we hit 10M downloads.

What I'd bring: specific patterns from a consumer app that scaled past 10M users with monetization and retention layered on the core, rather than bolted on at growth-crisis time.

What I'd want to know before scoping firmly: what stack you're already on (Flutter, React Native, native iOS + Android, brownfield or greenfield), what your monetization wedge is (subscription, marketplace, ads, freemium), and what the team you'd be collaborating with already has built. Those three answers change the scope and timeline meaningfully.

Dmytro
Senior Full-Stack / Mobile Developer

---

## 6. Full Stack Developer (Webflow + WordPress Roster)

**Freelancer:** Vadim Balabukha
**Rate:** $45/hr
**Format:** Separate-blocks (5 questions)
**Client identified:** Richard "Rich" Valtr / Structure (London branding agency)

### Job text

Full service brand agency looking for full stack developers to join roster and support multiple projects over coming months.

Looking for experienced developers who specialise in both Webflow and WordPress, with substantial portfolio across multiple industries including retail, fintech and SaaS.

Fast growing team, responsive communication, fast deliveries. Work range: small day-to-day fixing and update tasks to full-scale website builds. Client-facing and fluent in English (team calls with key clients).

Apply questions:
1. Approach to testing and improving QA.
2. Frameworks worked with.
3. GitHub profile and/or website.
4. Certifications.
5. Recent experience with similar projects.

### Mandatory skills

Website Redesign, Google Analytics, Web Development, JavaScript, CSS, WordPress, API Integration, Webflow, HTML

### Our proposal

**Cover letter:**
Hi Rich,

Caught your post. Honest flag upfront: my deep specialty is WordPress and full-stack custom development, not Webflow. If Webflow is a mandatory must-have for every roster member I'll step aside, but if WordPress + custom build work covers a meaningful share of the roster's day-to-day I'd be a strong fit. Detailed answers to your five questions below.

Vadim
Senior Full-Stack Developer (Node.js / React / Angular / WordPress)

**Q1 (QA approach):**
I treat QA as part of the build, not a phase after it. Unit tests where logic is non-trivial (auth flows, business rules, integration boundaries), integration tests at the API contract level for anything that touches external systems, end-to-end tests on the critical user paths (sign-up, checkout, primary flow). For WordPress specifically, I lean on browser-level regression testing via Playwright or Cypress for theme and plugin changes, because the WordPress ecosystem makes silent breakage especially common after a plugin update. CI pre-deploy on a staging environment that mirrors prod data shapes, with rollback playbooks documented before anything ships to live.

**Q2 (Frameworks):**
Backend: Node.js, NestJS, Express, Moleculer (microservices), Python FastAPI for AI microservices, WordPress / PHP.
Frontend: React, Next.js, Angular, Ionic (cross-platform mobile).
Data: PostgreSQL, MongoDB, Firestore, GraphQL.
DevOps: Docker, CI/CD via GitHub Actions and similar, Google Cloud, deployment automation.

**Q3 (GitHub/site):** [agency site or freelancer-provided link]

**Q4 (Certifications):**
No formal certifications specific to Webflow or WordPress. My credential is shipped product across regulated fintech, edtech, and consumer-scale platforms.

**Q5 (Recent similar work):**
Ministik School (https://mfidsab.ca/). Full-stack educational platform with WordPress and a companion Ionic mobile app, Firebase backend. Worked directly with the school's administration through delivery.

Ginmon (https://www.ginmon.de/). Fintech / wealth-tech build for a German robo-advisor with ~€400M AUM, BaFin-regulated. Complex KYC, video-ident onboarding, custody account integration with partner bank. Direct fintech experience with European clients. WordPress marketing surfaces with custom API integration into the regulated platform.

Mentormatic (https://mentormatic.com/). AI-powered mentoring SaaS platform with psychosocial-based matching, KPI tracking, calendar and chat. Node.js microservices on Moleculer, Google Cloud, Firestore.

Stepler (https://www.steplerapp.com/). Backend optimization on Sweden's #1 fitness app, 10M+ users. MongoDB optimization that the core MongoDB team validated during on-site training and consultations.

That covers fintech (Ginmon), SaaS (Mentormatic), edtech (Ministik), and consumer scale (Stepler). The retail vertical from your list I'd be picking up new, but the patterns transfer cleanly from the others.

---

## 7. Next.js / Supabase Lead Developer (Maritime Crew Marketplace)

**Freelancer:** Dmytro Mamaiev
**Rate:** $45/hr (above $15-35 range, with honest rate justification)
**Format:** Single block

### Job text

Live, paying-customer crew marketplace platform in the maritime industry built on Next.js (Vercel) and Supabase/PostgreSQL. Product is functional but has accumulated technical debt, unresolved security gaps, and UX friction.

Senior full-stack developer to begin with structured audit, then move into ongoing monthly engagement.

Audit scope: security posture (RLS policies, Next.js API route session enforcement, Supabase anon key exposure, Realtime table policies, Cloudflare proxy/bot protection); identified bugs and UX friction; missing or incomplete features (40% implementation of existing Anti-Scraper & Security Spec v1.1); prioritized fix list with effort estimates.

Following audit: one developer who owns the platform — not a task executor, someone who reads the spec, understands product goals, flags issues unprompted.

Stack: Next.js on Vercel, Supabase/PostgreSQL, Stripe, Cloudflare, GoHighLevel (light familiarity is a plus, not required).

Apply with: brief description of a Next.js/Supabase project you've shipped, how you'd approach auditing an existing codebase you've never seen, preferred audit format and deliverable, proposed rate.

### Mandatory skills

Next.js, Vercel, PostgreSQL, Supabase

### Our proposal

Hi,

Caught your post. Maritime crew marketplace on Next.js + Supabase with RLS, session enforcement, anti-scraper gaps, and a Stripe + Cloudflare surface is a senior-flavoured engagement, not an intermediate one. I'll be honest about that in the rate question below.

**1. Brief description of a Next.js / Supabase project I've shipped:**

Honest flag upfront: my deepest production marketplace work is on DevMatch (https://github.com/dima-mamaev/devMatch_frontend and https://github.com/dima-mamaev/devMatch_backend), a two-sided talent marketplace (developers on one side, recruiters and founders on the other) built on Next.js 16 App Router + NestJS GraphQL + PostgreSQL + Auth0 + Redis, not Supabase. The architectural patterns map directly: Postgres with row-level access control (TypeORM + per-tenant scoping equivalent to Supabase RLS), Auth0 session enforcement at the API layer (equivalent to Supabase Auth + Next.js middleware enforcement), GraphQL subscriptions for realtime (equivalent to Supabase Realtime), per-user rate limits in Redis (operational abuse-control patterns). Public on GitHub so you can read the architecture before we talk. If Supabase specifically is a hard must-have over architectural fit, I'd be coming up the Supabase-specific curve in the first sprint while applying production marketplace patterns from day one.

**2. How I'd approach auditing an existing codebase I've never seen:**

Three passes, each producing artifacts you can read without me on the call.

Pass 1, Map. Read top-to-bottom for two days: directory structure, dependency graph, env vars and what they protect, Next.js route inventory (server vs client components, API routes, middleware), Supabase schema and migrations (tables, RLS policies, function definitions), Stripe webhook receivers, Cloudflare and DNS configuration. Output: a system-map document describing what exists in plain language.

Pass 2, Probe. Targeting your stated concerns specifically. RLS policies enumerated and tested with fixtures (insert as user A, assert no row reaches user B's queries). Next.js API route session enforcement audited (every route gets a checklist entry: is auth enforced, what's the failure mode if it's not). Supabase anon key surface area mapped (where is it exposed, what can a holder do). Realtime table policies checked (which tables broadcast, to whom, with what filters). Cloudflare proxy and bot protection state confirmed against your spec. Output: a security-posture document, severity-tagged.

Pass 3, Gap assessment against your Anti-Scraper and Security Spec v1.1. Item by item: spec'd, implemented (the 40% baseline), how I'd verify implementation, what's missing, effort estimate per missing item. Output: a prioritized fix list with effort estimates in hours.

**3. Preferred audit format and deliverable:**

Three markdown documents committed to a private branch of your repo (or shared via Notion or Google Docs if you prefer): SYSTEM_MAP.md, SECURITY_POSTURE.md, GAP_AND_FIX_LIST.md. Plus a one-hour walkthrough call where I show you the most important findings and we agree on the first three fixes to ship. Timeline: 8-10 working days for the audit deliverables.

**4. Proposed rate:**

$45/hr. That's above the $15-35 range you posted, and I'll be straight about why. The scope (senior security audit plus ongoing platform ownership on Next.js + Supabase + Stripe + Cloudflare + marketplace) is senior work. At $45/hr I'm well-priced against the EU and UK senior market for this stack ($60-90/hr typical) while honest about the architectural patterns coming from PostgreSQL + Auth0, not Supabase specifically. Open to a fixed monthly retainer post-audit once we've agreed on the prioritized fix list.

Dmytro
Senior Full-Stack Developer (Next.js, NestJS, PostgreSQL, GraphQL, Auth0)

---

## Patterns this set shows

1. **Honest gap flag works.** Q1 in Yevhen's Supabase proposal and Q1 in Dmytro's maritime proposal both opened with the gap. The brief is more credible because of it, not less.
2. **Lead with the architectural primitive, not the brand.** "postgres_changes vs broadcast" and "RLS + Postgres + GraphQL subscriptions = Supabase Auth + Realtime" beat name-dropping.
3. **Custom Twenty CRM pitch.** When the budget can't sustain from-scratch, propose a foundation. Real Estate Document Management at $35/hr cap is impossible from scratch, very possible on Twenty.
4. **Stepler is the consumer-monetization-at-scale answer.** Used for both the mobile household app pitch (monetization patterns) and the multiple-portfolio listings (10M+ users).
5. **DevMatch is the marketplace + production-engineering answer.** Two-sided pattern, Next.js + NestJS + Postgres + GraphQL + Auth + realtime — pattern-recognized across many proposals.
6. **Rate justification when above range.** $45/hr against $15-35 with explicit market comp ("$60-90/hr typical EU and UK senior") reads honest, not greedy.
7. **No em-dashes anywhere.** Colons, periods, parens, hyphens, comma + clause — all the substitutes preserve flow without falling into AI-tell punctuation.
8. **Sign-off with name + short title.** No "Best regards," no exclamations, no emojis.

---

## Want more?

This compilation has 7 proposals with full job context preserved. To grow to 20:
- Pull 13 more from `/Users/2mc/projects/2mc_upwork/proposals/drafts/` (older drafts; job context may be partial or missing — would need to reconstruct)
- Pull from won contracts under `/Users/2mc/projects/2mc_upwork/contracts/` (contract.yaml has rate + skills but no proposal text)
- Mine the freelancer-specific stories under `/Users/2mc/projects/2mc_upwork/stylistic_requirements/stories/` for additional pattern examples

Ask if you want any of those added.
