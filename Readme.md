<p align="center">
  <img src="https://zane-nostalgia.kiyo-n-zane.com/scenes/rainy/api?bannerText=Ankit+Arsh&height=400&density=14&geoSeed=dvYg8ozYGW"/>
</p>

<!-- ========================= -->
<!--        STATS              -->
<!-- ========================= -->

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/AnkitArsh19/AnkitArsh19/main/dark_mode.svg">
    <img alt="Ankit Arsh's GitHub Stats" src="https://raw.githubusercontent.com/AnkitArsh19/AnkitArsh19/main/light_mode.svg">
  </picture>
</div>

<hr style="border: none; border-top: 1px solid #30363d; margin: 2em 0;" />

<!-- ========================= -->
<!--        INTRO              -->
<!-- ========================= -->

<p style="color: #9aa0a6; max-width: 700px;">
Backend-focused engineer interested in how complex systems work beneath the surface.
</p>

<p style="max-width: 750px;">
I care about <b>why systems behave the way they do</b>, how design decisions scale over time,
and where abstractions start to leak.
</p>

<p style="max-width: 750px;">
Most of my work revolves around <b>Java and backend development</b>. I'm comfortable with frontend,
but backend aligns more naturally with how I think: APIs, data flow, state management,
performance trade-offs, and architectures that don't collapse as requirements evolve.
I'm still learning, but I'm serious and methodical about it, and I prefer depth over speed.
</p>

<hr style="border: none; border-top: 1px solid #30363d; margin: 2em 0;" />

<!-- ========================= -->
<!--        PROJECTS           -->
<!-- ========================= -->

<h3>Projects</h3>

<h4>YapLab</h4>

<p style="max-width: 750px;">
  <a href="https://yaplab.ankitarsh.me"><b>Live App</b></a> &nbsp;•&nbsp;
  <a href="https://github.com/AnkitArsh19/yaplab-app"><b>Repository</b></a>
</p>

<p style="max-width: 750px;">
<b>YapLab</b> is a backend-driven messaging application built with Spring Boot.
It was designed to be simple in scope, but realistic in behavior.
</p>

<p style="max-width: 750px;">
The system supports core messaging features such as text messages, file sharing,
emojis, audio messages, group chats, read receipts, typing indicators,
and message state handling.
</p>

<p style="max-width: 750px;">
YapLab does <b>not</b> implement end-to-end encryption.
Instead, it focuses on foundational backend security practices such as
password hashing, JWT-based authentication on every request,
and controlled access to resources.
</p>

<p style="max-width: 750px;">
The primary learning outcome was not feature delivery, but understanding
how messaging systems behave: delivery semantics, state transitions,
data modeling, and API design that remains flexible.
</p>

<p style="color: #9aa0a6; max-width: 750px;">
YapLab is no longer actively developed. I reached a point where further work would
mostly be polishing, and I chose to move on to problems that required new architectural thinking.
</p>

<br/>

<h4>Crescendo</h4>

<p style="max-width: 750px;">
  <a href="https://app.crescendo.run"><b>Live Platform</b></a> &nbsp;•&nbsp;
  <a href="https://app.crescendo.run/docs"><b>Documentation & API</b></a> &nbsp;•&nbsp;
  <a href="https://github.com/AnkitArsh19/crescendo"><b>Repository</b></a> &nbsp;•&nbsp;
  <a href="https://github.com/AnkitArsh19/crescendo-sdk"><b>SDK Ecosystem</b></a> &nbsp;•&nbsp;
  <a href="https://github.com/AnkitArsh19/crescendo/releases/tag/v1.0.3"><b>Desktop App (v1.0.3)</b></a>
</p>

<p style="max-width: 750px;">
<b>Crescendo</b> is an enterprise-grade workflow automation platform spanning 114+ application integrations, an autonomous agentic AI runtime, native desktop clients, and a full ESP-grade transactional email infrastructure.
</p>

<p style="max-width: 750px;">
I built Crescendo as an architectural deep-dive to explore distributed systems challenges beyond standard CRUD: asynchronous queue processing, state machines, consensus and distributed locks, fault tolerance, and platform-level extensibility.
</p>

<p style="max-width: 750px;">
<b>Architectural Highlights:</b>
</p>

