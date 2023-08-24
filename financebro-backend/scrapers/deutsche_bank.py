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
    assign_program_cities_countries,
    assign_program_countries,
    DEFAULT_REQUESTS_TIMEOUT,
    delete_program_cities_countries_association,
    headers,
    get_clean_inner_html,
    map_city,
    map_country,
    send_slack_message_not_found,
    set_programs_inactive_based_on_latest_scrape_flag,
    set_programs_latest_scrape_flag,
)

from myLogger import logger


company = Company.objects.get(name=CompanyChoices.DEUTSCHE_BANK)

DEUTSCHE_BANK_CITIES_MAPPING = {
    'multiple cities': 'MULTIPLE',
    'deutschlandweit': 'MULTIPLE',
}

def assign_program_city_country_region(
    program: Program,
    city: str,
    country: str,
    cities_not_found: list[str],
    countries_not_found: list[str]
):
    delete_program_cities_countries_association(program)

    program.cities = [f'{city}, {country}']
    mapped_city = map_city(city, extra_mapping_to_check=DEUTSCHE_BANK_CITIES_MAPPING)
    if mapped_city is None:
        cities_not_found.append(city)
        mapped_city = 'MULTIPLE'
    assign_program_cities_countries(program, mapped_city)

    mapped_country = map_country(country)
    if mapped_country:
        assign_program_countries(program, mapped_country)
        program.region = program.countries_mapped.first().region
    else:
        countries_not_found.append(country)

    program.save()


@transaction.atomic
def scrape_new_programs():
    logger.info('Scraping Programs from Citibank...')
    cities_not_found = []
    countries_not_found = []

    base_url = 'https://api-deutschebank.beesite.de/graduatesearch/?data='
    data = {
        "LanguageCode":"EN",
        "SearchParameters": {
            "FirstItem": 1,
            "CountItem": 100,
            "MatchedObjectDescriptor": [
                "Facet:ProfessionCategory", "Facet:UserArea.ProDivision", "Facet:Profession",
                "Facet:PositionLocation.CountrySubDivision", "Facet:PositionOfferingType.Code",
                "Facet:PositionSchedule.Code", "Facet:PositionLocation.City", "Facet:PositionLocation.Country",
                "Facet:JobCategory.Code", "Facet:CareerLevel.Code", "Facet:PositionHiringYear",
                "Facet:PositionFormattedDescription.Content", "PositionID", "PositionTitle", "PositionURI",
                "ScoreThreshold", "OrganizationName", "PositionFormattedDescription.Content",
                "PositionLocation.CountryName", "PositionLocation.CountrySubDivisionName",
                "PositionLocation.CityName", "PositionLocation.Longitude", "PositionLocation.Latitude",
                "PositionIndustry.Name", "JobCategory.Name", "CareerLevel.Name", "PositionSchedule.Name",
                "PositionOfferingType.Name", "PublicationStartDate", "UserArea.GradEduInstCountry",
                "PositionImport" ,"PositionHiringYear" ,"PositionID"
            ],
            "Sort": [{"Criterion":"PublicationStartDate","Direction":"DESC"}]
        },
        "SearchCriteria": [None]
    }
    page_count = 0
    while True:
        page_count += 1
        logger.debug('Deutsche Bank: Page %s', page_count)

        url = f'{base_url}{json.dumps(data)}'
        r = requests.get(url, timeout=DEFAULT_REQUESTS_TIMEOUT).json()

        for record_dict in r['SearchResult']['SearchResultItems']:
            accepted_career_levels = {'Praktikum', 'Analyst Internship Programme'}
            program_career_levels = set([c['Name'] for c in record_dict['MatchedObjectDescriptor']['CareerLevel']])
            if not accepted_career_levels.intersection(program_career_levels):
                continue
            external_id = record_dict['MatchedObjectId']
            program = Program.objects.filter(company=company, external_id=external_id).first()
            if program is None:
                program = Program(company=company, external_id=external_id)

            matched_record_dict = record_dict['MatchedObjectDescriptor']

            program.url = matched_record_dict['PositionURI']
            program.title = matched_record_dict['PositionTitle']
            program.extra_data = {
                'Position Industry': [p['Name'] for p in matched_record_dict['PositionIndustry']],
                'Position Schedule': [p['Name'] for p in matched_record_dict['PositionSchedule']],
                'Job Category': [p['Name'] for p in matched_record_dict['JobCategory']],
            }

            program.program_type = 'INTERNSHIP'
            program.category = assign_program_category(program.title)
            program.is_application_open = True
            program.found_in_latest_scrape = True
            program.is_details_scraped = False

            program.save()

            assign_program_city_country_region(
                program,
                matched_record_dict['PositionLocation'][0]['CityName'],
                matched_record_dict['PositionLocation'][0]['CountryName'],
                cities_not_found,
                countries_not_found
            )

        if r['SearchResult']['SearchResultCount'] < data['SearchParameters']['CountItem']:
            break
        data['FirstItem'] += data['SearchParameters']['CountItem']

    if cities_not_found:
        send_slack_message_not_found(company, cities_not_found, prefix='Cities')
    if countries_not_found:
        send_slack_message_not_found(company, countries_not_found, prefix='Countries')


def scrape_details_single_program(program: Program):
    r = requests.get(program.url, headers=headers, timeout=DEFAULT_REQUESTS_TIMEOUT)
    doc = lxml.html.fromstring(r.content)
    doc.make_links_absolute(r.url)

    program.description = get_clean_inner_html(doc.xpath('//ul[@data-id="requisition-fields"]')[0])
    program.application_url = doc.xpath('//a[.="Apply"]')[0].get('href')
    program.is_details_scraped = True
    program.save()


def scrape_details_all_programs():
    logger.info('Scraping details from Deutsche Bank')
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
        logger.error('Deutsche Bank Scraper Failed', exc_info=exc)
        message = f'Deutsche Bank Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)
