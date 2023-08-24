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

django.setup()


def main():
    jobs = []

    url = "https://careers.marshmclennan.com/global/en/oliver-wyman-early-careers-search"
    response = requests.request("GET", url).content.decode(
        encoding='CP1252', errors='ignore')
    jobData = response.split('"eagerLoadRefineSearch":')[
        1].split(',"jobCartV2":{')[0]
    jobData = json.loads(jobData)
    jobs = jobData['data']['jobs']

    jobNum = jobData['totalHits']
    pageNum = int(jobNum / 10) + 1
    for i in range(1, pageNum):
        url = f"https://careers.marshmclennan.com/global/en/oliver-wyman-early-careers-search?from={i * 10}&s=1&rk=l-oliver-wyman-campus-search"
        jobData = response.split('"eagerLoadRefineSearch":')[
            1].split(',"jobCartV2":{')[0]
        jobData = json.loads(jobData)
        jobs = jobs + jobData['data']['jobs']

    company = Company.objects.get(name=CompanyChoices.MARSHMCLENNAN)

    for i in jobs:
        external_id = i['jobId']
        program = Program.objects.filter(
            company=company,
            external_id=external_id
        ).first()
        if program is None:
            program = Program(company=company, external_id=external_id)

        program.url = i['applyUrl']
        program.application_url = i['applyUrl']
        program.title = i['title']
        program.description = i['descriptionTeaser']
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
    "country": "Worldwide",
    "city": "Worldwide",
    "ml_skills": [
            "Applications",
            "Engineering",
            "Science",
        "Humanities",
        "Law"
    ],
    "latitude": "40.0421401",
    "industry": "",
    "locale": "en_US",
    "multi_location": ["Worldwide, Worldwide"],
    "title": "Consulting - Internship",
    "multi_location_array": [
        {
                "country": "Worldwide",
                "cityState": "Worldwide",
                "city": "Worldwide",
                "latlong": {"lon": -76.3888087, "lat": 40.0421401},
                "latitude": "40.0421401",
                "location": "Worldwide, Worldwide",
                "state": "",
                "cityCountry": "Worldwide, Worldwide",
                "cityStateCountry": "Worldwide, Worldwide",
                "mapQueryLocation": "Worldwide, Worldwide",
                "stateCountry": "Worldwide",
                "longitude": "-76.3888087"
        }
    ],
    "jobSeqNo": "BCG1US10013667EXTERNALENUS",
    "postedDate": "2019-01-01T00:00:00.000Z",
    "descriptionTeaser": "We accept online applications from exceptional business school, engineering, science, law, and humanities students who are nearing completion of their undergraduate or graduate studies. You\u2019ll collaborate...",
    "dateCreated": "2020-11-17T12:11:06.473+0000",
    "state": "",
    "keywordClicks": 5121,
    "locationClicks": 16768,
    "longitude": "-76.3888087",
    "siteType": "external",
    "categoryClicks": 6323,
    "landingPageClicks": 15449,
    "isMultiCategory": true,
    "totalClicks": 62696,
    "multi_category": ["Consulting", "Technology & Engineering"],
    "reqId": "10013667",
    "jobId": "10013667",
    "badge": "",
    "jobVisibility": ["external"],
    "isMultiLocation": true,
    "applyUrl": "https://talent.bcg.com/en_US/apply/Login?folderIdAuto=10020333&folderId1=10013667",
    "multi_category_array": [
        {"category": "Consulting"},
        {"category": "Technology & Engineering"}
    ],
    "location": "",
    "category": "Consulting",
    "ml_job_parser": {
        "descriptionTeaser": "We accept online applications from exceptional business school, engineering, science, law, and humanities students who are nearing completion of their undergraduate or graduate studies. You\u2019ll collaborate...",
        "descriptionTeaser_keyword": "Who We Are. Boston Consulting Group partners with leaders in business and society to tackle their most important challenges and capture their greatest opportunities. BCG was the pioneer in business strategy...",
        "descriptionTeaser_ats": "",
        "descriptionTeaser_first200": "Who We Are. Boston Consulting Group partners with leaders in business and society to tackle their most important challenges and capture their greatest opportunities. BCG was the pioneer in business strategy..."
    },
    "externalApply": true,
    "totalSearchClicks": 62696
}
"""
