---
name: react-hooks-patterns
description: 'Patrones correctos para React hooks, especialmente useCallback y useMemo con hooks custom. Usa esta skill cuando trabajes con hooks custom que retornan objetos, al optimizar renders con useCallback/useMemo, o cuando experimentes bucles infinitos de re-renders. Cubre dependencias correctas, estabilidad de referencias, y patrones anti-fragilidad.'
---

# Patrones de React Hooks

Guia para usar React hooks correctamente, especialmente cuando se combinan con hooks custom que retornan objetos.

## Problema Critico: Bucles Infinitos con Hooks Custom

### El Anti-Patron Peligroso

```typescript
// Hook custom que retorna un objeto
function useEntityManager<T>() {
  const [items, setItems] = useState<T[]>([]);
  
  const resetForm = useCallback(() => {
    // ...
  }, []);
  
  // Este objeto se RECREA en cada render!
  return {
    items,
    resetForm,
    handleCreate,
    handleUpdate,
    // ...
  };
}

// Componente que usa el hook
function MyComponent() {
  const manager = useEntityManager();
  
  // PROBLEMA: manager es un objeto nuevo cada vez
  // Esto invalida el useCallback en CADA render
  const handleClick = useCallback(() => {
    manager.resetForm();
  }, [manager]); // ❌ BUCLE INFINITO
  
  return <button onClick={handleClick}>Click</button>;
}
```

### La Solucion Correcta

```typescript
function MyComponent() {
  const manager = useEntityManager();
  
  // SOLUCION: Usa propiedades ESPECIFICAS del manager
  const handleClick = useCallback(() => {
    manager.resetForm();
  }, [manager.resetForm]); // ✅ ESTABLE
  
  return <button onClick={handleClick}>Click</button>;
}
```

## Reglas de Oro

### Regla 1: Nunca Uses Objetos Completos como Dependencias

```typescript
// ❌ MAL - el objeto entero
const handler = useCallback(() => {
  api.fetchData();
}, [api]);

// ✅ BIEN - la funcion especifica
const handler = useCallback(() => {
  api.fetchData();
}, [api.fetchData]);
```

### Regla 2: Destructura Temprano si Usas Multiples Propiedades

```typescript
// ❌ PROPENSO A ERRORES - facil olvidar una dependencia
const handler = useCallback(() => {
  manager.resetForm();
  manager.setError(null);
  manager.clearSelection();
}, [manager.resetForm, manager.setError, manager.clearSelection]);

// ✅ MAS CLARO - destructura al inicio del componente
function MyComponent() {
  const {
    resetForm,
    setError,
    clearSelection,
    handleCreate,
    handleUpdate,
  } = useEntityManager();
  
  const handler = useCallback(() => {
    resetForm();
    setError(null);
    clearSelection();
  }, [resetForm, setError, clearSelection]);
}
```

### Regla 3: Hooks Custom Deben Retornar Referencias Estables

```typescript
// ❌ MAL - funciones recreadas en cada render
function useMyHook() {
  const doSomething = () => { /* ... */ };
  return { doSomething };
}

// ✅ BIEN - funciones memorizadas
function useMyHook() {
  const doSomething = useCallback(() => { /* ... */ }, []);
  return { doSomething };
}

// ✅ MEJOR - retorno memoizado completo (cuando es necesario)
function useMyHook() {
  const doSomething = useCallback(() => { /* ... */ }, []);
  
  return useMemo(() => ({
    doSomething,
    data,
    loading,
  }), [doSomething, data, loading]);
}
```

### Regla 4: Usa Primitivos en Lugar de Objetos Cuando Sea Posible

```typescript
// ❌ MAL - objeto como dependencia
const handler = useCallback(() => {
  if (filters.status === 'active') {
    // ...
  }
}, [filters]);

// ✅ BIEN - primitivo como dependencia
const { status } = filters;
const handler = useCallback(() => {
  if (status === 'active') {
    // ...
  }
}, [status]);
```

