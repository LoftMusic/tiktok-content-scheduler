---
name: youtube-optimizer
description: >
  Optimize YouTube videos for maximum views, CTR, and subscriber growth. Use when
  preparing a new video upload (title, description, tags, chapters, thumbnail strategy),
  analyzing video performance, or planning content strategy. Triggers on "YouTube",
  "video SEO", "thumbnail", "upload optimization", "video performance", "CTR",
  "watch time", "YouTube growth".
---

# YouTube Optimizer

## Video Upload Optimization Workflow

When you have a new video to upload:

1. **Extract frames** for thumbnail candidates (use ffmpeg or video-frames skill)
2. **Get transcript** (whisper or manual)
3. **Generate in parallel:**
 - 3 title options (curiosity gap + keyword + benefit)
 - SEO description (keyword-rich, timestamps, links)
 - 15-20 tags targeting search terms
 - Chapter timestamps from transcript
 - 3 thumbnail concepts
4. **Present options** to choose from

### Title Formula (Proven Patterns)
- `[Action] + [Result] + [Qualifier]` -- "I Built a Full SaaS App in 2 Hours (No Code)"
- `[Surprising Hook] + [Topic]` -- "This AI Agent Replaced My Entire Workflow"
- `[Number] + [Benefit]` -- "5 AI Tools That Actually Make You Money"
- Keep under 60 characters. Front-load keywords. Emotional/curiosity words boost CTR.

### Thumbnail Best Practices
- **Face + emotion** -- expressive reaction shot
- **3 elements max** -- Face, text overlay (2-4 words), visual prop
- **High contrast** -- Bold colors, readable at mobile size
- **Text overlay:** 2-4 words MAX, large font, contrasting outline

### Description Template
```
[Hook sentence with primary keyword]

[2-3 sentence summary of what the video covers]

Links:
[Lead magnet / tool links]

Chapters:
[Timestamp chapters from transcript]

Keywords in natural sentences for SEO

#hashtag1 #hashtag2 #hashtag3
```

### Tags Strategy
- Primary keyword exact match
- Long-tail variations ("build app with AI no code", "vibe coding tutorial")
- Competitor channel topics
- Trending adjacent terms
- 15-20 tags, mix of broad and specific

## Performance Analysis

When checking video/channel performance:
1. Pull stats via YouTube Data API v3 (read-only)
2. Compare against previous benchmarks
3. Identify what's working (high CTR, retention) vs underperforming
4. Give actionable recommendations

### Key Metrics to Track
- **CTR** -- Target 8%+, 12%+ is exceptional
- **Average view duration** -- Target 50%+ retention
- **Subscriber conversion** -- Views to subs ratio
- **Impressions** -- Algorithm reach indicator
- **Lead conversion** -- Views to email signups (via UTM tracking)

## Content Strategy

### Posting Cadence
- 2-3 videos/week for algorithm momentum
- Shorts from long-form clips (best 60-sec moments)
- Community posts between uploads (polls, BTS, teasers)

### Content Types That Work
- **Build videos** -- "I Built X in Y Hours" (hero content)
- **Tool reviews** -- "This AI Tool Changes Everything" (search traffic)
- **Tutorials** -- Step-by-step how-tos (evergreen SEO)
- **Behind the scenes** -- Building in public, real process (community)

### Algorithm Signals to Maximize
- Reply to every comment in first 24h (engagement signal)
- Pin a comment with lead magnet link
- End screens linking to next best video
- Cards at key moments
- Post within 48-72h of a viral video (algorithm tests channel)

## Viral Video Playbook

When a video pops off:
1. **Don't touch it** -- Don't change title/thumbnail while it's working
2. **Engage hard** -- Reply to every comment, heart them all
3. **Pin a CTA** comment (lead magnet, subscribe reminder)
4. **Community post** thanking new subs, teasing next video
5. **Upload follow-up within 48-72h** -- Algorithm is testing your channel
6. **Ride the wave** -- Make related content while the topic is hot

## New Video Launch Checklist
- [ ] Generate 3 title options
- [ ] Write SEO description with chapters
- [ ] Suggest 15-20 tags
- [ ] Thumbnail strategy (3 concepts)
- [ ] Remind: pin lead magnet comment after upload
- [ ] Remind: reply to every comment in first 24h
