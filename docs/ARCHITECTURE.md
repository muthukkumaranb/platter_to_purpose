# System architecture
This document describes the architectural layout, system components, layer data flows, and design patterns of the Platter to Purpose project.

## Table of Contents
- [Architectural overview](#architectural-overview)
- [Monorepo layout mapping](#monorepo-layout-mapping)
- [Layer diagram](#layer-diagram)
- [Data flow patterns](#data-flow-patterns)
- [Background processing pipeline](#background-processing-pipeline)

## Architectural overview
Platter to Purpose is built as a Django-based monorepo applying a service-selector separation pattern. Business logic operations are isolated into services (`services.py`), read-heavy operations are encapsulated in selectors (`selectors.py`), background queues are run via Celery, and caching is offloaded to Redis.

## Monorepo layout mapping
The repository is split into logical modules:
- **`apps/`**: Contains the decoupled core applications:
  - `accounts/`: User registration, roles (`HOTEL`, `ORPHANAGE`), phone validations, and verification OTPs.
  - `food/`: Food donation listings, location tags, and priority time windows.
  - `orders/`: Reservations of food, token verification, and pickup completions.
  - `dashboard/`: Web-based user dashboard rendering.
  - `feedback/`: Multi-point ratings and comments for orders.
  - `analytics/`: Meal counts, CO2 saving metrics, and badge algorithms.
  - `notifications/`: Alert generation and emailing schedules.
  - `core/`: Common components, mixins (`SoftDeleteMixin`), and base querysets.
- **`config/`**: Contains project configurations, global routing rules, celery app, settings splits, and API exception handlers.
- **`requirements/`**: Environment dependency files (base, development, production).
- **`templates/`**: Global reusable web templates.
- **`static/`**: Stylesheets and assets.

## Layer diagram
The following ASCII flow diagram maps how data enters the system and cascades through the logical layout:

```
                  [ Web Client ]               [ API Client / Mobile ]
                        |                                |
                [ Django Templates ]              [ Django Rest (DRF) ]
                        |                                |
                        +---------------+----------------+
                                        |
                                        v
                 +----------------------+----------------------+
                 |                                             |
                 v (Write Operations)                          v (Read Operations)
        [ Services Layer ]                            [ Selectors Layer ]
        (services.py)                                 (selectors.py)
                 |                                             |
                 v                                             v
        [ Models & DB Transactions ]                  [ Caching Layer (Redis) ]
                 |                                             |
                 v                                             v
       [ Database (SQLite / Postgres) ] <---------------------+
```

## Data flow patterns
The codebase uses a strict command-query responsibility separation pattern:

### 1. Read operations (queries)
All data fetches must go through `selectors.py`. Controllers (views, API views, management commands) should call selectors to retrieve QuerySets or serialized records. Selectors manage database queries, apply filtering, and manage the caching layer.
- Example: `get_available_food()` checks role contexts, applies filters, and returns a QuerySet of active postings.

### 2. Write operations (commands)
All mutation operations (creation, updates, deletions) must go through `services.py`. Services handle authentication validation, form validation, database writes inside atomic transactions, cache invalidations, and trigger notifications or Celery background tasks.
- Example: `claim_food(user, food_id)` locks the post via `select_for_update`, verifies orphanage priority windows, writes the order record, and clears the active food cache.

## Background processing pipeline
Decoupled background tasks are orchestrated using Celery and Redis:
- **Celery workers**: Consume events from the Redis broker (e.g. sending emails or dispatching OTPs).
- **Celery beat**: Periodically schedules checks (such as scanning for expiring food or notifying hotels about priority window expirations).
- **Task definitions**: Contained inside `tasks.py` files within each app directory to allow auto-discovery by the main Celery app.
