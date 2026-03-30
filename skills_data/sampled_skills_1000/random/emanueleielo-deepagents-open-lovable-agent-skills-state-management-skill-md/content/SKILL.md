---
name: state-management
description: State management patterns - Zustand, Jotai, Context
---

# State Management

## When to Use What

| State Type | Solution | Example |
|------------|----------|---------|
| Server state | TanStack Query | API data, user profile |
| Form state | React Hook Form | Form inputs, validation |
| Local UI | useState | Modal open, input value |
| Shared UI | Zustand / Jotai | Theme, sidebar open, filters |
| Complex shared | Zustand | Shopping cart, multi-step wizard |

**Rule:** Server data belongs in TanStack Query, NOT in global state.

## 1. Zustand - Simple Global State

```tsx
import { create } from "zustand";
import { persist } from "zustand/middleware";

// Basic store
interface CounterStore {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

const useCounterStore = create<CounterStore>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}));

// Usage
function Counter() {
  const { count, increment, decrement } = useCounterStore();

  return (
    <div>
      <span>{count}</span>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  );
}

// Select specific values (prevents re-renders)
function CountDisplay() {
  const count = useCounterStore((state) => state.count);
  return <span>{count}</span>;
}
```

## 2. Zustand - Complex Store with Slices

```tsx
import { create, StateCreator } from "zustand";
import { devtools, persist } from "zustand/middleware";

// User slice
interface UserSlice {
  user: User | null;
  setUser: (user: User | null) => void;
}

const createUserSlice: StateCreator<UserSlice> = (set) => ({
  user: null,
  setUser: (user) => set({ user }),
});

// Cart slice
interface CartSlice {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  total: () => number;
}

const createCartSlice: StateCreator<CartSlice & UserSlice, [], [], CartSlice> = (set, get) => ({
  items: [],
  addItem: (item) => set((state) => ({
    items: [...state.items, item]
  })),
  removeItem: (id) => set((state) => ({
    items: state.items.filter((i) => i.id !== id)
  })),
  clearCart: () => set({ items: [] }),
  total: () => get().items.reduce((sum, item) => sum + item.price, 0),
});

// Combined store
type Store = UserSlice & CartSlice;

const useStore = create<Store>()(
  devtools(
    persist(
      (...a) => ({
        ...createUserSlice(...a),
        ...createCartSlice(...a),
      }),
      { name: "app-store" }
    )
  )
);
```

## 3. Jotai - Atomic State

```tsx
import { atom, useAtom, useAtomValue, useSetAtom } from "jotai";
import { atomWithStorage } from "jotai/utils";

// Primitive atom
const countAtom = atom(0);

// Derived atom (read-only)
const doubleAtom = atom((get) => get(countAtom) * 2);

// Writable derived atom
const countWithMaxAtom = atom(
  (get) => get(countAtom),
  (get, set, newValue: number) => {
    set(countAtom, Math.min(newValue, 100));
  }
);

// Async atom
const userAtom = atom(async () => {
  const res = await fetch("/api/user");
  return res.json();
});

// Persisted atom
const themeAtom = atomWithStorage<"light" | "dark">("theme", "light");

// Usage
function Counter() {
  const [count, setCount] = useAtom(countAtom);
  const double = useAtomValue(doubleAtom);

  return (
    <div>
      <span>{count} (double: {double})</span>
      <button onClick={() => setCount((c) => c + 1)}>+</button>
    </div>
  );
}

// Only set (no re-render on value change)
function IncrementButton() {
  const setCount = useSetAtom(countAtom);
  return <button onClick={() => setCount((c) => c + 1)}>+</button>;
}
```

## 4. Jotai - Atom Families

```tsx
import { atom } from "jotai";
import { atomFamily } from "jotai/utils";

// Atom family for per-item state
const itemQuantityAtomFamily = atomFamily((itemId: string) =>
  atom(1)
);

// Usage
function ItemQuantity({ itemId }: { itemId: string }) {
  const [quantity, setQuantity] = useAtom(itemQuantityAtomFamily(itemId));

  return (
    <div>
      <button onClick={() => setQuantity((q) => Math.max(1, q - 1))}>-</button>
      <span>{quantity}</span>
      <button onClick={() => setQuantity((q) => q + 1)}>+</button>
    </div>
  );
}
```

## 5. Context API - When Appropriate

Use Context for:
- Dependency injection (services, config)
- Compound components (sharing state between parent/children)
- Theme/i18n that rarely changes

```tsx
import { createContext, useContext, useState, ReactNode } from "react";

interface ThemeContextValue {
  theme: "light" | "dark";
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("useTheme must be used within ThemeProvider");
  return context;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  const toggle = () => setTheme((t) => (t === "light" ? "dark" : "light"));

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

## 6. Combining with TanStack Query

```tsx
// Store for UI state only
const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  // Filters affect query key
  filters: { status: "all", search: "" },
  setFilters: (filters) => set({ filters }),
}));

// Component
function UserList() {
  const filters = useUIStore((s) => s.filters);

  // Server state in Query, UI filters in Zustand
  const { data: users } = useQuery({
    queryKey: ["users", filters],
    queryFn: () => fetchUsers(filters),
  });

  return (
    <div>
      <FilterBar />
      {users?.map((user) => <UserCard key={user.id} user={user} />)}
    </div>
  );
}
```

## Comparison

| Feature | Zustand | Jotai | Context |
|---------|---------|-------|---------|
| Boilerplate | Low | Very low | Medium |
| DevTools | Yes | Yes | React DevTools |
| Persistence | Middleware | Built-in | Manual |
| Selectors | Built-in | Atoms | useMemo |
| Async | Manual | Built-in | Manual |
| Best for | Single store | Many atoms | DI, compound |

## Best Practices

1. **Don't put server data in global state** - use TanStack Query
2. **Use selectors** to prevent unnecessary re-renders
3. **Keep stores small** and focused
4. **Colocate state** - prefer local state when possible
5. **Use devtools** in development
6. **Persist** only necessary data (user preferences, cart)
