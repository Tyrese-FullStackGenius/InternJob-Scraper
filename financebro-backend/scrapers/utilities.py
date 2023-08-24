from enum import Enum
import typing as t

import django
django.setup()

from lxml import etree

from internships.models import City
from internships.models import Country
from internships.models import Program
from internships.models import ProgramCategoryChoices
from scrapers.city_country_mapping import CITY_MAPPING
from scrapers.city_country_mapping import COUNTRIES_MAPPING
from scrapers.slack_utilities import post_slack_message
from myLogger import logger


headers = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    )
}


DEFAULT_REQUESTS_TIMEOUT = 30


def get_or_create_country(country_name: str, region_code: t.Optional[str]) -> Country:
    country = Country.objects.filter(name=country_name).first()
    if country:
        return country
    country = Country.objects.create(name=country_name, region_id=region_code)
    return country


def get_or_create_city(city_mapping_code: str) -> t.Tuple[City, Country]:
    city_mapping_dict = CITY_MAPPING[city_mapping_code]
    country_name = city_mapping_dict.get('country')
    country = (
        get_or_create_country(country_name, city_mapping_dict.get('region'))
        if country_name
        else None
    )

    city = City.objects.filter(name=city_mapping_dict['name'], country=country).first()
    if city is None:
        city = City.objects.create(name=city_mapping_dict['name'], country=country)

    return city, country


def assign_program_cities_countries(program: Program, mapped_city: str) -> None:
    city, country = get_or_create_city(mapped_city)
    if city:
        program.cities_mapped.add(city)
    if country:
        program.countries_mapped.add(country)


def assign_program_countries(program: Program, mapped_country: str) -> None:
    country_mapping_dict = COUNTRIES_MAPPING[mapped_country]
    country = get_or_create_country(country_mapping_dict['country'], country_mapping_dict.get('region'))
    if country:
        program.countries_mapped.add(country)


def delete_program_cities_countries_association(program: Program) -> None:
    program.cities_mapped.clear()
    program.countries_mapped.clear()


def assign_program_category(title):
    title_lower = title.lower()
    if 'summer' in title_lower:
        return ProgramCategoryChoices.SUMMER
    elif 'off-cycle' in title_lower:
        return ProgramCategoryChoices.OFFCYCLE
    elif 'insight' in title_lower or 'spring' in title_lower:
        return ProgramCategoryChoices.INSIGHT
    else:
        return ProgramCategoryChoices.OTHER


def get_clean_inner_html(div_tag):
    for tag in div_tag.iter():
        tag.attrib.clear()
    return etree.tostring(div_tag).decode('utf-8')


def get_next_div_text_from_label(doc, label_name, return_html: bool = False) -> t.Optional[str]:
    try:
        div_tag = doc.xpath(f'//label[./span[.="{label_name}"]]/following-sibling::div')[0]
        if return_html:
            return get_clean_inner_html(div_tag)
        return div_tag.text_content().strip()
    except IndexError:
        return None


def set_programs_latest_scrape_flag(company_id: int, found_in_latest_scrape: bool):
    (
        Program.objects
        .filter(company_id=company_id)
        .update(found_in_latest_scrape=found_in_latest_scrape)
    )


def set_programs_inactive_based_on_latest_scrape_flag(company_id: int):
    (
        Program.objects
        .filter(
            company_id=company_id,
            found_in_latest_scrape=False
        )
        .update(is_application_open=False)
    )


class RegionsEnum(Enum):
    AMERICAS = 'AMERICAS'
    ASIA = 'ASIA'
    EMEA = 'EMEA'


def send_slack_message_not_found(company: str, items: t.List[str], prefix: str):
    if len(items) == 0:
        return
    try:
        items = sorted(list(set(items)))
        message = f'{prefix} not found for: {company}\n' + '\n'.join(items)
        post_slack_message(message)
    except Exception as exc:
        logger.error('Error in send_slack_message_cities_not_found - %s, %s', company, items, exc_info=exc)


def map_city(city: str, extra_mapping_to_check: t.Optional[dict]) -> t.Optional[str]:
    if extra_mapping_to_check and city.lower() in extra_mapping_to_check:
        return extra_mapping_to_check[city.lower()]
    if city in CITY_MAPPING.keys():
        return city
    if city.upper() in CITY_MAPPING.keys():
        return city.upper()
    return None


def map_country(country: str) -> t.Optional[str]:
    if country in COUNTRIES_MAPPING.keys():
        return country
    if country.upper() in COUNTRIES_MAPPING.keys():
        return country.upper()
    return None


def assign_program_city_country_region(
    program: Program,
    cities_countries_text: str,
    cities_not_found: list[str],
    countries_not_found: list[str]
):
    delete_program_cities_countries_association(program)

    program.cities = [cities_countries_text]

    cities_countries_list = list(map(lambda x: x.strip(), cities_countries_text.split(',')))

    city, country = (
        (cities_countries_list[0], cities_countries_list[-1])
        if len(cities_countries_list) > 1
        else (None, cities_countries_list[0])
    )

    if city:
        mapped_city = map_city(city, extra_mapping_to_check=None)
        if mapped_city is None:
            cities_not_found.append(cities_countries_text)
            mapped_city = 'MULTIPLE'

        city = mapped_city

        assign_program_cities_countries(program, mapped_city)


    if not country:
        country = CITY_MAPPING.get(city).get("country")

    if country is not None:
        mapped_country = map_country(country)
        if mapped_country:
            assign_program_countries(program, mapped_country)
            program.region = program.countries_mapped.first().region
        else:
            countries_not_found.append(country)

    program.save()


def assign_program_city_country_region_test(
    cities_countries_text: str
):
    cities_countries_list = list(map(lambda x: x.strip(), cities_countries_text.split(',')))

    print("cities_countries_list", cities_countries_list)

    city, country = (
        (cities_countries_list[0], cities_countries_list[-1])
        if len(cities_countries_list) > 1
        else (None, cities_countries_list[0])
    )

    print("city", city)
    print("country", country)

    if city:
        mapped_city = map_city(city, extra_mapping_to_check=None)
        if mapped_city is None:
            mapped_city = 'MULTIPLE'
        city = mapped_city
        print("mapped_city", mapped_city)

    if not country:
        country = CITY_MAPPING.get(city).get("country")
    print("country", country)
    if country:
        mapped_country = map_country(country)
    print("mapped_country", mapped_country)


if __name__ == '__main__':
    assign_program_city_country_region_test("London123,")
