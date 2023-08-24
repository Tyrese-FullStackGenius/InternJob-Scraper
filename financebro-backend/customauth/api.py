from asgiref.sync import sync_to_async
from ninja import Router

from customauth.async_orm_utils import (
    retrieve_user_profile,
    update_user_autofill_profile
)
from customauth.schemas import UserAutoFillProfileSchema
from customauth.utilities import await_auth

router = Router()


@router.get('/me')
@await_auth
async def get_current_user_details(request):
    user = await sync_to_async(lambda: request.user)()
    return {
        'email': user.email,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'plan': await user.plan
    }


@router.get('/user-profile', response={200: UserAutoFillProfileSchema, 500: None})
@await_auth
async def get_current_user_profile(request):
    return await retrieve_user_profile(request.user.id)


@router.put('/user-profile', response={200: UserAutoFillProfileSchema, 500: None})
@await_auth
async def update_user_autofill_profile_action(
    request,
    user_autofill_profile_data: UserAutoFillProfileSchema
):
    return await update_user_autofill_profile(
        request.user.id,
        user_autofill_profile_data.dict()
    )
