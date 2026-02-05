from celery import shared_task
from apps.orders.models import Order
@shared_task
def send_order_confirmation(order_id: int) -> None:
    order = Order.objects.filter(pk=order_id).first()#to avoid crashing if the order_id does not exist
    if not order:
        return
    print("these is where we put would normally the logic like send order confirmation")
    return
