import django
django.setup()

import traceback
import typing as t

import lxml.html
import requests

from internships.models import (
    Company,
    CompanyChoices,
    Program,
    ProgramCategoryChoices
)
from scrapers.slack_utilities import post_slack_message
from scrapers.utilities import (
    assign_program_category,
    assign_program_cities_countries,
    RegionsEnum,
    DEFAULT_REQUESTS_TIMEOUT,
    delete_program_cities_countries_association,
    get_next_div_text_from_label,
    headers,
    map_city,
    send_slack_message_not_found,
    set_programs_inactive_based_on_latest_scrape_flag,
    set_programs_latest_scrape_flag
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.BANK_OF_AMERICA)


REGION_MAPPING = {
    'Europe, Middle East & Africa': RegionsEnum.EMEA.name,
    'U.S. and Canada': RegionsEnum.AMERICAS.name,
    'Latin America': RegionsEnum.AMERICAS.name,
    'Asia Pacific': RegionsEnum.ASIA.name,
}

PROGRAM_TYPE_MAPPING = {
    'Off-cycle internship': 'INTERNSHIP',
    'Summer internship': 'INTERNSHIP'
}


def scrape_new_programs():
    logger.info('BankOfAmerica: Scraping New Programs...')
    url = (
        'https://bankcampuscareers.tal.net'
        '/vx/lang-en-GB/mobile-0/brand-4/xf-fbfaa673c065/candidate/jobboard/vacancy/1/adv/'
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
        td_ahref = tds[1].xpath('./a')[0]

        program_url = td_ahref.get('href')
        program.url = program_url
        program.application_url = program_url
        program.title = td_ahref.text.strip()

        program.is_application_open = True
        program.found_in_latest_scrape = True

        program.is_details_scraped = False

        program.save()


def scrape_details_single_program(
    program: Program,
    regions_not_found: t.List[str],
    cities_not_found: t.List[str]
):
    r = requests.get(program.url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content.decode('utf-8'))

    program.description = get_next_div_text_from_label(doc, 'Program description', return_html=True)
    program.eligibility = get_next_div_text_from_label(doc, 'Entry level')
    program_type = get_next_div_text_from_label(doc, 'Program type')
    program.program_type = PROGRAM_TYPE_MAPPING.get(program_type, program_type)

    program.extra_data = {}
    extra_data_labels = ['Program']
    for extra_data_label in extra_data_labels:
        extra_data_value = get_next_div_text_from_label(doc, extra_data_label)
        if extra_data_value:
            program.extra_data[extra_data_label] = extra_data_value

    program.save()

    # Cities / Countries
    delete_program_cities_countries_association(program=program)
    cities = get_next_div_text_from_label(doc, 'City ')
    cities = cities.split(',')
    cities = list(map(lambda x: x.strip(), cities))

    cities = list(filter(lambda x: len(x) > 2, cities))
    for city in cities:
        mapped_city = map_city(city, extra_mapping_to_check=None)
        if mapped_city is None:
            cities_not_found.append(city)
            mapped_city = 'MULTIPLE'
        assign_program_cities_countries(program, mapped_city)

    program.cities = cities

    boa_program_region_name = get_next_div_text_from_label(doc, 'Region')
    program.region_id = REGION_MAPPING.get(boa_program_region_name)
    if program.region_id is None:
        regions_not_found.append(boa_program_region_name)

    if 'off-cycle' in program.program_type.lower():
        program.category = ProgramCategoryChoices.OFFCYCLE
    elif 'summer' in program.program_type.lower():
        program.category = ProgramCategoryChoices.SUMMER
    else:
        program.category = assign_program_category(program.title)

    program.is_details_scraped = True
    program.save()


def scrape_details_all_programs():
    logger.info('BOA: Scraping details')
    unp_programs = Program.objects.filter(company=company, is_details_scraped=False)
    unp_programs_count = unp_programs.count()

    regions_not_found = []
    cities_not_found = []

    count = 0
    for program in unp_programs:
        count += 1
        logger.debug(f'{count}/{unp_programs_count}: {program.id}: {program.url}')
        scrape_details_single_program(program, regions_not_found, cities_not_found)

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
        logger.error('BOA Scraper Failed', exc_info=ex)
        message = f'BOA Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
