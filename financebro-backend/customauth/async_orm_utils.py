from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from customauth.models import UserAutoFillProfile


User = get_user_model()


@sync_to_async
def get_first_matching_token(tokenvalue):
    return Token.objects.filter(key=tokenvalue).first()


async def get_user(pk):
    return await User.objects.aget(pk=pk)


@sync_to_async
def retrieve_user_profile(user_id):
    user_autofill_profile = UserAutoFillProfile.objects.filter(user_id=user_id).first()
    if user_autofill_profile is None:
        user_autofill_profile = UserAutoFillProfile.objects.create(user_id=user_id)
    return user_autofill_profile


@sync_to_async
def update_user_autofill_profile(user_id, profile_data):
    user_autofill_profile = UserAutoFillProfile.objects.filter(user_id=user_id).first()
    if user_autofill_profile is None:
        user_autofill_profile = UserAutoFillProfile.objects.create(user_id=user_id)

    fields_to_update = [
        'first_name', 'middle_name', 'last_name', 'email', 'phone',
        'address1', 'address2', 'city', 'country', 'postal_code',
        'education1', 'education2', 'education3',
        'employment1', 'employment2', 'employment3'
    ]
    for field_name in fields_to_update:
        if field_name in profile_data:
            setattr(user_autofill_profile, field_name, profile_data[field_name])
    user_autofill_profile.save()

    return 200, user_autofill_profile
