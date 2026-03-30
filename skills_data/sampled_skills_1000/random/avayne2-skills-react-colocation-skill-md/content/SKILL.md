---
name: react-colocation
description: Guide for organizing React and React Native projects using the Colocation pattern (Feature-based Architecture). Use this skill when creating new React/React Native components, structuring project folders, refactoring existing codebases to feature-based architecture, or when the user asks about component organization, folder structure, or mentions colocation, feature folders, or component folder patterns.
license: MIT
metadata:
  author: community
  version: "1.0"
  tags: react, react-native, architecture, colocation, folder-structure
---

# React Colocation Architecture

This skill guides the creation and organization of React and React Native projects using the **Colocation pattern** (also known as Feature-based Architecture or Component Folder Pattern).

## Core Principle

> **"Code that changes together should live together."**

Everything a component needs to function lives in its own folder: subcomponents, hooks, context, types, styles, tests, and utilities.

## When to Use This Pattern

- Projects with more than 10 components
- Teams with multiple developers
- Components that have their own state, hooks, or context
- When you want to easily move, delete, or share components
- Long-term maintainability is a priority

## Standard Component Structure

```
/ComponentName
  /components          # Subcomponents only used by this component
    SubComponent.tsx
  /hooks               # Custom hooks for this component
    useComponentLogic.ts
  /context             # Context providers for this component tree
    ComponentContext.tsx
  /utils               # Helper functions
    component.helpers.ts
  /types               # TypeScript types/interfaces
    component.types.ts
  ComponentName.tsx    # Main presentational component
  ComponentName.container.tsx  # Optional: Logic/state container
  ComponentName.styles.ts      # Styles (or .css/.module.css for web)
  ComponentName.test.tsx       # Tests
  index.ts             # Public exports
```

## File Naming Conventions

| File Type | Convention | Example |
|-----------|------------|---------|
| Component | PascalCase | `Button.tsx` |
| Hook | camelCase with `use` prefix | `useButtonState.ts` |
| Context | PascalCase with `Context` suffix | `ButtonContext.tsx` |
| Types | camelCase with `.types` suffix | `button.types.ts` |
| Styles | Component name with `.styles` suffix | `Button.styles.ts` |
| Tests | Component name with `.test` suffix | `Button.test.tsx` |
| Utilities | camelCase with `.helpers` suffix | `button.helpers.ts` |

## Index File Pattern

Always export the public API through `index.ts`:

```typescript
// /Button/index.ts
export { Button } from './Button';
export { ButtonProvider, useButtonContext } from './context/ButtonContext';
export type { ButtonProps, ButtonVariant } from './types/button.types';
```

This allows clean imports:
```typescript
import { Button, useButtonContext } from '@/components/Button';
```

## Container/Presentational Split (Optional)

For complex components, separate logic from UI:

```typescript
// Button.tsx (Presentational - Pure UI)
export const Button = ({ label, loading, onPress }: ButtonProps) => (
  <Pressable onPress={onPress} style={styles.button}>
    {loading ? <Spinner /> : <Text>{label}</Text>}
  </Pressable>
);

// Button.container.tsx (Container - Logic & State)
export const ButtonContainer = () => {
  const [loading, setLoading] = useState(false);
  const { theme } = useTheme();
  
  const handlePress = async () => {
    setLoading(true);
    await submitAction();
    setLoading(false);
  };

  return <Button label="Submit" loading={loading} onPress={handlePress} />;
};
```

## Component-Scoped Context

When a component needs shared state across its children:

```typescript
// /Button/context/ButtonContext.tsx
import { createContext, useContext, useState, ReactNode } from 'react';

interface ButtonContextType {
  isPressed: boolean;
  setIsPressed: (value: boolean) => void;
}

const ButtonContext = createContext<ButtonContextType | null>(null);

export const useButtonContext = () => {
  const context = useContext(ButtonContext);
  if (!context) {
    throw new Error('useButtonContext must be used within ButtonProvider');
  }
  return context;
};

export const ButtonProvider = ({ children }: { children: ReactNode }) => {
  const [isPressed, setIsPressed] = useState(false);
  
  return (
    <ButtonContext.Provider value={{ isPressed, setIsPressed }}>
      {children}
    </ButtonContext.Provider>
  );
};
```

## Component-Scoped Hooks

Extract reusable logic into hooks within the component folder:

