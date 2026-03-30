#!/usr/bin/env python3
"""
Build large sampled skill cohorts with guaranteed content counts.

Goal:
- popular: top-by-stars skills, keep downloading until N with content
- random: random skills (excluding selected popular IDs), keep downloading until N with content
"""

from __future__ import annotations

import argparse
import json
import random
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from download_sampled_skills import (
    GitHubTarget,
    build_manifest_item,
    copy_content,
    load_skills,
    parse_github_url,
    run_cmd,
    sanitize_name,
    write_json,
)


@dataclass
class DownloadBatchResult:
    successes: list[dict[str, Any]]
    failures: list[dict[str, Any]]
    parse_errors: list[dict[str, Any]]
    group_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build popular/random cohorts with target content counts.")
    parser.add_argument(
        "--metadata-path",
        default="skills_data/skills_metadata.json",
        help="Path to metadata JSON.",
    )
    parser.add_argument(
        "--output-root",
        default="skills_data/sampled_skills_1000",
        help="Output root folder for generated run.",
    )
    parser.add_argument(
        "--target-count",
        type=int,
        default=1000,
        help="Target content count for each cohort.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260226,
        help="Random seed for random cohort.",
    )
    parser.add_argument(
        "--popular-batch-size",
        type=int,
        default=250,
        help="Candidate count per popular batch.",
    )
    parser.add_argument(
        "--random-batch-size",
        type=int,
        default=300,
        help="Candidate count per random batch.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate manifests only, skip network download.",
    )
    return parser.parse_args()


def valid_skill_id(skill: dict[str, Any]) -> str | None:
    sid = skill.get("id")
    if not sid or not isinstance(sid, str):
        return None
    return sid


def pick_next_batch(
    ordered_skills: list[dict[str, Any]],
    start_idx: int,
    attempted_ids: set[str],
    batch_size: int,
) -> tuple[list[dict[str, Any]], int]:
    batch: list[dict[str, Any]] = []
    idx = start_idx
    while idx < len(ordered_skills) and len(batch) < batch_size:
        skill = ordered_skills[idx]
        idx += 1
        sid = valid_skill_id(skill)
        if not sid or sid in attempted_ids:
            continue
        batch.append(skill)
    return batch, idx


def download_batch(
    batch_skills: list[dict[str, Any]],
    cohort: str,
    run_dir: Path,
    id_to_folder: dict[str, str],
) -> DownloadBatchResult:
    entries = [build_manifest_item(skill=s, sample_type=cohort, index=0) for s in batch_skills]
    tasks: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []

    for skill, entry in zip(batch_skills, entries):
        url = entry.get("githubUrl")
        try:
            target = parse_github_url(url)
            tasks.append({"skill": skill, "entry": entry, "target": target})
        except Exception as e:  # noqa: BLE001
            parse_errors.append(
                {
                    "id": entry.get("id"),
                    "sampleType": cohort,
                    "githubUrl": url,
                    "error": f"parse_failed: {e}",
                }
            )

    groups: dict[tuple[str, str, str | None], list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        t: GitHubTarget = task["target"]
        groups[(t.owner, t.repo, t.ref)].append(task)

    successes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    group_idx = 0
    group_total = len(groups)
    for (owner, repo, ref), group_tasks in groups.items():
        group_idx += 1
        print(f"[{cohort}]   group {group_idx}/{group_total}: {owner}/{repo} ref={ref or '<default>'} tasks={len(group_tasks)}")

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
                                    "sampleType": cohort,
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
                                "sampleType": cohort,
                                "githubUrl": task["entry"]["githubUrl"],
                                "error": f"clone_failed: {err}",
                            }
                        )

            if not clone_ok:
                continue

            sparse_paths: list[str] = []
            seen_rel: set[str] = set()
            for task in group_tasks:
                rel = task["target"].rel_path or "."
                if rel not in seen_rel:
                    seen_rel.add(rel)
                    sparse_paths.append(rel)

            try:
                run_cmd(["git", "-C", str(tmp), "sparse-checkout", "set", "--no-cone", *sparse_paths])
            except Exception as e:  # noqa: BLE001
                err = str(e)
                for task in group_tasks:
                    failures.append(
                        {
                            "id": task["entry"]["id"],
                            "sampleType": cohort,
                            "githubUrl": task["entry"]["githubUrl"],
                            "error": f"sparse_checkout_failed: {err}",
                        }
                    )
                continue

            for task in group_tasks:
                entry = task["entry"]
                target: GitHubTarget = task["target"]
                sid = entry.get("id")
                if not sid:
                    failures.append(
                        {
                            "id": None,
                            "sampleType": cohort,
                            "githubUrl": entry.get("githubUrl"),
                            "error": "invalid_id",
                        }
                    )
                    continue

                rel = target.rel_path
                src = tmp if rel in {"", "."} else tmp / rel
                folder_name = sanitize_name(sid)
                skill_dir = run_dir / cohort / folder_name

                metadata_payload = {
                    "sampleType": cohort,
                    "sampleIndex": 0,
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
                            "id": sid,
                            "sampleType": cohort,
                            "githubUrl": entry.get("githubUrl"),
                            "error": f"path_not_found: {rel or '.'}",
                        }
                    )
                    continue

                try:
                    copy_content(src, skill_dir / "content")
                    id_to_folder[sid] = folder_name
                    successes.append(
                        {
                            "id": sid,
                            "sampleType": cohort,
                            "githubUrl": entry.get("githubUrl"),
                            "savedTo": str(skill_dir / "content"),
                            "skill": task["skill"],
                        }
                    )
                except Exception as e:  # noqa: BLE001
                    failures.append(
                        {
                            "id": sid,
                            "sampleType": cohort,
                            "githubUrl": entry.get("githubUrl"),
                            "error": f"copy_failed: {e}",
                        }
                    )

    return DownloadBatchResult(
        successes=successes,
        failures=failures,
        parse_errors=parse_errors,
        group_count=len(groups),
    )


