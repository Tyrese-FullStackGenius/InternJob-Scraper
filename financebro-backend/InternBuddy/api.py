from django.http import JsonResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError
from ninja.parser import Parser
from ninja.security import HttpBearer
import orjson

from customauth.api import router as customauth_router
from customauth.async_orm_utils import get_first_matching_token
from customauth.async_orm_utils import get_user
from customauth.utilities import UserNotPaidMemberError
from internships.api import router as internships_router
from payments.api import router as payments_router, webhooks_router


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


class AuthBearer(HttpBearer):
    async def authenticate(self, request, token):
        token = await get_first_matching_token(token)
        if token:
            request.user = await get_user(token.user_id)
            return True
        return False


api = NinjaAPI(parser=ORJSONParser())
api.add_router('/', customauth_router, auth=AuthBearer())
api.add_router('/', internships_router, auth=AuthBearer())
api.add_router('/payments', payments_router, auth=AuthBearer())
api.add_router('/webhooks', webhooks_router)


@api.exception_handler(ValidationError)
def validation_errors(request, exc):
    response = {
        'code': 422,
        'message': 'Validation Error',
        'details': []
    }
    for exc_error in exc.errors:
        error = {
            'path': '.'.join(exc_error['loc'][1:]),
            'info': exc_error['msg']
        }
        response['details'].append(error)
    return JsonResponse(response, status=422)


@api.exception_handler(UserNotPaidMemberError)
def on_user_not_paid_member_error(request, exc):
    return api.create_response(request, {"message": "User is not a PAID member"}, status=403)
