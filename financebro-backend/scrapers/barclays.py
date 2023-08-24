import django

django.setup()

import traceback
from urllib.parse import urlencode

from django.db import transaction
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
    assign_program_city_country_region,
    DEFAULT_REQUESTS_TIMEOUT,
    headers,
    get_clean_inner_html,
    send_slack_message_not_found,
    set_programs_inactive_based_on_latest_scrape_flag,
    set_programs_latest_scrape_flag,
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.BARCLAYS)

PROGRAM_CATEGORY_MAPPING = {
    'Summer Internship': ProgramCategoryChoices.SUMMER,
    'Off-Cycle Internship': ProgramCategoryChoices.OFFCYCLE
}


@transaction.atomic
def scrape_new_programs():
    logger.info('Scraping Programs from Barclays...')
    cities_not_found = []
    countries_not_found = []
    url = 'https://search.jobs.barclays/search-jobs/results'
    params = {
        'CurrentPage': 0,
        'RecordsPerPage': 100,
        'IsPagination': 'True',
        'CustomFacetName': '',
        'FacetTerm': '',
        'FacetType': 0,
        'FacetFilters[0].ID': 'Off-Cycle+Internship',
        'FacetFilters[0].FacetType': 5,
        'FacetFilters[0].Count': 6,
        'FacetFilters[0].Display': 'Off-Cycle+Internship',
        'FacetFilters[0].IsApplied': 'true',
        'FacetFilters[0].FieldName': 'job_type',
        'FacetFilters[1].ID': 'Summer+Internship', 
        'FacetFilters[1].FacetType': 5,
        'FacetFilters[1].Count': 15,
        'FacetFilters[1].Display': 'Summer+Internship',
        'FacetFilters[1].IsApplied': 'true',
        'FacetFilters[1].FieldName': 'job_type',
        'SearchResultsModuleName': 'Refresh+-+Search+Results',
        'SearchFiltersModuleName': 'Refresh+-+Search+Filter',
        'SortCriteria': 0,
        'SortDirection': 0,
        'SearchType': 5,
        'ResultsType': 0
    }
    while True:
        params['CurrentPage'] += 1
        logger.debug('Barclays: Page %s', params['CurrentPage'])
        r = requests.get(url, params=urlencode(params, safe='+'), timeout=DEFAULT_REQUESTS_TIMEOUT).json()
        doc = lxml.html.fromstring(r['results'])
        doc.make_links_absolute('https://search.jobs.barclays/')

        programs_lis = doc.xpath('//ul[contains(@class, "search-results--list")]/li[contains(@class, "list-item")]')
        for li in programs_lis:
            program_ahref = li.xpath('./a')[0]
            external_id = program_ahref.get('data-job-id')
            program = Program.objects.filter(company=company, external_id=external_id).first()
            if program is None:
                program = Program(company=company, external_id=external_id)
            program.url = program_ahref.get('href')
            program.title = program_ahref.xpath('.//span[contains(@class, "job-jobtitle")]')[0].text.strip()
            program.is_application_open = True
            program.found_in_latest_scrape = True
            program.is_details_scraped = False

            program.save()

            # Cities / Countries / Regions
            cities_countries_text = program_ahref.xpath('.//span[contains(@class, "job-location")]')[0].text.strip()
            assign_program_city_country_region(
                program=program,
                cities_countries_text=cities_countries_text,
                cities_not_found=cities_not_found,
                countries_not_found=countries_not_found
            )

        if len(programs_lis) < params['RecordsPerPage']:
            break

    if cities_not_found:
        send_slack_message_not_found(company, cities_not_found, prefix='Cities')
    if countries_not_found:
        send_slack_message_not_found(company, countries_not_found, prefix='Countries')


def scrape_details_single_program(program: Program):
    r = requests.get(program.url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content)

    program.application_url = doc.xpath('//a[contains(@class, "job-apply")]')[0].get('href')
    program.description = get_clean_inner_html(doc.xpath('//div[contains(@class, "ats-description")]')[0])

    extra_data = {}
    contract = None
    extra_info_p_tags = doc.xpath('//section[contains(@class, "job-description")]//p[contains(@class, "job-info")]')
    for extra_info_p in extra_info_p_tags:
        span_tags = extra_info_p.xpath('./span')
        label = span_tags[0].text_content().strip()
        value = span_tags[1].text_content().strip()
        extra_data[label] = value
        if 'Contract' in label:
            contract = value
    program.extra_data = extra_data
    if contract:
        program.category = PROGRAM_CATEGORY_MAPPING[contract]
        program.program_type = PROGRAM_CATEGORY_MAPPING[contract]

    program.is_details_scraped = True
    program.save()


def scrape_details_all_programs():
    logger.info('Scraping details from Barclays')
    unp_programs = Program.objects.filter(company=company, is_details_scraped=False)
    unp_programs_count = unp_programs.count()

    count = 0
    read_timeout_failed_count = 0
    for program in unp_programs:
        count += 1
        logger.debug(f'{count}/{unp_programs_count}: {program.id}: {program.url}')
        try:
            scrape_details_single_program(program)
        except requests.exceptions.ReadTimeout:
            read_timeout_failed_count += 1

    if read_timeout_failed_count > 0:
        post_slack_message(f'Barclays Scraper: Read Timeout Failed Count: {read_timeout_failed_count}')


def main():
    set_programs_latest_scrape_flag(company_id=company.id, found_in_latest_scrape=False)
    scrape_new_programs()
    scrape_details_all_programs()
    set_programs_inactive_based_on_latest_scrape_flag(company_id=company.id)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.error('Barclays Scraper Failed', exc_info=exc)
        message = f'Barclays Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
