---
name: mobile-android-design
description: >
  Android design patterns and Material Design guidelines.
---

# Android Design (Material Design 3)

## Material You
- Dynamic Color: Extract palette from user's wallpaper
- Tonal color system: Primary, secondary, tertiary + surface tones
- Shape system: Small (4dp), Medium (12dp), Large (16dp) rounding

## Navigation
- **Bottom Navigation:** 3-5 top-level destinations
- **Navigation Drawer:** 5+ destinations or secondary nav
- **Top App Bar:** Title + actions + navigation icon
- **Navigation Rail:** Tablet/foldable side navigation

## Compose Patterns
```kotlin
@Composable
fun ItemList(items: List<Item>, onItemClick: (Item) -> Unit) {
 LazyColumn {
 items(items, key = { it.id }) { item ->
 ListItem(
 headlineContent = { Text(item.title) },
 modifier = Modifier.clickable { onItemClick(item) }
 )
 }
 }
}
```

## Layout
- Use `Scaffold` for standard screen structure (top bar, FAB, bottom bar)
- Touch targets: Minimum 48×48dp
- Content padding: 16dp horizontal
- Use `WindowSizeClass` for adaptive layouts (compact/medium/expanded)

## Architecture
- MVVM with `ViewModel` + `StateFlow`
- Hilt for dependency injection
- Room for local database
- Navigation Compose for type-safe routing

## Tips
- Support edge-to-edge (draw behind system bars)
- Predictive back gesture (Android 14+)
- Use `rememberSaveable` to survive config changes
- Test on foldables: use `WindowLayoutInfo` for fold-aware UI
