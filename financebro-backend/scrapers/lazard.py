import django
django.setup()

import traceback
import typing as t

from django.db import transaction
import lxml.html
import requests

from internships.models import (
    Company,
    CompanyChoices,
    Program
)
from internships.models import ProgramCategoryChoices
from scrapers.slack_utilities import post_slack_message
from scrapers.utilities import  (
    assign_program_category,
    assign_program_cities_countries,
    DEFAULT_REQUESTS_TIMEOUT,
    delete_program_cities_countries_association,
    get_next_div_text_from_label,
    RegionsEnum,
    headers,
    map_city,
    send_slack_message_not_found,
    set_programs_inactive_based_on_latest_scrape_flag,
    set_programs_latest_scrape_flag
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.LAZARD)

REGION_MAPPING = {
    'Americas': RegionsEnum.AMERICAS.name,
    'EMEA': RegionsEnum.EMEA.name,
    'APAC': RegionsEnum.ASIA.name,
}

PROGRAM_TYPE_MAPPING = {
    'Summer Internship': 'INTERNSHIP',
    'Off-cycle Internship': 'INTERNSHIP'
}


def find_regions_and_urls(regions_not_found: t.List[str]):
    logger.info('Lazard: Finding Regions & URLs')
    url = 'https://lazard-careers.tal.net/vx/lang-en-GB/appcentre-ext/brand-4/candidate/jobboard/vacancy/2/adv/'
    r = requests.get(url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content.decode('utf-8'))

    regions = []
    regions_lis = doc.xpath('//fieldset[@class="search-filter-group" and ./legend[.="Region"]]/ul/li')
    for li in regions_lis:
        region_name = li.xpath('.//span[@class="facet_label"]')[0].text.strip()
        if region_name not in REGION_MAPPING:
            regions_not_found.append(region_name)
        region_checkbox_input = li.xpath('./input[@type="checkbox"]')[0]
        region_url = f'{url}?{region_checkbox_input.get("name")}={region_checkbox_input.get("value")}'
        regions.append((region_name, region_url))
    return regions


def scrape_new_programs_single_region(region_name, region_url):
    logger.info(f'Lazard: Scraping New Programs for {region_name}')
    r = requests.get(region_url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content.decode('utf-8'))
    doc.make_links_absolute(r.url)

    for li in doc.xpath('//ul[@id="tile-results-list"]/li'):
        external_id = li.get('data-oppid')
        program = Program.objects.filter(company=company, external_id=external_id).first()
        if program is None:
            program = Program(company=company, external_id=external_id)

        subject_ahref = li.xpath('.//a[@class="subject"]')[0]
        program_url = subject_ahref.get('href')

        program.url = program_url
        program.application_url = program_url
        program.title = subject_ahref.text.strip()
        program.region_id = REGION_MAPPING[region_name]

        program.is_application_open = True
        program.found_in_latest_scrape = True

        program.is_details_scraped = (
            False
            if program.found_in_latest_scrape
            else True
        )

        program.save()


@transaction.atomic
def scrape_details_single_program(
    program: Program,
    cities_not_found: t.List[str]
):
    r = requests.get(program.url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content)
    program.description = get_next_div_text_from_label(doc, 'Description', return_html=True)
    program_type = get_next_div_text_from_label(doc, 'Program Type')
    program.program_type = PROGRAM_TYPE_MAPPING.get(program_type, program_type)

    program.extra_data = {}
    extra_data_labels = ['Business Unit']
    for extra_data_label in extra_data_labels:
        extra_data_value = get_next_div_text_from_label(doc, extra_data_label)
        if extra_data_value:
            program.extra_data[extra_data_label] = extra_data_value

    program.save()

    # Cities / Countries
    delete_program_cities_countries_association(program)

    cities = get_next_div_text_from_label(doc, 'Location').split(',')
    cities = list(map(lambda x: x.strip(), cities))

    for city in cities:
        mapped_city = map_city(city, extra_mapping_to_check=None)
        if mapped_city is None:
            cities_not_found.append(city)
            mapped_city = 'MULTIPLE'
        assign_program_cities_countries(program, mapped_city)

    program.cities = cities

    program.cities = [get_next_div_text_from_label(doc, 'Location')]
    program.is_details_scraped = True

    if 'off-cycle' in program_type.lower():
        program.category = ProgramCategoryChoices.OFFCYCLE
    else:
        program.category = assign_program_category(program.title)

    program.save()


def scrape_details_all_programs(cities_not_found: t.List[str]):
    logger.info('Lazard: Scraping details')
    unp_programs = Program.objects.filter(company=company, is_details_scraped=False)
    unp_programs_count = unp_programs.count()

    count = 0
    for program in unp_programs:
        count += 1
        logger.debug(f'{count}/{unp_programs_count}: {program.id}: {program.url}')
        scrape_details_single_program(program, cities_not_found)


def main():
    set_programs_latest_scrape_flag(company_id=company.id, found_in_latest_scrape=False)

    cities_not_found = []
    regions_not_found = []

    regions = find_regions_and_urls(regions_not_found)
    for region_name, region_url in regions:
        scrape_new_programs_single_region(region_name, region_url)

    scrape_details_all_programs(cities_not_found)

    if cities_not_found:
        send_slack_message_not_found(company, cities_not_found, prefix='Cities')
    if regions_not_found:
        send_slack_message_not_found(company, regions_not_found, prefix='Regions')
    set_programs_inactive_based_on_latest_scrape_flag(company_id=company.id)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        logger.error('Lazard Scraper Failed', exc_info=ex)
        message = f'Lazard Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
