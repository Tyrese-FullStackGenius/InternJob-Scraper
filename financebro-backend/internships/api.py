import typing as t

from ninja import Query
from ninja import Router

from customauth.utilities import (
    await_auth,
    paid_member_required
)
from internships.async_orm_utilities import (
    create_user_program_note,
    get_all_available_filters,
    get_all_programs,
    get_all_user_programs,
    get_user_favorite_programs_ids,
    perform_userprogram_pipeline_action,
    retrieve_company_stats,
    retrieve_dashboard_stats,
    retrieve_program_community_reported_data,
    retrieve_single_user_program,
    retrieve_user_email_preferences,
    retrieve_user_program_preferences,
    save_user_email_preferences,
    save_user_program_preferences,
    toggle_program_as_favorite
)
from internships.schemas import (
    AvailableFiltersSchema,
    SingleCompanyStatsSchema,
    DashboardStatsSchema,
    ProgramCommunityReportedDataOutSchema,
    ProgramsFiltersSchema,
    ProgramsOutSchema,
    ToggleProgramFavoriteInSchema,
    UserEmailPreferencesSchema,
    UserProgramDetailOutWithNotesAndDescriptionSchema,
    UserProgramNoteInSchema,
    UserProgramPipelineActionInSchema,
    UserProgramPreferencesSchema,
    UserProgramOutSchema
)
from myLogger import logger


router = Router()


@router.get(
    '/programs',
    response={200: ProgramsOutSchema}
)
@await_auth
async def get_programs(
    request,
    filters: ProgramsFiltersSchema = Query(...)
):
    result = await get_all_programs(
        user=request.user,
        **filters.dict()
    )
    result['favorite_programs'] = await get_user_favorite_programs_ids(user=request.user)
    return result


@router.get(
    '/user-programs',
    response={200: UserProgramOutSchema}
)
@await_auth
@paid_member_required
async def get_user_programs(request):
    result = await get_all_user_programs(user=request.user)
    return result


@router.get('/available-filters', response={200: AvailableFiltersSchema})
@await_auth
async def available_filters(request):
    return await get_all_available_filters(user=request.user)


@router.post(
    '/toggle-program-favorite',
    response={
        200: list[int],
        404: None,
        500: None
    }
)
@await_auth
@paid_member_required
async def toggle_program_favorite(
    request,
    toggle_program_favorite_request_data: ToggleProgramFavoriteInSchema
):
    try:
        res = await toggle_program_as_favorite(
            user=request.user,
            program_id=toggle_program_favorite_request_data.program_id,
            set_favorite=toggle_program_favorite_request_data.set_favorite
        )
        favorite_programs = await get_user_favorite_programs_ids(user=request.user)
        return res, favorite_programs
    except Exception as exc:
        logger.error('Error in toggle_program_favorite', exc_info=exc)
        return 500, None


@router.get(
    '/user-program-preferences',
    response={200: UserProgramPreferencesSchema, 500: None}
)
@await_auth
@paid_member_required
async def get_user_program_preferences(request):
    return await retrieve_user_program_preferences(user=request.user)


@router.post(
    '/user-program-preferences',
    response={200: UserProgramPreferencesSchema, 500: None}
)
@await_auth
@paid_member_required
async def set_user_program_preferences(
    request,
    user_program_preferences_request_data: UserProgramPreferencesSchema
):
    await save_user_program_preferences(
        user=request.user,
        regions=user_program_preferences_request_data.regions,
        company_categories=user_program_preferences_request_data.company_categories,
        program_categories=user_program_preferences_request_data.program_categories
    )

    return await retrieve_user_program_preferences(user=request.user)


@router.get(
    '/user-email-preferences',
    response={200: UserEmailPreferencesSchema, 500: None}
)
@await_auth
@paid_member_required
async def get_user_email_preferences(request):
    return await retrieve_user_email_preferences(user=request.user)


