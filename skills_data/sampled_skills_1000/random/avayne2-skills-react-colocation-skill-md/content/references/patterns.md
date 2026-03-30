# Advanced Colocation Patterns

This reference covers advanced patterns and real-world scenarios for the Colocation architecture.

## Compound Components Pattern

When building components with multiple related parts that share state:

```typescript
// /Select/Select.tsx
import { createContext, useContext, useState, ReactNode } from 'react';

interface SelectContextType {
  value: string | null;
  onChange: (value: string) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const SelectContext = createContext<SelectContextType | null>(null);

const useSelectContext = () => {
  const context = useContext(SelectContext);
  if (!context) throw new Error('Select components must be used within Select');
  return context;
};

// Main component
export const Select = ({ children, value, onChange }: SelectProps) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <SelectContext.Provider value={{ value, onChange, isOpen, setIsOpen }}>
      <div className="select">{children}</div>
    </SelectContext.Provider>
  );
};

// Subcomponents attached to main component
Select.Trigger = ({ children }: { children: ReactNode }) => {
  const { isOpen, setIsOpen, value } = useSelectContext();
  return (
    <button onClick={() => setIsOpen(!isOpen)}>
      {value || children}
    </button>
  );
};

Select.Options = ({ children }: { children: ReactNode }) => {
  const { isOpen } = useSelectContext();
  if (!isOpen) return null;
  return <ul className="options">{children}</ul>;
};

Select.Option = ({ value, children }: { value: string; children: ReactNode }) => {
  const { onChange, setIsOpen } = useSelectContext();
  return (
    <li onClick={() => { onChange(value); setIsOpen(false); }}>
      {children}
    </li>
  );
};
```

**Usage:**
```tsx
<Select value={selected} onChange={setSelected}>
  <Select.Trigger>Choose an option</Select.Trigger>
  <Select.Options>
    <Select.Option value="a">Option A</Select.Option>
    <Select.Option value="b">Option B</Select.Option>
  </Select.Options>
</Select>
```

**Folder Structure:**
```
/Select
  /components
    SelectTrigger.tsx
    SelectOptions.tsx
    SelectOption.tsx
  /context
    SelectContext.tsx
  /hooks
    useSelectKeyboard.ts
  Select.tsx              # Assembles compound component
  index.ts
```

## Feature Module Pattern

For self-contained features with screens, API calls, and state:

```
/features
  /Authentication
    /api
      auth.api.ts         # API calls
      auth.queries.ts     # React Query hooks
    /components
      LoginForm.tsx
      RegisterForm.tsx
      PasswordReset.tsx
    /hooks
      useAuth.ts
      useSession.ts
    /context
      AuthContext.tsx
    /screens
      LoginScreen.tsx
      RegisterScreen.tsx
    /types
      auth.types.ts
    /utils
      validation.ts
      tokens.ts
    index.ts              # Public API
```

**Feature Index Export:**
```typescript
// /features/Authentication/index.ts
export { AuthProvider, useAuth } from './context/AuthContext';
export { LoginScreen } from './screens/LoginScreen';
export { RegisterScreen } from './screens/RegisterScreen';
export type { User, AuthState } from './types/auth.types';
```

## Shared Component Variants

When a component has multiple variants, organize them together:

```
/Button
  /variants
    PrimaryButton.tsx
    SecondaryButton.tsx
    GhostButton.tsx
    IconButton.tsx
  Button.tsx              # Base component or variant selector
  Button.styles.ts
  index.ts
```

**Base Component with Variants:**
```typescript
// /Button/Button.tsx
import { PrimaryButton } from './variants/PrimaryButton';
import { SecondaryButton } from './variants/SecondaryButton';
import { GhostButton } from './variants/GhostButton';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';

interface ButtonProps {
  variant?: ButtonVariant;
  // ... other props
}

const variantMap = {
  primary: PrimaryButton,
  secondary: SecondaryButton,
  ghost: GhostButton,
};

export const Button = ({ variant = 'primary', ...props }: ButtonProps) => {
  const Component = variantMap[variant];
  return <Component {...props} />;
};
```

