"""
SkillsMP 全量元数据采集 v3 — 异步并发版

策略:
  1. 关键词并发采集: 320 个关键词，每个关键词分配一个协程，信号量控制并发上限
  2. Author 补全轮: 从已采集数据提取 author，逐 author 查询补漏
  3. 所有结果按 id 去重
"""

import asyncio
import aiohttp
import json
import csv
import os
import time
from datetime import datetime

# ============ 配置 ============
API_KEY = "sk_live_skillsmp_fVvwe4IY7oGmRU0m3Bxcq0P0ZjpfGIIE0A7fHywoD3Y"
API_URL = "https://skillsmp.com/api/v1/skills/search"
OUTPUT_DIR = "/Users/tan/Desktop/RA3/skills_data"
CHECKPOINT_PATH = os.path.join(OUTPUT_DIR, "skills_checkpoint.json")

MAX_CONCURRENCY = 15      # 并发数
PAGE_DELAY = 0.15         # 同一查询翻页间隔
LIMIT = 100               # 每页条数

# ============ 关键词 ============
SEARCH_QUERIES = [
    # 通配符
    "*",
    # 编程语言
    "python", "javascript", "typescript", "rust", "go", "golang", "java",
    "ruby", "swift", "kotlin", "php", "csharp", "cpp", "lua", "perl",
    "scala", "elixir", "clojure", "haskell", "dart", "zig", "nim",
    "objective-c", "matlab", "julia", "fortran", "cobol", "assembly",
    # 前端
    "react", "vue", "angular", "svelte", "nextjs", "nuxt", "remix",
    "astro", "gatsby", "tailwind", "css", "html", "sass", "webpack",
    "vite", "rollup", "esbuild", "babel", "postcss", "bootstrap",
    # 后端
    "django", "flask", "fastapi", "express", "nestjs", "spring",
    "rails", "laravel", "symfony", "gin", "echo", "fiber",
    "actix", "axum", "rocket", "phoenix", "sinatra", "koa",
    # 数据库
    "database", "sql", "mysql", "postgres", "postgresql", "sqlite",
    "mongodb", "redis", "elasticsearch", "dynamodb", "cassandra",
    "supabase", "firebase", "prisma", "sequelize", "typeorm", "drizzle",
    # DevOps
    "docker", "kubernetes", "k8s", "terraform", "ansible", "aws",
    "azure", "gcp", "cloudflare", "nginx", "apache", "linux",
    "github actions", "jenkins", "circleci",
    "vercel", "netlify", "heroku", "digitalocean", "monitoring",
    # AI/ML
    "machine learning", "deep learning", "neural", "transformer",
    "llm", "gpt", "claude", "openai", "anthropic", "langchain",
    "embedding", "vector", "rag", "fine-tuning", "pytorch", "tensorflow",
    "huggingface", "diffusion", "computer vision", "nlp",
    # 通用开发
    "test", "testing", "unittest", "jest", "pytest", "vitest",
    "deploy", "deployment", "security", "authentication", "authorization",
    "api", "rest", "graphql", "grpc", "websocket", "microservice",
    "architecture", "design pattern", "refactor", "debug", "logging",
    "performance", "optimization", "cache", "queue", "message",
    # 工具
    "git", "github", "gitlab", "bitbucket", "npm", "yarn", "pnpm",
    "pip", "cargo", "maven", "gradle", "make", "cmake", "bazel",
    "linter", "formatter", "eslint", "prettier", "ruff",
    "editor", "vscode", "neovim", "cursor", "copilot",
    # 领域
    "documentation", "markdown", "json", "yaml", "toml", "xml",
    "cli", "terminal", "shell", "bash", "zsh", "powershell",
    "scraper", "crawler", "automation", "workflow", "agent",
    "plugin", "extension", "middleware", "hook", "event",
    "file", "image", "video", "audio", "pdf", "csv",
    "email", "notification", "payment", "stripe", "auth0",
    "oauth", "jwt", "session", "cookie", "cors",
    "responsive", "accessibility", "i18n", "localization",
    "analytics", "seo", "sitemap",
    "blockchain", "web3", "smart contract", "solidity",
    "game", "unity", "unreal", "godot",
    # 动作类
    "build", "create", "generate", "convert", "transform",
    "analyze", "review", "check", "validate", "verify",
    "migrate", "upgrade", "install", "setup", "configure",
    "manage", "monitor", "report", "export", "import",
    "fix", "error", "warning", "issue", "bug",
    "clean", "format", "lint", "style", "convention",
    "plan", "estimate", "document", "explain", "summarize",
    # 架构
    "server", "client", "frontend", "backend", "fullstack",
    "mobile", "ios", "android", "flutter", "react native",
    "desktop", "electron", "tauri", "wasm", "webassembly",
    "container", "serverless", "lambda", "function", "trigger",
    "schema", "model", "entity", "component", "module",
    "template", "scaffold", "boilerplate", "starter", "example",
    "integration", "connector", "adapter", "wrapper", "proxy",
    "config", "environment", "variable", "secret", "vault",
    "backup", "restore", "snapshot", "migration", "seed",
    "release", "version", "changelog", "tag", "branch",
    # 补充：更细分的领域词
    "regex", "parsing", "compiler", "interpreter", "debugger",
    "profiler", "benchmark", "load test", "stress test",
    "oauth2", "saml", "sso", "ldap", "active directory",
    "graphite", "prometheus", "grafana", "datadog", "sentry",
    "webpack", "parcel", "turbopack", "snowpack",
    "storybook", "chromatic", "playwright", "cypress", "selenium",
    "puppeteer", "cheerio", "jsdom",
    "orm", "activerecord", "hibernate", "sqlalchemy",
    "rabbitmq", "kafka", "nats", "zeromq", "celery",
    "nginx", "caddy", "traefik", "envoy", "istio",
    "helm", "kustomize", "argocd", "flux",
    "vault", "consul", "nomad",
    "packer", "vagrant", "pulumi",
    "opentelemetry", "jaeger", "zipkin",
    "markdown", "latex", "rst", "asciidoc",
    "figma", "sketch", "adobe", "canva",
    "shopify", "wordpress", "drupal", "joomla",
    "salesforce", "hubspot", "zendesk",
    "twilio", "sendgrid", "mailgun",
    "s3", "blob", "storage", "cdn",
    "cron", "scheduler", "worker", "daemon",
    "socket", "tcp", "udp", "http",
    "tls", "ssl", "certificate", "encryption",
    "hash", "signature", "token", "key",
    "rbac", "acl", "permission", "role",
    "audit", "compliance", "gdpr", "hipaa",
    "onboarding", "tutorial", "guide", "readme",
    "changelog", "roadmap", "sprint", "kanban", "jira",
    "slack", "discord", "telegram", "webhook",
    "ci", "cd", "pipeline", "artifact",
    "monorepo", "turborepo", "nx", "lerna",
    "prettier", "biome", "deno", "bun",
    "htmx", "alpine", "livewire", "stimulus",
    "prisma", "kysely", "knex",
    "trpc", "hono", "elysia",
    "solid", "qwik", "fresh",
    "tauri", "capacitor", "ionic",
    "expo", "metro",
    "supabase", "appwrite", "pocketbase",
    "neon", "planetscale", "turso",
    "upstash", "vercel kv",
    "cloudflare workers", "edge function",
    "wrangler", "miniflare",
]

