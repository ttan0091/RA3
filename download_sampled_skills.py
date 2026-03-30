#!/usr/bin/env python3
"""
Sample skills from metadata and download selected skill contents from GitHub.

Sampling rules:
1) top-N popular skills by stars
2) random-N skills from remaining pool
"""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


@dataclass(frozen=True)
class GitHubTarget:
    owner: str
    repo: str
    ref: str | None
    rel_path: str
    source_url: str

    @property
    def repo_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}.git"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample and download skills from GitHub URLs.")
    parser.add_argument(
        "--metadata-path",
        default="skills_data/skills_metadata.json",
        help="Path to skills metadata JSON.",
    )
    parser.add_argument(
        "--output-root",
        default="skills_data/sampled_skills",
        help="Directory where sampled skills will be written.",
    )
    parser.add_argument("--popular-count", type=int, default=100, help="Top popular sample size.")
    parser.add_argument("--random-count", type=int, default=100, help="Random sample size.")
    parser.add_argument(
        "--seed",
        type=int,
        default=20260226,
        help="Random seed for reproducible random sampling.",
    )
    parser.add_argument(
        "--allow-random-overlap",
        action="store_true",
        help="Allow random sample to overlap with popular sample.",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Only generate sample manifests without downloading content.",
    )
    return parser.parse_args()


