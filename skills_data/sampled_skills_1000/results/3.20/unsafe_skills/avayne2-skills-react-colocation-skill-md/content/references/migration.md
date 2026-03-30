# Migration Guide: Type-Based to Colocation

This guide helps teams migrate from a traditional type-based folder structure to the Colocation pattern.

## Before: Type-Based Structure

```
/src
  /components
    Button.tsx
    Modal.tsx
    UserCard.tsx
    LoginForm.tsx
  /hooks
    useButton.ts
    useModal.ts
    useAuth.ts
    useUser.ts
  /contexts
    ButtonContext.tsx
    ModalContext.tsx
    AuthContext.tsx
  /utils
    buttonHelpers.ts
    formatters.ts
    validation.ts
  /types
    button.types.ts
    modal.types.ts
    user.types.ts
  /styles
    Button.css
    Modal.css
```

## After: Colocation Structure

```
/src
  /components
    /Button
      Button.tsx
      Button.module.css
      index.ts
    /Modal
      /hooks
        useModal.ts
      /context
        ModalContext.tsx
      Modal.tsx
      Modal.module.css
      index.ts
  /features
    /Authentication
      /components
        LoginForm.tsx
      /hooks
        useAuth.ts
      /context
        AuthContext.tsx
      index.ts
    /Users
      /components
        UserCard.tsx
      /hooks
        useUser.ts
      /types
        user.types.ts
      index.ts
  /shared
    /utils
      formatters.ts
      validation.ts
```

## Migration Steps

### Phase 1: Preparation

1. **Audit your codebase**
   - List all components and their dependencies
   - Identify which hooks/contexts are component-specific vs. shared
   - Map out feature boundaries

2. **Set up path aliases**
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

3. **Create new folder structure** (keep old files in place)
   ```bash
   mkdir -p src/components
   mkdir -p src/features
   mkdir -p src/shared/{hooks,utils,types,context}
   ```

### Phase 2: Migrate Shared Utilities First

Move truly global code to `/shared`:

```bash
# Move global hooks
mv src/hooks/useLocalStorage.ts src/shared/hooks/
mv src/hooks/useDebounce.ts src/shared/hooks/

# Move global utils
mv src/utils/formatters.ts src/shared/utils/
mv src/utils/api-client.ts src/shared/utils/

# Move global types
mv src/types/common.types.ts src/shared/types/
```

### Phase 3: Migrate Components One-by-One

For each component:

1. **Create the component folder**
   ```bash
   mkdir -p src/components/Button/{hooks,context,types}
   ```

2. **Move the main component**
   ```bash
   mv src/components/Button.tsx src/components/Button/Button.tsx
   ```

3. **Move related files**
   ```bash
   mv src/hooks/useButton.ts src/components/Button/hooks/
   mv src/contexts/ButtonContext.tsx src/components/Button/context/
   mv src/types/button.types.ts src/components/Button/types/
   mv src/styles/Button.css src/components/Button/Button.module.css
   ```

4. **Create index.ts**
   ```typescript
   // src/components/Button/index.ts
   export { Button } from './Button';
   export { useButton } from './hooks/useButton';
   export { ButtonProvider, useButtonContext } from './context/ButtonContext';
   export type { ButtonProps } from './types/button.types';
   ```

5. **Update imports throughout codebase**
   ```typescript
   // Before
   import { Button } from '@/components/Button';
   import { useButton } from '@/hooks/useButton';
   import { ButtonContext } from '@/contexts/ButtonContext';
   
   // After
   import { Button, useButton, ButtonContext } from '@/components/Button';
   ```

### Phase 4: Migrate Features

For feature modules:

1. **Identify feature boundaries**
   - What screens belong to this feature?
   - What components are feature-specific?
   - What API calls does it make?

2. **Create feature structure**
   ```bash
   mkdir -p src/features/Authentication/{components,hooks,context,api,screens,types}
   ```

