from scrapers.slack_utilities import post_slack_message
from myLogger import logger
from internships.models import (
    HistoricalData,
    Program
)
from urllib3 import disable_warnings
from sentry_sdk.crons import monitor
from sentry_sdk import capture_exception
from django.conf import settings
import traceback
from time import sleep
import importlib
from datetime import datetime
import django
django.setup()


SCRAPERS_TO_RUN = [
    'goldman_sachs',
    'morgan_stanley',
    'jp_morgan',
    'evercore',
    'lazard',
    'bankofamerica',
    'bnp_paribas',
    'societe_generale',
    'rothschild',
    'barclays',
    'hsbc',
    'citibank',
    'deutsche_bank',
    'bain',
    'mckinsey',
    'careers_bcg',
    'careers_marshmclennan',
    'accenture'
]


def update_historical_data(historical_date=datetime.now().date()):
    logger.info('Updating Historical Data')
    historical_data, _ = HistoricalData.objects.get_or_create(
        historical_date=historical_date)
    historical_data.total_programs_count = Program.objects.count()
    historical_data.open_programs_count = (
        Program.objects
        .get_programs_with_applications_open(is_application_open=True)
        .count()
    )
    historical_data.save()


@monitor(monitor_slug='scrapers-cron')
def main():
    for scraper_to_run in SCRAPERS_TO_RUN:
        try:
            module = importlib.import_module(name=f'scrapers.{scraper_to_run}')
            module.main()
        except Exception as exc:
            capture_exception(exc)
            logger.error('%s Scraper Failed', scraper_to_run, exc_info=exc)
            message = f'{scraper_to_run} Scraper Failed.\n{traceback.format_exc()}'
            if settings.ENVIRONMENT != 'DEV':
                post_slack_message(message)
        sleep(1)

    try:
        update_historical_data()
    except Exception as exc:
        capture_exception(exc)
        logger.error('update_historical_data Failed', exc_info=exc)
        message = f'update_historical_data Failed.\n{traceback.format_exc()}'
        if settings.ENVIRONMENT != 'DEV':
            post_slack_message(message)


if __name__ == '__main__':
    disable_warnings()
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    if settings.ENVIRONMENT != 'DEV':
        post_slack_message(
            f'Scrapers Completed. Time Taken: {end_time-start_time}')
