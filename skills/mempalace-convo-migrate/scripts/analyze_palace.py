#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze mempalace palace and categorize records."""

import sys
import json
from pathlib import Path


def is_conversation_record(metadata):
    """Check if a record is a conversation record."""
    source = metadata.get("source_file", "")
    ingest_mode = metadata.get("ingest_mode", "")
    wing = metadata.get("wing", "")

    return (
        ".claude" in source and "projects" in source
    ) or ingest_mode == "convos" or wing in ("sessions", "wing_sessions") or wing.endswith("-sessions")


def analyze_palace(palace_path):
    """Analyze palace and print statistics."""
    try:
        import chromadb
    except ImportError:
        print("Error: chromadb not installed. Run: pip install chromadb")
        sys.exit(1)

    client = chromadb.PersistentClient(path=palace_path)
    collections = client.list_collections()

    if not collections:
        print(f"No collections found in {palace_path}")
        return

    for col_info in collections:
        col = client.get_collection(col_info.name)
        total = col.count()

        print(f"\n{'='*60}")
        print(f"Collection: {col.name}")
        print(f"Total records: {total}")
        print(f"{'='*60}")

        if total == 0:
            continue

        # Sample and categorize
        results = col.get(limit=min(1000, total))

        convo_count = 0
        file_count = 0
        wings = {}
        halls = {}
        sources = {}

        for meta in results["metadatas"]:
            if is_conversation_record(meta):
                convo_count += 1
            else:
                file_count += 1

            wing = meta.get("wing", "unknown")
            wings[wing] = wings.get(wing, 0) + 1

            hall = meta.get("hall", "unknown")
            halls[hall] = halls.get(hall, 0) + 1

            source = meta.get("source_file", "unknown")
            ext = Path(source).suffix or "no_ext"
            sources[ext] = sources.get(ext, 0) + 1

        # Scale up if sampled
        scale = total / len(results["metadatas"]) if results["metadatas"] else 1

        print(f"\nEstimated breakdown:")
        print(f"  Conversations: {int(convo_count * scale)}")
        print(f"  Project files: {int(file_count * scale)}")

        print(f"\nWings:")
        for wing, count in sorted(wings.items(), key=lambda x: -x[1])[:10]:
            print(f"  {wing}: {int(count * scale)}")

        print(f"\nHalls:")
        for hall, count in sorted(halls.items(), key=lambda x: -x[1]):
            print(f"  {hall}: {int(count * scale)}")

        print(f"\nFile types:")
        for ext, count in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"  {ext}: {int(count * scale)}")

        # Show sample conversation
        for i, meta in enumerate(results["metadatas"]):
            if is_conversation_record(meta):
                print(f"\n{'='*60}")
                print("Sample conversation record:")
                print(f"{'='*60}")
                print(f"ID: {results['ids'][i]}")
                print(f"Metadata: {json.dumps(meta, indent=2, ensure_ascii=False)}")
                doc = results["documents"][i]
                if doc:
                    print(f"Text preview (first 300 chars):")
                    print(doc[:300])
                break


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_palace.py <palace_path>")
        print("Example: python analyze_palace.py ~/.mempalace/palace")
        sys.exit(1)

    analyze_palace(sys.argv[1])
