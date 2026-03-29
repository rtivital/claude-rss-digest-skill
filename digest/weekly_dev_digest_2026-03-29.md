# Weekly Dev Digest — 2026-03-29

_88 articles collected · 20 selected as relevant_

## AI Tooling

### Auto Mode for Claude Code
**Source:** Simon Willison's Blog · [Read →](https://simonwillison.net/2026/Mar/24/auto-mode-for-claude-code/#atom-everything)

Claude Code introduced "auto mode" as an alternative to `--dangerously-skip-permissions`. A separate Claude Sonnet 4.6 classifier reviews each action before execution, blocking anything that escalates beyond task scope or appears driven by hostile content. You can customize the default filters with your own rules — a meaningful step toward safer agentic workflows.

---

### Anatomy of the .claude/ Folder
**Source:** Hacker News (Best) / Daily Dose of DS · [Read →](https://blog.dailydoseofds.com/p/anatomy-of-the-claude-folder)

A comprehensive walkthrough of Claude Code's `.claude` folder structure: CLAUDE.md for project instructions, rules/ for scoped conventions, commands/ for custom slash commands, skills for auto-triggered behaviors, and agents for specialized subagent personas. A useful reference for anyone optimizing their Claude Code setup.

---

### LiteLLM Supply Chain Malware Attack
**Source:** Simon Willison's Blog · [Read →](https://simonwillison.net/2026/Mar/26/response-to-the-litellm-malware-attack/#atom-everything)

Callum McMahon documented his minute-by-minute response to discovering malicious code in `litellm==1.82.8` on PyPI — a `.pth` file that executed base64-encoded payloads on install. He used Claude to confirm the vulnerability in an isolated Docker container and identify the right reporting channel. A sobering reminder about supply chain trust.

---

### Package Managers Need to Cool Down
**Source:** Simon Willison's Blog · [Read →](https://simonwillison.net/2026/Mar/24/package-managers-need-to-cool-down/#atom-everything)

Prompted by the LiteLLM attack, a review of dependency cooldown mechanisms across package managers. pnpm 10.16, Yarn 4.10.0, Bun 1.3, Deno 2.6, and uv all now support `minimumReleaseAge` or equivalent — letting you delay installing freshly-published packages until the community has had time to vet them. Worth enabling in your projects.

---

### Vibe Porting JSONata to Go with AI — Saved $500K/Year
**Source:** Simon Willison's Blog · [Read →](https://simonwillison.net/2026/Mar/27/vine-porting-jsonata/#atom-everything)

A case study of AI-assisted "vibe porting": rewriting the JSONata JSON expression language from JS to Go in 7 hours and $400 of tokens, validated by the existing test suite and a week of shadow deployment. The key enabler was comprehensive tests, not the AI itself — a pattern worth noting for similar migration projects.

---

### Architecture Thinking in the Age of Agentic Coding
**Source:** Simon Willison's Blog (quoting Matt Webb) · [Read →](https://simonwillison.net/2026/Mar/28/matt-webb/#atom-everything)

Matt Webb argues that as agentic coding tools grind problems into dust via brute force, the human value shifts to architecture: designing great libraries with interfaces that make the "right" way the easy way. "I am looking at lines of code less than ever before, and thinking about architecture more than ever before."

---

### Streaming Experts: 1T Parameter Models on Consumer Hardware
**Source:** Simon Willison's Blog · [Read →](https://simonwillison.net/2026/Mar/24/streaming-experts/#atom-everything)

Researchers are running massive Mixture-of-Experts models on consumer hardware by streaming expert weights from SSD per token. Kimi K2.5 (1 trillion parameters) now runs in 96GB RAM on an M2 Max MacBook Pro, and Qwen3.5-397B runs on an iPhone at 0.6 tok/s. The technique is rapidly improving via autoresearch optimization loops.

---

### How Anthropic's Claude Thinks
**Source:** ByteByteGo · [Read →](https://blog.bytebytego.com/p/how-anthropics-claude-thinks)

Anthropic's interpretability research reveals that Claude's internal computation diverges from its verbal explanations — arithmetic uses parallel estimation strategies rather than the carrying method it describes. Other findings: Claude thinks in language-independent concepts, plans rhyming words before writing poetry lines, and hallucinations occur when a "known entity" recognition circuit misfires on unfamiliar topics.

---

## JavaScript / TypeScript

### TypeScript 6.0 Released
**Source:** JavaScript Weekly / Node Weekly · [Read →](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/)

The biggest TS release in years, designed to bridge the gap to the Go-powered TypeScript 7.0 compiler. Key changes: `strict` now defaults to `true`, `module` defaults to `esnext`, `types` defaults to `[]` (no longer auto-including `@types/*`), and `rootDir` defaults to `.`. Deprecations include es5 target, AMD/UMD/SystemJS module emit, and `--baseUrl`. Use `--stableTypeOrdering` to preview 7.0 inference behavior now.

---

### Next.js 16.2: Faster Dev, Adapter API, AI Features
**Source:** This Week in React / JavaScript Weekly · [Read →](https://nextjs.org/blog/next-16-2)

Major performance release: ~400% faster `next dev` startup and ~50% faster rendering via React core RSC improvements. The Adapter API is now stable, letting platforms (Netlify, Cloudflare, AWS) customize the build process. Also adds `transitionTypes` for Links and new AI-focused features.

---

### GitHub Will Train on Private Repos Unless You Opt Out by Apr 24
**Source:** Hacker News (Best) · [Read →](https://news.ycombinator.com/item?id=47548243)

GitHub is auto-opting users into allowing training on private repositories. Opt out at github.com/settings/copilot/features before April 24, 2026. The HN thread (719 points, 310 comments) reflects widespread frustration with the default-on approach.

---

## Node.js

### Node.js Security Releases (March 24)
**Source:** Node.js Blog · [Read →](https://nodejs.org/en/blog/release/v25.8.2)

Security patches across all active lines: v25.8.2, v24.14.1, v22.22.2, and v20.20.2. Nine vulnerabilities addressed (two high severity) spanning TLS, HTTP/HTTP2, the permission model, HMAC verification, URL processing, and V8 hashing. Update promptly.

---

### Where Did 400 Megabytes of Memory Go?
**Source:** Node Weekly · [Read →](https://nodeweekly.com/issues/617)

A deep investigation into why a Node.js WebSocket pod on k8s consumed far more memory than peers, despite `process.memoryUsage()` showing normal values. Powerful debugging techniques for production Node memory issues worth bookmarking.

---

### pnpm 11 Beta
**Source:** Node Weekly · [Read →](https://nodeweekly.com/issues/617)

The next major version of pnpm introduces a SQLite-powered store, a config overhaul, and stricter build security by default. Worth testing early if pnpm is in your toolchain.

---

## Frontend / CSS

### The Great CSS Expansion: Replacing JS with Native Features
**Source:** Frontend Focus · [Read →](https://frontendfoc.us/issues/734)

A well-organized walkthrough of modern CSS features that replace JavaScript-dependent solutions — scroll-driven animations, container queries, `:has()`, `@layer`, and more. A solid checklist for identifying JS you can drop in favor of native CSS.

---

### Sneaky Header Blocker Trick
**Source:** Josh W. Comeau · [Read →](https://www.joshwcomeau.com/css/header-blockers/)

An elegant CSS-only technique for making a sticky header appear to change background color as you scroll between page sections. The header itself is transparent with `position: fixed`; colored sticky "blocker" elements behind it create the illusion of color transitions as they unstick at container boundaries.

---

### CSS is DOOMed: Rendering DOOM in 3D with CSS
**Source:** Hacker News (Best) · [Read →](https://nielsleenheer.com/articles/2026/css-is-doomed-rendering-doom-in-3d-with-css/)

A fully playable 3D DOOM rendered entirely through CSS transforms — walls via `atan2()`/`hypot()`, floors via `clip-path`, sprites via spritesheet positioning, and lighting via cascading custom properties. JavaScript handles game logic only. The performance solutions (frustum culling via animation-delay tricks) and browser limitation workarounds are technically fascinating.

---

### WebKit Features in Safari 26.4
**Source:** Frontend Focus · [Read →](https://frontendfoc.us/issues/734)

Safari 26.4 adds CSS Grid Lanes (the layout formerly known as Masonry), anchor positioning refinements, CSS zoom fixes, and math function support in `<img>` elements. A significant release for cross-browser CSS parity.

---

## React

### Test IDs Are an Accessibility Smell
**Source:** React Status / TkDodo · [Read →](https://tkdodo.eu/blog/test-ids-are-an-a11y-smell)

Dominik Dorfmeister argues `data-testid` masks accessibility problems — a button replaced with a clickable `div` still passes testid-based tests despite breaking keyboard nav and screen readers. Role-based selectors like `getByRole('button', { name: 'Open Widget' })` give you accessibility verification "almost for free." With the European Accessibility Act in effect, this matters more than ever.

---

### Name Your useEffect Functions
**Source:** This Week in React / Neciu Dan · [Read →](https://neciudan.dev/name-your-effects)

A practical argument for using named function expressions in `useEffect` instead of anonymous arrows. Beyond readability and stack traces, the key insight: struggling to name an effect without "and" reveals it handles multiple concerns and should be split. One real-world example reduced 5 effects to 3 after naming exposed redundancy.

---

## System Design

### How Netflix Live Streams to 100 Million Devices
**Source:** ByteByteGo · [Read →](https://blog.bytebytego.com/p/how-netflix-live-streams-to-100-million)

Netflix's Live Origin system sits between encoding and their CDN, running dual redundant encoding pipelines across regions. When one produces a bad segment, the other covers. After discovering S3 couldn't meet 2-second retry budgets, they built custom KV storage on Cassandra + EVCache, dropping median latency from 113ms to 25ms. Priority-based rate limiting ensures live edge traffic wins over DVR during load spikes.

---

### Cloudflare Uses ASTs to Visualize Workflow Diagrams
**Source:** Cloudflare Blog · [Read →](https://blog.cloudflare.com/workflow-diagrams/)

Cloudflare Workflows now shows visual step diagrams in the dashboard by parsing bundled TypeScript with `oxc-parser` (from the Oxidation Compiler) and mapping AST nodes to workflow types. They track `Promise` and `await` relationships to determine parallel vs. sequential execution. Plans to expand into real-time execution tracing and step-skipping for debugging.

---

### JavaScript Sandboxing Research
**Source:** Simon Willison's Blog · [Read →](https://simonwillison.net/2026/Mar/22/javascript-sandboxing-research/#atom-everything)

Inspired by a post on Node.js worker threads, a Claude Code research task produced a thorough comparison of JS sandboxing options: isolated-vm, vm2, quickjs-emscripten, QuickJS-NG, ShadowRealm, and Deno Workers. Useful reference if you're evaluating sandboxed JS execution in Node.