def load_skills(metadata_path: Path) -> list[dict[str, Any]]:
    with metadata_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and isinstance(data.get("skills"), list):
        return data["skills"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported metadata structure in {metadata_path}")


def parse_github_url(url: str) -> GitHubTarget:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host not in {"github.com", "www.github.com"}:
        raise ValueError(f"Not a GitHub URL: {url}")

    parts = [unquote(p) for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub path: {url}")

    owner = parts[0]
    repo = parts[1]
    ref: str | None = None
    rel_path = ""

    if len(parts) >= 4 and parts[2] in {"tree", "blob"}:
        tail = parts[3:]
        if not tail:
            raise ValueError(f"Missing ref in GitHub URL: {url}")
        # Heuristic: most entries use single-segment refs (main/master/dev/canary/etc.).
        ref = tail[0]
        rel_path = "/".join(tail[1:])
    elif len(parts) > 2:
        rel_path = "/".join(parts[2:])

    return GitHubTarget(owner=owner, repo=repo, ref=ref, rel_path=rel_path, source_url=url)


def sanitize_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def run_cmd(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        stdout = proc.stdout.strip()
        msg = stderr if stderr else stdout
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{msg}")


def copy_content(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    if src.is_file():
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst / src.name)
    else:
        shutil.copytree(src, dst)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_manifest_item(skill: dict[str, Any], sample_type: str, index: int) -> dict[str, Any]:
    return {
        "sampleType": sample_type,
        "sampleIndex": index,
        "id": skill.get("id"),
        "name": skill.get("name"),
        "author": skill.get("author"),
        "stars": skill.get("stars", 0),
        "githubUrl": skill.get("githubUrl"),
        "skillUrl": skill.get("skillUrl"),
        "updatedAt": skill.get("updatedAt"),
        "description": skill.get("description"),
    }


def main() -> int:
    args = parse_args()
    metadata_path = Path(args.metadata_path)
    output_root = Path(args.output_root)
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / f"run_{run_ts}"

    skills = load_skills(metadata_path)
    skills = [s for s in skills if s.get("githubUrl")]
    skills_sorted = sorted(
        skills,
        key=lambda s: (-(s.get("stars") or 0), s.get("id") or ""),
    )

    if len(skills_sorted) < args.popular_count:
        raise ValueError("Not enough skills for popular sample.")

    popular = skills_sorted[: args.popular_count]
    pool = skills_sorted if args.allow_random_overlap else skills_sorted[args.popular_count :]
    if len(pool) < args.random_count:
        raise ValueError("Not enough skills for random sample.")

    rng = random.Random(args.seed)
    random_sample = rng.sample(pool, args.random_count)

    popular_manifest = [
        build_manifest_item(skill=s, sample_type="popular", index=i + 1)
        for i, s in enumerate(popular)
    ]
    random_manifest = [
        build_manifest_item(skill=s, sample_type="random", index=i + 1)
        for i, s in enumerate(random_sample)
    ]
    combined_manifest = popular_manifest + random_manifest

    write_json(run_dir / "manifests" / "popular_top.json", popular_manifest)
    write_json(run_dir / "manifests" / "random_sample.json", random_manifest)
    write_json(run_dir / "manifests" / "combined_sample.json", combined_manifest)

    print(f"[INFO] Run dir: {run_dir}")
    print(f"[INFO] Popular sample: {len(popular_manifest)}")
    print(f"[INFO] Random sample:  {len(random_manifest)} (seed={args.seed})")

    if args.skip_download:
        print("[INFO] Skip download enabled. Manifest files generated only.")
        return 0

    tasks: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []

    for entry in combined_manifest:
        url = entry.get("githubUrl")
        try:
            target = parse_github_url(url)
            tasks.append(
                {
                    "entry": entry,
                    "target": target,
                }
            )
        except Exception as e:  # noqa: BLE001
            parse_errors.append({"id": entry.get("id"), "githubUrl": url, "error": str(e)})

    groups: dict[tuple[str, str, str | None], list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        t: GitHubTarget = task["target"]
        groups[(t.owner, t.repo, t.ref)].append(task)

    print(f"[INFO] GitHub groups: {len(groups)}")
    print(f"[INFO] Parse errors:  {len(parse_errors)}")

    successes = []
    failures = []
    group_idx = 0
    group_total = len(groups)

    for (owner, repo, ref), group_tasks in groups.items():
        group_idx += 1
        print(f"[INFO] [{group_idx}/{group_total}] {owner}/{repo} ref={ref or '<default>'} tasks={len(group_tasks)}")
        with tempfile.TemporaryDirectory(prefix="skill_repo_", dir="/tmp") as tmp_dir:
            tmp = Path(tmp_dir)
            repo_url = f"https://github.com/{owner}/{repo}.git"
            clone_ok = False

            clone_cmd = ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse"]
            if ref:
                clone_cmd += ["--branch", ref]
            clone_cmd += [repo_url, str(tmp)]

            try:
                run_cmd(clone_cmd)
                clone_ok = True
            except Exception as e:  # noqa: BLE001
                if ref:
                    try:
                        run_cmd(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", repo_url, str(tmp)])
                        run_cmd(["git", "-C", str(tmp), "fetch", "--depth", "1", "origin", ref])
                        run_cmd(["git", "-C", str(tmp), "checkout", "FETCH_HEAD"])
                        clone_ok = True
                    except Exception:  # noqa: BLE001
                        err = str(e)
                        for task in group_tasks:
                            failures.append(
                                {
                                    "id": task["entry"]["id"],
                                    "sampleType": task["entry"]["sampleType"],
                                    "githubUrl": task["entry"]["githubUrl"],
                                    "error": f"clone_failed: {err}",
                                }
                            )
                else:
                    err = str(e)
                    for task in group_tasks:
                        failures.append(
                            {
                                "id": task["entry"]["id"],
                                "sampleType": task["entry"]["sampleType"],
                                "githubUrl": task["entry"]["githubUrl"],
                                "error": f"clone_failed: {err}",
                            }
                        )

            if not clone_ok:
                continue

            sparse_paths = []
            seen = set()
            for task in group_tasks:
                rel = task["target"].rel_path or "."
                if rel not in seen:
                    seen.add(rel)
                    sparse_paths.append(rel)

            try:
                run_cmd(["git", "-C", str(tmp), "sparse-checkout", "set", "--no-cone", *sparse_paths])
            except Exception as e:  # noqa: BLE001
                err = str(e)
                for task in group_tasks:
                    failures.append(
                        {
                            "id": task["entry"]["id"],
                            "sampleType": task["entry"]["sampleType"],
                            "githubUrl": task["entry"]["githubUrl"],
                            "error": f"sparse_checkout_failed: {err}",
                        }
                    )
                continue

            for task in group_tasks:
                entry = task["entry"]
                target: GitHubTarget = task["target"]
                rel = target.rel_path
                src = tmp if rel in {"", "."} else tmp / rel
                sample_type = entry["sampleType"]
                skill_id = entry["id"] or "unknown"
                skill_dir = run_dir / sample_type / sanitize_name(skill_id)

                metadata_payload = {
                    "sampleType": sample_type,
                    "sampleIndex": entry["sampleIndex"],
                    "skill": entry,
                    "github": {
                        "owner": target.owner,
                        "repo": target.repo,
                        "ref": target.ref,
                        "relativePath": target.rel_path,
                        "sourceUrl": target.source_url,
                    },
                }
                write_json(skill_dir / "metadata.json", metadata_payload)

                if not src.exists():
                    failures.append(
                        {
                            "id": skill_id,
                            "sampleType": sample_type,
                            "githubUrl": entry["githubUrl"],
                            "error": f"path_not_found: {rel or '.'}",
                        }
                    )
                    continue

                try:
                    copy_content(src, skill_dir / "content")
                    successes.append(
                        {
                            "id": skill_id,
                            "sampleType": sample_type,
                            "githubUrl": entry["githubUrl"],
                            "savedTo": str(skill_dir / "content"),
                        }
                    )
                except Exception as e:  # noqa: BLE001
                    failures.append(
                        {
                            "id": skill_id,
                            "sampleType": sample_type,
                            "githubUrl": entry["githubUrl"],
                            "error": f"copy_failed: {e}",
                        }
                    )

    summary = {
        "runDir": str(run_dir),
        "metadataPath": str(metadata_path),
        "popularCount": args.popular_count,
        "randomCount": args.random_count,
        "seed": args.seed,
        "allowRandomOverlap": args.allow_random_overlap,
        "groupCount": len(groups),
        "parseErrors": len(parse_errors),
        "successCount": len(successes),
        "failureCount": len(failures),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }

    write_json(run_dir / "results" / "summary.json", summary)
    write_json(run_dir / "results" / "parse_errors.json", parse_errors)
    write_json(run_dir / "results" / "successes.json", successes)
    write_json(run_dir / "results" / "failures.json", failures)

    print("[INFO] Download complete.")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        raise SystemExit(130)
