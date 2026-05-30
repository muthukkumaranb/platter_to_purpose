# Testing strategy
This document describes the test execution processes, directories, layout, and testing standards for the Platter to Purpose project.

## Table of Contents
- [Test suite layout](#test-suite-layout)
- [Running tests locally](#running-tests-locally)
- [Test coverage targets](#test-coverage-targets)
- [Factory pattern implementation](#factory-pattern-implementation)
- [App-specific test scenarios](#app-specific-test-scenarios)

## Test suite layout
The testing files are separated by scope and location within the monorepo structure:
- **Unit tests**: Located inside each application under `apps/<app_name>/tests/`. These files cover selectors, services, models, forms, and serializers in isolation.
- **Integration tests**: Grouped inside the root-level `tests/` directory to verify cross-app workflows, template rendering, and end-to-end user flows.

## Running tests locally
You can execute the test suite using either the Django test runner or pytest:

### Running with Django runner
```bash
python manage.py test
```

### Running with pytest
```bash
pytest --ds=config.settings.development
```

## Test coverage targets
The target test coverage is **80% or higher** for each active application. You can run coverage analysis with:
```bash
pytest --ds=config.settings.development --cov=apps --cov-report=term-missing
```

## Factory pattern implementation
We use `factory-boy` to manage test database fixtures dynamically. The following code fragment shows the standard declaration of factories for users, food posts, and orders:

```python
import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.food.models import FoodPost
from apps.orders.models import Order

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    role = 'HOTEL'

class FoodPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FoodPost

    donor = factory.SubFactory(UserFactory)
    title = "Fresh Rice and Vegetables"
    description = "20 servings of fresh vegetarian food"
    quantity = 20
    location = "Main Kitchen Hall"
    expiry_time = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=4))

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    recipient = factory.SubFactory(UserFactory, role='ORPHANAGE')
    food_post = factory.SubFactory(FoodPostFactory)
    status = 'PENDING'
```

## App-specific test scenarios
To maintain high code quality, every application must cover at least these three functional test scenarios:

### Accounts app
- **User registration**: Validating credentials, email formatting, and assigning the correct user role.
- **OTP verification**: Simulating successful verification cache hits and expired/invalid cache misses.
- **Asynchronous dispatch**: Verifying that the Celery task triggers SMS/WhatsApp OTP dispatch workflows.

### Food app
- **Donation listing**: Validating that hotel users can create a new `FoodPost` and that default priority windows are assigned.
- **Availability queries**: Confirming that orphanage priority restrictions hide posts from hotel users during the first 30 minutes.
- **Expiry daemon checks**: Verifying that periodic Celery tasks identify food posts reaching the end of their priority window.

### Orders app
- **Concurrent claims**: Simulating database transaction locks (`select_for_update`) to prevent duplicate claims on the same food post.
- **Token verification**: Verifying order pickups using secret UUID tokens and validating that the donor is the one who initiates the confirmation.
- **Order withdrawal**: Verifying that claims can be withdrawn within 5 minutes, but are locked after the cancellation period.

### Dashboard app
- **Hotel layouts**: Rendering active and completed food posts associated with the authenticated hotel user.
- **Orphanage layouts**: Displaying claimed orders, completed pickups, and feedback links for orphanage users.
- **Auth access**: Ensuring anonymous users are redirected to login and cannot access dashboard pages.

### Feedback app
- **Submit rating**: Posting ratings (1-5 scale) and textual comments for completed orders.
- **Duplicate submission**: Asserting that submitting multiple feedback entries for a single order returns a validation error.
- **Feedback visibility**: Ensuring hotels can view average rating scores derived from feedback left by orphanages.

### Notifications app
- **In-app queries**: Listing notifications filtered by read and unread status for a logged-in user.
- **Mark read**: Confirming patch endpoints transition notifications from unread to read.
- **Expiring food alert**: Running tasks to scan food expiring within 1 hour and verifying alerts are sent to the donor.

### Analytics app
- **Platform metrics**: Verifying aggregation queries for total meals saved, active donors, and carbon emission savings.
- **Personal impact stats**: Confirming specific metrics show accurate values based on completed orders.
- **Badges awarding**: Checking badge tier thresholds and validating that badges are cached for 1 day.