3. **Move feature-specific code**
   ```bash
   mv src/components/LoginForm.tsx src/features/Authentication/components/
   mv src/hooks/useAuth.ts src/features/Authentication/hooks/
   mv src/contexts/AuthContext.tsx src/features/Authentication/context/
   mv src/api/auth.ts src/features/Authentication/api/
   mv src/screens/LoginScreen.tsx src/features/Authentication/screens/
   ```

4. **Create feature index**
   ```typescript
   // src/features/Authentication/index.ts
   export { AuthProvider, useAuth } from './context/AuthContext';
   export { LoginScreen } from './screens/LoginScreen';
   export { RegisterScreen } from './screens/RegisterScreen';
   export type { User, AuthState } from './types/auth.types';
   ```

### Phase 5: Clean Up

1. **Remove empty old folders**
   ```bash
   rmdir src/hooks  # if empty
   rmdir src/contexts  # if empty
   ```

2. **Update all imports**
   Use your IDE's "Find and Replace" or a tool like `jscodeshift`:
   ```bash
   # Example: Update Button imports
   find . -name "*.tsx" -exec sed -i 's|from "@/components/Button"|from "@components/Button"|g' {} +
   ```

3. **Run tests**
   ```bash
   npm test
   ```

4. **Update documentation**
   - Update README with new structure
   - Update contribution guidelines

## Automated Migration Script

```bash
#!/bin/bash
# migrate-component.sh

COMPONENT=$1

if [ -z "$COMPONENT" ]; then
  echo "Usage: ./migrate-component.sh ComponentName"
  exit 1
fi

# Create new structure
mkdir -p "src/components/$COMPONENT"/{hooks,context,types}

# Move files (adjust paths as needed)
[ -f "src/components/$COMPONENT.tsx" ] && mv "src/components/$COMPONENT.tsx" "src/components/$COMPONENT/$COMPONENT.tsx"
[ -f "src/hooks/use$COMPONENT.ts" ] && mv "src/hooks/use$COMPONENT.ts" "src/components/$COMPONENT/hooks/"
[ -f "src/contexts/${COMPONENT}Context.tsx" ] && mv "src/contexts/${COMPONENT}Context.tsx" "src/components/$COMPONENT/context/"
[ -f "src/styles/$COMPONENT.css" ] && mv "src/styles/$COMPONENT.css" "src/components/$COMPONENT/$COMPONENT.module.css"

# Create index.ts
cat > "src/components/$COMPONENT/index.ts" << EOF
export { $COMPONENT } from './$COMPONENT';
EOF

echo "✅ Migrated $COMPONENT"
```

## Common Issues & Solutions

### Issue: Circular Dependencies

**Symptom**: Import errors after migration

**Solution**: 
- Move shared code to `/shared`
- Use dependency injection
- Create a common parent module

### Issue: Test Imports Breaking

**Symptom**: Tests can't find modules

**Solution**: Update Jest config:
```javascript
// jest.config.js
module.exports = {
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@features/(.*)$': '<rootDir>/src/features/$1',
  },
};
```

### Issue: Large Bundle Size After Migration

**Symptom**: Bundle size increased

**Solution**: Check your barrel exports aren't causing tree-shaking issues:
```typescript
// ❌ Bad - exports everything
export * from './Button';
export * from './Modal';

// ✅ Good - explicit exports
export { Button } from './Button';
export { Modal } from './Modal';
```

### Issue: IDE Autocomplete Not Working

**Symptom**: VS Code doesn't suggest new paths

**Solution**: 
1. Restart TypeScript server (Cmd/Ctrl + Shift + P → "Restart TS Server")
2. Verify `tsconfig.json` paths are correct
3. Check `jsconfig.json` if not using TypeScript

## Rollback Plan

If something goes wrong:

1. **Git to the rescue**
   ```bash
   git stash  # Save current changes
   git checkout main  # Return to stable state
   ```

2. **Gradual rollback**
   - Keep both structures temporarily
   - Use path aliases to point to old structure
   - Migrate back one component at a time

## Success Metrics

Track these to measure migration success:

- [ ] All tests passing
- [ ] No circular dependency warnings
- [ ] Bundle size maintained or reduced
- [ ] Developer onboarding time decreased
- [ ] Time to find related code decreased
- [ ] PR review complexity reduced