@router.post(
    '/user-email-preferences',
    response={200: UserEmailPreferencesSchema, 500: None}
)
@await_auth
@paid_member_required
async def set_user_email_preferences(
    request,
    user_email_preferences_request_data: UserEmailPreferencesSchema
):
    await save_user_email_preferences(
        user=request.user,
        email_notifications_enabled=user_email_preferences_request_data.email_notifications_enabled,
        regions=user_email_preferences_request_data.regions,
        company_categories=user_email_preferences_request_data.company_categories,
        program_categories=user_email_preferences_request_data.program_categories,
        emails_per_day_count=user_email_preferences_request_data.emails_per_day_count,
        near_deadline_notifications_enabled=user_email_preferences_request_data.near_deadline_notifications_enabled
    )

    return await retrieve_user_email_preferences(user=request.user)


@router.get(
    '/user-program/{program_id}',
    response={200: UserProgramDetailOutWithNotesAndDescriptionSchema, 404: None, 500: None}
)
@await_auth
@paid_member_required
async def get_single_user_program(
    request,
    program_id: int
):
    return await retrieve_single_user_program(
        user=request.user,
        program_id=program_id,
        retrieve_notes=True
    )


@router.get(
    '/program-community-reported-data/{program_id}',
    response={200: ProgramCommunityReportedDataOutSchema, 404: None, 500: None}
)
@await_auth
@paid_member_required
async def get_single_program_community_reported_data(
    request,
    program_id: int
):
    return await retrieve_program_community_reported_data(
        program_id=program_id
    )


@router.post(
    '/user-program-pipeline-action',
    response={200: UserProgramDetailOutWithNotesAndDescriptionSchema, 404: None, 500: None}
)
@await_auth
@paid_member_required
async def user_program_pipeline_action(
    request,
    user_program_pipeline_action_request_data: UserProgramPipelineActionInSchema
):
    """
    Perform Pipeline Action on a Program by User.

    Possible Values for _optional_info_:

    | Action | optional_info keys & values |
    | ------ | --------------------------- |
    | submitted | `does_ask_for_cover_letter` : bool |
    | online_test | `online_test_questions` : str |
    | pre_recorded_video_interview | `was_there_no_online_test` : bool <br /> `pre_recorded_video_interview_format` : str |
    | personal_interview | `was_there_no_online_test` : bool <br /> `was_there_no_pre_recorded_video_interview_stage` : bool <br /> `personal_interview_questions` : str |
    | close | `application_close_reason` : Enum(str) : possible values - `"ACCEPTED", "REJECTED", "CANCELLED", "OTHER"` |

    """
    res = await perform_userprogram_pipeline_action(
        user=request.user,
        program_id=user_program_pipeline_action_request_data.program_id,
        action=user_program_pipeline_action_request_data.action,
        value=user_program_pipeline_action_request_data.value,
        optional_info=user_program_pipeline_action_request_data.optional_info
    )
    if res != 200:
        return res, None
    return await retrieve_single_user_program(
        user=request.user,
        program_id=user_program_pipeline_action_request_data.program_id,
        retrieve_notes=True
    )


@router.post(
    '/user-program-note',
    response={
        200: UserProgramDetailOutWithNotesAndDescriptionSchema,
        404: None,
        500: None
    }
)
@await_auth
@paid_member_required
async def user_program_create_note(
    request,
    user_program_note_request_data: UserProgramNoteInSchema
):
    result = await create_user_program_note(
        user=request.user,
        program_id=user_program_note_request_data.program_id,
        note=user_program_note_request_data.note
    )
    if result != 200:
        return result, None
    return await retrieve_single_user_program(
        user=request.user,
        program_id=user_program_note_request_data.program_id,
        retrieve_notes=True
    )


@router.get(
    '/dashboard-stats',
    response={200: DashboardStatsSchema, 500: None}
)
@await_auth
@paid_member_required
async def get_dashboard_stats(request):
    return await retrieve_dashboard_stats(request.user)


@router.get(
    '/companies-stats',
    response={200: t.List[SingleCompanyStatsSchema], 500: None}
)
@await_auth
async def get_company_stats(request):
    return await retrieve_company_stats()
