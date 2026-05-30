# Authentication architecture
This document outlines the authentication model, roles, verification flows, token configurations, and session management used in the Platter to Purpose project.

## Table of Contents
- [User role model](#user-role-model)
- [Registration and verification flow](#registration-and-verification-flow)
- [JSON Web Token architecture](#json-web-token-architecture)
- [Template session management](#template-session-management)

## User role model
The platform implements a strict role-based user model defined in `apps/accounts/models.py`. The two core roles are:
- **Hotel (`HOTEL`)**: Donors who post surplus food details, specify pickup locations, and confirm pickups by scanning tokens or entering verification IDs.
- **Orphanage (`ORPHANAGE`)**: Recipients who search for available food posts, reserve portions within a priority window, and present verification tokens at pickup.

Users can check their roles via model utility methods:
```python
# Check role eligibility
user.is_hotel()      # Returns True if role is HOTEL
user.is_orphanage()  # Returns True if role is ORPHANAGE
```

## Registration and verification flow
To register a new user and verify their mobile number, the following multi-step workflow is performed:

```
[User Registration] -> [Status: Inactive] -> [Cache OTP generated] -> [Celery Dispatch OTP]
                                                                            |
[Access Activated]  <- [OTP Matches Cache] <- [User Submits OTP]    <- [User Receives OTP]
```

### 1. Account creation
A user registers via the REST API at `POST /api/v1/auth/register/` or the registration template. The user's account is created with `is_active = False` to prevent unauthorized usage before verification.

### 2. OTP dispatch
An OTP (6-digit numeric string) is generated using `apps/accounts/utils.py`. The OTP is saved in the cache with a 10-minute TTL:
- Cache Key: `otp_<username>`
- Cache Value: `<6_digit_otp>`
- TTL: 600 seconds (10 minutes)

The OTP is dispatched asynchronously via the Celery background task:
```python
# Async Celery execution
send_otp_task.delay(user.phone, otp)
```

### 3. Verification
The user submits the received code to `POST /api/v1/auth/verify-otp/`. If the entered code matches the cached OTP, the user is marked `is_active = True`, and the OTP cache entry is deleted.

## JSON Web Token architecture
The REST API uses JSON Web Tokens (JWT) for stateless session authentication. The simplejwt package is configured in `config/settings/base.py`:
- **Algorithm**: `HS256` signed using the project's `SECRET_KEY`.
- **Token lifetimes**: Access token: 60 minutes. Refresh token: 7 days.
- **Blacklisting**: Old refresh tokens are blacklisted upon rotation.

### JWT REST API endpoints
- `POST /api/v1/auth/token/`: Obtain a new access/refresh token pair using credentials.
- `POST /api/v1/auth/token/refresh/`: Rotate a valid refresh token to get a new access token.

### Request authentication header
Requests to authenticated endpoints must include the access token in the `Authorization` header:
```json
{
  "Authorization": "Bearer <access_token>"
}
```

## Template session management
For template-based views, standard Django session middleware is used.
- **Login redirect**: Upon successful login, users are redirected to `dashboard` (`/dashboard/`).
- **Logout redirect**: Logging out redirects users back to `home` (`/`).
- **Cookies security**: In production settings, session cookies are configured with `SESSION_COOKIE_SECURE = True` to ensure they are only transmitted over HTTPS connections.
