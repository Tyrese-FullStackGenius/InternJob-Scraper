from asgiref.sync import sync_to_async
from datetime import timedelta

from django.utils import timezone

from customauth.models import UserSubscription
from myLogger import logger


subscription_end_timedeltas = {
    'price_1NNVm1D5UNPd1Scm4AeScWSf': timedelta(days=90),
    'price_1NNVm1D5UNPd1ScmucSwF63S': timedelta(days=180),
}



@sync_to_async
def create_user_subscription(stripe_session):
    logger.debug(stripe_session)
    price_dict = stripe_session.line_items.data[0].price
    UserSubscription.objects.create(
        user_id=stripe_session.client_reference_id,
        stripe_id=stripe_session.id,
        stripe_amount_total=stripe_session.amount_total,
        stripe_customer_id=stripe_session.customer or '',
        stripe_customer_email=stripe_session.customer_email,
        stripe_subscription_id=stripe_session.payment_intent,
        stripe_subscription_starts_at=timezone.now(),
        stripe_subscription_ends_at=timezone.now() + subscription_end_timedeltas.get(price_dict.id, timedelta(days=90)),
        stripe_subscription_plan_name=price_dict.nickname or '',
        stripe_subscription_plan_id=price_dict.id,
        stripe_subscription_product_id=price_dict.product
    )
