import uuid
from django.db import models
from django.conf import settings
from api.common.models import BaseModel
from api.products.models import Product
from api.users.models import Address
from api.common.utils import send_email

class Order(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    checked_out_at = models.DateTimeField(auto_now_add=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    admin_note = models.TextField(blank=True, null=True)
    # New fields for discounts, taxes, shipping, and coupon
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} for {self.user.email}"

    def can_transition(self, new_status):
        transitions = {
            self.Status.PENDING: [self.Status.PAID, self.Status.CANCELLED],
            self.Status.PAID: [self.Status.SHIPPED, self.Status.CANCELLED],
            self.Status.SHIPPED: [self.Status.DELIVERED],
            self.Status.DELIVERED: [],
            self.Status.CANCELLED: [],
        }
        return new_status in transitions[self.status]

    def set_status(self, new_status, notify=True):
        if self.can_transition(new_status):
            self.status = new_status
            self.save()
            if notify:
                self.send_status_email()
            return True
        return False

    def send_status_email(self):
        subject = f"Order {self.id} status update: {self.get_status_display()}"
        message = f"Your order status is now: {self.get_status_display()}"
        if self.tracking_number:
            message += f"\nTracking Number: {self.tracking_number}"
        send_email(subject, message, [self.user.email])

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at checkout

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in order {self.order.id}"

class OrderReview(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for order {self.order.id} by {self.user.email}"
