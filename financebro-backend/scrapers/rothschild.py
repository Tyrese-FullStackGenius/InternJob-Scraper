import django

django.setup()

from datetime import datetime
import traceback
import typing as t

from dateutil.parser import parse as dateutil_parse
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
    assign_program_countries,
    DEFAULT_REQUESTS_TIMEOUT,
    headers,
    get_next_div_text_from_label,
    map_country,
    send_slack_message_not_found,
    set_programs_inactive_based_on_latest_scrape_flag,
    set_programs_latest_scrape_flag,
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.ROTHSCHILD)


PROGRAM_TYPE_MAPPING = {
    'Summer Internship': 'INTERNSHIP',
    'Long Term Internship': 'INTERNSHIP'
}


def scrape_new_programs():
    logger.info('Rothschild: Scraping New Programs...')
    url = (
        'https://rothschildandco.tal.net/vx/lang-en-GB/mobile-0/appcentre-ext/brand-4/candidate/jobboard/vacancy/2/adv/'
    )
    r = requests.get(url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content.decode('utf-8'))
    doc.make_links_absolute(r.url)

    for div in doc.xpath('//ul[@id="tile-results-list"]/li/div'):
        external_id = div.get('data-oppid')
        program = Program.objects.filter(company=company, external_id=external_id).first()
        if program is None:
            program = Program(company=company, external_id=external_id)

        title_ahref = div.xpath('.//a[@class="subject"]')[0]
        program.url = title_ahref.get('href')
        program.application_url = title_ahref.get('href')
        program.title = title_ahref.text.strip()

        deadline = div.xpath('.//span[.="Application Deadline:"]/following-sibling::text()')[0].strip()
        program.deadline_text = deadline
        program.deadline = dateutil_parse(deadline).date()

        program.is_application_open = program.deadline >= datetime.today().date()
        program.found_in_latest_scrape = True
        program.is_details_scraped = False
        program.save()


def scrape_details_single_program(
    program: Program,
    countries_not_found: t.List[str]
):
    r = requests.get(program.url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content.decode('utf-8'))

    program.description = get_next_div_text_from_label(doc, 'Programme Description', return_html=True)

    country = get_next_div_text_from_label(doc, 'Country')
    program.cities = [country]
    mapped_country = map_country(country)
    if mapped_country:
        assign_program_countries(program, mapped_country)
        program.region = program.countries_mapped.first().region
    else:
        countries_not_found.append(country)

    program_type = get_next_div_text_from_label(doc, 'Programme')
    program.program_type = PROGRAM_TYPE_MAPPING.get(program_type, program_type)

    if 'off-cycle' in program_type.lower():
        program.category = ProgramCategoryChoices.OFFCYCLE
    elif 'summer' in program_type.lower():
        program.category = ProgramCategoryChoices.SUMMER
    else:
        program.category = assign_program_category(program.title)

    program.extra_data = {'Division': get_next_div_text_from_label(doc, 'Division')}
    program.is_details_scraped = True
    program.save()


def scrape_details_all_programs():
    logger.info('Rothschild: Scraping details')
    unp_programs = Program.objects.filter(company=company, is_details_scraped=False)
    unp_programs_count = unp_programs.count()

    countries_not_found = []

    count = 0
    for program in unp_programs:
        count += 1
        logger.debug(f'{count}/{unp_programs_count}: {program.id}: {program.url}')
        scrape_details_single_program(program, countries_not_found)

    if countries_not_found:
        send_slack_message_not_found(company, countries_not_found, prefix='Cities')


def main():
    set_programs_latest_scrape_flag(company_id=company.id, found_in_latest_scrape=False)
    scrape_new_programs()
    scrape_details_all_programs()
    set_programs_inactive_based_on_latest_scrape_flag(company_id=company.id)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.error('Rothschild Scraper Failed', exc_info=exc)
        message = f'Rothschild Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
