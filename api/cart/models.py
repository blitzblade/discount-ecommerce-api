from django.conf import settings
from django.db import models

from api.common.models import BaseModel
from api.products.models import Product


class Cart(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    is_active = models.BooleanField(default=True)
    checked_out = models.BooleanField(default=False)

    def clear_items(self):
        self.items.all().delete()

    def __str__(self):
        return f"Cart {self.id} for {self.user.email}"


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart {self.cart.id}"
