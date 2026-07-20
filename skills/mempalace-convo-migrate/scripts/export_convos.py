#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export conversation records from mempalace palace."""

import sys
import json
import os
from pathlib import Path
from datetime import datetime


def is_conversation_record(metadata):
    """Check if a record is a conversation record."""
    source = metadata.get("source_file", "")
    ingest_mode = metadata.get("ingest_mode", "")
    wing = metadata.get("wing", "")

    return (
        ".claude" in source and "projects" in source
    ) or ingest_mode == "convos" or wing in ("sessions", "wing_sessions") or wing.endswith("-sessions")


def export_convos(palace_path, output_dir):
    """Export conversation records to JSONL files."""
    try:
        import chromadb
    except ImportError:
        print("Error: chromadb not installed. Run: pip install chromadb")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    client = chromadb.PersistentClient(path=palace_path)
    collections = client.list_collections()

    total_convos = 0
    total_files = 0

    for col_info in collections:
        col = client.get_collection(col_info.name)
        total = col.count()

        if total == 0:
            continue

        print(f"Processing collection: {col.name} ({total} records)")

        # Export in batches
        batch_size = 1000
        convo_records = []

        for offset in range(0, total, batch_size):
            results = col.get(
                limit=min(batch_size, total - offset),
                offset=offset,
                include=["documents", "metadatas"]
            )

            for i in range(len(results["ids"])):
                meta = results["metadatas"][i]
                if is_conversation_record(meta):
                    record = {
                        "id": results["ids"][i],
                        "document": results["documents"][i],
                        "metadata": meta
                    }
                    convo_records.append(record)
                    total_convos += 1
                else:
                    total_files += 1

        # Write to JSONL
        output_file = os.path.join(output_dir, f"{col.name}_conversations.jsonl")
        with open(output_file, "w", encoding="utf-8") as f:
            for record in convo_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"  Exported {len(convo_records)} conversations to {output_file}")

    # Write summary
    summary = {
        "exported_at": datetime.now().isoformat(),
        "source_palace": palace_path,
        "total_conversations": total_convos,
        "total_project_files": total_files,
        "output_dir": output_dir
    }

    summary_file = os.path.join(output_dir, "summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Export complete!")
    print(f"  Conversations: {total_convos}")
    print(f"  Project files (skipped): {total_files}")
    print(f"  Summary: {summary_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python export_convos.py <palace_path> <output_dir>")
        print("Example: python export_convos.py ~/.mempalace/palace /tmp/export")
        sys.exit(1)

    export_convos(sys.argv[1], sys.argv[2])
