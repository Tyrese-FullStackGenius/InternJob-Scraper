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
        'https://www.bain.com/en/api/jobsearch/keyword/get?start=0&results=10&filters=employmenttype(E10)|&searchValue='
    ).content.decode(encoding='CP1252', errors='ignore')
    numFound = json.loads(tmp)['totalResults']

    res = requests.get(
        f'https://www.bain.com/en/api/jobsearch/keyword/get?start=0&results={numFound}&filters=employmenttype(E10)|&searchValue='
    ).content.decode(encoding='CP1252', errors='ignore')
    res = json.loads(res)['results']

    company = Company.objects.get(name=CompanyChoices.BAIN)

    for i in res:
        external_id = i['jobID']
        program = Program.objects.filter(
            company=company,
            external_id=external_id
        ).first()
        if program is None:
            program = Program(company=company, external_id=external_id)

        program.url = 'https://www.bain.com/careers/find-a-role/position/?jobid=' + \
            i['jobID']
        program.application_url = 'https://www.bain.com/careers/find-a-role/position/?jobid=' + \
            i['jobID']
        program.title = i['JobTitle']
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
        program.eligibility = i['Categories'][0]
        program.program_type = i['EmployeeType']
        program.program_type_description = i['EmployeeType']
        program.cities = {'cities': i['Location']}
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
    "JobId": "10329",
    "JobTitle": "Associate Consultant Intern",
    "JobDescription": "<p id=\"isPasted\"><strong><span>WHO YOU’LL WORK WITH:</span></strong></p><p><span>Our summer internship program for bachelor's and master's degree candidates provides broad exposure to the consulting industry and teaches business strategy through full-time immersion on a Bain case team. See application for full list of global locations.</span></p><p><span>As an Associate Consultant Intern (ACI), you'll begin with a week of intensive training to learn core consulting skills. You’ll work alongside Bain knowledge experts tackling complex business challenges and use your skills to help drive change in a range of organizations from global leaders to start-ups. You’ll also have the opportunity to secure a full-time offer to join Bain as an Associate Consultant upon completion of your studies.</span></p><p><span><strong>WHAT YOU’LL DO:</strong></span></p><ul><li>After training, you'll be assigned to an active case. Here's a sample of what you can expect to experience and accomplish:</li><li>Work on a case team with three to five other consultants, taking charge of a distinct aspect of the project</li><li>Interview clients' customers, competitors, suppliers and employers—work that will become the basis of the case team's strategic recommendations</li><li>Own and identify information sources, gather and interpret data, and execute analysis to translate into meaningful insights</li><li>Present your findings to case team members and client stakeholders</li></ul><p><span><strong>ABOUT YOU:</strong></span></p><p><span>To apply, you'll need to submit the following items, plus any additional requirements for the main office you wish to join:</span></p><ul><li>Resume/CV (Word doc or PDF files only)</li><li>Educational background information</li><li>Work experience</li><li>Relevant test scores</li><li>Strong academic background and analytical skills, high motivation levels, and outstanding interpersonal skills</li><li>All majors welcome</li><li>Must be a 3rd year on track to graduate by June 2025</li></ul><p><span><strong>COMPENSATION FOR US APPLICANTS</strong></span></p><p><span>Compensation for this role in the United States includes a monthly base salary of $9,000 and Bain’s best in class benefits package (details listed below).</span></p><p><span>Bain &amp; Company's comprehensive U.S. benefits and wellness program is designed to help employees achieve personal independence, protection and stability in the areas most important to you and your family. Bain pays 100% individual employee premiums for medical, dental and vision programs, offering one of the most comprehensive medical plans for employees without impacting your paycheck.</span></p><p><span><strong>WHAT MAKES US A GREAT PLACE TO WORK</strong></span></p><p><span>We are proud to be consistently recognized as one of the world's best places to work, a champion of diversity and a model of social responsibility. We are currently ranked the #1 consulting firm on Glassdoor’s Best Places to Work list, and we have maintained a spot in the top four on Glassdoor's list for the last 13 years. We believe that diversity, inclusion and collaboration is key to building extraordinary teams. We hire people with exceptional talents, abilities and potential, then create an environment where you can become the best version of yourself and thrive both professionally and personally. We are publicly recognized by external parties such as Fortune, Vault, Mogul, Working Mother, Glassdoor and the Human Rights Campaign for being a great place to work for diversity and inclusion, women, LGBTQ and parents.&nbsp;</span></p>",
    "Link": "https://careers.bain.com/recruits",
    "Location": [
        "Amsterdam ",
        " Athens ",
        " Atlanta ",
        " Austin ",
        " Bangkok ",
        " Beijing ",
        " Bengaluru ",
        " Berlin ",
        " Bogota ",
        " Boston ",
        " Brussels ",
        " Buenos Aires ",
        " Chicago ",
        " Copenhagen ",
        " Dallas ",
        " Denver ",
        " Doha ",
        " Dubai ",
        " Dusseldorf ",
        " Frankfurt ",
        " Helsinki ",
        " Hong Kong ",
        " Houston ",
        " Istanbul ",
        " Jakarta ",
        " Kuala Lumpur ",
        " Lagos ",
        " Lisbon ",
        " Los Angeles ",
        " Madrid ",
        " Manila ",
        " Mexico City ",
        " Milan ",
        " Monterrey ",
        " Mumbai ",
        " Munich ",
        " New Delhi ",
        " New York ",
        " Oslo ",
        " Paris ",
        " Rio de Janeiro ",
        " Riyadh ",
        " Rome ",
        " San Francisco ",
        " Santiago ",
        " São Paulo ",
        " Seattle ",
        " Shanghai ",
        " Silicon Valley ",
        " Singapore ",
        " Stockholm ",
        " Tokyo ",
        " Toronto ",
        " Vienna ",
        " Warsaw ",
        " Washington, DC ",
        " Zurich"
    ],
    "Categories": ["Management Consulting"],
    "EmployeeType": "Intern (Full-Time)"
}
"""
