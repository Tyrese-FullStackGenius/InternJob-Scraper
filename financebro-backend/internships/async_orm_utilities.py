from asgiref.sync import sync_to_async
from copy import deepcopy
from datetime import timedelta
import typing as t

from django.utils import timezone

from internships.models import (
    Company,
    CompanyCategoryChoices,
    Country,
    Program,
    ProgramCategoryChoices,
    Region,
    UserProgram,
    UserEmailNotificationPreferences,
    UserProgramNotes,
    UserProgramPreferences
)


def list_company_categories():
    return [
        {
            'value': companycategorychoice[0],
            'viewValue': companycategorychoice[1]
        }
        for companycategorychoice in CompanyCategoryChoices.choices
    ]


def list_program_categories():
    return [
        {
            'value': programcategorychoice[0],
            'viewValue': programcategorychoice[1]
        }
        for programcategorychoice in ProgramCategoryChoices.choices
    ]


async def list_regions():
    return [
        {
            'value': region.code,
            'viewValue': region.name
        }
        async for region in Region.objects.all()
    ]


async def list_companies(is_paid_user):
    if is_paid_user:
        companies_queryset = Company.objects.all()
    else:
        companies_queryset = Company.objects.filter(name__in=get_company_names_for_free_users())
    return [
        {
            'value': company.id,
            'viewValue': company.name
        }
        async for company in companies_queryset
    ]


async def list_countries():
    return [
        {
            'value': country.name,
            'viewValue': country.name
        }
        async for country in Country.objects.all()
    ]


def get_company_names_for_free_users() -> t.List[str]:
    return ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan', 'Evercore', 'Lazard']



async def get_all_available_filters(
    user,
    company=True,
    company_category=True,
    program_category=True,
    region=True,
    is_application_open=True,
    does_ask_for_cover_letter=True,
    country=True,
    is_visa_sponsorship_provided=True
):
    filters = {}
    is_paid_user = await user.plan == "PAID"
    if company:
        filters['company'] = await list_companies(is_paid_user)
    if company_category:
        filters['company_category'] = list_company_categories()
    if program_category:
        filters['program_category'] = list_program_categories()
    if region:
        filters['region'] = await list_regions()
    if country:
        filters['country'] = await list_countries()
    if is_application_open:
        filters['is_application_open'] = [
            {'value': True, 'viewValue': 'Yes'},
            {'value': False, 'viewValue': 'No'},
        ]
    if is_visa_sponsorship_provided:
        filters['is_visa_sponsorship_provided'] = [
            {'value': True, 'viewValue': 'Yes'},
            {'value': False, 'viewValue': 'No'},
        ]
    if does_ask_for_cover_letter:
        filters['does_ask_for_cover_letter'] = [
            {'value': True, 'viewValue': 'Yes'},
            {'value': False, 'viewValue': 'No'},
            {'value': 'NA', 'viewValue': 'Not Enough Data'}
        ]
    return {'filters': filters}


async def get_all_programs(
    user: t.Optional = None,
    force_check_for_paid_user: bool = True,
    company_id: int = None,
    company_category: str = None,
    program_category: str = None,
    region: str = None,
    is_application_open: bool = None,
    is_visa_sponsorship_provided: bool = None,
    does_ask_for_cover_letter: str = None,
    countries: t.Optional[t.List[str]] = None,
    most_recent_posts_since: t.Optional[timedelta] = None,
    search_term: t.Optional[str] = None
):
    filters = {}
    programs = (
        Program.objects
        .select_related('company', 'region')
        .prefetch_related('cities_mapped', 'countries_mapped')
    )

    if company_id:
        programs = programs.filter(company_id=company_id)
        filters['company_id'] = company_id

    if company_category:
        programs = programs.filter(company__category=company_category)
        filters['company_category'] = company_category

    if program_category:
        programs = programs.filter(category=program_category.upper())
        filters['program_category'] = program_category.upper()

    if region:
        programs = programs.filter(region_id=region.upper())
        filters['region'] = region.upper()

    if countries:
        programs = programs.filter(countries_mapped__in=countries)
        filters['countries'] = countries

    if is_application_open is not None:
        programs = programs.get_programs_with_applications_open(
            is_application_open=is_application_open
        )
        filters['is_application_open'] = is_application_open

    if is_visa_sponsorship_provided is not None:
        programs = programs.filter(is_visa_sponsorship_provided=is_visa_sponsorship_provided)
        filters['is_visa_sponsorship_provided'] = is_visa_sponsorship_provided

    if does_ask_for_cover_letter is not None:
        if does_ask_for_cover_letter.upper() in ['TRUE', 'FALSE']:
            programs = programs.does_ask_for_cover_letter(
                does_ask_for_cover_letter.upper() == 'TRUE'
            )
            filters['does_ask_for_cover_letter'] = does_ask_for_cover_letter
        elif does_ask_for_cover_letter.upper() == 'NA':
            programs = programs.does_ask_for_cover_letter_not_enough_data()
            filters['does_ask_for_cover_letter'] = does_ask_for_cover_letter

    if most_recent_posts_since is not None:
        programs = programs.filter(created_date__gte=timezone.now()-most_recent_posts_since)

    if search_term is not None and search_term.strip() != '':
        programs = programs.filter(search_vector_column=search_term.strip())
        filters['search_term'] = search_term


    total = await programs.acount()

    if force_check_for_paid_user and await user.plan != 'PAID':
        programs = programs.filter(company__name__in=get_company_names_for_free_users())

    return {
        'total': total,
        'programs': [program async for program in programs],
        'applied_filters': filters
    }


