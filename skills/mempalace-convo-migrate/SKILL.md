---
name: mempalace-convo-migrate
description: |
  Migrate mempalace conversation records between palaces with different embedding models.
  
  Use this skill when the user needs to:
  - Extract conversation records from a mempalace palace
  - Identify which records are Claude Code conversations vs project files
  - Export conversations for re-import with a different embedding model
  - Migrate mempalace data from WSL to Windows or vice versa
  - Switch embedding models (e.g., MiniLM to Qwen) while preserving conversation history
  - Backup or inspect mempalace conversation data
  
  This skill handles Chinese text properly and supports both Windows and WSL environments.
---

# MemPalace Conversation Migration Skill

## Purpose

MemPalace stores both **project files** (code, docs) and **conversation records** (Claude Code sessions) in the same palace. When switching embedding models (e.g., from 384d MiniLM to 1024d Qwen), the vector embeddings cannot be reused, but the **original text content can**.

This skill provides tools to:
1. **Identify** conversation records in a palace
2. **Export** them with metadata preserved
3. **Re-import** them into a new palace with a different model

## When to Use

| Scenario | Action |
|----------|--------|
| Switching from MiniLM to Qwen/BAAI | Export convos, create new palace, re-import |
| Migrating WSL palace to Windows | Export from WSL, import to Windows |
| Backup conversation history | Export convos to JSON/JSONL files |
| Inspecting what's in a palace | List and categorize records |
| Cleaning up old conversations | Identify and selectively remove |

## Identifying Conversation Records

Conversation records have these distinguishing features in their metadata:

```python
{
    "source_file": "C:\\Users\\...\\.claude\\projects\\<project-id>\\<session-id>.jsonl",
    "ingest_mode": "convos",           # <-- Key indicator
    "extract_mode": "exchange",        # <-- Key indicator
    "wing": "sessions",                # <-- Key indicator (or "rain-qa-func-sessions")
    "hall": "technical" | "diary",     # Conversation classification
    "room": "technical" | "diary",
    "added_by": "mempalace",
    "filed_at": "2026-05-20T18:33:20.063290",
    "chunk_index": 0,
    "normalize_version": 2
}
```

**Detection rules** (any of these indicates a conversation record):
1. `source_file` contains `.claude/projects/`
2. `ingest_mode` == `"convos"`
3. `wing` == `"sessions"` or ends with `-sessions`

**Non-conversation records** (project files) typically have:
- `source_file`: project code paths (`.go`, `.vue`, `.md`, etc.)
- `ingest_mode`: `"files"` or missing
- `wing`: project name (e.g., `"rain-qa-func"`, `"config"`, `"server"`)

## Workflow

### Step 1: Analyze Palace

Use the bundled script to analyze a palace:

```bash
python scripts/analyze_palace.py <palace_path>
```

Output shows:
- Total records
- Conversation count vs file count
- Wings and rooms distribution
- Sample records for verification

### Step 2: Export Conversations

```bash
python scripts/export_convos.py <source_palace> <output_dir>
```

This exports:
- `conversations.jsonl` — All conversation records with text and metadata
- `summary.json` — Statistics and mapping info
- `verification_sample.txt` — Human-readable samples for verification

### Step 3: Create New Palace (with new model)

Configure the new embedding model in `~/.mempalace/config.json`, then:

```bash
# Re-mine project files (fresh vectors with new model)
mempalace mine ~/project --wing myproject

# Or start with empty palace
mempalace init ~/project
```

### Step 4: Import Conversations

```bash
python scripts/import_convos.py <new_palace> <conversations.jsonl>
```

This re-generates embeddings using the **new palace's configured model** while preserving original text and metadata.

## Environment Support

### Windows

```powershell
# Palace path
$env:MEMPALACE_PALACE = "$env:USERPROFILE\.mempalace\palace"

# Run script
python scripts/export_convos.py "$env:MEMPALACE_PALACE" "C:\tmp\export"
```

### WSL

```bash
# Palace path
export MEMPALACE_PALACE="/root/.mempalace/palace"

# Run script
python3 scripts/export_convos.py "$MEMPALACE_PALACE" "/mnt/c/tmp/export"
```

### Cross-Platform Migration (WSL → Windows)

```bash
# In WSL: export
python3 scripts/export_convos.py /root/.mempalace/palace /mnt/c/tmp/wsl_export

# In Windows: import to new palace
python scripts/import_convos.py C:\Users\...\.mempalace\palace C:\tmp\wsl_export\conversations.jsonl
```

