# Publishing playbook

Step-by-step for getting `blog-post-final.md` in front of people. Pick the venues that match where the audience you want already reads.

## Pre-publish checklist (5 minutes)

- [ ] Skim `blog-post-final.md` one more time aloud — any awkward sentences become obvious
- [ ] Make sure the README screenshot URL renders correctly on github.com
- [ ] Verify [`runs/baseline/FINDINGS.md`](../../runs/baseline/FINDINGS.md) is up to date with v0.2 numbers
- [ ] Confirm the GitHub release for v0.2.0 has release notes (it does — created when you tagged)
- [ ] Optional: add the hero SVG (`docs/assets/cli-demo.svg`) to the blog post as a featured image

## Venue priorities, by ROI

### Tier 1 — Highest ROI for portfolio impact

**1. Your personal site / domain** (if you have one — or set up a quick one).

This is the canonical version. Every other venue should link back here. If you don't have a personal site yet, the simplest options:
- **GitHub Pages** — free, lives at `desledishant10.github.io`. Single Markdown file → published in 10 minutes. Best for a developer-coded portfolio.
- **Vercel + a starter template** — `next-mdx-blog` or `astro-starter`. 30 minutes to deploy. Gives you a real site for future posts.

Why this matters for the portfolio: a recruiter clicking "blog" on your resume lands on your domain, not a third-party platform.

**2. Hacker News submission**

Title suggestion (test both, see which gets traction):
- `Vex: an agent-first AI red team tool, and what calibration mistake taught me about red-teaming`
- `12 vulnerabilities, 11 of them mine — building an AI red-team tool and watching it lie to me`

Submission URL is the GitHub repo (`https://github.com/desledishant10/vex`), not the blog post — HN audience tends to convert better when the click goes straight to the code. Drop the blog post link in the first comment.

Post timing: Tuesday-Thursday between 9am and 11am Eastern is the sweet spot for the technical audience.

Be ready to engage. The first hour of comments determines whether the post survives. Expect questions like:
- "Doesn't Garak already do this?" → see comparison in README + the v0.2 thread
- "Doesn't Microsoft PyRIT already do this?" → similar; you're agent-first / context-aware, they're not
- "Did you disclose to Anthropic?" → yes, see `docs/disclosures/`
- "Where's the LLM-judge implementation?" → `src/vex/detectors/llm_judge.py`

### Tier 2 — Broad reach, lower per-reader value

**3. Twitter / X**

Use [`twitter-thread-v02.md`](twitter-thread-v02.md) — 14 tweets, calibration-arc framing. Post around 9am or 4pm Eastern, weekday. Quote-tweet from your own account once a day for the first two days with new context (e.g. day 2: "Just got the first PR contribution from a stranger" or "Anthropic acknowledged the disclosure").

Tag: `@simonw` (Simon Willison covers AI security extensively and amplifies thoughtful work), `@AnthropicAI` (for the disclosure framing), `@HiddenLayerSec`, `@protectai`, `@LakeraAI` (peers in the space who may engage).

**4. LinkedIn**

Post a condensed version (3-4 paragraphs) of the blog with the GitHub link. LinkedIn's algorithm rewards posts that drive comments, not link-outs — so structure it as a question or strong claim that invites discussion. Something like:

> "I built an AI red-team tool. The first time I ran it against Claude, it told me 67% of my probes had succeeded.
>
> Most of those were false positives in my own detectors.
>
> Fixing them taught me more about red-team tooling than the 6% real finding did. The full story:
> [link]
>
> If you do AI security, what's the one calibration mistake you've seen kill a tool's credibility?"

The genuine question at the end is what gets it in the LinkedIn feed.

### Tier 3 — Domain-specific reach

**5. r/LocalLLaMA, r/MachineLearning, r/cybersecurity**

Markdown posts work natively. Tag with `[Project]` or `[Open Source]`. r/MachineLearning is strict about self-promotion — only post there if you can honestly frame it as a methodology contribution (the calibration story qualifies; "look at my tool" doesn't).

**6. dev.to / Medium / Substack** (mirror copies)

Don't make these primary — they're SEO-positive mirrors. Canonical URL points back to your personal site or the GitHub repo. Cross-post 1-2 weeks after the main launch so each gets fresh discovery.

**7. Newsletters**

Three names worth a polite cold email with the post:
- **Simon Willison's Weblog** (`simonw@gmail.com` or via his contact form)
- **TLDR Sec** (Clint Gibler) — `clint@tldrsec.com` — actively covers AI security tooling
- **The Pragmatic Engineer** (Gergely Orosz) — if you can frame it as a "what I learned shipping" piece

Subject template: "Vex 0.2 calibration story — might fit TLDR Sec readers"
Body: 3 sentences max. Lead with the calibration arc, link the post, mention the open-source angle.

### Tier 4 — Long-term plays (skip for now, revisit later)

- Workshop paper at NeurIPS/USENIX safety tracks (3-4 months of work)
- Conference talk (BSides / DEF CON / Black Hat)
- Podcast: SANS Internet Stormcenter, Risky Business, ThursdAI

## Post-launch follow-up moves

These are higher-effort but compound the original post:

**1. The Anthropic response.** When Anthropic acknowledges/disposes the disclosure (Tier 1 item from the previous round), publish a short follow-up: "Anthropic responded to my reversed-text encoding disclosure. Here's what they said." The follow-up is its own micro-post and re-promotes the underlying work.

**2. Cross-vendor comparison.** Run v0.2 against `gpt-4.1` and `gemini-2.5-pro`. Each new model produces:
- A new `runs/baselines/` artifact
- A new short blog post comparing refusal patterns / vulnerability surfaces across labs
- A reason to re-tweet the original thread with new data

**3. First contribution.** When someone files a PR or a substantive issue, post about it. "First external contribution to Vex this morning — patches the X attack family. Open source is wild."

**4. Ship issue #1 (MCP adapter) and write the launch post.** This is the bridge between Vex and your MCP-Scan capstone — single biggest compound-credibility move available.

## How to know it worked

Lagging indicators (these tell you whether the post moved anything):
- **GitHub stars** — 50+ in first week is real engagement, 200+ is the post landed
- **Issues opened by strangers** — even one is meaningful for credibility
- **Inbound recruiter DMs** referencing the project specifically (not just "saw your profile")
- **Citations** in other people's blog posts or papers about AI red-teaming
- **PRs from non-you** within 6 weeks

Track these for ~30 days. If you get traction, the next post writes itself (one of the follow-up moves above). If not, the artifact still exists and your portfolio link is still strong.

## Anti-patterns to avoid

- **Don't oversell.** The honest calibration framing is the strength. If you write the blog post as "I broke Claude", anyone who reads carefully spots it instantly and the post loses credibility.
- **Don't dunk on Garak/PyRIT/Promptfoo.** The comparison in the README is factual and unbiased; the blog post says they're "good tools and you should use them." Keep it that way. The maintainers of those tools have networks you might want to join later.
- **Don't post and ghost.** Engage with comments for at least the first 24 hours on every venue. Especially on HN, where engagement determines whether the post survives the first page.
- **Don't link-spam your own post.** One post per venue, spaced 1-2 weeks apart. Tweeting "blog post about Vex!" five times in a week is how you get unfollowed.
