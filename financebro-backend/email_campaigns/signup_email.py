import traceback

from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from myLogger import logger


def send_signup_email(user):
    logger.info(f'Sending Signup Email, user id - {user.id}')
    brevo_config = sib_api_v3_sdk.Configuration()
    brevo_config.api_key['api-key'] = settings.BREVO_API_KEY
    brevo_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(brevo_config))
    subject = "Your account is created"
    sender = {"name": "Opportunify Team", "email": "neha.nehavikas.vikas@gmail.com"}
    to = [{"email": user.email, "name": user.first_name or user.email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        template_id=4,
        to=to,
        sender=sender,
        subject=subject,
        params={'first_name': user.first_name}
    )
    try:
        res = brevo_api_instance.send_transac_email(send_smtp_email)
        print(res)
    except ApiException as ex:
        logger.error('send_signup_email Failed', exc_info=ex)
        message = f'Sending Email Failed.\n{traceback.format_exc()}'
        return message
    return None
