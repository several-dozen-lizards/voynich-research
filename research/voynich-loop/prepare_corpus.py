"""One-shot custody preparation, not filesystem sealing or research scoring.

Copies only the existing atlas transcription rows. Images and raw EVT are NOT
worker inputs. The candidate label reserve is exposed/uncertified and awaits v6.
Run on the keeper side, never from a worker process.
"""
import argparse
import json
from pathlib import Path
from loop import require, filehash, writejson, utc


def prepare(source, plan_path, open_dir, vault_dir):
    source, plan_path = Path(source).resolve(), Path(plan_path).resolve()
    open_dir, vault_dir = Path(open_dir).resolve(), Path(vault_dir).resolve()
    require(open_dir != vault_dir and open_dir not in vault_dir.parents and vault_dir not in open_dir.parents,
            "Open and vault folders must be disjoint")
    require(not open_dir.exists() and not vault_dir.exists(), "One-shot output folders must not exist")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    require(filehash(source) == plan["source_sha256"], "Atlas changed since split")
    zodiac = set(plan["reserved_zodiac_folios"])
    label_folios = {x["folio"] for x in plan["folios"] if x["partition"] == "candidate_reserve"}
    require(not zodiac & label_folios, "Overlapping reserve definitions")
    rows = json.loads(source.read_text(encoding="utf-8"))
    require(all(isinstance(r, list) and len(r) == 11 for r in rows), "Unexpected atlas schema")
    partitions = {"open": [], "zodiac": [], "candidate-label-folios": []}
    for row in rows:
        group = "zodiac" if row[1] in zodiac else "candidate-label-folios" if row[1] in label_folios else "open"
        partitions[group].append(row)
    require(sum(len(v) for v in partitions.values()) == len(rows), "Partition accounting failure")
    require(all(r[1] not in zodiac | label_folios for r in partitions["open"]), "Reserved folio leaked into open packet")
    require(all(partitions.values()), "Empty partition: review schema before custody preparation")
    open_dir.mkdir(parents=True)
    vault_dir.mkdir(parents=True)
    writejson(open_dir / "ROWS.json", partitions["open"])
    for name in ("zodiac", "candidate-label-folios"):
        writejson(vault_dir / (name + ".json"), partitions[name])
    # Confirm actual bytes written, not just in-memory partitions.
    actual_open = json.loads((open_dir / "ROWS.json").read_text(encoding="utf-8"))
    require(actual_open == partitions["open"] and all(r[1] not in zodiac | label_folios for r in actual_open),
            "File-level reserve leakage")
    receipt = dict(status="PREPARED_UNSEALED", utc=utc(), source_sha256=filehash(source),
        split_plan_sha256=filehash(plan_path),
        exposure="EXPOSED_OR_UNCERTIFIED; not a never-touched reserve",
        stronger_exclusion="Whole candidate-reserve folios removed from open rows across ALL readings and formats; support must be recalculated on this reduced corpus before freezing.",
        counts={name: len(v) for name, v in partitions.items()},
        folio_counts={name: len({r[1] for r in v}) for name, v in partitions.items()},
        open_files={str(open_dir / "ROWS.json"): filehash(open_dir / "ROWS.json")},
        vault_files={str(vault_dir / (name + ".json")): filehash(vault_dir / (name + ".json")) for name in ("zodiac", "candidate-label-folios")},
        file_level_exclusion_verified=True,
        filesystem_isolation_qualified=False,
        no_worker_launch=True, no_analysis=True,
        missing="OS-denied access probes for every worker, code/keeper write denial, clean context, network denial, and approved v6 eligibility/custody before activation. No images/raw EVT/archives/reports in worker packet.")
    writejson(open_dir / "OPEN-MANIFEST.json", dict(status="FILTERED_TEXT_ONLY", files=receipt["open_files"],
        source_sha256=receipt["source_sha256"], split_plan_sha256=receipt["split_plan_sha256"],
        note="Worker gets this folder only, no access to original atlas or project tree. Never fetch full public manuscript text or scans during protected work."))
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault-target", required=True, type=Path)
    args = p.parse_args()
    root = Path(__file__).resolve().parent
    require(not (root / "CUSTODY-PREPARATION.json").exists(), "Preparation already exists")
    receipt = prepare(root.parent / "complete-atlas-v56/ROWS.json", root / "SPLIT-PLAN.json",
                      root / "open-data", args.vault_target)
    writejson(root / "CUSTODY-PREPARATION.json", receipt)
    print(json.dumps({k: receipt[k] for k in ("status", "counts", "folio_counts", "file_level_exclusion_verified", "filesystem_isolation_qualified")}, indent=2))


if __name__ == "__main__":
    main()
