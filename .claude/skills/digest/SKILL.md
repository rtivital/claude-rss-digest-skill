You are generating a weekly learning digest for the user. Follow these steps exactly:

## Step 1: Collect articles

Run the collector and filter scripts from the project root:

```bash
cd $PROJECT_ROOT && python3 collector.py --days 7
```

Then run the filter:

```bash
cd $PROJECT_ROOT && python3 filter.py
```

If the collector reports any auto-disabled feeds, note them at the end of the digest so the user knows.

## Step 2: Read your configuration

Read the file `topics.json` in the project root. This defines the user's roles, high/medium/low priority topics, and exclusion rules. You will use this to judge every article.

## Step 3: Get filtered articles from the database

Query the SQLite database at `db/articles.db` to get all articles that passed the keyword filter:

```bash
cd $PROJECT_ROOT && sqlite3 -json db/articles.db "SELECT id, title, source, category, source_type, full_content_rss, url, summary FROM articles WHERE status = 'new' ORDER BY category, published DESC;"
```

## Step 4: Fetch and analyze each article

Classify each article into one of three groups and handle accordingly:

### Group A: Full-content RSS (`full_content_rss = 1`)
These feeds already include the complete article text in the `summary` field (e.g., Simon Willison's Blog). **Do NOT use WebFetch** — evaluate directly from the database summary.

### Group B: Newsletter sources (`source_type = "newsletter"`)
These are curated newsletter issues containing many linked articles (e.g., JavaScript Weekly, Node Weekly, Frontend Focus, This Week in React, React Status). **Do NOT use WebFetch** — the RSS summary already contains the newsletter content. Instead:
- Read the summary and extract the 2-4 most notable individual items that match the user's topic priorities
- Present each notable item as its own entry in the digest, attributing it to the newsletter source

### Group C: Regular articles (everything else)
Use WebFetch to retrieve the full article content. Use the prompt: "Extract the main article content. Ignore ads, navigation, sidebars, cookie banners, and promotional content. Return only the article text."

**IMPORTANT: Call all WebFetch requests as parallel tool calls in a single message.** Do NOT use the Agent tool for fetching — it causes permission issues. Simply issue multiple WebFetch calls at once.

If WebFetch fails for any article (timeout, paywall, 404, etc.), fall back to evaluating based on the database summary. If the summary is also too short to evaluate, skip the article.

### Evaluation criteria (apply to all groups)

Based on the content AND the user's `topics.json` profile, decide if each article is genuinely interesting. Skip articles that are:
- Ads or sponsored content disguised as articles
- Job listings
- Product advertisements without technical depth
- Beginner tutorials (the user is senior-level)
- Not relevant to any of the user's high or medium priority topics

For articles you keep, note down: title, source, url, category, and prepare a 2-3 sentence summary of why it's interesting to this specific user.

## Step 5: Present the digest

Output a well-formatted Markdown digest to `./digest/weekly_dev_digest_{today's date}.md` with this structure:

```
# Weekly Dev Digest — {today's date}

_{N} articles collected · {M} selected as relevant_

## {Category Name}

### {Article Title}
**Source:** {source} · [Read →]({url})

{2-3 sentence summary explaining what the article covers and why it matters for the user's interests}

---
```

Group articles by category. Within each category, put the most relevant articles first.

If no articles passed your analysis, say so honestly.

If any feeds were auto-disabled during collection, add a footer:
```
---
⚠️ **Feed health:** {feed name} has been auto-disabled after 3+ consecutive failures. Check `sources.json` to update the URL or re-enable.
```

## Step 6: Clear the database

After presenting the digest, delete all rows from the articles table (but keep feed_health intact):

```bash
cd $PROJECT_ROOT && sqlite3 db/articles.db "DELETE FROM articles;"
```

Confirm to the user that the database has been cleared.
