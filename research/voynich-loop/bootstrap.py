"""One-shot initialization from existing receipts. No analysis, no vault contents copied.

The candidate L/S split is metadata-only and EXPOSED_OR_UNCERTIFIED. It is not a
never-touched v6 replication cohort. Missing v6 eligibility is an activation blocker.
"""
from pathlib import Path
import json
import shutil
from loop import Store, filehash, writejson, require

R = Path(__file__).resolve().parent
P = R.parent
SPEC = Path(r"C:\Users\lewis\.codex\attachments\5cd60a24-a87a-4786-aeb8-90345e57f701\Pasted text.txt")
SEED = "voynich-loop-2026-10-24-label-folio-split-v1"
RESERVED = ["f72v1", "f72v2", "f73r", "f73v"]


def candidate_split(rows_path):
    import hashlib
    from collections import defaultdict
    # Existing published atlas, never treated as untouched input. Discard text fields.
    rows = json.loads(rows_path.read_text(encoding="utf-8"))
    groups = defaultdict(set)
    for row in rows:
        if row[1] not in RESERVED and str(row[5]).startswith(("L", "S")):
            groups[row[1]].add(row[8])
    order = sorted(groups, key=lambda folio: hashlib.sha256((SEED + ":" + folio).encode()).hexdigest())
    total = sum(len(v) for v in groups.values())
    sizes = [0]
    for folio in order:
        sizes.append(sizes[-1] + len(groups[folio]))
    k = min(range(1, len(order)), key=lambda n: abs(sizes[n] - .3 * total)) if len(order) > 1 else 0
    reserved = set(order[:k])
    return dict(status="CANDIDATE_METADATA_SPLIT_ONLY", seed=SEED,
        algorithm="SHA256(seed + ':' + folio) ascending, prefix nearest 30% of unique physical candidate loci; no folio split",
        source_sha256=filehash(rows_path), eligibility="All atlas reading codes, raw format starts L or S; v6 eligibility NOT supplied",
        exposure="EXPOSED_OR_UNCERTIFIED", never_touched=False,
        target_locus_fraction=.30, actual_locus_fraction=sizes[k] / total if total else 0,
        unique_candidate_loci=total, reserved_candidate_loci=sizes[k],
        reserved_zodiac_folios=RESERVED,
        folios=[dict(folio=f, partition="candidate_reserve" if f in reserved else "open",
                     loci=sorted(groups[f])) for f in order],
        limitation="Fixed now to prevent seed shopping. Does not certify novel labels, untouched material, or OS custody. New eligibility requires a separately versioned design and exposure review, preserving this assignment.")


def main():
    require(not (R / "EVENTS.jsonl").exists(), "Already bootstrapped")
    shutil.copyfile(SPEC, R / "ORIGINAL-SPEC.md")
    plan = candidate_split(P / "complete-atlas-v56" / "ROWS.json")
    writejson(R / "SPLIT-PLAN.json", plan)
    def sources(*names):
        return {str((P / name).resolve()): filehash(P / name) for name in names}
    def task(id, tier, status, reason, evidence, rank):
        return dict(id=id, tier=tier, status=status, reason=reason, sources=evidence,
                    priority=rank, expected_information=None, cost=None,
                    ranking="User seed order; planner must estimate information/cost before dispatch")
    queue = [
        task("v4.2-C", "descriptive", "READY", "Optional retrospective OR context map; separate from v3 primaries and image work. Infrastructure activation first.",
             sources("sh-qok-image-context-v4/AMENDMENT-v4.2-effect-scale.md", "sh-qok-context-map-v3/PROTOCOL.json"), 7),
        task("v3.1-rescore", "historical", "COMPLETE", "Already separately frozen/re-adjudicated; retrospective, no global-alpha credit or automatic held-up promotion.",
             sources("sh-qok-retrospective-readjudication-v1/REPORT.md", "sh-qok-retrospective-readjudication-v1/PROTOCOL.json"), 6),
        task("v5-system-type", "exploratory", "BLOCKED", "Full v5 spec absent; generator/recovery/support definitions needed before sandboxing.", {}, 5),
        task("v6-label-objects", "infrastructure", "BLOCKED", "Full v6 spec/label eligibility absent; existing candidate split is exposed, not never-touched replication.", {}, 4),
        task("attempt-C-transcription-upgrade", "robustness", "BLOCKED", "No newer licensed transcription selected or custody/overlap review; freeze unchanged estimand before robustness work.",
             sources("sh-qok-single-target-attempt-c/PROTOCOL.json"), 3),
        task("v4-image-context", "infrastructure", "BLOCKED", "Concurrent owners have different source-specific release scopes. Do not dispatch their work; require owner handoff and >=30% registration yield on rated pages, else park.",
             sources("image-context-v4/registration/HOLD.json", "sh-qok-image-context-v4/V4.2-FREEZE.json"), 2),
        task("source-tradition-structure", "exploratory", "BLOCKED", "Depends on v5 survivors.", {}, 1),
        task("v103", "exploratory", "PARKED", "Explicitly parked by supplied design.", {}, 0),
        task("rosettes-leaveout", "exploratory", "COMPLETE", "Closed by supplied design; no new leave-out grids.", {}, 0),
        task("ey-blocking", "exploratory", "COMPLETE", "Closed by supplied design.", {}, 0),
        task("letter-substitution", "exploratory", "COMPLETE", "Closed by supplied design.", {}, 0),
    ]
    Store(R).initialize(queue, {str(R / "SPLIT-PLAN.json"): filehash(R / "SPLIT-PLAN.json")})
    print(Store(R).report())


if __name__ == "__main__":
    main()
