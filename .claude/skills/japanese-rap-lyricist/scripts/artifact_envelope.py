#!/usr/bin/env python3
"""Wrap and validate portable lyric-workflow artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


STATUSES = {"ready", "partial", "blocked", "unverified", "stale"}


def brief_hash(brief: dict) -> str:
    encoded = json.dumps(brief, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def wrap(
    payload: dict | list,
    *,
    schema: str,
    run_id: str,
    brief: dict,
    role: str,
    instance_id: str,
    status: str,
    inputs: list[str],
    evidence: list[str],
    warnings: list[str],
) -> dict:
    if status not in STATUSES:
        raise ValueError(f"invalid status: {status}")
    if not run_id.strip() or not role.strip() or not instance_id.strip():
        raise ValueError("run_id, role, and instance_id must be nonempty")
    return {
        "schema": schema,
        "run_id": run_id,
        "brief_hash": brief_hash(brief),
        "producer": {"role": role, "instance_id": instance_id},
        "status": status,
        "inputs": [{"artifact": item} for item in inputs],
        "evidence": [{"pointer": item} for item in evidence],
        "warnings": warnings,
        "payload": payload,
    }


def validate_envelopes(items: list[dict], brief: dict) -> dict:
    expected = brief_hash(brief)
    errors: list[str] = []
    run_ids = set()
    for index, item in enumerate(items, 1):
        for field in (
            "schema", "run_id", "brief_hash", "producer", "status",
            "inputs", "evidence", "warnings", "payload",
        ):
            if field not in item:
                errors.append(f"artifact {index}: missing {field}")
        if item.get("brief_hash") != expected:
            errors.append(f"artifact {index}: stale or foreign brief_hash")
        if item.get("status") not in STATUSES:
            errors.append(f"artifact {index}: invalid status")
        producer = item.get("producer") or {}
        if not producer.get("role") or not producer.get("instance_id"):
            errors.append(f"artifact {index}: producer is incomplete")
        if item.get("run_id"):
            run_ids.add(item["run_id"])
    if len(run_ids) > 1:
        errors.append("artifacts contain multiple run_ids")
    return {
        "valid": not errors,
        "errors": errors,
        "brief_hash": expected,
        "artifact_count": len(items),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    wrap_parser = sub.add_parser("wrap")
    wrap_parser.add_argument("payload", type=Path)
    wrap_parser.add_argument("--brief", type=Path, required=True)
    wrap_parser.add_argument("--schema", required=True)
    wrap_parser.add_argument("--run-id", required=True)
    wrap_parser.add_argument("--role", required=True)
    wrap_parser.add_argument("--instance-id", required=True)
    wrap_parser.add_argument("--status", choices=sorted(STATUSES), required=True)
    wrap_parser.add_argument("--input", action="append", default=[])
    wrap_parser.add_argument("--evidence", action="append", default=[])
    wrap_parser.add_argument("--warning", action="append", default=[])
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("artifacts", type=Path, nargs="+")
    validate_parser.add_argument("--brief", type=Path, required=True)
    args = parser.parse_args()
    brief = json.loads(args.brief.read_text(encoding="utf-8"))
    if args.command == "wrap":
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
        result = wrap(
            payload,
            schema=args.schema,
            run_id=args.run_id,
            brief=brief,
            role=args.role,
            instance_id=args.instance_id,
            status=args.status,
            inputs=args.input,
            evidence=args.evidence,
            warnings=args.warning,
        )
    else:
        items = [
            json.loads(path.read_text(encoding="utf-8")) for path in args.artifacts
        ]
        result = validate_envelopes(items, brief)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
