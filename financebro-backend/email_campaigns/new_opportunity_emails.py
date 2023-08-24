import django
django.setup()
from datetime import datetime
import traceback

from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from internships.models import (
    Configuration,
    Program,
    UserEmailNotificationPreferences
)
from myLogger import logger
from scrapers.slack_utilities import post_slack_message


config = Configuration.objects.get()
brevo_config = sib_api_v3_sdk.Configuration()
brevo_config.api_key['api-key'] = settings.BREVO_API_KEY


def get_matching_programs_single_user(user_email_preferences: UserEmailNotificationPreferences):
    programs = Program.objects.select_related('company', 'region')
    if config.new_opportunity_emails_job_last_run:
        programs = programs.filter(created_date__gte=config.new_opportunity_emails_job_last_run)
    programs = (
        programs
        .filter(region_id__in=user_email_preferences.regions)
        .filter(company__category__in=user_email_preferences.company_categories)
        .filter(category__in=user_email_preferences.program_categories)
    )

    return programs.all()


def prepare_email_params_single_user(programs, user_email_preferences: UserEmailNotificationPreferences):
    params = {
        'first_name': user_email_preferences.user.first_name,
        'programs_count': len(programs),
        'programs': []
    }

    for program in programs:
        program_dict = {'company': program.company.name}
        if program.cities:
            program_dict['location'] = ';'.join(program.cities)
        if program.deadline:
            program_dict['deadline'] = program.deadline.strftime('%b %-d, %Y')
        params['programs'].append(program_dict)

    return params


def send_email_single_user(user, email_params):
    if not settings.BREVO_API_KEY:
        return
    brevo_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(brevo_config))
    subject = "New Internship Alert"
    sender = {"name": "Opportunify Team", "email": "neha.nehavikas.vikas@gmail.com"}
    to = [{"email": "neha.nehavikas.vikas@gmail.com", "name": "Vikas Ojha"}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        template_id=2,
        to=to,
        sender=sender,
        subject=subject,
        params=email_params
    )
    try:
        brevo_api_instance.send_transac_email(send_smtp_email)
    except ApiException as ex:
        logger.error('Sending Email Failed', exc_info=ex)
        message = f'Sending Email Failed.\n{traceback.format_exc()}'
        return message
    return None


def process_all_users(test_mode: bool):
    email_sending_failure_messages = []

    user_email_notification_preferences = (
        UserEmailNotificationPreferences.objects
        .filter(email_notifications_enabled=True)
        .select_related('user')
    )
    if test_mode:
        test_users_emails = ['neha.nehavikas.automationtest@gmail.com']
        user_email_notification_preferences = (
            user_email_notification_preferences
            .filter(user__email__in=test_users_emails)
        )

    for user_email_preferences in user_email_notification_preferences:
        if user_email_preferences.user.plan != 'PAID':
            continue
        programs = get_matching_programs_single_user(user_email_preferences)
        if len(programs) > 0:
            email_params = prepare_email_params_single_user(programs, user_email_preferences)
            result = send_email_single_user(user_email_preferences.user, email_params)
            if result:
                email_sending_failure_messages.append(result)

    if email_sending_failure_messages:
        post_slack_message('\n'.join(email_sending_failure_messages))

def main():
    test_mode = settings.ENVIRONMENT != 'PRODUCTION'
    process_all_users(test_mode)


if __name__ == '__main__':
    job_start_time = datetime.now()
    main()
    config.new_opportunity_emails_job_last_run = job_start_time
    config.save()