## Patron para Componentes CRUD con useEntityManager

Este proyecto usa un patron estandar para managers de entidades:

```typescript
function EntityManager() {
  const manager = useEntityManager<Entity, EntityInput>({
    entityName: 'entidad',
    fetchAll: () => api.getAll(),
    create: (data) => api.create(data),
    update: (id, data) => api.update(id, data),
    remove: (id) => api.delete(id),
    // ...
  });

  // Modal State local
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Handlers con dependencias ESPECIFICAS
  const handleOpenCreateModal = useCallback(() => {
    manager.resetForm();
    setFormMode('create');
    setIsFormModalOpen(true);
  }, [manager.resetForm]); // ✅ Solo la funcion usada

  const handleOpenEditModal = useCallback((entity: Entity) => {
    manager.selectForEdit(entity);
    setFormMode('edit');
    setIsFormModalOpen(true);
  }, [manager.selectForEdit]); // ✅ Solo la funcion usada

  const handleCloseFormModal = useCallback(() => {
    setIsFormModalOpen(false);
    manager.clearSelection();
  }, [manager.clearSelection]); // ✅ Solo la funcion usada

  const handleFormSubmit = useCallback(async (e: React.FormEvent) => {
    const success = formMode === 'create' 
      ? await manager.handleCreate(e)
      : await manager.handleUpdate(e);
    
    if (success) {
      setIsFormModalOpen(false);
    }
    return success;
  }, [formMode, manager.handleCreate, manager.handleUpdate]); // ✅ Funciones especificas

  const handleOpenDeleteDialog = useCallback((entity: Entity) => {
    manager.selectForDelete(entity);
    setIsDeleteDialogOpen(true);
  }, [manager.selectForDelete]); // ✅ Solo la funcion usada

  const handleCloseDeleteDialog = useCallback(() => {
    setIsDeleteDialogOpen(false);
    manager.clearSelection();
  }, [manager.clearSelection]); // ✅ Solo la funcion usada

  const handleDelete = useCallback(async () => {
    const success = await manager.handleDelete();
    if (success) {
      setIsDeleteDialogOpen(false);
    }
  }, [manager.handleDelete]); // ✅ Solo la funcion usada

  // Render...
}
```

## Checklist de Verificacion

Antes de commitear componentes con hooks:

- [ ] Ningun useCallback/useMemo usa objetos completos de hooks custom
- [ ] Todas las dependencias son primitivos o funciones memorizadas
- [ ] Los handlers que usan multiples propiedades del hook las listan todas
- [ ] Los hooks custom retornan funciones con useCallback
- [ ] No hay dependencias faltantes (ESLint exhaustive-deps)

## Debugging de Bucles Infinitos

Si sospechas un bucle infinito:

1. **Abre React DevTools Profiler**
2. **Graba una sesion corta**
3. **Busca componentes que renderizan muchas veces**
4. **Verifica las dependencias de sus useCallback/useMemo**
5. **Busca objetos de hooks custom en las dependencias**

### Comando Util

```bash
# Busca el anti-patron en tu codigo
grep -rn "\[manager\]" src/components/
grep -rn "\[hook\]" src/components/
grep -rn "}, \[.*\.\.\." src/components/  # Spread en dependencias
```

## Componentes del Proyecto que Siguen Este Patron

- `UsuariosManager.tsx` - ✅ Corregido
- `ProveedoresManager.tsx` - ✅ Corregido
- `ClientesManager.tsx` - ✅ Corregido
- `CategoriasManager.tsx` - ✅ Corregido
- `ProductosManager.tsx` - ✅ Usa useProductos correctamente
- `OrdenesManager.tsx` - ✅ Usa useOrdenes correctamente

## Referencias

- React docs: Rules of Hooks
- React docs: useCallback
- Vercel React Best Practices: rerender-dependencies
- Este proyecto: src/hooks/useEntityManager.ts