def find_current_stage_user_program(userprogram: UserProgram) -> str:
    if userprogram.is_application_closed:
        return 'Closed'
    if userprogram.is_personal_interview_taken:
        return 'Personal Interview Done'
    if userprogram.is_pre_recorded_video_interview_taken:
        return 'Pre-recorded Video Interview Done'
    if userprogram.is_online_test_taken:
        return 'Online Test Done'
    if userprogram.is_application_submitted:
        return 'Submitted'
    return 'Not Submitted'


@sync_to_async
def get_all_user_programs(user):
    userprograms = (
        UserProgram
        .objects
        .filter(user=user, is_favorite=True)
        .select_related('program__company', 'program__region')
        .prefetch_related('program__cities_mapped', 'program__countries_mapped')
    )
    total = userprograms.count()
    for userprogram in userprograms:
        userprogram.current_stage = find_current_stage_user_program(userprogram)
    return {
        'total': total,
        'programs': list(userprograms),
        'applied_filters': {}
    }


@sync_to_async
def toggle_program_as_favorite(user, program_id: int, set_favorite: bool):
    if not Program.objects.filter(id=program_id).exists():
        return 404

    userprogram = UserProgram.objects.filter(user=user, program_id=program_id).first()
    if not userprogram:
        userprogram = UserProgram.objects.create(user=user, program_id=program_id)
    userprogram.is_favorite = set_favorite
    userprogram.save()
    return 200


@sync_to_async
def get_user_favorite_programs_ids(user):
    return list(
        UserProgram.objects
        .filter(
            user=user,
            is_favorite=True
        )
        .values_list('program_id', flat=True)
    )


@sync_to_async
def save_user_program_preferences(
    user,
    regions: t.List[str],
    company_categories: t.List[str],
    program_categories: t.List[str]
):
    user_program_preferences = UserProgramPreferences.objects.filter(user=user).first()
    if not user_program_preferences:
        user_program_preferences = UserProgramPreferences.objects.create(user=user)
    user_program_preferences.regions = regions
    user_program_preferences.company_categories = company_categories
    user_program_preferences.program_categories = program_categories
    user_program_preferences.save()


@sync_to_async
def retrieve_user_program_preferences(user):
    user_program_preferences = UserProgramPreferences.objects.filter(user=user).first()
    if not user_program_preferences:
        user_program_preferences = UserProgramPreferences.objects.create(user=user)
    return user_program_preferences


@sync_to_async
def retrieve_user_email_preferences(user):
    user_email_preferences = UserEmailNotificationPreferences.objects.filter(user=user).first()
    if not user_email_preferences:
        user_email_preferences = UserEmailNotificationPreferences.objects.create(user=user)
    return user_email_preferences


@sync_to_async
def save_user_email_preferences(
    user,
    email_notifications_enabled: bool,
    regions: t.List[str],
    company_categories: t.List[str],
    program_categories: t.List[str],
    near_deadline_notifications_enabled: bool,
    emails_per_day_count: t.Optional[int] = None
):
    user_email_preferences = UserEmailNotificationPreferences.objects.filter(user=user).first()
    if not user_email_preferences:
        user_email_preferences = UserEmailNotificationPreferences.objects.create(user=user)
    user_email_preferences.email_notifications_enabled = email_notifications_enabled
    user_email_preferences.regions = regions
    user_email_preferences.company_categories = company_categories
    user_email_preferences.program_categories = program_categories
    if emails_per_day_count:
        user_email_preferences.emails_per_day_count = emails_per_day_count
    user_email_preferences.near_deadline_notifications_enabled = near_deadline_notifications_enabled
    user_email_preferences.save()


