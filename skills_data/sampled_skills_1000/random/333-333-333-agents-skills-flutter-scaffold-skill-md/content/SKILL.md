---
name: flutter-scaffold
description: >
  Scaffold Flutter features with screaming + clean architecture: domain-driven directories, layered separation, and project conventions.
  Trigger: When creating a new feature/domain, adding layers to an existing feature, or reviewing mobile app structure.
metadata:
  author: 333-333-333
  version: "1.0"
  type: project
  scope: [mobile]
  auto_invoke:
    - "Creating a new Flutter feature or domain"
    - "Adding a new domain to the mobile app"
    - "Reviewing mobile app directory structure"
    - "Scaffolding a new screen or page"
---

## When to Use

- Creating a new feature/domain from scratch (e.g., `auth`, `booking`, `pet`)
- Adding layers to an existing feature
- Reviewing or refactoring app structure
- Onboarding someone to the mobile architecture

## Architecture Principles

| Principle | Rule |
|-----------|------|
| **Screaming Architecture** | Directory names = business domains, NOT technical concerns |
| **Clean Architecture** | Dependencies point INWARD: infrastructure → application → domain |
| **Ports & Adapters** | Domain defines interfaces, infrastructure implements them |
| **Feature-first** | Each feature is self-contained with all 4 layers |
| **Shared is shared** | Only truly cross-feature code goes in `shared/` |

## Dependency Rule (CRITICAL)

```
Presentation  → can import → Application, Domain
Application   → can import → Domain ONLY
Domain        → imports NOTHING (pure Dart)
Infrastructure → implements → Domain interfaces
```

Domain layer has ZERO dependencies on Flutter, Firebase, or any external package. Pure Dart only.

## Feature Structure

Every feature follows this exact structure:

```
features/{feature}/
  domain/
    entities/                # Business objects
      {entity}.dart
    repositories/            # Abstract interfaces (ports)
      {feature}_repository.dart
    value_objects/            # Immutable typed values
      {value_object}.dart
  application/
    use_cases/               # One class per use case
      {verb}_{noun}_use_case.dart
  presentation/
    providers/               # Riverpod providers
      {feature}_providers.dart
    pages/                   # Full-screen widgets (Atomic: pages level)
      {feature}_{action}_page.dart
    widgets/                 # Feature-specific widgets
      {descriptive_name}.dart
  infrastructure/
    datasources/             # External data access
      {source}_{feature}_datasource.dart
    repositories/            # Concrete implementations (adapters)
      {feature}_repository_impl.dart
    models/                  # DTOs / API response models
      {entity}_model.dart
```

## Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Feature dir | singular noun | `features/booking/` |
| Entity | singular PascalCase | `Booking`, `Pet`, `User` |
| Repository interface | `{Feature}Repository` | `AuthRepository` |
| Repository impl | `{Feature}RepositoryImpl` | `AuthRepositoryImpl` |
| Use case | `{Verb}{Noun}UseCase` | `LoginUseCase`, `CreateBookingUseCase` |
| Page | `{Feature}{Action}Page` | `LoginPage`, `BookingDetailPage` |
| Provider | `{feature}{Purpose}Provider` | `authStateProvider`, `bookingListProvider` |
| Datasource | `{Source}{Feature}Datasource` | `FirebaseAuthDatasource` |
| Model (DTO) | `{Entity}Model` | `UserModel`, `BookingModel` |

## Adding a New Feature

1. Create directory: `lib/features/{feature}/`
2. Create all 4 layers: `domain/`, `application/`, `presentation/`, `infrastructure/`
3. Define entities in `domain/entities/`
4. Define repository interface in `domain/repositories/`
5. Implement use cases in `application/use_cases/`
6. Create Riverpod providers in `presentation/providers/`
7. Build pages and widgets in `presentation/pages/` and `presentation/widgets/`
8. Implement repository in `infrastructure/repositories/`
9. Register providers in `app/di/providers.dart` if global

## Commands

```bash
# Create a new feature scaffold
mkdir -p lib/features/{feature}/{domain/{entities,repositories,value_objects},application/use_cases,presentation/{providers,pages,widgets},infrastructure/{datasources,repositories,models}}

# Verify structure
find lib/features/{feature} -type d | sort
```

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| `lib/screens/login_screen.dart` | `lib/features/auth/presentation/pages/login_page.dart` |
| `lib/models/user.dart` (global) | `lib/features/auth/domain/entities/user.dart` |
| Import Firebase in domain | Define interface in domain, implement in infrastructure |
| `lib/utils/` grab bag | Put in the feature or `shared/` where it belongs |
| Business logic in widgets | Widgets call providers, providers call use cases |
| One massive `providers.dart` | One provider file per feature, global DI in `app/di/` |
| Domain entities with `toJson` | DTOs in infrastructure/models handle serialization |
