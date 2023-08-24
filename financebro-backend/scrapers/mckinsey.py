from internships.models import (
    Company,
    CompanyChoices,
    Program
)
from myLogger import logger
from scrapers.slack_utilities import post_slack_message
from lxml import etree
import traceback
import requests
import json
import django

django.setup()


def convert_html_to_text(html_string):
    root = etree.HTML(html_string)
    text = root.xpath("string()")
    return text.strip()


def main():
    tmp = requests.get(
        'https://mckapi.mckinsey.com/api/jobsearch?q=Intern&lang=en'
    ).content.decode(encoding='CP1252', errors='ignore')
    numFound = json.loads(tmp)['numFound']

    res = requests.get(
        f'https://mckapi.mckinsey.com/api/jobsearch?pageSize={numFound}&q=Intern&lang=en'
    ).content.decode(encoding='CP1252', errors='ignore')
    res = json.loads(res)['docs']

    company = Company.objects.get(name=CompanyChoices.MCKINSEY)

    for i in res:
        external_id = i['jobID']
        program = Program.objects.filter(
            company=company,
            external_id=external_id
        ).first()
        if program is None:
            program = Program(company=company, external_id=external_id)

        program.url = i['jobApplyURL']
        program.application_url = i['jobApplyURL']
        program.title = i['title']
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
        program.description = convert_html_to_text(
            i['JobDescription'])
        program.eligibility = i['jobSkillGroup'][0]
        program.program_type = i['jobSkillCode'][0]
        program.program_type_description = i['jobSkillCode'][0]
        program.cities = {'cities': i['cities']}
        program.save()

    print(f'Successfully find {len(res)} jobs')


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
    "jobID": "51626",
    "title": "Intern - Digital Technology",
    "showOnTop": false,
    "recordTypeName": ["Job"],
    "jobSkillGroup": ["CSS Pre-Associate Short Term"],
    "jobSkillCode": ["INT - Intern"],
    "interest": "Consulting",
    "interestCategory": "Serve Clients",
    "cities": ["Geneva", "Zurich"],
    "countries": ["Switzerland", "Switzerland"],
    "continents": ["Europe", "Europe"],
    "functions": ["Technology"],
    "industries": ["High Tech"],
    "whoYouWillWorkWith": "<div>You'll work in our Zurich or Geneva office as a full-time intern for 12 weeks. You'll be a part of a client project team, collaborating with colleagues and our clients to solve their toughest business problems. You'll work on 2-3 consulting projects at the intersection of business and technology.&nbsp;</div><div></div><div>When you join McKinsey as an intern, you are joining a firm that will challenge you and invest in your professional development. You will work on the best teams to help the best organizations in the world - in private, public and social sectors - solve their most difficult problems. You will also work with many experts, from data scientists and researchers to software and app designers.</div>",
    "whatYouWillDo": "<div><div>You’ll work in teams of typically 3-5 consultants, playing an active role in all aspects of the client engagement.&nbsp;&nbsp;</div><div></div><div>This includes gathering and analyzing information, formulating and testing hypotheses, and developing and communicating recommendations. You’ll also have the opportunity to present results to client management and implement recommendations in collaboration with client team members.</div><div></div><div>You’ll gain new skills and build on the strengths you bring to the firm. Interns receive exceptional training as well as frequent coaching and mentoring from colleagues on their teams. This support includes a partner from the Swiss office assigned to you to help guide your career as well as formal training in your first few weeks as an intern.</div><div></div><div>Successful interns may be given a full-time return offer.</div></div>",
    "yourBackground": "<ul><li>Bachelors degree (as of 4th semester) or Master’s degree in progress in a technology-related study field with outstanding record of academic achievement&nbsp;</li><li>Previous internship(s), ideally in an area with exposure to technological topics (software engineering, cloud computing, digital transformation, cyber security etc.)</li><li>Strong interest to explore the breadth of technology related topics</li><li>Ability to work collaboratively in a team environment</li><li>Exceptional analytical and quantitative problem-solving skills</li><li>Skills to communicate complex ideas effectively</li><li>Willingness to travel</li><li>Fluency in German (for Zurich) or French (for Geneva) and in English</li><li><strong>To apply,&nbsp;</strong><strong>please hand in:</strong><span>&nbsp;CV, copies of academic transcripts (from high school onward), and letters of reference/certificates from past employment, if any.</span></li><li><strong>Next application deadlines for internships in Switzerland</strong><span>:&nbsp; May 31, 2023 for an internship in fall/winter 2023 and November 30, 2023 for an internship in spring/summer 2024. Full details&nbsp;</span><a href=\"https://www.mckinsey.com/ch/careers-in-switzerland\" target=\"_blank\" rel=\"noreferrer noopener\">here.</a></li></ul><div><br></div>",
    "postToLinkedIn": "No",
    "jobApplyURL": "https://mckinsey.avature.net/careers/ApplicationMethods?folderId=51626",
    "Post_to_GE": "No",
    "friendlyURL": "intern-digitaltechnology-51626"
}
"""
