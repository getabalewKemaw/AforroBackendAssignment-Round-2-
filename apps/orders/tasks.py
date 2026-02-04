from celery import shared_task

from apps.orders.models import Order


@shared_task
def send_order_confirmation(order_id: int) -> None:
    order = Order.objects.filter(pk=order_id).first()
    if not order:
        return
    return
