from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    balance = 0

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class PaymentSides(models.TextChoices):
    Debit = "Debit"
    Credit = "Credit"


class ProductStatus(models.TextChoices):
    Active = "Active"


class Payment(models.Model):
    createdAt = models.DateTimeField("date published")
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    side = models.TextField(choices=PaymentSides)
    amount = models.PositiveIntegerField(default=0)


class Product(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=600)
    customer = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    status = models.TextField(choices=ProductStatus, default=ProductStatus.Active)
    in_stock = models.PositiveIntegerField(default=0)
