import django

django.setup()

import json
import traceback

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


company = Company.objects.get(name=CompanyChoices.SOCIETE_GENERALE)


def get_authorization_token():
    url = 'https://careers.societegenerale.com/search-proxy.php'
    headers2 = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'authorization-api': '',
        'x-proxy-url': 'https://sso.sgmarkets.com/sgconnect/oauth2/access_token'
    }
    body = "grant_type=client_credentials&scope=api.corpsrc-00257.v1"

    r = requests.post(url, headers=headers2, data=body, timeout=DEFAULT_REQUESTS_TIMEOUT).json()
    return r['access_token']


@transaction.atomic
def scrape_new_programs():
    logger.info('Scraping Programs from Societe Generale...')
    url = 'https://careers.societegenerale.com/search-proxy.php'
    headers2 = {
        'content-type': 'application/json',
        'x-proxy-url': (
            'https://api.socgen.com/business-support/it-for-it-support'
            '/cognitive-service-knowledge/api/v1/search-profile'
        ),
        'authorization-api': f'Bearer {get_authorization_token()}',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    body = {
        "profile": "ces_profile_sgcareers",
        "query": {
            "advanced": [
                {"type": "simple", "name": "sourcestr6", "op": "eq", "value": "job"},
                {"type": "multi", "name": "sourcestr8", "op": "eq", "values": ["INTERNSHIP"]}
            ],
            "skipCount": 100,
            "skipFrom": 0
        },
        "lang": "en",
        "responseType": "SearchResult"
    }

    cities_not_found = []
    countries_not_found = []
    page_count = 0
    while True:
        body['query']['skipFrom'] = page_count * 100
        page_count += 1
        logger.debug('Societe Generale: Page %s', page_count)
        r = requests.post(url, headers=headers2, data=json.dumps(body), timeout=DEFAULT_REQUESTS_TIMEOUT).json()

        for record_dict in r['Result']['Docs']:
            program_url = record_dict['resulturl']
            program = Program.objects.filter(company=company, url=program_url).first()
            if program is None:
                program = Program(company=company, url=program_url)
            program.title = record_dict['title']
            program.program_type = 'INTERNSHIP'
            program.is_application_open = True
            program.found_in_latest_scrape = True
            program.is_details_scraped = False
            program.category = assign_program_category(program.title)

            program.save()

            # Cities / Countries / Regiona
            assign_program_city_country_region(
                program=program,
                cities_countries_text=record_dict['sourcestr7'],
                cities_not_found=cities_not_found,
                countries_not_found=countries_not_found
            )

        if r['PageCount'] == r['CurrentPage']:
            break

    if cities_not_found:
        send_slack_message_not_found(company, cities_not_found, prefix='Cities')
    if countries_not_found:
        send_slack_message_not_found(company, countries_not_found, prefix='Countries')


def scrape_details_single_program(program: Program):
    r = requests.get(program.url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    if r.status_code == 410:
        program.is_application_open = False
        program.is_details_scraped = True
        program.save()
        return

    doc = lxml.html.fromstring(r.content)

    program.application_url = doc.xpath('//a[contains(@class, "btnApply")]')[0].get('href')
    description_div_tag = doc.xpath('//div[contains(@class, "joboffer-description")]')[0]
    program.description = get_clean_inner_html(description_div_tag)
    program.is_details_scraped = True
    program.save()


def scrape_details_all_programs():
    logger.info('Scraping details from Societe Generale')
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
        logger.error('Societe Generale Scraper Failed', exc_info=exc)
        message = f'Societe Generale Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
