#!/usr/bin/env python3
"""
Download all Claude Code skills (.claude/ directory) from GitHub.

Strategy:
  1. Load metadata, filter for skills with '.claude/' in githubUrl
  2. Group by (owner, repo, ref) to minimise git clone operations
  3. For each repo group: sparse-checkout only the .claude/ directory
  4. Copy out each skill's content to the output directory
  5. Support resume via checkpoint file

Usage:
  python download_claude_skills.py [--concurrency 8] [--resume]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


# ============ Config ============
METADATA_PATH = Path("skills_data/skills_metadata.json")
OUTPUT_DIR = Path("skills_data/claude_skills")
CHECKPOINT_PATH = OUTPUT_DIR / "_checkpoint.json"
RESULTS_DIR = OUTPUT_DIR / "_results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download all Claude Code skills from GitHub.")
    p.add_argument("--metadata-path", type=Path, default=METADATA_PATH)
    p.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    p.add_argument("--concurrency", type=int, default=1, help="(reserved for future async)")
    p.add_argument("--resume", action="store_true", help="Resume from checkpoint.")
    p.add_argument("--limit", type=int, default=0, help="Limit repos to process (0=all).")
    p.add_argument("--clone-timeout", type=int, default=120, help="Git clone timeout in seconds.")
    return p.parse_args()


def load_skills(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and isinstance(data.get("skills"), list):
        return data["skills"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported metadata structure in {path}")


def parse_github_url(url: str) -> dict:
    """Parse GitHub URL into components."""
    parsed = urlparse(url)
    parts = [unquote(p) for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub path: {url}")

    owner = parts[0]
    repo = parts[1]
    ref = None
    rel_path = ""

    if len(parts) >= 4 and parts[2] in {"tree", "blob"}:
        ref = parts[3]
        rel_path = "/".join(parts[4:])
    elif len(parts) > 2:
        rel_path = "/".join(parts[2:])

    return {
        "owner": owner,
        "repo": repo,
        "ref": ref,
        "rel_path": rel_path,
        "source_url": url,
    }


def sanitize(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def run_cmd(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, timeout=timeout
    )


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def copy_skill_content(src: Path, dst: Path) -> int:
    """Copy skill content from src to dst. Returns number of files copied."""
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    if src.is_file():
        shutil.copy2(src, dst / src.name)
        count = 1
    elif src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        count = sum(1 for _ in dst.rglob("*") if _.is_file())
    return count


def load_checkpoint(path: Path) -> set[str]:
    """Load set of completed repo keys from checkpoint."""
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("completed_repos", []))
    return set()


def save_checkpoint(path: Path, completed: set[str], stats: dict) -> None:
    write_json(path, {
        "completed_repos": sorted(completed),
        "stats": stats,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "_checkpoint.json"

    # ---------- Step 1: Load & filter ----------
    print("=" * 60)
    print("Claude Code Skills Bulk Downloader")
    print("=" * 60)

    skills = load_skills(args.metadata_path)
    claude_skills = [
        s for s in skills
        if s.get("githubUrl", "") and ".claude/" in s.get("githubUrl", "")
    ]
    print(f"Total Claude Code skills: {len(claude_skills)}")

    # ---------- Step 2: Parse URLs & group by repo ----------
    parse_errors = []
    parsed_skills = []
    for s in claude_skills:
        url = s["githubUrl"]
        try:
            info = parse_github_url(url)
            parsed_skills.append({"skill": s, "github": info})
        except Exception as e:
            parse_errors.append({"id": s.get("id"), "url": url, "error": str(e)})

    # Group by (owner, repo, ref)
    groups: dict[str, list[dict]] = defaultdict(list)
    for ps in parsed_skills:
        g = ps["github"]
        key = f"{g['owner']}/{g['repo']}@{g['ref'] or 'HEAD'}"
        groups[key].append(ps)

    total_groups = len(groups)
    print(f"Unique repos to clone: {total_groups}")
    print(f"Parse errors: {len(parse_errors)}")

    # ---------- Step 3: Load checkpoint for resume ----------
    completed_repos = set()
    if args.resume:
        completed_repos = load_checkpoint(checkpoint_path)
        print(f"Resuming: {len(completed_repos)} repos already completed")

    remaining = {k: v for k, v in groups.items() if k not in completed_repos}
    if args.limit > 0:
        keys = list(remaining.keys())[:args.limit]
        remaining = {k: remaining[k] for k in keys}

    print(f"Repos to process this run: {len(remaining)}")
    print()

    # ---------- Step 4: Clone & extract ----------
    stats = {
        "total_repos": total_groups,
        "repos_processed": 0,
        "repos_success": 0,
        "repos_failed": 0,
        "skills_saved": 0,
        "skills_failed": 0,
        "files_copied": 0,
    }
    failures = []
    successes_count = 0
    processed = 0

    start_time = time.time()
    repo_items = list(remaining.items())

    for idx, (repo_key, group_tasks) in enumerate(repo_items, 1):
        processed += 1
        sample_github = group_tasks[0]["github"]
        owner = sample_github["owner"]
        repo = sample_github["repo"]
        ref = sample_github["ref"]

        # Progress display
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        eta_s = (len(remaining) - processed) / rate if rate > 0 else 0
        eta_m = eta_s / 60

        skill_count = len(group_tasks)
        print(
            f"[{idx}/{len(remaining)}] {owner}/{repo} "
            f"(ref={ref or 'HEAD'}, {skill_count} skills) "
            f"| ETA: {eta_m:.0f}m",
            flush=True,
        )

        with tempfile.TemporaryDirectory(prefix="claude_skill_", dir="/tmp") as tmp_dir:
            tmp = Path(tmp_dir)
            repo_url = f"https://github.com/{owner}/{repo}.git"
            clone_ok = False

            # Collect all unique relative paths in this repo group
            sparse_paths = set()
            for task in group_tasks:
                rel = task["github"]["rel_path"]
                if rel:
                    sparse_paths.add(rel)
                    # Also add parent .claude directory for context
                    parts = rel.split("/")
                    claude_idx = None
                    for i, p in enumerate(parts):
                        if p == ".claude":
                            claude_idx = i
                            break
                    if claude_idx is not None:
                        # Add the whole .claude directory
                        sparse_paths.add("/".join(parts[:claude_idx + 1]))

            # Try clone
            clone_cmd = ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse"]
            if ref and ref != "HEAD":
                clone_cmd += ["--branch", ref]
            clone_cmd += [repo_url, str(tmp)]

            try:
                result = run_cmd(clone_cmd, timeout=args.clone_timeout)
                if result.returncode != 0:
                    raise RuntimeError(result.stderr.strip() or result.stdout.strip())
                clone_ok = True
            except Exception as e:
                # Fallback: try without ref
                if ref and ref != "HEAD":
                    try:
                        fallback_cmd = [
                            "git", "clone", "--depth", "1",
                            "--filter=blob:none", "--sparse",
                            repo_url, str(tmp)
                        ]
                        result = run_cmd(fallback_cmd, timeout=args.clone_timeout)
                        if result.returncode == 0:
                            fetch = run_cmd(
                                ["git", "-C", str(tmp), "fetch", "--depth", "1", "origin", ref],
                                timeout=args.clone_timeout
                            )
                            if fetch.returncode == 0:
                                checkout = run_cmd(
                                    ["git", "-C", str(tmp), "checkout", "FETCH_HEAD"],
                                    timeout=60
                                )
                                clone_ok = checkout.returncode == 0
                    except Exception:
                        pass

                if not clone_ok:
                    err_msg = str(e)[:200]
                    for task in group_tasks:
                        failures.append({
                            "id": task["skill"].get("id"),
                            "url": task["skill"]["githubUrl"],
                            "error": f"clone_failed: {err_msg}",
                        })
                    stats["repos_failed"] += 1
                    completed_repos.add(repo_key)
                    # Save checkpoint every 50 repos
                    if processed % 50 == 0:
                        stats["repos_processed"] = processed
                        save_checkpoint(checkpoint_path, completed_repos, stats)
                    continue

            # Sparse checkout
            if sparse_paths:
                try:
                    sc_result = run_cmd(
                        ["git", "-C", str(tmp), "sparse-checkout", "set", "--no-cone"]
                        + list(sparse_paths),
                        timeout=60,
                    )
                    if sc_result.returncode != 0:
                        raise RuntimeError(sc_result.stderr.strip())
                except Exception as e:
                    # Try without sparse checkout — maybe the paths are already available
                    pass

            # Extract each skill
            repo_skills_ok = 0
            for task in group_tasks:
                skill = task["skill"]
                gh = task["github"]
                rel = gh["rel_path"]
                src = tmp if not rel else tmp / rel
                skill_id = skill.get("id", "unknown")
                skill_name = sanitize(skill.get("name", skill_id))
                author = sanitize(skill.get("author", "unknown"))

                # Output path: claude_skills/<author>/<skill_name>/
                skill_dir = output_dir / author / skill_name

                if not src.exists():
                    failures.append({
                        "id": skill_id,
                        "url": skill["githubUrl"],
                        "error": f"path_not_found: {rel}",
                    })
                    stats["skills_failed"] += 1
                    continue

                try:
                    n_files = copy_skill_content(src, skill_dir / "content")

                    # Write metadata
                    write_json(skill_dir / "metadata.json", {
                        "id": skill_id,
                        "name": skill.get("name"),
                        "author": skill.get("author"),
                        "description": skill.get("description"),
                        "stars": skill.get("stars", 0),
                        "githubUrl": skill["githubUrl"],
                        "skillUrl": skill.get("skillUrl"),
                        "updatedAt": skill.get("updatedAt"),
                        "github": gh,
                    })

                    stats["files_copied"] += n_files
                    stats["skills_saved"] += 1
                    repo_skills_ok += 1
                except Exception as e:
                    failures.append({
                        "id": skill_id,
                        "url": skill["githubUrl"],
                        "error": f"copy_failed: {str(e)[:200]}",
                    })
                    stats["skills_failed"] += 1

            if repo_skills_ok > 0:
                stats["repos_success"] += 1

        # Mark done
        completed_repos.add(repo_key)

        # Periodic checkpoint
        if processed % 50 == 0:
            stats["repos_processed"] = processed
            save_checkpoint(checkpoint_path, completed_repos, stats)
            print(f"  [checkpoint] {processed} repos done, "
                  f"{stats['skills_saved']} skills saved, "
                  f"{stats['skills_failed']} failed")

    # ---------- Step 5: Final save ----------
    stats["repos_processed"] = processed
    save_checkpoint(checkpoint_path, completed_repos, stats)

    # Save results
    write_json(RESULTS_DIR / "failures.json", failures)
    write_json(RESULTS_DIR / "parse_errors.json", parse_errors)
    write_json(RESULTS_DIR / "summary.json", {
        **stats,
        "parse_errors": len(parse_errors),
        "total_failures": len(failures),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.time() - start_time, 1),
    })

    elapsed_total = time.time() - start_time
    print()
    print("=" * 60)
    print("Download Complete")
    print(f"  Repos processed:   {stats['repos_processed']}")
    print(f"  Repos success:     {stats['repos_success']}")
    print(f"  Repos failed:      {stats['repos_failed']}")
    print(f"  Skills saved:      {stats['skills_saved']}")
    print(f"  Skills failed:     {stats['skills_failed']}")
    print(f"  Files copied:      {stats['files_copied']}")
    print(f"  Parse errors:      {len(parse_errors)}")
    print(f"  Elapsed:           {elapsed_total/60:.1f} minutes")
    print(f"  Output:            {output_dir}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Use --resume to continue later.")
        raise SystemExit(130)
