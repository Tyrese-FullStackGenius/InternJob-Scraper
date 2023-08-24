from asgiref.sync import sync_to_async
import traceback

from django.conf import settings
from django.contrib.auth import get_user_model
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from myLogger import logger


UserModel = get_user_model()

@sync_to_async
def send_payment_success_email(user_id):
    logger.info(f'Sending Payment Success Email, user id - {user_id}')
    user = UserModel.objects.get(id=user_id)
    brevo_config = sib_api_v3_sdk.Configuration()
    brevo_config.api_key['api-key'] = settings.BREVO_API_KEY
    brevo_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(brevo_config))
    subject = "We have received your payment"
    sender = {"name": "Opportunify Team", "email": "neha.nehavikas.vikas@gmail.com"}
    to = [{"email": user.email, "name": user.first_name or user.email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        template_id=5,
        to=to,
        sender=sender,
        subject=subject,
        params={'first_name': user.first_name}
    )
    try:
        res = brevo_api_instance.send_transac_email(send_smtp_email)
        print(res)
    except ApiException as ex:
        logger.error('send_payment_success_email Failed', exc_info=ex)
        message = f'Sending Email Failed.\n{traceback.format_exc()}'
        return message
    return None
