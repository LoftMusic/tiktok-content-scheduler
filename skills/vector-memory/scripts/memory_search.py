#!/usr/bin/env python3
"""Search memories by semantic similarity."""
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

def search(query, limit=5, category=None, min_score=0.0):
    embedding = get_embedding(query)
    vec_str = "[" + ",".join(str(v) for v in embedding) + "]"
    sql = "SELECT id, text, label, category, source, created_at, 1-(embedding<=>%s::vector) as similarity FROM memories"
    params = [vec_str]
    if category:
        sql += " WHERE category=%s"
        params.append(category)
    sql += " ORDER BY embedding<=>%s::vector LIMIT %s"
    params.extend([vec_str, limit])
    conn = psycopg2.connect(DB)
    cur = conn.cursor()
    cur.execute(sql, params)
    results = [{"id": r[0], "text": r[1], "label": r[2], "category": r[3], "source": r[4], "created_at": r[5].isoformat(), "similarity": round(float(r[6]),4)} for r in cur.fetchall() if float(r[6]) >= min_score]
    cur.close(); conn.close()
    print(json.dumps({"query": query, "count": len(results), "results": results}, indent=2))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--limit", "-n", type=int, default=5)
    p.add_argument("--category", "-c", default=None)
    p.add_argument("--min-score", type=float, default=0.3)
    args = p.parse_args()
    search(args.query, args.limit, args.category, args.min_score)
