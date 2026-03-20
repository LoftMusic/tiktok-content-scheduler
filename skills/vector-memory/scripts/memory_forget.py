#!/usr/bin/env python3
"""Delete memories by id, category, or age."""
import argparse, json
import psycopg2
from datetime import datetime, timedelta

DB = "dbname=openclaw_memory"

def forget(id=None, category=None, older_than_days=None):
    conn = psycopg2.connect(DB)
    cur = conn.cursor()
    if id:
        cur.execute("DELETE FROM memories WHERE id=%s RETURNING id,text", (id,))
    elif category:
        cur.execute("DELETE FROM memories WHERE category=%s RETURNING id,text", (category,))
    elif older_than_days:
        cutoff = datetime.now() - timedelta(days=older_than_days)
        cur.execute("DELETE FROM memories WHERE created_at < %s RETURNING id,text", (cutoff,))
    else:
        print("Error: must specify --id, --category, or --older-than")
        return
    deleted = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    print(json.dumps({"deleted": len(deleted), "ids": [r[0] for r in deleted]}))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--id", type=int, default=None)
    p.add_argument("--category", default=None)
    p.add_argument("--older-than", type=int, default=None)
    args = p.parse_args()
    forget(id=args.id, category=args.category, older_than_days=args.older_than)
