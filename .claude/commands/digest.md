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

## Step 2: Read your configuration

Read the file `topics.json` in the project root. This defines the user's roles, high/medium/low priority topics, and exclusion rules. You will use this to judge every article.

## Step 3: Get filtered articles from the database

Query the SQLite database at `db/articles.db` to get all articles that passed the keyword filter:

```bash
cd $PROJECT_ROOT && sqlite3 -json db/articles.db "SELECT id, title, source, category, url, summary FROM articles WHERE status = 'new' ORDER BY category, published DESC;"
```

## Step 4: Fetch and analyze each article

For each article returned from the database:
1. Use WebFetch to retrieve the full article content from its URL. Use the prompt: "Extract the main article content. Ignore ads, navigation, sidebars, cookie banners, and promotional content. Return only the article text."
2. Based on the full content AND the user's topics.json profile, decide if this article is genuinely interesting to the user. Skip articles that are:
   - Ads or sponsored content disguised as articles
   - Job listings
   - Product advertisements without technical depth
   - Beginner tutorials (the user is senior-level)
   - Not relevant to any of the user's high or medium priority topics
3. For articles you keep, note down: title, source, url, category, and prepare a 2-3 sentence summary of why it's interesting to this specific user.

Process articles in parallel where possible using the Agent tool — launch multiple WebFetch agents concurrently to speed things up.

## Step 5: Present the digest

Output a well-formatted Markdown digest to the user with this structure:

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

## Step 6: Clear the database

After presenting the digest, delete all rows from the articles table:

```bash
cd $PROJECT_ROOT && sqlite3 db/articles.db "DELETE FROM articles;"
```

Confirm to the user that the database has been cleared.
