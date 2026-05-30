# REST API reference
This document provides the technical reference for all REST API endpoints, parameters, request formats, and response payloads in the Platter to Purpose platform.

## Table of Contents
- [Global configurations](#global-configurations)
- [Authentication endpoints](#authentication-endpoints)
- [Food donation endpoints](#food-donation-endpoints)
- [Order and claim endpoints](#order-and-claim-endpoints)
- [Feedback endpoints](#feedback-endpoints)
- [Analytics endpoints](#analytics-endpoints)
- [Notification endpoints](#notification-endpoints)

## Global configurations
- **Base URL**: `/api/v1/`
- **Request/Response header**: Content-Type: `application/json`
- **Authentication header**: Bearer JWT token required for all endpoints unless marked as public:
  ```http
  Authorization: Bearer <access_token>
  ```

---

## Authentication endpoints

### User registration [Public]
Creates a new inactive user and dispatches an OTP.
- **Method & URL**: `POST /api/v1/auth/register/`
- **Request payload**:
  ```json
  {
    "username": "greenhotel",
    "email": "contact@greenhotel.com",
    "password": "SecurePassword123",
    "role": "HOTEL",
    "phone": "+919876543210",
    "address": "12 Main St, Kolkata"
  }
  ```
- **Response payload** (`201 Created`):
  ```json
  {
    "message": "User registered successfully. Please verify OTP sent to your phone.",
    "user": {
      "id": 1,
      "username": "greenhotel",
      "email": "contact@greenhotel.com",
      "role": "HOTEL",
      "phone": "+919876543210",
      "address": "12 Main St, Kolkata"
    }
  }
  ```

### Verify phone OTP [Public]
Activates an account using the verification code.
- **Method & URL**: `POST /api/v1/auth/verify-otp/`
- **Request payload**:
  ```json
  {
    "username": "greenhotel",
    "otp": "123456"
  }
  ```
- **Response payload** (`200 OK`):
  ```json
  {
    "message": "Phone verification successful. You can now log in."
  }
  ```

### Obtain JWT tokens [Public]
Exchanges credentials for JWT access and refresh tokens.
- **Method & URL**: `POST /api/v1/auth/token/`
- **Request payload**:
  ```json
  {
    "username": "greenhotel",
    "password": "SecurePassword123"
  }
  ```
- **Response payload** (`200 OK`):
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsIn...",
    "refresh": "eyJhbGciOiJIUzI1NiIsIn..."
  }
  ```

### Refresh JWT tokens [Public]
Acquires a new access token using a refresh token.
- **Method & URL**: `POST /api/v1/auth/token/refresh/`
- **Request payload**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsIn..."
  }
  ```
- **Response payload** (`200 OK`):
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsIn..."
  }
  ```

---

## Food donation endpoints

### List available food posts [Public]
Retrieves a list of unclaimed, unexpired food posts. Priority window limitations apply automatically based on user roles.
- **Method & URL**: `GET /api/v1/food/`
- **Query parameters**:
  - `q`: Search keyword.
  - `location`: Location filter.
  - `min_qty`: Minimum servings quantity.
  - `sort`: Ordering option (`newest`, `expiry`, `quantity`).
- **Response payload** (`200 OK`):
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Fresh Vegetables",
        "description": "Vegetable curry and rice",
        "quantity": 30,
        "location": "Main Hall",
        "expiry_time": "2026-05-30T18:00:00+05:30",
        "created_at": "2026-05-30T12:00:00+05:30",
        "is_claimed": false,
        "priority_window_ends": "2026-05-30T12:30:00+05:30",
        "image": null
      }
    ]
  }
  ```

### Create food post [Authenticated - Hotel]
- **Method & URL**: `POST /api/v1/food/`
- **Request payload**:
  ```json
  {
    "title": "Pasta",
    "description": "Red sauce pasta",
    "quantity": 15,
    "location": "West Wing Cafe",
    "expiry_time": "2026-05-30T22:00:00+05:30"
  }
  ```
- **Response payload** (`201 Created`):
  ```json
  {
    "id": 2,
    "title": "Pasta",
    "description": "Red sauce pasta",
    "quantity": 15,
    "location": "West Wing Cafe",
    "expiry_time": "2026-05-30T22:00:00+05:30",
    "created_at": "2026-05-30T12:45:00+05:30",
    "is_claimed": false,
    "priority_window_ends": "2026-05-30T13:15:00+05:30",
    "image": null
  }
  ```

---

## Order and claim endpoints

### Claim food post [Authenticated - Orphanage]
Reserves a food post. Blocks other users from reserving it.
- **Method & URL**: `POST /api/v1/orders/claim/<food_id>/`
- **Response payload** (`201 Created`):
  ```json
  {
    "id": 5,
    "recipient": 3,
    "food_post": 1,
    "claimed_at": "2026-05-30T13:00:00+05:30",
    "status": "PENDING",
    "secret_token": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6"
  }
  ```

### Verify pickup [Authenticated - Hotel]
Confirms order pickup using the unique token presented by the orphanage. Only callable by the donor hotel.
- **Method & URL**: `POST /api/v1/orders/verify/<token>/`
- **Response payload** (`200 OK`):
  ```json
  {
    "id": 5,
    "recipient": 3,
    "food_post": 1,
    "claimed_at": "2026-05-30T13:00:00+05:30",
    "status": "COMPLETED",
    "secret_token": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6"
  }
  ```

### Withdraw claim [Authenticated - Orphanage]
Cancels a pending claim. Only allowed within 5 minutes of claiming.
- **Method & URL**: `DELETE /api/v1/orders/<order_id>/withdraw/`
- **Response payload** (`204 No Content`)

---

## Feedback endpoints

### Submit feedback [Authenticated - Orphanage]
Submits rating and comments for a completed order.
- **Method & URL**: `POST /api/v1/feedback/<order_id>/`
- **Request payload**:
  ```json
  {
    "rating": 5,
    "comment": "Food was fresh and neatly packed."
  }
  ```
- **Response payload** (`201 Created`):
  ```json
  {
    "id": 3,
    "order": 5,
    "rating": 5,
    "comment": "Food was fresh and neatly packed."
  }
  ```

---

## Analytics endpoints

### Public impact statistics [Public]
Returns aggregated system-wide impact metrics.
- **Method & URL**: `GET /api/v1/analytics/public/`
- **Response payload** (`200 OK`):
  ```json
  {
    "total_meals": 1250,
    "active_donors": 12,
    "orphanages_served": 8,
    "co2_prevented": 3125.0
  }
  ```

### Personal impact statistics [Authenticated]
Returns user-specific metrics and lists earned badges.
- **Method & URL**: `GET /api/v1/analytics/me/`
- **Response payload** (`200 OK`):
  ```json
  {
    "role": "hotel",
    "total_posts": 25,
    "completed_count": 20,
    "total_meals": 600,
    "completion_pct": 80.0,
    "co2_prevented": 1500.0,
    "badges": [
      {
        "name": "First Donation",
        "description": "Completed your first food donation rescue",
        "earned": true,
        "date_earned": "2026-05-20"
      }
    ]
  }
  ```

---

## Notification endpoints

### List user notifications [Authenticated]
Lists notifications received by the logged-in user.
- **Method & URL**: `GET /api/v1/notifications/`
- **Response payload** (`200 OK`):
  ```json
  [
    {
      "id": 14,
      "notification_type": "PRIORITY_OPEN",
      "title": "🍽️ Priority Claim Window Open — Act Fast!",
      "message": "Green Hotel just posted Pasta - 15 servings available. Claim it now!",
      "is_read": false,
      "created_at": "2026-05-30T12:45:00+05:30"
    }
  ]
  ```

### Mark notification as read [Authenticated]
- **Method & URL**: `PATCH /api/v1/notifications/<id>/read/`
- **Response payload** (`200 OK`):
  ```json
  {
    "id": 14,
    "notification_type": "PRIORITY_OPEN",
    "title": "🍽️ Priority Claim Window Open — Act Fast!",
    "message": "Green Hotel just posted Pasta - 15 servings available. Claim it now!",
    "is_read": true,
    "created_at": "2026-05-30T12:45:00+05:30"
  }
  ```
