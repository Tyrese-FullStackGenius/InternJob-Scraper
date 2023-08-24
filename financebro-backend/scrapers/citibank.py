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
    Program
)
from scrapers.slack_utilities import post_slack_message
from scrapers.utilities import (
    assign_program_category,
    assign_program_city_country_region,
    DEFAULT_REQUESTS_TIMEOUT,
    headers,
    get_clean_inner_html,
    send_slack_message_not_found,
    set_programs_inactive_based_on_latest_scrape_flag,
    set_programs_latest_scrape_flag,
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.CITIBANK)


@transaction.atomic
def scrape_new_programs():
    logger.info('Scraping Programs from Citibank...')
    cities_not_found = []
    countries_not_found = []
    url = 'https://jobs.citi.com/search-jobs/results'

    params = {
        'ActiveFacetID': 'Internship',
        'CurrentPage': 0,
        'RecordsPerPage': 100,
        'CustomFacetName': '',
        'FacetTerm': '',
        'FacetType': 0,
        'FacetFilters[0].ID': 'University+Programs',
        'FacetFilters[0].FacetType': 5,
        'FacetFilters[0].Display': 'University+Programs',
        'FacetFilters[0].IsApplied': 'true',
        'FacetFilters[0].FieldName': 'custom_fields.ECAMPUS',
        'FacetFilters[1].ID': 'Internship',
        'FacetFilters[1].FacetType': 5,
        'FacetFilters[1].Display': 'Internship',
        'FacetFilters[1].IsApplied': 'true',
        'FacetFilters[1].FieldName': 'job_level',
        'SearchResultsModuleName': 'Search+Results',
        'SearchFiltersModuleName': 'Search+Filters',
        'SortCriteria': 0,
        'SortDirection': 0,
        'SearchType': 6,
        'ResultsType': 0
    }

    while True:
        params['CurrentPage'] += 1
        logger.debug('Citibank: Page %s', params['CurrentPage'])
        r = requests.get(url, params=urlencode(params, safe='+'), timeout=DEFAULT_REQUESTS_TIMEOUT).json()
        doc = lxml.html.fromstring(r['results'])
        doc.make_links_absolute('https://jobs.citi.com/')

        programs_lis = doc.xpath('//section[@id="search-results-list"]/ul/li')
        for li in programs_lis:
            program_ahref = li.xpath('./a')[0]
            external_id = program_ahref.get('data-job-id')
            program = Program.objects.filter(company=company, external_id=external_id).first()
            if program is None:
                program = Program(company=company, external_id=external_id)
            program.url = program_ahref.get('href')
            program.title = program_ahref.xpath('./h2')[0].text.strip()
            program.category = assign_program_category(program.title)

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
    program.extra_data = {
        'Job Category': doc.xpath('//span[@class="job-info__item" and ./b[.="Job Category"]]/text()')[0].strip()
    }
    program.is_details_scraped = True
    program.save()


def scrape_details_all_programs():
    logger.info('Scraping details from Citibank')
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
        post_slack_message(f'Citibank Scraper: Read Timeout Failed Count: {read_timeout_failed_count}')


def main():
    set_programs_latest_scrape_flag(company_id=company.id, found_in_latest_scrape=False)
    scrape_new_programs()
    scrape_details_all_programs()
    set_programs_inactive_based_on_latest_scrape_flag(company_id=company.id)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.error('Citibank Scraper Failed', exc_info=exc)
        message = f'Citibank Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
