import django
django.setup()

from datetime import datetime
import traceback
import typing as t

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
    get_next_div_text_from_label,
    headers,
    map_city,
    RegionsEnum,
    send_slack_message_not_found,
    set_programs_inactive_based_on_latest_scrape_flag,
    set_programs_latest_scrape_flag
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.EVERCORE)


REGION_MAPPING = {
    'Americas': RegionsEnum.AMERICAS.name,
    'EMEA': RegionsEnum.EMEA.name
}

PROGRAM_TYPE_MAPPING = {
    'Summer internship': 'INTERNSHIP'
}


def scrape_new_programs():
    logger.info('Evercore: Scraping New Programs...')
    url = (
        'https://evercore.tal.net'
        '/vx/lang-en-GB/mobile-0/appcentre-ext/brand-6/xf-61abc8ce0d6f/candidate/jobboard/vacancy/2/adv/'
    )
    r = requests.get(url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content.decode('utf-8'))
    doc.make_links_absolute(r.url)

    for tr in doc.xpath('//table[@class="table solr_search_list"]/tbody/tr'):
        external_id = tr.get('data-oppid')
        program = Program.objects.filter(company=company, external_id=external_id).first()
        if program is None:
            program = Program(company=company, external_id=external_id)

        tds = tr.xpath('./td')
        td_ahref = tds[0].xpath('./a')[0]
        program_url = td_ahref.get('href')

        program.url = program_url
        program.application_url = program_url
        program.title = td_ahref.text.strip()
        program.deadline_text = tds[1].text.strip()
        program.deadline = dateutil_parse(tds[1].text.strip()).date()
        program.is_application_open = program.deadline >= datetime.today().date()

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


@transaction.atomic
def scrape_details_single_program(
    program: Program,
    cities_not_found: t.List[str],
    regions_not_found: t.List[str],
):
    r = requests.get(program.url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content, parser=lxml.html.HTMLParser(remove_comments=True))

    program.description = get_next_div_text_from_label(doc, 'Job description', return_html=True)

    program_type = get_next_div_text_from_label(doc, 'Program type')
    program.program_type = PROGRAM_TYPE_MAPPING.get(program_type, program_type)

    program.extra_data = {}
    extra_data_labels = ['Group', 'Level']
    for extra_data_label in extra_data_labels:
        extra_data_value = get_next_div_text_from_label(doc, extra_data_label)
        if extra_data_value:
            program.extra_data[extra_data_label] = extra_data_value

    program.save()

    # Cities / Countries
    delete_program_cities_countries_association(program)
    city = get_next_div_text_from_label(doc, 'Location')

    mapped_city = map_city(city, extra_mapping_to_check=None)
    if mapped_city is None:
        cities_not_found.append(city)
        mapped_city = 'MULTIPLE'
    assign_program_cities_countries(program, mapped_city)

    program.cities = [city]

    evercore_program_region_name = get_next_div_text_from_label(doc, 'Region')
    program.region_id = REGION_MAPPING.get(evercore_program_region_name)
    if program.region_id is None:
        regions_not_found.append(evercore_program_region_name)

    program.is_details_scraped = True
    program.category = assign_program_category(program.title)
    program.save()


def scrape_details_all_programs():
    logger.info('Evercore: Scraping details')
    unp_programs = Program.objects.filter(company=company, is_details_scraped=False)
    unp_programs_count = unp_programs.count()

    cities_not_found = []
    regions_not_found = []
    count = 0
    for program in unp_programs:
        count += 1
        logger.debug(f'{count}/{unp_programs_count}: {program.id}: {program.url}')
        scrape_details_single_program(program, cities_not_found, regions_not_found)

    if cities_not_found:
        send_slack_message_not_found(company, cities_not_found, prefix='Cities')
    if regions_not_found:
        send_slack_message_not_found(company, regions_not_found, prefix='Regions')


def main():
    set_programs_latest_scrape_flag(company_id=company.id, found_in_latest_scrape=False)
    scrape_new_programs()
    scrape_details_all_programs()
    set_programs_inactive_based_on_latest_scrape_flag(company_id=company.id)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        logger.error('Evercore Scraper Failed', exc_info=ex)
        message = f'Evercore Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
