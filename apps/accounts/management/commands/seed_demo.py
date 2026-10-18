from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.feedback.models import Feedback
from apps.food.models import FoodPost
from apps.notifications.models import Notification
from apps.orders.constants import OrderStatus
from apps.orders.models import Order


class Command(BaseCommand):
    help = "Create or reset the safe demo users and their sample data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete only demo-owned records before recreating them.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_demo_data()

        demo_users = {}
        for role, label in User.Role.choices:
            username = f"demo_{role.lower()}"
            user, _created = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "role": role,
                    "is_demo": True,
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                    "phone": "",
                    "address": f"Demo {label}",
                },
            )
            user.set_unusable_password()
            user.save(
                update_fields=[
                    "password",
                    "email",
                    "role",
                    "is_demo",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "phone",
                    "address",
                ]
            )
            demo_users[role] = user

        donor = demo_users[User.Role.HOTEL]
        recipient = demo_users[User.Role.ORPHANAGE]
        posts = []
        for index in range(9):
            post, _created = FoodPost.objects.update_or_create(
                donor=donor,
                title=f"Demo surplus meal {index + 1}",
                defaults={
                    "description": "Fresh surplus food prepared for community sharing.",
                    "quantity": 10 + index * 5,
                    "location": f"Demo Kitchen {index % 3 + 1}",
                    "expiry_time": timezone.now() + timedelta(days=2),
                    "is_claimed": index < 3,
                },
            )
            posts.append(post)

        statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.COMPLETED,
        ]
        for post, status in zip(posts[:3], statuses):
            order, _created = Order.objects.update_or_create(
                food_post=post,
                defaults={"recipient": recipient, "status": status},
            )
            if status == OrderStatus.COMPLETED:
                Feedback.objects.update_or_create(
                    order=order,
                    defaults={
                        "rating": 5,
                        "comment": "A reliable and generous demo donation.",
                    },
                )

        for index, post in enumerate(posts[:3], start=1):
            Notification.objects.update_or_create(
                user=recipient,
                title=f"Demo notification {index}",
                defaults={
                    "notification_type": Notification.Type.FOOD_POSTED,
                    "message": f"Sample update about {post.title}.",
                    "related_food_post": post,
                    "is_read": index == 3,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(demo_users)} demo users, {len(posts)} food posts, "
                "3 orders, feedback, and notifications."
            )
        )

    def _reset_demo_data(self):
        demo_users = User.objects.filter(is_demo=True)
        demo_posts = FoodPost.all_objects.filter(donor__in=demo_users)
        demo_orders = Order.all_objects.filter(
            recipient__in=demo_users
        ) | Order.all_objects.filter(food_post__in=demo_posts)
        Feedback.objects.filter(order__in=demo_orders).delete()
        Notification.objects.filter(user__in=demo_users).delete()
        demo_orders.delete()
        demo_posts.delete()
        demo_users.delete()
