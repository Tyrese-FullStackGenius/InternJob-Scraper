import django
django.setup()

import traceback

from dateutil.parser import parse as dateutil_parse
from django.db import transaction
import lxml.html
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
    set_programs_latest_scrape_flag,
    set_programs_inactive_based_on_latest_scrape_flag
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.GOLDMAN_SACHS)

REGION_MAPPING = {
    'AMERICAS': RegionsEnum.AMERICAS.name,
    'ASIA': RegionsEnum.ASIA.name,
    'EMEA': RegionsEnum.EMEA.name,
    'INDIA': RegionsEnum.ASIA.name
}

PROGRAM_TYPE_MAPPING = {
    'an internship': 'INTERNSHIP'
}


GOLDMAN_SACHS_CITIES_MAPPING = {
    'please reference the application for available locations': 'MULTIPLE',
    'all americas locations': 'MULTIPLE',
    'hybrid': 'MULTIPLE',
}


@transaction.atomic
def scrape_new_programs():
    logger.info('Scraping Programs from Goldman Sachs...')
    url = 'https://www.goldmansachs.com/careers/students/programs/programs-list.json'
    r = requests.get(url, timeout=DEFAULT_REQUESTS_TIMEOUT).json()

    internship_node_id = 151025

    cities_not_found = []
    regions_not_found = []

    for program_dict in r['programs']:
        if program_dict['programType'][0]['nodeId'] != internship_node_id:
            continue

        program_url = f'https://www.goldmansachs.com{program_dict["url"]}'
        program = Program.objects.filter(company=company, url=program_url).first()
        if program is None:
            program = Program(company=company, url=program_url)

        program.title = program_dict['title'].replace('\r', '').replace('\n', '').strip()
        program.eligibility = program_dict['eligibility'].replace('\r', '').replace('\n', '').strip()
        program.program_type = PROGRAM_TYPE_MAPPING[program_dict['programType'][0]['name'].strip('.')]
        program.program_type_description = program_dict['programTypeDescription'].strip()
        program.is_application_open = program_dict['applicationAvailability']
        program.region_id = REGION_MAPPING.get(program_dict['region']['geoTag'].strip().upper())
        if program.region_id is None:
            regions_not_found.append(program_dict['region']['geoTag'].strip().upper())
        program.category = assign_program_category(program.title)

        program.save()

        # Cities / Countries
        delete_program_cities_countries_association(program)

        for city in program_dict['cities']:
            mapped_city = map_city(city, extra_mapping_to_check=GOLDMAN_SACHS_CITIES_MAPPING)
            if mapped_city is None:
                cities_not_found.append(city)
                mapped_city = 'MULTIPLE'
            assign_program_cities_countries(program, mapped_city)
        program.cities = program_dict['cities']

        program.found_in_latest_scrape = (
            program_dict['applicationAvailability']
            if program_dict['applicationAvailability'] is not None
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


def scrape_details_single_program(program: Program):
    r = requests.get(program.url, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content)

    deadline_ps = doc.xpath('//h6[.="Application Deadline"]/following-sibling::p')
    if len(deadline_ps) > 0:
        deadline = deadline_ps[0].text.strip()
        try:
            program.deadline = dateutil_parse(deadline)
        except Exception:
            pass
        program.deadline_text = '\n'.join([p.text.strip() for p in deadline_ps])
    program.description = doc.xpath('//div[contains(@class, "summer-body__content")]')[0].text_content().strip()
    try:
        program.application_url = doc.xpath('//div[@class="featured-modules__button"]/a[.="Apply Now"]')[0].get('href')
    except IndexError:
        pass
    program.is_details_scraped = True
    program.save()


def scrape_details_all_programs():
    logger.info('Scraping details from Goldman Sachs')
    unp_programs = Program.objects.filter(company=company, is_details_scraped=False)
    unp_programs_count = unp_programs.count()

    count = 0
    for program in unp_programs:
        count += 1
        logger.debug(f'{count}/{unp_programs_count}: {program.id}: {program.url}')
        scrape_details_single_program(program)


def main():
    set_programs_latest_scrape_flag(company_id=company.id, found_in_latest_scrape=False)
    scrape_new_programs()
    scrape_details_all_programs()
    set_programs_inactive_based_on_latest_scrape_flag(company_id=company.id)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.error('Goldman Sachs Scraper Failed', exc_info=exc)
        message = f'Goldman Sachs Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
