import django

django.setup()

from datetime import datetime
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
    assign_program_countries,
    DEFAULT_REQUESTS_TIMEOUT,
    headers,
    get_clean_inner_html,
    map_country,
    send_slack_message_not_found,
    set_programs_inactive_based_on_latest_scrape_flag,
    set_programs_latest_scrape_flag,
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.HSBC)


@transaction.atomic
def scrape_new_programs():
    logger.info('Scraping Programs from HSBC...')
    countries_not_found = []
    url = 'https://www.hsbc.com/careers/students-and-graduates/find-a-programme'
    params = {'page': 0, 'take': 100}
    while True:
        params['page'] += 1
        logger.debug('Barclays: Page %s', params['page'])

        r = requests.get(url, params=params, timeout=DEFAULT_REQUESTS_TIMEOUT)
        doc = lxml.html.fromstring(r.content)
        doc.make_links_absolute(r.url)

        for tr in doc.xpath('//div[contains(@class, "table__container")]//tbody//tr'):
            program_url = tr.xpath('.//a[@aria-label="More information and apply"]')[0].get('href')
            program = Program.objects.filter(company=company, url=program_url).first()
            if program is None:
                program = Program(company=company, url=program_url)
            program.application_url = program_url
            tds = tr.xpath('./td')
            program.title = tds[0].text.strip()
            program.eligibility = tds[1].text.strip()
            program.extra_data = {
                'Business area': tds[3].text.strip(),
            }
            program.program_type = tds[4].text.strip()
            program.category = assign_program_category(program.title)

            program.is_application_open = True
            program.found_in_latest_scrape = True
            program.is_details_scraped = False

            program.save()

            country = tds[2].text
            if country:
                program.cities = [country]

                countries = map(lambda x: x.strip(), country.split(','))
                for country in countries:
                    mapped_country = map_country(country)
                    if mapped_country:
                        assign_program_countries(program, mapped_country)
                        program.region = program.countries_mapped.first().region
                    else:
                        countries_not_found.append(country)
                program.save()

        if len(doc.xpath('//a[contains(@class, "pagination__next")]')) == 0:
            break

    if countries_not_found:
        send_slack_message_not_found(company, countries_not_found, prefix='Countries')


def find_desc_tag(doc):
    div_tag = doc.xpath('//div[@id="content-0"]')
    if div_tag:
        return div_tag[0]

    p_tag = doc.xpath('//div[contains(@class, "article-sublayout__content")]/p[@class="stand-first"]')
    if p_tag:
        return p_tag[0]

    div_tag = doc.xpath('//div[contains(@class, "article-sublayout__content")]/div[@class="pageTitleAndText__lead"]')
    if div_tag:
        return div_tag[0]

    p_tag = doc.xpath('//div[contains(@class, "sublayout--content")]/p[@class="stand-first"]')
    if p_tag:
        return p_tag[0]

    return None


def scrape_details_single_program(program: Program):
    r = requests.get(program.url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content)

    desc_tag = find_desc_tag(doc)
    if desc_tag is not None:
        program.description = get_clean_inner_html(desc_tag)

    extra_data = {}
    extra_data_labels = [
        'For:', 'Duration:', 'Areas:', 'Start date:', 'Location:', 'Requirements:', 'Applications open:',
        'Applications close:', 'Start date:'
    ]
    for label in extra_data_labels:
        try:
            text_value = doc.xpath(f'//tr[./th[.="{label}"]]/td')[0].text
            if text_value:
                extra_data[label] = text_value.strip()
        except IndexError:
            pass
    program.extra_data.update(extra_data)

    if 'Applications close:' in extra_data:
        program.deadline_text = extra_data['Applications close:']
        program.deadline = dateutil_parse(program.deadline_text).date()
        program.is_application_open = program.deadline >= datetime.today().date()
    elif 'Applications for this programme are currently closed' in r.text:
        program.is_application_open = False
    program.is_details_scraped = True
    program.save()


def scrape_details_all_programs():
    logger.info('Scraping details from HSBC')
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
        logger.error('HSBC Failed', exc_info=exc)
        message = f'HSBC Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