## Important Notes

### Text Encoding

All scripts handle UTF-8 properly. Chinese text is preserved in both export and import.

### Vector Regeneration

When importing to a new palace, embeddings are **re-generated** using the new model. This is correct and expected — old vectors from a different model cannot be reused.

### Metadata Preservation

The following metadata is preserved during migration:
- `wing`, `room`, `hall`
- `source_file` (original conversation path)
- `filed_at` (original timestamp)
- `chunk_index`
- `ingest_mode`, `extract_mode`

### Chunking

Conversation records may be split into chunks (indicated by `chunk_index`). The export script preserves chunk relationships. On import, chunks are re-embedded individually.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| No conversations found | Palace only has project files | Check if conversations were ever saved (via hook or manual mine) |
| Import fails with dimension error | New palace uses different model | Ensure new palace is created AFTER configuring the new model |
| Chinese text garbled | Encoding issue | Scripts use UTF-8; check terminal encoding |
| WSL path not found | Path format mismatch | Use `/mnt/c/...` format in WSL |

## Environment Setup

### Windows (Python 3.12)

MemPalace runs on Python 3.12 with ChromaDB and sentence-transformers.

**1. Install MemPalace**

```bash
# 使用 Python 3.12 安装
py -3.12 -m pip install mempalace==3.3.5

# 安装 GPU 加速（可选）
py -3.12 -m pip install mempalace[gpu]   # CUDA
py -3.12 -m pip install mempalace[dml]   # DirectML (AMD/Intel)
```

**2. Install sentence-transformers（用于 BAAI 中文模型）**

```bash
py -3.12 -m pip install sentence-transformers
```

**3. Configure Embedding Model**

Edit `~/.mempalace/config.json`:

```json
{
  "embedding_model": "baai-zh"
}
```

Or set environment variable:

```powershell
$env:MEMPALACE_EMBEDDING_MODEL = "baai-zh"
```

**Available models:**

| Model | Key | Dimension | Language | Dependency |
|-------|-----|-----------|----------|------------|
| BAAI/bge-base-zh-v1.5 | `baai-zh` | 768 | Chinese | sentence-transformers |
| all-MiniLM-L6-v2 | `minilm` | 384 | English | onnxruntime (built-in) |

**4. Modify embedding.py（切换模型必需）**

The default `embedding.py` only supports ONNX MiniLM. To use BAAI model, replace `Python312\Lib\site-packages\mempalace\embedding.py` with a custom implementation.

**Key changes:**
- Add `_BAAIEmbeddingFunction` class using `SentenceTransformer('BAAI/bge-base-zh-v1.5')`
- Modify `get_embedding_function()` to accept `model` parameter
- Return `_BAAIEmbeddingFunction` when `model="baai-zh"`
- Fall back to `_build_onnx_ef_class()` when `model="minilm"`
- Cache models per-process to avoid repeated loading

**Complete modified embedding.py structure:**

```python
class _BAAIEmbeddingFunction:
    """ChromaDB-compatible embedding function using BAAI/bge-base-zh-v1.5.

    Critical: ChromaDB validates the EmbeddingFunction interface strictly.
    - __call__ must accept exactly (self, input) — no **kwargs
    - embed_query must return Embeddings (list of lists), not a single list
    - All methods must handle both str and list[str] input
    """
    _model = None
    _dimension = 768

    def __init__(self):
        if _BAAIEmbeddingFunction._model is None:
            from sentence_transformers import SentenceTransformer
            _BAAIEmbeddingFunction._model = SentenceTransformer(
                "BAAI/bge-base-zh-v1.5"
            )

    @staticmethod
    def name() -> str:
        return "baai_bge_base_zh_v1_5"

    def __call__(self, input) -> list[list[float]]:
        """Embed texts. ChromaDB calls this with both str and list input."""
        if isinstance(input, str):
            input = [input]
        embeddings = _BAAIEmbeddingFunction._model.encode(
            input, normalize_embeddings=True
        )
        return embeddings.tolist()

    def embed_query(self, input, **kwargs) -> list[list[float]]:
        """Embed query. Returns list of lists (ChromaDB Embeddings type).

        ChromaDB passes input as either str or list[str].
        Must return [[float, float, ...]] not [float, float, ...].
        """
        if isinstance(input, list):
            input = input[0] if input else ""
        embeddings = _BAAIEmbeddingFunction._model.encode(
            [input], normalize_embeddings=True
        )
        return embeddings.tolist()  # Returns [[768 floats]]

    def embed_documents(self, input: list[str], **kwargs) -> list[list[float]]:
        """Embed documents."""
        return self.__call__(input)

def get_embedding_function(device=None, model=None):
    model = (model or _get_model_from_config()).strip().lower()
    if model == "baai-zh":
        # Return BAAI embedding function
        ...
    elif model == "minilm":
        # Return ONNX MiniLM embedding function
        ...
```

