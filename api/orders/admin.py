from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'checked_out_at', 'tracking_number')
    search_fields = ('user__email', 'id')
    list_filter = ('status', 'checked_out_at')
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    readonly_fields = ('user', 'total', 'checked_out_at')
    fieldsets = (
        (None, {'fields': ('user', 'address', 'status', 'total', 'checked_out_at', 'tracking_number', 'admin_note')}),
    )

    def mark_as_paid(self, request, queryset):
        for order in queryset:
            order.set_status(Order.Status.PAID)
        self.message_user(request, "Selected orders marked as paid.")
    mark_as_paid.short_description = "Mark selected orders as Paid"

    def mark_as_shipped(self, request, queryset):
        for order in queryset:
            order.set_status(Order.Status.SHIPPED)
        self.message_user(request, "Selected orders marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            order.set_status(Order.Status.DELIVERED)
        self.message_user(request, "Selected orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            order.set_status(Order.Status.CANCELLED)
        self.message_user(request, "Selected orders marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_name', 'quantity', 'price', 'created_at')
    search_fields = ('order__id', 'product_name')
    list_filter = ('created_at',)
