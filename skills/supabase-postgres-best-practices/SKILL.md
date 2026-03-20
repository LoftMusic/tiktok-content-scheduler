---
name: supabase-postgres-best-practices
description: >
  Supabase/PostgreSQL patterns — RLS, migrations, edge functions.
---

# Supabase + PostgreSQL

## Row Level Security (RLS)
```sql
-- Enable RLS on every table
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Users can read all posts
CREATE POLICY "read_posts" ON posts FOR SELECT USING (true);

-- Users can only edit their own
CREATE POLICY "edit_own" ON posts FOR UPDATE USING (auth.uid() = user_id);

-- Service role bypasses RLS — use for server-side admin operations
```

## Migrations
```bash
supabase migration new create_posts # creates timestamped SQL file
supabase db push # apply to remote
supabase db reset # reset local to migrations
```
- Keep migrations small and atomic
- Never edit applied migrations — create new ones

## Edge Functions
```ts
// supabase/functions/hello/index.ts
Deno.serve(async (req) => {
 const { name } = await req.json();
 return new Response(JSON.stringify({ message: `Hello ${name}` }), {
 headers: { 'Content-Type': 'application/json' },
 });
});
```

## Client Patterns
```ts
// Typed client
const { data, error } = await supabase.from('posts').select('*, author:users(name)').eq('published', true).order('created_at', { ascending: false }).limit(10);
```

## Tips
- Generate types: `supabase gen types typescript --project-id <id> > types/supabase.ts`
- Use database functions for complex logic (keeps it close to data)
- Realtime: `supabase.channel('posts').on('postgres_changes', { event: '*', schema: 'public', table: 'posts' }, handler).subscribe()`
- Storage: use signed URLs for private files, public buckets for assets
