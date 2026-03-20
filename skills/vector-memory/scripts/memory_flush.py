#!/usr/bin/env python3
"""Flush daily memory files into vector database."""
import argparse, glob, hashlib, json, os, re, sys, urllib.request
import psycopg2

DB = "dbname=openclaw_memory"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
EMBED_MODEL = "gemini-embedding-001"
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
FLUSH_TRACKER = os.path.join(MEMORY_DIR, "vector-flush-tracker.json")

def get_embedding(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBED_MODEL}:embedContent?key={GEMINI_KEY}"
    payload = json.dumps({"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": text}]}, "outputDimensionality": 768}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["embedding"]["values"]

def load_tracker():
    if os.path.exists(FLUSH_TRACKER):
        with open(FLUSH_TRACKER) as f:
            return json.load(f)
    return {"flushed_files": {}}

def save_tracker(t):
    with open(FLUSH_TRACKER, "w") as f:
        json.dump(t, f, indent=2)

def chunk_markdown(text, source_file):
    chunks, current_section, current_text = [], "", []
    for line in text.split("\n"):
        if re.match(r'^#{1,3}\s', line):
            if current_text:
                content = "\n".join(current_text).strip()
                if len(content) > 20:
                    chunks.append({"text": content, "label": current_section.strip("# ").strip(), "source_file": source_file})
            current_section, current_text = line, [line]
        else:
            current_text.append(line)
    if current_text:
        content = "\n".join(current_text).strip()
        if len(content) > 20:
            chunks.append({"text": content, "label": current_section.strip("# ").strip(), "source_file": source_file})
    return chunks

def file_hash(fp):
    with open(fp) as f:
        return hashlib.md5(f.read().encode()).hexdigest()

def flush(dry_run=False, force=False):
    tracker = load_tracker()
    conn = psycopg2.connect(DB) if not dry_run else None
    files = sorted(glob.glob(os.path.join(MEMORY_DIR, "*.md")))
    memory_md = os.path.join(WORKSPACE, "MEMORY.md")
    if os.path.exists(memory_md):
        files.append(memory_md)
    total_stored = 0
    for filepath in files:
        fname = os.path.basename(filepath)
        fhash = file_hash(filepath)
        if not force and fname in tracker["flushed_files"] and tracker["flushed_files"][fname] == fhash:
            continue
        with open(filepath) as f:
            content = f.read()
        chunks = chunk_markdown(content, fname)
        if dry_run:
            print(f"[DRY RUN] {fname}: {len(chunks)} chunks")
            continue
        cur = conn.cursor()
        cur.execute("DELETE FROM memories WHERE metadata->>'source_file' = %s", (fname,))
        for chunk in chunks:
            embedding = get_embedding(chunk["text"])
            vec_str = "[" + ",".join(str(v) for v in embedding) + "]"
            cur.execute("INSERT INTO memories (text, label, category, source, embedding, metadata) VALUES (%s,%s,%s,%s,%s::vector,%s)", (chunk["text"], chunk["label"], "daily-note", "flush", vec_str, json.dumps({"source_file": fname})))
            total_stored += 1
        conn.commit(); cur.close()
        tracker["flushed_files"][fname] = fhash
        print(f"[FLUSHED] {fname}: {len(chunks)} chunks stored")
    if conn:
        conn.close()
    save_tracker(tracker)
    print(json.dumps({"total_stored": total_stored, "files_processed": len(files)}))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    flush(args.dry_run, args.force)
