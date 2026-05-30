# Platform workflows
This document describes the end-to-end user journeys, role transitions, and state machines for food donations and claims in the Platter to Purpose system.

## Table of Contents
- [User workflows overview](#user-workflows-overview)
- [Hotel donation workflow](#hotel-donation-workflow)
- [Orphanage claiming workflow](#orphanage-claiming-workflow)
- [Order states and transitions](#order-states-and-transitions)
- [Verification and pickup journey](#verification-and-pickup-journey)

## User workflows overview
The system relies on a collaborative workflow where Hotels donation postings are claimed by Orphanages. Time windows and verification tokens secure the handoff.

---

## Hotel donation workflow
The hotel lifecycle for listing surplus food follows this process:
1. **Posting**: The hotel enters food details (quantity, location, description, and expiry time) through the dashboard or `POST /api/v1/food/`.
2. **Priority locking**: The system automatically computes a 30-minute priority window. During this window, only orphanages can view and claim the listing.
3. **Open access**: If the priority window expires and the food remains unclaimed, the listing opens to all recipient groups.
4. **Spoilage/Claims**: The post remains active until it is either claimed or reaches its designated `expiry_time`.

---

## Orphanage claiming workflow
The orphanage lifecycle for reserving and acquiring food is as follows:
1. **Search**: The orphanage views available listings via `GET /api/v1/food/` or the public listings dashboard.
2. **Reservation**: The orphanage submits a claim request via `POST /api/v1/orders/claim/<food_id>/`.
3. **Locking**: The system creates a pending `Order` record, links it to the `FoodPost`, and sets `is_claimed = True` to block concurrent reservations.
4. **Token acquisition**: The orphanage receives a unique UUID `secret_token` associated with the order.
5. **Withdrawal option**: The orphanage can withdraw the claim within a 5-minute cancellation window. This deletes the order and returns `is_claimed` to `False`.

---

## Order states and transitions
The lifecycle of an order is managed through the following state machine transitions:

```
[ FoodPost Created ]
         |
         v
     [ Status: Open / Priority ]
         |
         +-------------------------------------------------+
         | (Orphanage Claims Food)                         | (Food Post Expires)
         v                                                 v
  [ Order: PENDING ]                                [ Status: EXPIRED ]
         |
         +------------------------+
         | (Completed Pickup)     | (Claim Withdrawn < 5 mins)
         v                        v
[ Order: COMPLETED ]     [ FoodPost: Re-opened ]
```

### State definitions
- **`PENDING`**: The food post is reserved. The recipient must pick up the food before the expiration time.
- **`COMPLETED`**: The pickup has been verified by the donor hotel using the secret token.
- **`RE-OPENED`**: The order is canceled, making the food post available for reservation again.

---

## Verification and pickup journey
The verification process ensures that the reserved food is delivered securely to the claiming orphanage:
1. **Arrival**: The orphanage representative arrives at the hotel's designated pickup location.
2. **Token presentation**: The representative presents their unique `secret_token` (as a UUID string or generated QR code).
3. **Verification check**: The hotel inputs the token via the dashboard or `POST /api/v1/orders/verify/<token>/`.
4. **Completion**: If the token matches, the system updates the order's status to `COMPLETED`. This invalidates the cached platform statistics and awards impact badges to both the donor and the recipient.
5. **Feedback**: The orphanage can submit a rating and comment via `POST /api/v1/feedback/<order_id>/` to rate their experience.