**5. Backup and Upgrade Recovery**

**Before upgrade:**
```bash
# Backup current embedding.py
cp Python312\Lib\site-packages\mempalace\embedding.py \
   Python312\Lib\site-packages\mempalace\embedding.py.bak
```

**After upgrade (restore BAAI support):**
```bash
# Option 1: Restore from backup
cp Python312\Lib\site-packages\mempalace\embedding.py.bak \
   Python312\Lib\site-packages\mempalace\embedding.py

# Option 2: Re-apply modifications manually
# Edit embedding.py and add _BAAIEmbeddingFunction class
```

**Verification after upgrade:**
```bash
# Test 1: Check model name and embedding dimension
py -3.12 -c "from mempalace.embedding import get_embedding_function; \
    ef = get_embedding_function(model='baai-zh'); \
    print(f'Model: {ef.name()}, Dim: {len(ef.embed_query(\"test\")[0])}')"
# Expected: Model: baai_bge_base_zh_v1_5, Dim: 768

# Test 2: Test ChromaDB integration (critical)
py -3.12 -c "
from mempalace.palace import get_collection
from mempalace.embedding import get_embedding_function
ef = get_embedding_function(model='baai-zh')
col = get_collection(r'C:\Users\v-wangtengda\.mempalace\palace', create=True)
col.add(documents=['测试文档'], metadatas=[{'wing': 'test'}], ids=['test-1'])
results = col.query(query_texts=['测试'], n_results=1)
print('ChromaDB integration: OK')
"

# Test 3: Test CLI search
py -3.12 -m mempalace search "测试"
```

**6. Troubleshooting**

| Error | Cause | Solution |
|-------|-------|----------|
| `Expected EmbeddingFunction.__call__ to have signature: odict_keys(['self', 'input'])` | `__call__` has `**kwargs` | Remove `**kwargs` from `__call__` signature |
| `object of type 'float' has no len()` | `embed_query` returns single list instead of list of lists | Return `embeddings.tolist()` not `embeddings.tolist()[0]` |
| `Search error: _BAAIEmbeddingFunction.embed_query() got unexpected keyword argument 'input'` | `embed_query` doesn't accept `**kwargs` | Add `**kwargs` to `embed_query` signature |
| `No palace found` | Palace directory missing or ChromaDB collection not created | Run `py -3.12 -m mempalace init ~/.mempalace/palace --no-llm --yes` |
| `SQLite-layer corruption detected` | ChromaDB FTS5 index corrupted | Delete palace directory and re-initialize |

**Critical implementation notes:**

1. **`__call__` signature**: Must be `def __call__(self, input)` — no type hints with `**kwargs`
2. **`embed_query` return type**: Must return `list[list[float]]` (Embeddings), not `list[float]`
3. **`embed_query` parameters**: Must accept `**kwargs` because ChromaDB calls `embed_query(input=text)`
4. **Palace initialization**: After modifying embedding.py, delete old palace and re-init to avoid dimension mismatch

### WSL (Ubuntu 24.04)

```bash
# 安装 Python 3.12
sudo apt update && sudo apt install python3.12 python3.12-pip

# 安装 mempalace
python3.12 -m pip install mempalace==3.3.5 sentence-transformers

# 验证
python3.12 -m mempalace status
```

### Model Switching Safety

**Critical:** One palace can only use ONE embedding model. Mixing models creates "dirty data":

```
❌ WRONG: Same palace with different models
   Record A: 768-dim (BAAI)
   Record B: 1024-dim (Qwen)  ← dimension mismatch → search fails

✅ CORRECT: One model per palace
   Palace 1: All records 768-dim (BAAI)
   Palace 2: All records 384-dim (MiniLM)
```

**To switch models:**
1. Export conversations from old palace (this skill)
2. Delete or backup old palace
3. Configure new model
4. Create new palace
5. Re-import conversations

## Safety

- **Always backup** before migration: `cp -r palace palace-backup-$(date +%Y%m%d)`
- Export is **read-only** — it doesn't modify the source palace
- Import creates **new records** — it doesn't overwrite existing ones
- **Never mix models** in the same palace
