from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.http import HttpResponse, HttpResponseBadRequest


class InsufficientBalance(Exception):
    def __init__(self, balance: int = 0, expected_amount: int = 0, *, message: str | None = None):
        _message = message or f"Insufficient Balance. Current balance is {balance}. Needs at least {expected_amount}"
        super().__init__(_message)


class CustomUser(AbstractUser):
    balance = models.PositiveIntegerField(default=0)

    def check_balance(self, amount: int):
        """Indicates whether the user has the ability to pay a payment with this amount."""
        return self.balance >= amount

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class PaymentSides(models.TextChoices):
    Debit = "Debit"
    Credit = "Credit"


class ProductStatus(models.TextChoices):
    Active = "Active"


class Payment(models.Model):
    created_at = models.DateTimeField("date published", auto_now=True)
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    side = models.TextField(choices=PaymentSides)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.side}: {self.amount} ({self.user})"


class Product(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=600)
    customer = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    status = models.TextField(choices=ProductStatus, default=ProductStatus.Active)
    in_stock = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
