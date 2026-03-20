---
name: vercel-react-best-practices
description: >
  React/Next.js best practices for Vercel deployment.
---

# React/Next.js on Vercel

## App Router (Next.js 14+)
- Default to Server Components — add `"use client"` only when needed (state, effects, browser APIs)
- Use `loading.tsx` for Suspense boundaries, `error.tsx` for error boundaries
- Colocate files: `page.tsx`, `layout.tsx`, `loading.tsx` in route folders

## Data Fetching
```tsx
// Server Component — fetch directly (no useEffect!)
async function Page() {
 const data = await fetch('https://api.example.com/items', { next: { revalidate: 60 } });
 return <ItemList items={await data.json()} />;
}
```
- `cache: 'force-cache'` (default) for static, `revalidate: N` for ISR, `cache: 'no-store'` for dynamic

## Server Actions
```tsx
"use server"
async function createItem(formData: FormData) {
 await db.insert({ name: formData.get('name') });
 revalidatePath('/items');
}
```

## Performance
- Use `next/image` (auto WebP, lazy loading, srcset)
- Use `next/font` for zero-layout-shift fonts
- Dynamic imports: `const Chart = dynamic(() => import('./Chart'), { ssr: false })`
- Middleware for auth/redirects at the edge

## Vercel-Specific
- Edge Runtime for low-latency: `export const runtime = 'edge'`
- Use Vercel KV/Postgres/Blob for serverless-compatible storage
- Preview deployments on every PR — use them for QA