def count_content_dirs(run_dir: Path, cohort: str) -> int:
    cohort_dir = run_dir / cohort
    if not cohort_dir.exists():
        return 0
    return sum(1 for p in cohort_dir.iterdir() if p.is_dir() and (p / "content").exists())


def ensure_clean_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def rewrite_metadata(
    run_dir: Path,
    cohort: str,
    manifest: list[dict[str, Any]],
    id_to_folder: dict[str, str],
) -> None:
    for item in manifest:
        sid = item["id"]
        folder = id_to_folder[sid]
        md_path = run_dir / cohort / folder / "metadata.json"
        payload = json.loads(md_path.read_text(encoding="utf-8"))
        payload["sampleType"] = cohort
        payload["sampleIndex"] = item["sampleIndex"]
        payload["skill"] = item
        md_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_failure_categories(failures: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for f in failures:
        err = str(f.get("error", "unknown"))
        category = err.split(":", 1)[0]
        counter[category] += 1
    return dict(counter)


def main() -> int:
    args = parse_args()
    metadata_path = Path(args.metadata_path)
    output_root = Path(args.output_root)
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / f"run_{run_ts}"

    ensure_clean_dir(run_dir / "popular")
    ensure_clean_dir(run_dir / "random")
    ensure_clean_dir(run_dir / "manifests")
    ensure_clean_dir(run_dir / "results")

    skills = load_skills(metadata_path)
    skills = [s for s in skills if s.get("githubUrl") and valid_skill_id(s)]
    skills_sorted = sorted(skills, key=lambda s: (-(s.get("stars") or 0), s.get("id") or ""))

    print(f"[INFO] Run dir: {run_dir}")
    print(f"[INFO] Metadata skills with githubUrl: {len(skills_sorted)}")
    print(f"[INFO] Target per cohort: {args.target_count}")
    print(f"[INFO] Seed: {args.seed}")
    print(f"[INFO] Dry-run: {args.dry_run}")

    if len(skills_sorted) < args.target_count * 2:
        raise ValueError("Skill pool too small for requested targets.")

    all_failures: list[dict[str, Any]] = []
    all_parse_errors: list[dict[str, Any]] = []
    all_successes: list[dict[str, Any]] = []

    popular_success_skills: list[dict[str, Any]] = []
    popular_attempted_ids: set[str] = set()
    popular_id_to_folder: dict[str, str] = {}
    popular_idx = 0
    popular_batches = 0
    popular_groups_total = 0

    while len(popular_success_skills) < args.target_count:
        need = args.target_count - len(popular_success_skills)
        batch_size = min(args.popular_batch_size, need)
        batch_skills, popular_idx = pick_next_batch(skills_sorted, popular_idx, popular_attempted_ids, batch_size)
        if not batch_skills:
            raise RuntimeError("Exhausted skill pool before popular target reached.")

        popular_batches += 1
        for s in batch_skills:
            popular_attempted_ids.add(s["id"])

        if args.dry_run:
            # In dry-run mode, mark all batch candidates as pseudo-success.
            for s in batch_skills:
                if len(popular_success_skills) >= args.target_count:
                    break
                popular_success_skills.append(s)
            print(f"[popular] batch {popular_batches}: dry-run accepted {len(batch_skills)} candidates")
            continue

        print(f"[popular] batch {popular_batches}: candidates={len(batch_skills)} need={need}")
        result = download_batch(batch_skills, "popular", run_dir, popular_id_to_folder)
        popular_groups_total += result.group_count
        all_failures.extend(result.failures)
        all_parse_errors.extend(result.parse_errors)

        seen_pop = {s["id"] for s in popular_success_skills}
        added = 0
        for suc in result.successes:
            sid = suc["id"]
            if sid in seen_pop:
                continue
            popular_success_skills.append(suc["skill"])
            all_successes.append(
                {
                    "id": sid,
                    "sampleType": "popular",
                    "githubUrl": suc["githubUrl"],
                    "savedTo": suc["savedTo"],
                }
            )
            seen_pop.add(sid)
            added += 1

        print(
            f"[popular] batch {popular_batches} done: +{added} success, "
            f"batch_fail={len(result.failures) + len(result.parse_errors)}, "
            f"total={len(popular_success_skills)}/{args.target_count}"
        )

    popular_success_skills = popular_success_skills[: args.target_count]
    popular_success_ids = {s["id"] for s in popular_success_skills}

    random_pool = [s for s in skills_sorted if s["id"] not in popular_success_ids]
    rng = random.Random(args.seed)
    rng.shuffle(random_pool)

    random_success_skills: list[dict[str, Any]] = []
    random_attempted_ids: set[str] = set()
    random_id_to_folder: dict[str, str] = {}
    random_idx = 0
    random_batches = 0
    random_groups_total = 0

    while len(random_success_skills) < args.target_count:
        need = args.target_count - len(random_success_skills)
        batch_size = min(args.random_batch_size, need)
        batch_skills, random_idx = pick_next_batch(random_pool, random_idx, random_attempted_ids, batch_size)
        if not batch_skills:
            raise RuntimeError("Exhausted skill pool before random target reached.")

        random_batches += 1
        for s in batch_skills:
            random_attempted_ids.add(s["id"])

        if args.dry_run:
            for s in batch_skills:
                if len(random_success_skills) >= args.target_count:
                    break
                random_success_skills.append(s)
            print(f"[random] batch {random_batches}: dry-run accepted {len(batch_skills)} candidates")
            continue

        print(f"[random] batch {random_batches}: candidates={len(batch_skills)} need={need}")
        result = download_batch(batch_skills, "random", run_dir, random_id_to_folder)
        random_groups_total += result.group_count
        all_failures.extend(result.failures)
        all_parse_errors.extend(result.parse_errors)

        seen_rnd = {s["id"] for s in random_success_skills}
        added = 0
        for suc in result.successes:
            sid = suc["id"]
            if sid in seen_rnd:
                continue
            random_success_skills.append(suc["skill"])
            all_successes.append(
                {
                    "id": sid,
                    "sampleType": "random",
                    "githubUrl": suc["githubUrl"],
                    "savedTo": suc["savedTo"],
                }
            )
            seen_rnd.add(sid)
            added += 1

        print(
            f"[random] batch {random_batches} done: +{added} success, "
            f"batch_fail={len(result.failures) + len(result.parse_errors)}, "
            f"total={len(random_success_skills)}/{args.target_count}"
        )

    random_success_skills = random_success_skills[: args.target_count]
    random_success_ids = {s["id"] for s in random_success_skills}
    overlap = popular_success_ids & random_success_ids
    if overlap:
        raise RuntimeError(f"Unexpected overlap between popular/random successes: {len(overlap)}")

    popular_manifest = [
        build_manifest_item(skill=s, sample_type="popular", index=i + 1)
        for i, s in enumerate(popular_success_skills)
    ]
    random_manifest = [
        build_manifest_item(skill=s, sample_type="random", index=i + 1)
        for i, s in enumerate(random_success_skills)
    ]
    combined_manifest = popular_manifest + random_manifest

    write_json(run_dir / "manifests" / "popular_top.json", popular_manifest)
    write_json(run_dir / "manifests" / "random_sample.json", random_manifest)
    write_json(run_dir / "manifests" / "combined_sample.json", combined_manifest)

    if not args.dry_run:
        rewrite_metadata(run_dir, "popular", popular_manifest, popular_id_to_folder)
        rewrite_metadata(run_dir, "random", random_manifest, random_id_to_folder)

    summary = {
        "runDir": str(run_dir),
        "metadataPath": str(metadata_path),
        "targetCount": args.target_count,
        "seed": args.seed,
        "dryRun": args.dry_run,
        "successCount": len(popular_manifest) + len(random_manifest),
        "popular": {
            "successCount": len(popular_manifest),
            "attemptedCount": len(popular_attempted_ids),
            "batchCount": popular_batches,
            "groupCount": popular_groups_total,
            "contentCount": count_content_dirs(run_dir, "popular"),
        },
        "random": {
            "successCount": len(random_manifest),
            "attemptedCount": len(random_attempted_ids),
            "batchCount": random_batches,
            "groupCount": random_groups_total,
            "contentCount": count_content_dirs(run_dir, "random"),
        },
        "failureCount": len(all_failures),
        "parseErrorCount": len(all_parse_errors),
        "failureCategories": summarize_failure_categories(all_failures),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }

    write_json(run_dir / "results" / "summary.json", summary)
    write_json(run_dir / "results" / "successes.json", all_successes)
    write_json(run_dir / "results" / "failures.json", all_failures)
    write_json(run_dir / "results" / "parse_errors.json", all_parse_errors)

    print("[INFO] Build complete.")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
