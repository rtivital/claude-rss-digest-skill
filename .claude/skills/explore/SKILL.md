You are discovering new RSS/Atom feed sources relevant to the user's interests. Follow these steps exactly:

## Step 1: Understand what's already covered

Read `sources.json` and `topics.json` from the project root.

From `sources.json`, build a list of existing source names and categories. From `topics.json`, understand the user's roles and topic priorities.

Identify **coverage gaps** — topic areas from `topics.json` that have few or no sources in `sources.json`. For example, if "AI coding tools" is high priority but only one AI source exists, that's a gap.

## Step 2: Research new sources

Use WebSearch to find high-quality blogs, newsletters, and technical publications that:
- Cover the user's high and medium priority topics
- Fill identified coverage gaps
- Are written at a senior engineering level (not beginner tutorials)
- Have active RSS/Atom feeds
- Are actively maintained (published within the last 3 months)

Search strategies (run these in parallel where possible):
- `"best RSS feeds" + {topic}` for each gap area
- `"engineering blog" RSS + {topic}`
- `"{topic} newsletter" RSS feed`
- Check well-known aggregators (e.g., bloggingfordevs.com, feedle.world) for curated lists

Aim to find **5-10 candidate sources** that aren't already in `sources.json`.

## Step 3: Validate each candidate

For each candidate source, perform ALL of these validation checks:

### 3a. Feed URL validation
Use Bash with curl to test the feed URL:
```bash
curl -sL --max-time 10 -o /dev/null -w "%{http_code}" "{feed_url}"
```
The feed must return HTTP 200. If not, try common alternatives (`/feed`, `/feed.xml`, `/rss`, `/rss.xml`, `/atom.xml`, `/index.xml`).

### 3b. Feed content validation
Fetch the first 30 lines of the feed and verify it's valid XML/RSS/Atom:
```bash
curl -sL --max-time 10 "{feed_url}" | head -30
```
Must contain `<rss`, `<feed`, or `<channel` tags. Skip feeds that return HTML, JSON, or error pages.

### 3c. Freshness check
Use WebFetch on the feed URL to check when the most recent entry was published. Skip sources with no posts in the last 3 months.

### 3d. Content quality check
Use WebFetch to read the source's main page or a recent article. Verify:
- Content is senior-level (not "Learn JavaScript in 10 days")
- Posts have technical depth (not just link aggregation or product announcements)
- Not primarily a sales/marketing blog

Run feed URL and content validations in parallel across candidates (use direct parallel tool calls, NOT the Agent tool).

## Step 4: Present findings

Output a summary table to the user:

```
## Source Discovery Results

### Validated Sources (ready to add)

| # | Name | Category | Type | Feed URL | Why |
|---|------|----------|------|----------|-----|
| 1 | ... | ... | article/newsletter | ... | ... |

### Rejected Candidates

| Name | Reason |
|------|--------|
| ... | Feed returns 404 / Stale (last post 6 months ago) / Beginner content / etc. |
```

For each validated source, include:
- **Name**: The blog/newsletter name
- **Category**: Best matching category from existing `sources.json` categories, or suggest a new one
- **Type**: `article` or `newsletter` (set `newsletter` if it's a curated link roundup)
- **Full content RSS**: Whether the feed includes full article text (set `full_content_rss: true` if so)
- **Feed URL**: The validated URL
- **Why**: 1 sentence on what gap it fills

## Step 5: Add approved sources

Ask the user which sources (by number) they want to add. Accept a response like "1, 3, 5" or "all".

Then for each approved source, add it to `sources.json` with the correct structure:
```json
{
  "name": "Source Name",
  "url": "https://example.com/feed.xml",
  "category": "Category",
  "enabled": true
}
```

Include `"type": "newsletter"` if applicable. Include `"full_content_rss": true` if applicable. Only add fields that are needed.

After updating `sources.json`, run a quick test:
```bash
cd $PROJECT_ROOT && python3 -c "
import json
with open('sources.json') as f:
    data = json.load(f)
enabled = [s for s in data['sources'] if s.get('enabled', True)]
print(f'{len(enabled)} enabled sources, {len(data[\"sources\"])} total')
"
```

Confirm to the user how many sources were added and the new total.
