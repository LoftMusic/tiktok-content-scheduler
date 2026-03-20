---
name: typescript-expert
description: >
  TypeScript best practices, advanced types, and generics.
---

# TypeScript Expert

## Utility Types
```ts
Partial<T> // All props optional
Required<T> // All props required
Pick<T, K> // Subset of props
Omit<T, K> // Exclude props
Record<K, V> // Key-value map
ReturnType<F> // Infer function return
Parameters<F> // Infer function params
Awaited<T> // Unwrap Promise
```

## Advanced Patterns
```ts
// Discriminated unions
type Result<T> = { ok: true; data: T } | { ok: false; error: string };

// Template literal types
type EventName = `on${Capitalize<string>}`;

// Conditional types
type IsArray<T> = T extends any[] ? true : false;

// Mapped types with filtering
type Getters<T> = { [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] };

// const assertions
const routes = ['home', 'about', 'contact'] as const;
type Route = typeof routes[number]; // 'home' | 'about' | 'contact'
```

## Generic Patterns
```ts
// Constrained generics
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key]; }

// Generic React components
function List<T>({ items, renderItem }: { items: T[]; renderItem: (item: T) => ReactNode }) {
 return <>{items.map(renderItem)}</>;
}
```

## Tips
- Use `satisfies` for type checking without widening: `const cfg = { ... } satisfies Config`
- Prefer `unknown` over `any` — forces type narrowing
- Use `strict: true` in tsconfig — always
- Zod for runtime validation that infers static types