@sync_to_async
def retrieve_single_user_program(user, program_id: int, retrieve_notes: bool):
    userprogram_query = (
        UserProgram.objects
        .filter(user=user, program_id=program_id)
        .select_related('program__company', 'program__region')
        .prefetch_related('program__cities_mapped', 'program__countries_mapped')

    )
    if retrieve_notes:
        userprogram_query = userprogram_query.prefetch_related('notes')
    userprogram = userprogram_query.first()
    if userprogram is None:
        return 404, None
    return 200, userprogram


def community_reported_count_helper_set(data, userprogram, field_name):
    if userprogram[field_name] is None:
        data[field_name]['unreported'] += 1
    elif userprogram[field_name] is True:
        data[field_name]['reported_true'] += 1
    elif userprogram[field_name] is False:
        data[field_name]['reported_false'] += 1


def community_reported_listfield_helper_set(data, userprogram, field_name):
    if userprogram[field_name] is not None:
        data[field_name].append(userprogram[field_name].strip())


@sync_to_async
def retrieve_program_community_reported_data(program_id: int):
    userprograms = list(
        map(
            lambda x: x.__dict__,
            UserProgram.objects.filter(program_id=program_id)
        )
    )

    reported_count_dict = {'reported_true': 0, 'reported_false': 0, 'unreported': 0}

    data = {
        'does_ask_for_cover_letter': deepcopy(reported_count_dict),
        'was_there_no_online_test': deepcopy(reported_count_dict),
        'online_test_questions': [],
        'was_there_no_pre_recorded_video_interview_stage': deepcopy(reported_count_dict),
        'pre_recorded_video_interview_format': [],
        'personal_interview_questions': []
    }

    for userprogram in userprograms:
        community_reported_count_helper_set(data, userprogram, 'does_ask_for_cover_letter')
        community_reported_count_helper_set(data, userprogram, 'was_there_no_online_test')
        community_reported_count_helper_set(data, userprogram, 'was_there_no_pre_recorded_video_interview_stage')

        community_reported_listfield_helper_set(data, userprogram, 'online_test_questions')
        community_reported_listfield_helper_set(data, userprogram, 'pre_recorded_video_interview_format')
        community_reported_listfield_helper_set(data, userprogram, 'personal_interview_questions')

    return {
        'program_id': program_id,
        'community_reported_data': data
    }


@sync_to_async
def perform_userprogram_pipeline_action(
    user,
    program_id: int,
    action: str,
    value: bool,
    optional_info: t.Optional[dict[str, t.Union[bool, str]]]
):
    if not Program.objects.filter(id=program_id).exists():
        return 404

    userprogram = UserProgram.objects.filter(user=user, program_id=program_id).first()
    if not userprogram:
        userprogram = UserProgram.objects.create(user=user, program_id=program_id)

    action_attr_mapping = {
        'submitted': 'is_application_submitted',
        'online_test': 'is_online_test_taken',
        'pre_recorded_video_interview': 'is_pre_recorded_video_interview_taken',
        'personal_interview': 'is_personal_interview_taken',
        'close': 'is_application_closed'
    }

    setattr(userprogram, action_attr_mapping[action], value)
    setattr(userprogram, f'{action_attr_mapping[action]}_datetime', timezone.now())
    if optional_info:
        for k, v in optional_info.items():
            setattr(userprogram, k, v)

    userprogram.save()
    return 200


@sync_to_async
def create_user_program_note(user, program_id: int, note: str):
    userprogram = UserProgram.objects.filter(user=user, program_id=program_id).first()
    if not userprogram:
        return 404
    UserProgramNotes.objects.create(userprogram_id=userprogram.id, note=note)
    return 200


async def retrieve_dashboard_stats(user):
    data = {
        'total_open_opportunities': await Program.objects.filter(is_application_open=True).acount(),
        'summer_internships_count': await Program.objects.filter(is_application_open=True, category='SUMMER').acount(),
        'offcycle_internships_count': await Program.objects.filter(is_application_open=True, category='OFFCYCLE').acount(),
        'spring_internships_count': await Program.objects.filter(is_application_open=True, category='INSIGHT').acount(),
        'recent_programs': await get_all_programs(
            user, force_check_for_paid_user=False, most_recent_posts_since=timedelta(days=7)
        )
    }
    return data


async def retrieve_company_stats():
    data = []
    async for company in Company.objects.all():
        data.append({
            'name': company.name,
            'total_programs_count': await company.program_set.acount(),
            'open_programs_count': (
                await
                Program.objects
                .filter(company_id=company.id)
                .get_programs_with_applications_open(is_application_open=True)
                .acount()
            )
        })

    return data