<ul style="max-width: 750px; line-height: 1.6; padding-left: 20px;">
  <li>
    <b>DAG Execution & Edge-State Routing:</b> Built a graph execution engine utilizing Kahn's algorithm for topological ordering. State transitions belong to discrete graph edges (<code>ST_PENDING</code>, <code>ST_COMPLETED</code>, <code>ST_SKIPPED</code>) enabling natural skip cascading across conditional branches (If/Else, Switch), deterministic merge joins (<code>logic:merge</code>), and deep recursive expression resolution with native JSON type preservation.
  </li>
  <li>
    <b>Distributed Reliability Primitives:</b> Architected on <b>CQRS</b> and an <b>Event-Driven Architecture</b> with a Transactional Outbox pattern (pessimistic locking) to ensure atomic publish-after-commit delivery. Stream processing runs on <b>Redis Streams</b> with consumer groups and explicit manual ACK for critical paths, backed by a background Pending-Entry List (PEL) reaper to reclaim zombie messages after consumer crashes, Dead Letter Queues (DLQ) with exponential backoff, and distributed locks with atomic Lua heartbeat lease extension.
  </li>
  <li>
    <b>Autonomous Agentic AI Runtime (<code>crescendo-aiml</code>):</b> Powers both design-time workflow generation and run-time execution. Features a multi-provider <b>ReAct (Reason → Act → Observe)</b> agentic loop (Google Gemini, Groq, OpenAI) dynamically synthesizing OpenAPI / JSON Schema tool definitions across 111+ apps, sub-workflow execution under distributed locks, XML output guarding against prompt injection, and a direct native Java REST fallback ensuring high availability if the Python service is unreachable.
  </li>
  <li>
    <b>Built-in Transactional Email Platform (ESP):</b> Implemented a 5-layer deliverability engine with strict SPF/DKIM/DMARC identity binding, multi-provider BYOK (SendGrid/SES fallback), automated 48-hour warming rate governance, a centralized Send Decision Gate with draft-time spam heuristics, and RFC 8058 compliant <code>List-Unsubscribe</code> headers. Supported by an 8-language universal SDK ecosystem (handwritten Node.js & Python SDKs; auto-generated Java, Go, Rust, C#, PHP, Ruby SDKs isolated via an ephemeral CI pipeline).
  </li>
  <li>
    <b>Cryptographic Erasure (Crypto-Shredding):</b> Solved the Write-Ahead Log (WAL) and immutable backup paradox (GDPR Article 17) where standard database deletes leave plaintext credentials in cold S3 backups. Implemented two-tier envelope encryption (per-user DEKs encrypted under a master KEK); destroying the user's DEK renders all historical backup ciphertext pure entropy in <i>O(1)</i> time, orchestrated through a strict 9-phase purge cascade.
  </li>
  <li>
    <b>Native Desktop Security (RFC 8252):</b> Engineered a lightweight native desktop application (&lt;15 MB, ~35-45 MB RAM) using <b>Tauri v2 and Rust</b>. Implemented OAuth 2.0 Best Current Practice for Native Apps: system browser authentication (zero embedded webviews), biometric Passkeys/WebAuthn, single-use 60-second handoff codes, zero token leakage in deep links (<code>crescendo://</code>), and single-instance OS process interception.
  </li>
  <li>
    <b>Performance & Concurrency Hardening:</b> Architected on <b>Java 25 and Virtual Threads</b> (using <code>Thread.ofVirtual()</code> for schedulers and lock heartbeats to eliminate OS thread pool exhaustion), strict HikariCP zero-OSIV boundaries to prevent connection leaks, 100-thread concurrent in-memory race-condition validation, and native PostgreSQL full-text search (<code>tsvector</code>/<code>pg_trgm</code>) with 5-second batched Redis metric rollups.
  </li>
</ul>

<p style="color: #9aa0a6; max-width: 750px;">
<b>Status:</b> Version 1.0 (v1.0.3) is released and running live in production. Core workflow orchestration, native desktop clients, transactional email delivery, and the AI agent runtime are fully operational, with continuous improvement focused on catalog expansion and performance optimizations.
</p>

<hr style="border: none; border-top: 1px solid #30363d; margin: 2em 0;" />

<!-- ========================= -->
<!--     HOW I LEARN           -->
<!-- ========================= -->

<h3>How I Learn and Work</h3>

<p style="max-width: 750px;">
I learn best by first understanding ideas through clear explanations,
often from videos or documentation, and then implementing them myself.
Building things, breaking them, and fixing what went wrong has been far
more valuable than passively consuming information.
</p>

<p style="max-width: 750px;">
AI plays a big role in my learning process as a second brain I can question deeply,
especially around edge cases and design decisions.
That said, implementation remains the final test.
Writing imperfect code once has taught me more than reading perfect explanations repeatedly.
</p>

<hr style="border: none; border-top: 1px solid #30363d; margin: 2em 0;" />

<!-- ========================= -->
<!--     TECHNICAL FOCUS       -->
<!-- ========================= -->

<h3>Technical Focus</h3>

<p style="max-width: 750px;">
<b>Core:</b> Java (21/25, Virtual Threads), Spring Boot 4, Distributed Systems, Event-Driven Architecture (Redis Streams, Transactional Outbox), Relational Databases (PostgreSQL), System Design & Reliability Engineering<br/>
</p>


<!-- ========================= -->
<!--        DIRECTION          -->
<!-- ========================= -->

<h3>Direction</h3>

<p style="max-width: 750px;">
This profile reflects how I think and work at the moment, not a finished state.
Over time, I want this page to clearly show growth: deeper understanding,
better architectural decisions, and systems that are built with intention
rather than habit.
</p>

<hr style="border: none; border-top: 1px solid #30363d; margin: 2em 0;" />

<!-- ========================= -->
<!--       MEDIUM BLOGS        -->
<!-- ========================= -->

<h3 style="margin-bottom: 0.5em;">Writing</h3>

<p style="max-width: 750px; color: #9aa0a6; margin-bottom: 0.5em;">
I occasionally write about backend systems and architecture to clarify my own thinking.
A couple of recent pieces are linked below.
</p>

<div style="display: flex; gap: 16px; flex-wrap: wrap;">
  
  <a target="_blank" href="https://github-readme-medium-recent-article.vercel.app/medium/@ankitarsh19/0">
    <img 
      src="https://github-readme-medium-recent-article.vercel.app/medium/@ankitarsh19/0"
      alt="Recent Medium Article 0"
      width="500"
      height="70"
      style="border-radius: 8px;"
    />
  </a>

  <a target="_blank" href="https://github-readme-medium-recent-article.vercel.app/medium/@ankitarsh19/1">
    <img 
      src="https://github-readme-medium-recent-article.vercel.app/medium/@ankitarsh19/1"
      alt="Recent Medium Article 1"
      width="500"
      height="70"
      style="border-radius: 8px;"
    />
  </a>
</div>


