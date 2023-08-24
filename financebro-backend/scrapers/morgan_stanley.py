import django
django.setup()

from datetime import datetime
import traceback

from django.db import transaction
import requests

from internships.models import (
    Company,
    CompanyChoices,
    Program
)
from scrapers.slack_utilities import post_slack_message
from scrapers.utilities import (
    assign_program_category,
    assign_program_cities_countries,
    DEFAULT_REQUESTS_TIMEOUT,
    delete_program_cities_countries_association,
    map_city,
    RegionsEnum,
    send_slack_message_not_found,
    set_programs_latest_scrape_flag
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.MORGAN_STANLEY)


REGION_MAPPING = {
    'Europe, Middle East, Africa': RegionsEnum.EMEA.name,
    'Americas': RegionsEnum.AMERICAS.name,
    'Non-Japan Asia': RegionsEnum.ASIA.name,
    'Japan': RegionsEnum.ASIA.name,
}

PROGRAM_TYPE_MAPPING = {
    'Internship': 'INTERNSHIP'
}


@transaction.atomic
def scrape_new_programs():
    logger.info('Morgan Stanley: Scraping Programs...')
    url = (
        'https://www.morganstanley.com/web/career_services/webapp/service/careerservice/resultset.json?'
        '&opportunity=sg&lang=en'
    )

    r = requests.get(url, timeout=DEFAULT_REQUESTS_TIMEOUT).json()

    cities_not_found = []
    regions_not_found = []

    for program_dict in r['resultSet']:
        if program_dict['employmentType'] not in PROGRAM_TYPE_MAPPING.keys():
            continue

        external_id = program_dict["jobNumber"]
        program = Program.objects.filter(company=company, external_id=external_id).first()
        if program is None:
            program = Program(company=company, external_id=external_id)
        program.url = f'https://www.morganstanley.com/careers/students-graduates/opportunities/{external_id}'
        program.title = program_dict['jobTitle']

        program.description = program_dict.get('jobHtmlDescription', program_dict['jobDescription'])
        program.application_url = program_dict['url']

        try:
            program.deadline = datetime.fromtimestamp(
                float(program_dict['sortingDate']/1000)
            ).date()
            program.is_application_open = program.deadline >= datetime.today().date()
        except Exception as exc:
            logger.error(
                'Morgan Stanley - Error Parsing Deadline Date %s, %s',
                program_dict['sortingDate'],
                program.url,
                exc_info=exc
            )
        program.deadline_text = program_dict['applicationDate']
        program.program_type = PROGRAM_TYPE_MAPPING[program_dict['employmentType']]

        program.region_id = REGION_MAPPING.get(program_dict['region'])
        if program.region_id is None:
            regions_not_found.append(program_dict['region'])
        program.category = assign_program_category(program.title)

        program.save()

        # Cities
        delete_program_cities_countries_association(program)

        city = program_dict['location'].split(',')[0]
        mapped_city = map_city(city, extra_mapping_to_check=None)
        if mapped_city is None:
            cities_not_found.append(city)
            mapped_city = 'MULTIPLE'
        program.cities = [program_dict['location']]
        assign_program_cities_countries(program, mapped_city)

        program.extra_data = {
            k: program_dict[k]
            for k in [
                'jobLevel', 'division', 'businessArea', 'db_business_unit', 'qualification', 'opportunity',
                'educationLevel'
            ]
        }

        program.found_in_latest_scrape = (
            program.is_application_open
            if program.is_application_open is not None
            else True
        )
        program.is_details_scraped = (
            False
            if program.found_in_latest_scrape
            else True
        )

        program.save()

    if cities_not_found:
        send_slack_message_not_found(company, cities_not_found, prefix='Cities')
    if regions_not_found:
        send_slack_message_not_found(company, regions_not_found, prefix='Regions')


def main():
    set_programs_latest_scrape_flag(company_id=company.id, found_in_latest_scrape=False)
    scrape_new_programs()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.error('Morgan Stanley Scraper Failed', exc_info=exc)
        message = f'Morgan Stanley Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