# 去重
SEARCH_QUERIES = list(dict.fromkeys(SEARCH_QUERIES))

# ============ 全局状态 ============
all_skills = {}  # id -> skill dict
lock = asyncio.Lock()
progress = {"done": 0, "total": 0, "new": 0}


async def fetch_page(session, sem, query, page, sort_by):
    """获取单页"""
    params = {"q": query, "limit": LIMIT, "page": page, "sortBy": sort_by}
    async with sem:
        try:
            async with session.get(API_URL, params=params, timeout=aiohttp.ClientTimeout(total=30)) as r:
                if r.status == 429:
                    await asyncio.sleep(5)
                    return None
                r.raise_for_status()
                return await r.json()
        except Exception as e:
            return None


async def fetch_query(session, sem, query, sort_by="stars"):
    """获取一个查询的全部分页结果"""
    new_count = 0
    page = 1
    total_fetched = 0
    total_available = "?"

    while True:
        data = await fetch_page(session, sem, query, page, sort_by)
        if not data or not data.get("success"):
            break

        skills = data["data"]["skills"]
        pagination = data["data"]["pagination"]
        total_available = pagination["total"]

        if not skills:
            break

        async with lock:
            for s in skills:
                if s["id"] not in all_skills:
                    all_skills[s["id"]] = s
                    new_count += 1
            total_fetched += len(skills)

        if not pagination.get("hasNext", False):
            break

        page += 1
        await asyncio.sleep(PAGE_DELAY)

    return total_fetched, new_count, total_available


