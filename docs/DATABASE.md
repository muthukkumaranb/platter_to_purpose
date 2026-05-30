# Database schema and models
This document describes the database models, fields, types, constraints, index optimizations, and relationship configurations in the Platter to Purpose application.

## Table of Contents
- [Entity relationship description](#entity-relationship-description)
- [Model specifications](#model-specifications)
- [Database indexing optimizations](#database-indexing-optimizations)
- [Soft deletion architecture](#soft-deletion-architecture)

## Entity relationship description
The database schema revolves around five core models. The relational logic is structured as follows:
- **`User`** acts as the primary entity representing hotels (donors) and orphanages (recipients).
- A **`User`** (Hotel) can create multiple **`FoodPost`** records (One-to-Many).
- A **`FoodPost`** can be claimed, generating exactly one **`Order`** (One-to-One).
- An **`Order`** can receive exactly one rating and textual review stored in **`Feedback`** (One-to-One).
- **`Notification`** alerts are linked to a **`User`** (One-to-Many) and optionally refer back to a **`FoodPost`** (Many-to-One).

---

## Model specifications

### User model (`accounts.User`)
Represents users, extending Django's default `AbstractUser`.
- **`role`**: `CharField` (max length 50). Choices: `HOTEL`, `ORPHANAGE`. Defaults to `HOTEL`.
- **`phone`**: `CharField` (max length 15). Used for OTP dispatches.
- **`address`**: `TextField`. Physical location of the entity.

### Food post model (`food.FoodPost`)
Represents surplus food listings posted by hotels.
- **`donor`**: `ForeignKey` to `accounts.User` (cascade deletion).
- **`title`**: `CharField` (max length 200).
- **`description`**: `TextField`.
- **`quantity`**: `PositiveIntegerField`. Number of servings.
- **`location`**: `CharField` (max length 255). Pickup address.
- **`expiry_time`**: `DateTimeField` (nullable). When the food will spoil.
- **`created_at`**: `DateTimeField` (auto-populated on creation).
- **`updated_at`**: `DateTimeField` (auto-updated).
- **`is_claimed`**: `BooleanField`. Indicates if a reservation exists.
- **`priority_window_ends`**: `DateTimeField` (nullable). When orphanage priority access expires.
- **`image`**: `ImageField` (nullable). Uploaded photo of the food.
- **`deleted_at`**: `DateTimeField` (nullable). Timestamp for soft deletion.

### Order model (`orders.Order`)
Represents a claim reservation on a food post.
- **`recipient`**: `ForeignKey` to `accounts.User` (cascade deletion).
- **`food_post`**: `OneToOneField` to `food.FoodPost` (cascade deletion).
- **`claimed_at`**: `DateTimeField` (auto-populated).
- **`created_at`**: `DateTimeField`. Defaults to current time.
- **`updated_at`**: `DateTimeField`.
- **`secret_token`**: `UUIDField`. Automatically generated unique ID.
- **`status`**: `CharField` (max length 20). Choices: `PENDING`, `COMPLETED`. Defaults to `PENDING`.
- **`deleted_at`**: `DateTimeField` (nullable). Timestamp for soft deletion.

### Feedback model (`feedback.Feedback`)
Represents reviews left by orphanages for completed orders.
- **`order`**: `OneToOneField` to `orders.Order` (cascade deletion).
- **`rating`**: `PositiveIntegerField`. Minimum value 1, maximum value 5.
- **`comment`**: `TextField`.
- **`created_at`**: `DateTimeField` (auto-populated).
- **`updated_at`**: `DateTimeField`.

### Notification model (`notifications.Notification`)
Stores alert logs dispatched to users.
- **`user`**: `ForeignKey` to `accounts.User` (cascade deletion).
- **`notification_type`**: `CharField` (max length 20). Choices: `PRIORITY_OPEN`, `PRIORITY_EXPIRED`, `FOOD_CLAIMED`, `PICKUP_VERIFIED`, `ORDER_WITHDRAWN`, `FOOD_EXPIRING`.
- **`title`**: `CharField` (max length 200).
- **`message`**: `TextField`.
- **`related_food_post`**: `ForeignKey` to `food.FoodPost` (nullable, set null on deletion).
- **`is_read`**: `BooleanField`. Defaults to `False`.
- **`created_at`**: `DateTimeField` (auto-populated).
- **`updated_at`**: `DateTimeField`.

---

## Database indexing optimizations
To maintain fast response times, indexes are configured on foreign keys and highly queried fields:
- **`User.role`**: Indexed for fast role-based user filtering.
- **`FoodPost.expiry_time`**, **`FoodPost.created_at`**, **`FoodPost.is_claimed`**: Indexed to accelerate listing query selections.
- **`Order.claimed_at`**, **`Order.secret_token`**, **`Order.status`**: Indexed for prompt claims verification and listing checks.
- **`Notification` composite index**: A combined database index on `('user', 'is_read')` speeds up template context processor count alerts.

---

## Soft deletion architecture
`FoodPost` and `Order` models inherit from `SoftDeleteMixin` (`apps/core/models.py`). This design ensures that deleting records only populates a `deleted_at` field:
- **Objects manager**: The default model manager (`objects`) automatically filters out records where `deleted_at` is populated.
- **All objects manager**: If soft-deleted records must be retrieved (e.g. for audit logs), you can access them via `all_objects`:
  ```python
  # Retrieve active and archived records
  all_food = FoodPost.all_objects.all()
  ```
