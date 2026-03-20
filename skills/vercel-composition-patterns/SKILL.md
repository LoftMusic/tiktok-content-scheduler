---
name: vercel-composition-patterns
description: >
  Advanced React composition patterns.
---

# React Composition Patterns

## Compound Components
```tsx
function Select({ children }) {
 const [value, setValue] = useState(null);
 return <SelectContext.Provider value={{ value, setValue }}>{children}</SelectContext.Provider>;
}
Select.Option = function Option({ value, children }) {
 const ctx = useContext(SelectContext);
 return <button onClick={() => ctx.setValue(value)}>{children}</button>;
};
// Usage: <Select><Select.Option value="a">A</Select.Option></Select>
```

## Render Props
```tsx
<DataFetcher url="/api/users">
 {({ data, loading }) => loading ? <Spinner /> : <UserList users={data} />}
</DataFetcher>
```

## Polymorphic Components
```tsx
function Box<C extends ElementType = 'div'>({ as, ...props }: { as?: C } & ComponentPropsWithoutRef<C>) {
 const Component = as || 'div';
 return <Component {...props} />;
}
// <Box as="a" href="/home">Link styled as Box</Box>
```

## Slots Pattern
- Pass components via props: `<Card header={<Title />} footer={<Actions />} />`
- More explicit than `children` for multi-slot layouts

## Provider Composition
```tsx
function AppProviders({ children }) {
 return (
 <ThemeProvider><AuthProvider><QueryClientProvider client={qc}>
 {children}
 </QueryClientProvider></AuthProvider></ThemeProvider>
 );
}
```

## Tips
- Prefer composition over prop drilling
- Use `children` for single-slot, named props for multi-slot
- HOCs are legacy — prefer hooks + composition
