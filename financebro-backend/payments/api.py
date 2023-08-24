from django.conf import settings
from django.http import HttpResponse
from ninja import Router
from sentry_sdk import capture_exception
import stripe

from customauth.utilities import await_auth
from email_campaigns.payment_success_email import send_payment_success_email
from myLogger import logger
from payments.async_orm_utilities import create_user_subscription
from payments.schemas import CreateStripeCheckoutSessionSchema


stripe.api_key = settings.STRIPE_API_KEY
router = Router()
webhooks_router = Router()

@router.post('/create-checkout-session')
@await_auth
async def create_checkout_session(
    request,
    create_stripe_checkout_session_data: CreateStripeCheckoutSessionSchema
):
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            line_items=[
                {
                    'price': create_stripe_checkout_session_data.price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            client_reference_id=request.user.id,
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL
        )
    except Exception as e:
        capture_exception(e)
        return str(e)

    return 200, {'redirect_url': checkout_session.url}


@webhooks_router.post('/checkout-completed')
async def checkout_completed(request):
    endpoint_secret = settings.STRIPE_WEBHOOK_CHECKOUT_COMPLETED_ENDPOINT_SECRET
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        capture_exception(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        capture_exception(e)
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )

        await create_user_subscription(session)

        if session.client_reference_id:
            try:
                await send_payment_success_email(session.client_reference_id)
            except Exception as ex:
                logger.error('Payment Success Email Failed', exc_info=ex)

    return 200, {}
