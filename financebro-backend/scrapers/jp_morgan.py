import django
django.setup()

from datetime import datetime
import traceback

from dateutil.parser import parse as dateutil_parse
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
    assign_program_countries,
    DEFAULT_REQUESTS_TIMEOUT,
    delete_program_cities_countries_association,
    map_city,
    map_country,
    RegionsEnum,
    send_slack_message_not_found,
    set_programs_inactive_based_on_latest_scrape_flag,
    set_programs_latest_scrape_flag
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.JP_MORGAN)


REGION_MAPPING = {
    'North America': RegionsEnum.AMERICAS.name,
    'Latin America': RegionsEnum.AMERICAS.name,
    'Asia Pacific': RegionsEnum.ASIA.name,
    'Europe, Middle East, & Africa': RegionsEnum.EMEA.name,
    'Europe, Middle East, and Africa': RegionsEnum.EMEA.name,
}

PROGRAM_TYPE_MAPPING = {
    'Internship': 'INTERNSHIP'
}


@transaction.atomic
def scrape_new_programs():
    logger.info('JP Morgan: Scraping Programs...')
    url_all_programs = 'https://careers.jpmorgan.com/services/json/careers/programs.global.en.json'
    all_programs_data = requests.get(url_all_programs, timeout=DEFAULT_REQUESTS_TIMEOUT).json()
    url_open_programs = 'https://careers.jpmorgan.com/services/json/careers/gate/programs.json'
    open_program_data = requests.get(url_open_programs, timeout=DEFAULT_REQUESTS_TIMEOUT).json()

    cities_not_found = []
    regions_not_found = []

    for jpmorgan_program_id, program_dict in all_programs_data.items():
        if (
            jpmorgan_program_id not in open_program_data
            or program_dict['type'] not in PROGRAM_TYPE_MAPPING.keys()
        ):
            continue
        for subprogram_dict in open_program_data[jpmorgan_program_id]:
            application_url = subprogram_dict['application_url'].split('?')[0]
            program = Program.objects.filter(company=company, application_url=application_url).first()
            if not program:
                program = Program(company=company, application_url=application_url)
            program.jpmorgan_program_id = jpmorgan_program_id
            program.url = f"https://careers.jpmorgan.com{program_dict['url']}"
            program.application_url = application_url
            program.title = program_dict['title']
            program.description = program_dict['description']
            program.program_type = program_dict['type']
            program.deadline = dateutil_parse(subprogram_dict['end_date']).date()
            program.category = assign_program_category(program.title)

            program.region_id = REGION_MAPPING.get(subprogram_dict['region'])
            if program.region_id is None:
                regions_not_found.append(program_dict['region'])

            program.is_application_open = (
                program.deadline >= datetime.today().date()
                if program.deadline
                else True
            )
            program.save()

            # Cities / Countries
            delete_program_cities_countries_association(program)

            for city in subprogram_dict['locations']:
                city = city.split(',')[0]
                mapped_city = map_city(city, extra_mapping_to_check=None)
                mapped_country = None
                if mapped_city is None:
                    mapped_country = map_country(city)
                    if mapped_country is None:
                        cities_not_found.append(city)
                    mapped_city = 'MULTIPLE'
                assign_program_cities_countries(program, mapped_city)
                if mapped_country:
                    assign_program_countries(program, mapped_country)

            program.cities = subprogram_dict['locations']

            program.extra_data = {
                k: program_dict[k]
                for k in [
                    'level', 'areas-of-interest', 'idealFor'
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
    set_programs_inactive_based_on_latest_scrape_flag(company_id=company.id)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        logger.error('JP Morgan Scraper Failed', exc_info=ex)
        message = f'JP Morgan Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
