from ninja import ModelSchema

from customauth.models import UserAutoFillProfile


class UserAutoFillProfileSchema(ModelSchema):
    class Config:
        model = UserAutoFillProfile
        model_fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'phone',
            'address1', 'address2', 'city', 'country', 'postal_code',
            'education1', 'education2', 'education3',
            'employment1', 'employment2', 'employment3'
        ]
