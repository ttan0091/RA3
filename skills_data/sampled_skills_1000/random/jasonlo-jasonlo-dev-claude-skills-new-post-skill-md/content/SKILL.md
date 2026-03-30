---
name: new-post
description: Generate a new content post (journey, project, tool, or blog). Interactively gathers context, identifies the best post type, and creates an MDX file with valid frontmatter in the correct content folder.
---

Generate a new content post for the site. Argument: optional free-text context about the post (e.g., `/new-post I just started using Cursor IDE`).

## Step 1 — Gather context

If `$ARGUMENTS` is provided, use it as the initial context. Otherwise, ask the user to describe what they want to write about.

Ask clarifying questions as needed to fill in the required frontmatter fields for the post type. Keep it conversational — don't dump a long form. Ask 1-3 questions at a time.

## Step 2 — Identify post type

Based on the context, determine which content type fits best:

| Type | When to use |
|------|-------------|
| **journey** | A career event, life milestone, learning moment, or job transition |
| **project** | A completed or ongoing project with technical decisions and outcomes. Academic publications and research papers also go here — frame them as the underlying research project. |
| **tool** | A tool, software, or technology the user wants to review or recommend |
| **blog** | A freeform article, essay, tutorial, or opinion piece that doesn't fit the structured project or journey format |

Present your best guess to the user and confirm before proceeding. Use `AskUserQuestion` with the four types as options.

## Step 3 — Gather remaining details

Read `src/content.config.ts` to confirm the exact schema for the chosen post type. Then ask the user for any required fields you don't already have from Step 1. For optional fields, use sensible defaults or ask only if the information would meaningfully improve the post.

### Required fields by type

**Journey:**
- `date` — when this happened (YYYY-MM-DD)
- `title` — short descriptive title
- `type` — milestone, learning, or transition
- `description` — 1-3 sentence summary

**Project:**
- `title`, `role`, `year`, `outcomeSummary`, `overview`, `problem`
- `constraints` — array of constraints faced
- `approach` — how the problem was solved
- `keyDecisions` — array of {decision, reasoning, alternatives?}
- `techStack` — technologies used
- `impact` — {metrics?, qualitative}
- `learnings` — array of takeaways

**Tool:**
- `name`, `description`, `date`, `best_for`

**Blog:**
- `title` — post title
- `description` — 1-2 sentence summary shown in listings and meta tags
- `publishDate` — publication date (YYYY-MM-DD)
- `tags` — optional array of topic tags

## Step 4 — Generate the file

1. **Filename**: Create a URL-friendly slug from the title/name (lowercase, hyphens, no special characters). Use `.mdx` extension.
2. **Location**: Place the file in the correct content directory:
   - Journey → `src/content/journey/`
   - Project → `src/content/projects/`
   - Tool → `src/content/tools/`
   - Blog → `src/content/blog/`
3. **Frontmatter**: Write valid YAML frontmatter matching the Zod schema exactly. Set `draft: true` by default so the user can review before publishing.
4. **Body content**: For journey, project, and blog posts, write substantive MDX body content based on the context provided. For blog posts specifically, write the full article — use headings, paragraphs, and lists as appropriate. For tools, leave the body empty (frontmatter only) unless the user requests otherwise.

## Step 5 — Validate

Run `bun run build` to verify the new file passes schema validation. If it fails, read the error, fix the frontmatter, and retry.

## Guidelines

- Match the tone and style of existing content in the collection — read 1-2 existing files for reference before writing.
- Keep descriptions concise and authentic. Avoid marketing language.
- Use ISO 8601 dates (YYYY-MM-DD).
- For projects, the `keyDecisions` format is critical: each must have `decision` and `reasoning`, with optional `alternatives` array.
- Always set `draft: true` so the user can review. Mention this in your final message.
