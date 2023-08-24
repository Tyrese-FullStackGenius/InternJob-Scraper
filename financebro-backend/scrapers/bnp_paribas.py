import django

django.setup()

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


company = Company.objects.get(name=CompanyChoices.BNP_PARIBAS)


@transaction.atomic
def scrape_new_programs():
    logger.info('Scraping Programs from BNP Paribas...')
    cities_not_found = []
    countries_not_found = []
    url = 'https://group.bnpparibas/en/careers/all-job-offers'
    params = {
        'json': 1,
        'form[hint]': '',
        'form[q]': '',
        'form[type][]]': 28,
        'form[coordinates]': '',
        'page': 0
    }
    s = requests.session()
    s.headers.update(headers)
    s.headers.update({'x-requested-with': 'XMLHttpRequest'})
    while True:
        params['page'] += 1
        logger.debug('BNP Paribas: Page %s', params['page'])
        r = s.get(url, headers=headers, params=params, timeout=DEFAULT_REQUESTS_TIMEOUT).json()

        doc = lxml.html.fromstring(r['html'])
        doc.make_links_absolute('https://group.bnpparibas')

        for article_tag in doc.xpath('.//article'):
            program_url = article_tag.xpath('./a')[0].get('href')
            program = Program.objects.filter(company=company, url=program_url).first()
            if program is None:
                program = Program(company=company, url=program_url)
            program.title = article_tag.xpath('.//h3[@class="title-4"]')[0].text.strip()
            program.program_type = 'INTERNSHIP'
            program.is_application_open = True
            program.found_in_latest_scrape = True
            program.is_details_scraped = False
            program.category = assign_program_category(program.title)

            program.save()

            # Cities / Countries / Regions
            cities_countries_text = article_tag.xpath('.//div[@class="offer-location"]')[0].text_content().strip()
            assign_program_city_country_region(program, cities_countries_text, cities_not_found, countries_not_found)

        if 'No more job offers' in r['pagination']:
            break

    if cities_not_found:
        send_slack_message_not_found(company, cities_not_found, prefix='Cities')
    if countries_not_found:
        send_slack_message_not_found(company, countries_not_found, prefix='Countries')


def scrape_details_single_program(program: Program):
    r = requests.get(program.url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    if r.url.endswith('#unavailable'):
        program.is_details_scraped = True
        program.is_application_open = True
        program.save()
        return

    doc = lxml.html.fromstring(r.content)
    program.application_url = doc.xpath('//div[contains(@class, "offer-apply apply")]/a')[0].get('href')

    description_div_tag = doc.xpath('//div[@class="description"]')[0]
    program.description = get_clean_inner_html(description_div_tag)
    try:
        program.eligibility = (
            doc.xpath('//div[@class="title-cat" and .="Level of experience"]/following-sibling::a')[0].text.strip()
        )
    except IndexError:
        pass

    program.extra_data = {}

    try:
        program.extra_data['Brand'] = (
            doc.xpath('//div[@class="title-cat" and .="Brand"]/following-sibling::a/img')[0].get('alt')
        )
    except IndexError:
        pass

    try:
        program.extra_data['Schedule'] = (
            doc.xpath('//div[@class="title-cat" and .="Schedule"]/following-sibling::span')[0].text.strip()
        )
    except IndexError:
        pass

    try:
        program.extra_data['Study level'] = (
            doc.xpath('//div[@class="title-cat" and .="Study level"]/following-sibling::a')[0].text.strip()
        )
    except IndexError:
        pass

    try:
        program.extra_data['Job Function'] = (
            doc.xpath('//div[@class="title-cat" and .="Job Function"]/following-sibling::a')[0].text.strip()
        )
    except IndexError:
        pass

    program.is_details_scraped = True
    program.save()


def scrape_details_all_programs():
    logger.info('Scraping details from BNP Paribas')
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
        logger.error('BNP Paribas Scraper Failed', exc_info=exc)
        message = f'BNP Paribas Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