## Form Component Pattern

Complex forms benefit from colocation:

```
/ContactForm
  /components
    FormField.tsx
    SubmitButton.tsx
    ErrorMessage.tsx
  /hooks
    useContactForm.ts     # Form state & validation
    useFormSubmit.ts      # Submission logic
  /context
    FormContext.tsx       # Share form state with fields
  /utils
    validation.ts
    formatters.ts
  /types
    form.types.ts
  ContactForm.tsx
  ContactForm.test.tsx
  index.ts
```

## Data Fetching Colocation

Keep data fetching close to where it's used:

```typescript
// /UserProfile/hooks/useUserProfile.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchUser, updateUser } from '../api/user.api';

export const useUserProfile = (userId: string) => {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  const mutation = useMutation({
    mutationFn: updateUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', userId] });
    },
  });

  return {
    user: query.data,
    isLoading: query.isLoading,
    error: query.error,
    updateUser: mutation.mutate,
    isUpdating: mutation.isPending,
  };
};
```

## Modal/Dialog Pattern

Modals often need their own state and can be colocated:

```
/ConfirmDialog
  /hooks
    useConfirmDialog.ts   # Open/close state, callbacks
  ConfirmDialog.tsx
  ConfirmDialog.styles.ts
  index.ts
```

**Hook for External Control:**
```typescript
// /ConfirmDialog/hooks/useConfirmDialog.ts
import { useState, useCallback } from 'react';

interface UseConfirmDialogOptions {
  onConfirm?: () => void | Promise<void>;
  onCancel?: () => void;
}

export const useConfirmDialog = (options: UseConfirmDialogOptions = {}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);

  const confirm = useCallback(async () => {
    if (options.onConfirm) {
      setIsLoading(true);
      await options.onConfirm();
      setIsLoading(false);
    }
    close();
  }, [options.onConfirm, close]);

  const cancel = useCallback(() => {
    options.onCancel?.();
    close();
  }, [options.onCancel, close]);

  return { isOpen, isLoading, open, close, confirm, cancel };
};
```

## Lazy Loading with Colocation

For code-splitting, export lazy versions:

```typescript
// /HeavyComponent/index.ts
import { lazy } from 'react';

// Eager export for type checking
export type { HeavyComponentProps } from './HeavyComponent';

// Lazy export for code splitting
export const HeavyComponent = lazy(() => import('./HeavyComponent'));

// Named export for non-lazy usage
export { HeavyComponent as HeavyComponentEager } from './HeavyComponent';
```

## Shared State Between Sibling Components

When siblings need shared state, lift the context to their common parent:

```
/ProductPage
  /components
    ProductGallery.tsx    # Needs selectedImage
    ProductThumbnails.tsx # Sets selectedImage
    ProductInfo.tsx
  /context
    ProductPageContext.tsx  # Shared state for all children
  ProductPage.tsx           # Wraps with provider
  index.ts
```

## Testing Patterns

### Unit Tests (colocated)
```typescript
// /Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders label', () => {
    render(<Button label="Click me" />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when pressed', () => {
    const handleClick = jest.fn();
    render(<Button label="Click" onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Integration Tests (feature level)
```
/features
  /Authentication
    __tests__
      auth.integration.test.tsx
```

## Real-World Example: E-commerce Product Card

```
/ProductCard
  /components
    ProductImage.tsx
    ProductBadge.tsx
    PriceDisplay.tsx
    AddToCartButton.tsx
    WishlistButton.tsx
  /hooks
    useProductCard.ts       # Hover state, quick view
    useAddToCart.ts         # Cart mutation
    useWishlist.ts          # Wishlist toggle
  /context
    ProductCardContext.tsx  # Share product data with children
  /types
    product-card.types.ts
  /utils
    price-formatter.ts
  ProductCard.tsx
  ProductCard.styles.ts
  ProductCard.test.tsx
  ProductCard.stories.tsx
  index.ts
```
