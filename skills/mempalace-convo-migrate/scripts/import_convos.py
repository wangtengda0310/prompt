#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import conversation records into mempalace palace with new embedding model."""

import sys
import json
import os
from datetime import datetime


def get_embedding_function():
    """Get embedding function from current mempalace config."""
    try:
        from mempalace.embedding import get_embedding_function as get_ef
        return get_ef()
    except ImportError:
        print("Error: mempalace not installed.")
        sys.exit(1)


def import_convos(palace_path, jsonl_file):
    """Import conversation records from JSONL file."""
    try:
        import chromadb
    except ImportError:
        print("Error: chromadb not installed. Run: pip install chromadb")
        sys.exit(1)

    if not os.path.exists(jsonl_file):
        print(f"Error: File not found: {jsonl_file}")
        sys.exit(1)

    # Get embedding function (uses current config)
    print("Initializing embedding function...")
    ef = get_embedding_function()

    # Test embedding to verify model
    test_vec = ef(["test"])[0]
    print(f"Embedding dimension: {len(test_vec)}")

    client = chromadb.PersistentClient(path=palace_path)

    # Get or create collection
    col_name = "mempalace_drawers"
    try:
        col = client.get_collection(col_name)
        print(f"Using existing collection: {col_name}")
    except Exception:
        col = client.create_collection(col_name)
        print(f"Created new collection: {col_name}")

    # Read and import records
    imported = 0
    errors = 0
    batch = []
    batch_size = 100

    print(f"\nImporting from {jsonl_file}...")

    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
                document = record.get("document", "")
                metadata = record.get("metadata", {})
                record_id = record.get("id", f"imported_{datetime.now().timestamp()}_{imported}")

                if not document:
                    continue

                # Generate new embedding with current model
                embedding = ef([document])[0]

                batch.append({
                    "id": record_id,
                    "embedding": embedding,
                    "document": document,
                    "metadata": metadata
                })

                if len(batch) >= batch_size:
                    _insert_batch(col, batch)
                    imported += len(batch)
                    print(f"  Imported {imported} records...")
                    batch = []

            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  Error processing record: {e}")

    # Insert remaining
    if batch:
        _insert_batch(col, batch)
        imported += len(batch)

    print(f"\n{'='*60}")
    print(f"Import complete!")
    print(f"  Imported: {imported}")
    print(f"  Errors: {errors}")
    print(f"  Collection: {col_name}")
    print(f"  Total in collection: {col.count()}")
    print(f"{'='*60}")


def _insert_batch(col, batch):
    """Insert a batch of records."""
    col.add(
        ids=[r["id"] for r in batch],
        embeddings=[r["embedding"] for r in batch],
        documents=[r["document"] for r in batch],
        metadatas=[r["metadata"] for r in batch]
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python import_convos.py <palace_path> <conversations.jsonl>")
        print("Example: python import_convos.py ~/.mempalace/palace /tmp/export/conversations.jsonl")
        sys.exit(1)

    import_convos(sys.argv[1], sys.argv[2])
