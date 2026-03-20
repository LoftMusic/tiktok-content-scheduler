---
name: vercel-react-native-skills
description: >
  React Native mobile development patterns.
---

# React Native Skills

## Project Setup
```bash
npx create-expo-app@latest myapp # Expo (recommended)
npx react-native init myapp # bare workflow
```

## Core Patterns
- **Navigation:** React Navigation with typed routes
 ```tsx
 <Stack.Navigator>
 <Stack.Screen name="Home" component={HomeScreen} />
 <Stack.Screen name="Detail" component={DetailScreen} />
 </Stack.Navigator>
 ```
- **Styling:** StyleSheet.create for performance, or NativeWind (Tailwind for RN)
- **Lists:** Always use `FlatList`/`SectionList` — never `ScrollView` + `map()`
- **State:** Zustand or Jotai for global state; React Query for server state

## Performance
- `useMemo`/`useCallback` for expensive renders
- `React.memo()` for pure list items
- Use Hermes engine (default in Expo SDK 49+)
- Avoid bridge overhead: use Expo modules or Turbo Modules (New Architecture)

## Platform-Specific
```tsx
import { Platform } from 'react-native';
const styles = { padding: Platform.select({ ios: 20, android: 16 }) };
// Or: MyComponent.ios.tsx / MyComponent.android.tsx
```

## Tips
- Test on real devices early (simulators lie about performance)
- Use `expo-haptics`, `expo-linear-gradient` for native feel
- EAS Build for cloud builds, EAS Update for OTA updates