```typescript
// /Button/hooks/useButtonAnimation.ts
import { useRef, useCallback } from 'react';
import { Animated } from 'react-native';

export const useButtonAnimation = () => {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const animatePress = useCallback(() => {
    Animated.sequence([
      Animated.timing(scaleAnim, { toValue: 0.95, duration: 100, useNativeDriver: true }),
      Animated.timing(scaleAnim, { toValue: 1, duration: 100, useNativeDriver: true }),
    ]).start();
  }, [scaleAnim]);

  return { scaleAnim, animatePress };
};
```

## Project-Level Structure

```
/src
  /components          # Shared/reusable components
    /Button
    /Modal
    /Card
  /features            # Feature modules (each is self-contained)
    /Authentication
      /components
      /hooks
      /context
      /api
      /screens
      index.ts
    /Dashboard
    /Settings
  /shared              # Truly global utilities
    /hooks             # App-wide hooks (useAuth, useTheme)
    /context           # Global providers (AuthProvider, ThemeProvider)
    /utils             # Generic helpers
    /types             # Shared type definitions
  /navigation          # Navigation configuration
  /api                 # API client setup
  App.tsx
```

## Decision Guide: Where Does Code Belong?

| Question | If Yes → | If No → |
|----------|----------|---------|
| Used by only one component? | Component folder | ↓ |
| Used by one feature only? | Feature folder | ↓ |
| Used across multiple features? | `/shared` folder | - |

## Anti-Patterns to Avoid

### ❌ Type-Based Structure (Don't Do This)
```
/src
  /components    # All components dumped here
  /hooks         # All hooks dumped here  
  /contexts      # All contexts dumped here
  /utils         # All utils dumped here
```

**Problem**: Files that change together are scattered. Deleting a feature requires hunting through multiple folders.

### ❌ Over-Nesting
```
/Button
  /components
    /ButtonIcon
      /components
        /IconWrapper
          /components    # Too deep!
```

**Rule**: Maximum 2 levels of `/components` nesting.

### ❌ Empty Folders
Don't create folders "just in case." Add them when needed.

### ❌ Circular Dependencies
Component A's hook imports from Component B, which imports from A.

**Solution**: Move shared code to `/shared` or a common parent.

## Migration Strategy

When refactoring from type-based to colocation:

1. **Start with one feature** - Pick a self-contained feature
2. **Create the folder structure** - Set up the feature folder
3. **Move files incrementally** - Move related files together
4. **Update imports** - Use search/replace or IDE refactoring
5. **Test thoroughly** - Ensure nothing breaks
6. **Repeat** - Move to the next feature

## Styling Approach by Platform

### React Native
```typescript
// Button.styles.ts
import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  button: {
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#007AFF',
  },
});
```

### React Web (CSS Modules)
```css
/* Button.module.css */
.button {
  padding: 12px;
  border-radius: 8px;
  background-color: #007AFF;
}
```

### React Web (Styled Components)
```typescript
// Button.styles.ts
import styled from 'styled-components';

export const StyledButton = styled.button`
  padding: 12px;
  border-radius: 8px;
  background-color: #007AFF;
`;
```

## Testing Colocation

Tests live next to what they test:

```
/Button
  Button.tsx
  Button.test.tsx        # Unit tests
  Button.stories.tsx     # Storybook stories (optional)
  __snapshots__/         # Jest snapshots (auto-generated)
```

## TypeScript Path Aliases

Configure path aliases for cleaner imports:

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@features/*": ["src/features/*"],
      "@shared/*": ["src/shared/*"]
    }
  }
}
```

## Quick Reference Checklist

When creating a new component:

- [ ] Create folder with PascalCase name
- [ ] Add main component file (`ComponentName.tsx`)
- [ ] Add `index.ts` with exports
- [ ] Add types file if using TypeScript (`component.types.ts`)
- [ ] Add styles file (`ComponentName.styles.ts`)
- [ ] Add test file (`ComponentName.test.tsx`)
- [ ] Create `/hooks` folder only if component has custom hooks
- [ ] Create `/context` folder only if component needs shared state
- [ ] Create `/components` folder only if there are subcomponents

## Skill Resources

- [Advanced Patterns](references/patterns.md) - Compound components, feature modules, data fetching patterns
- [Migration Guide](references/migration.md) - Step-by-step migration from type-based to colocation
- [Example Component](assets/example-component.tsx) - Complete UserProfile demonstrating all patterns
- [Component Generator](scripts/generate-component.js) - Script to scaffold new components

## References

- [Bulletproof React](https://github.com/alan2207/bulletproof-react) - Production-ready architecture
- [React Documentation on File Structure](https://react.dev/learn/thinking-in-react)
- [Kent C. Dodds on Colocation](https://kentcdodds.com/blog/colocation)
