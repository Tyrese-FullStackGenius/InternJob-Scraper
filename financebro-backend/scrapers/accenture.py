from internships.models import (
    Company,
    CompanyChoices,
    Program
)
from myLogger import logger
from scrapers.slack_utilities import post_slack_message
import traceback
import django
import requests
import json
from lxml import etree

django.setup()


def convert_html_to_text(html_string):
    root = etree.HTML(html_string)
    text = root.xpath("string()")
    return text.strip()


def main():
    URL = "https://www.accenture.com/sg-en/careers/jobsearch?jk=internship&sb=0&vw=1&is_rj=0&pg=1"
    params = URL.split("?")[1].split("&")
    paramdata = {}
    paramdata['startIndex'] = int(params[4].split("=")[1])-1
    paramdata['maxResultSize'] = 15
    paramdata['jobKeyword'] = params[0].split("=")[1]
    paramdata['jobLanguage'] = 'en'
    paramdata['countrySite'] = 'sg-en'
    paramdata['sortBy'] = params[1].split("=")[1]
    paramdata['aggregations'] = '[{"fieldName":"location"},{"fieldName":"postedDate"},{"fieldName":"jobTypeDescription"},{"fieldName":"workforceEntity"},{"fieldName":"businessArea"},{"fieldName":"skill"},{"fieldName":"travelPercentage"},{"fieldName":"yearsOfExperience"},{"fieldName":"specialization"}]'
    paramdata['jobCountry'] = 'Singapore,Vietnam'
    paramdata['componentId'] = 'careerjobsearchresults-001'
    paramdata['jobFilters'] = '[]'

    resp = requests.post(
        'https://www.accenture.com/api/accenture/jobsearch/result', data=paramdata)
    jobs = json.loads(resp.text)['data']

    company = Company.objects.get(name=CompanyChoices.ACCENTURE)

    for i in jobs:
        external_id = i['jobId']
        program = Program.objects.filter(
            company=company,
            external_id=external_id
        ).first()
        if program is None:
            program = Program(company=company, external_id=external_id)

        program.url = i['jobDetailUrl']
        program.application_url = i['jobDetailUrl']
        program.title = i['title']
        program.description = convert_html_to_text(i['jobDescription'])
        program.is_application_open = True
        program.found_in_latest_scrape = (
            program.is_application_open
            if program.is_application_open is not None
            else True
        )
        program.is_details_scraped = (
            False
            if program.found_in_latest_scrape
            else True
        )
        program.cities = {'cities': i['jobCityState']}
        program.save()

    print(f'Successfully find {len(jobs)} jobs')


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        logger.error('BOA Scraper Failed', exc_info=ex)
        message = f'BOA Scraper Failed.\n{traceback.format_exc()}'
        post_slack_message(message)

"""
Sample data
{
    'title': 'Accenture Internship Program - Consulting (Aug to Dec 2023)',
    'jobCityState': ['Singapore'],
    'jobId': 'R00152094_en',
    'postedDate': 1680739200000,
    'skill': 'Consulting',
    'requisitionId': 'R00152094',
    'jobCardData': {
        'careerjobsearchresults-001-item0': {
            'analytics-module-name': 'jobCard-0',
            'analytics-engagement': 'false',
            'xdm:linkURL': 'https://www.accenture.com/sg-en/careers/jobdetails?id=R00152094_en&title=Accenture+Internship+Program+-+Consulting+(Aug+to+Dec+2023)',
            'analytics-link-type': 'engagement',
            'analytics-link-name': 'accenture internship program - consulting (aug to dec 2023)'
        }
    },
    'jobCardSaveId': 'careerjobsearchresults-001-item0-save-button',
    'jobCardSaveData': {
        'careerjobsearchresults-001-item0-save-button': {
            'analytics-link-name': '<saved-name-placeholder>'
        }
    },
    'postedDateText': 'Posted more than 1 month ago',
    'jobCardId': 'careerjobsearchresults-001-item0',
    'savedJobInformationId': '',
    'jobDetailUrl': 'https://www.accenture.com/sg-en/careers/jobdetails?id=R00152094_en&title=Accenture+Internship+Program+-+Consulting+(Aug+to+Dec+2023)',
    'internalReferUrl': 'https://accenture.wd3.myworkdayjobs.com/AccentureCareers/job/Singapore/Accenture-Summer-Internship-Program---Consulting--Aug-to-Dec-2023-_R00152094/apply',
    'jobLanguageCd': 'en',
    'jobDescription': '<p><b>About Accenture</b></p><p></p><p><span>Accenture is a global professional services company with leading capabilities in digital, cloud and security. Combining unmatched experience and specialized skills across more than 40 industries, we offer Strategy and Consulting, Technology and Operations services and Accenture Song�all powered by the world�s largest network of Advanced Technology and Intelligent Operations centers. Our 721,000</span><span> </span><span>people deliver on the promise of technology and human ingenuity every day, serving clients in more than 120 countries. We embrace the power of change to create value and shared success for our clients, people, shareholders, partners and communities. Visit us at </span><a href="http://www.accenture.com" target="_blank"><span>www.accenture.com</span></a><span>. </span></p><p></p><p>This is your opportunity to begin your professional journey with Accenture. Our internship program will provide you with everything you need to shape the start of your career by learning new skills and getting insights into the work you could be doing when you graduate.</p><p></p><p><b>Your role</b></p><p>Your internship experience with Accenture Consulting will provide you an opportunity to bring innovation, intelligence and industry experience together with the newest technologies to help clients innovate at scale and transform their businesses.</p><p></p><p>As an intern, you will have the opportunity to experience life at Accenture, expand your professional network and build transferrable skills that you will be able to apply anywhere.</p><p></p><p>� You will be assigned to real-life projects and responsibilities<br />� Gain experience and exposure to emerging technologies<br />� Be part of a fast-paced and dynamic team</p><p></p><p>Your role assignment will be based on business needs, your personal strengths, and it may be in any of the following industries:</p><p></p><p>� Communications, Media and Technology<br />� Financial Services<br />� Health and Public Service<br />� Resources<br />� Products\xa0</p>',
    'jobRemoteType': '',
    'regionDescription': '',
    'careerLevelCd': 'Analyst',
    'country': 'Singapore',
    'workforceEntity': '',
    'yearsOfExperience': '2-5',
    'businessArea': 'Strategy & Consulting',
    'jobLinkData': {
        'analytics-link-name': 'Accenture Internship Program - Consulting (Aug to Dec 2023)',
        'xdm:linkURL': 'https://www.accenture.com/sg-en/careers/jobdetails?id=R00152094_en&title=Accenture+Internship+Program+-+Consulting+(Aug+to+Dec+2023)',
        'analytics-engagement': 'false',
        'analytics-link-type': 'serp-job-actionable'
    },
    'IsSavedJob': False
}
"""
