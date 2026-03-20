#!/usr/bin/env python3
"""Store a memory with vector embedding."""
import argparse, json, os, urllib.request
import psycopg2

DB = "dbname=openclaw_memory"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
EMBED_MODEL = "gemini-embedding-001"

def get_embedding(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBED_MODEL}:embedContent?key={GEMINI_KEY}"
    payload = json.dumps({"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": text}]}, "outputDimensionality": 768}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["embedding"]["values"]

def store(text, label=None, category=None, source="conversation", metadata=None):
    embedding = get_embedding(text)
    vec_str = "[" + ",".join(str(v) for v in embedding) + "]"
    conn = psycopg2.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO memories (text,label,category,source,embedding,metadata) VALUES (%s,%s,%s,%s,%s::vector,%s) RETURNING id,created_at", (text, label, category, source, vec_str, json.dumps(metadata or {})))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    print(json.dumps({"id": row[0], "created_at": row[1].isoformat(), "label": label, "category": category, "text": text[:100]}))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("text")
    p.add_argument("--label", "-l", default=None)
    p.add_argument("--category", "-c", default=None)
    p.add_argument("--source", "-s", default="conversation")
    p.add_argument("--meta", "-m", default=None)
    args = p.parse_args()
    store(args.text, args.label, args.category, args.source, json.loads(args.meta) if args.meta else None)