async def process_query(session, sem, idx, total, query):
    """处理一个关键词（stars + recent 两种排序）"""
    fetched_s, new_s, total_s = await fetch_query(session, sem, query, "stars")
    fetched_r, new_r, total_r = await fetch_query(session, sem, query, "recent")

    total_new = new_s + new_r
    async with lock:
        progress["done"] += 1
        progress["new"] += total_new
        current = len(all_skills)

    if total_new > 0 or progress["done"] % 20 == 0:
        print(f"  [{progress['done']}/{total}] q=\"{query}\" "
              f"匹配={total_s} 新增={total_new} 累计={current}", flush=True)


def load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle both list format and dict with 'skills' key
            if isinstance(data, list):
                return {s["id"]: s for s in data}
            elif isinstance(data, dict) and "skills" in data:
                return {s["id"]: s for s in data["skills"]}
    return {}


def save_results():
    skills_list = sorted(all_skills.values(), key=lambda x: x.get("stars", 0), reverse=True)

    # Checkpoint
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(skills_list, f, ensure_ascii=False)

    # JSON
    final_json = os.path.join(OUTPUT_DIR, "skills_metadata.json")
    with open(final_json, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "total_skills": len(skills_list),
                "total_authors": len({s["author"] for s in skills_list}),
                "fetched_at": datetime.now().isoformat(),
                "source": "skillsmp.com",
            },
            "skills": skills_list,
        }, f, ensure_ascii=False, indent=2)

    # CSV
    final_csv = os.path.join(OUTPUT_DIR, "skills_metadata.csv")
    with open(final_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "name", "author", "description", "githubUrl", "skillUrl", "stars", "updatedAt"
        ])
        writer.writeheader()
        for s in skills_list:
            writer.writerow({k: s.get(k, "") for k in writer.fieldnames})

    return skills_list


async def run_keyword_phase(session, sem):
    """阶段 1: 关键词并发采集"""
    total = len(SEARCH_QUERIES)
    progress["total"] = total

    print(f"▶ 阶段 1: 关键词并发采集 ({total} 个关键词, 并发={MAX_CONCURRENCY})")

    tasks = []
    for idx, query in enumerate(SEARCH_QUERIES):
        tasks.append(process_query(session, sem, idx, total, query))

    await asyncio.gather(*tasks)
    save_results()
    print(f"  ✓ 阶段 1 完成: {len(all_skills)} 条\n")


async def run_author_phase(session, sem):
    """阶段 2: Author 补全"""
    authors = sorted({s["author"] for s in all_skills.values()})
    print(f"▶ 阶段 2: Author 补全 ({len(authors)} 个 author, 并发={MAX_CONCURRENCY})")

    before = len(all_skills)
    batch_size = 50
    for i in range(0, len(authors), batch_size):
        batch = authors[i:i+batch_size]
        tasks = []
        for author in batch:
            tasks.append(fetch_query(session, sem, author, "stars"))
        results = await asyncio.gather(*tasks)

        new_this_batch = sum(r[1] for r in results)
        if new_this_batch > 0 or (i // batch_size) % 5 == 0:
            print(f"  [{i+len(batch)}/{len(authors)}] 累计 {len(all_skills)} 条 "
                  f"(本批新增 {new_this_batch})", flush=True)

    after = len(all_skills)
    save_results()
    print(f"  ✓ 阶段 2 完成: 新增 {after - before} 条, 累计 {after} 条\n")


async def main():
    global all_skills

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 加载已有数据
    all_skills = load_checkpoint()
    print(f"{'='*60}")
    print(f"SkillsMP 全量采集 v3 (异步并发)")
    print(f"已有数据: {len(all_skills)} 条")
    print(f"关键词: {len(SEARCH_QUERIES)} 个, 并发: {MAX_CONCURRENCY}")
    print(f"{'='*60}\n")

    headers = {"Authorization": f"Bearer {API_KEY}"}
    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async with aiohttp.ClientSession(headers=headers) as session:
        # 阶段 1: 关键词
        await run_keyword_phase(session, sem)

        # 阶段 2: Author 补全（可能多轮）
        for round_num in range(1, 4):
            before = len(all_skills)
            print(f"--- Author 补全第 {round_num} 轮 ---")
            await run_author_phase(session, sem)
            after = len(all_skills)
            if after - before < 100:
                print(f"  增量 < 100, 停止补全轮次\n")
                break

    # 最终统计
    skills_list = save_results()
    authors = {s["author"] for s in skills_list}
    print(f"{'='*60}")
    print(f"采集完成")
    print(f"  唯一 Skill: {len(skills_list)}")
    print(f"  唯一 Author: {len(authors)}")
    print(f"  覆盖率: {len(skills_list)/185359*100:.1f}%")
    print(f"  JSON: {OUTPUT_DIR}/skills_metadata.json")
    print(f"  CSV:  {OUTPUT_DIR}/skills_metadata.csv")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
