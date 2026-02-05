
# these are just admi configuration and it does not have nothing business logics it is all abt what we have to seen in the  django admin panel


from django.contrib import admin
from .models import Order, OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'status', 'created_at')
    list_filter = ('status', 'store')
    inlines = [OrderItemInline]

