import functools

from ninja.errors import AuthenticationError


def await_auth(f):
    @functools.wraps(f)
    async def decorator(*args, **kwargs):
        auth = await args[0].auth  # args[0] is always the request instance injected from ninja
        if not auth:
            raise AuthenticationError()
        args[0].auth = auth
        return await f(*args, **kwargs)
    return decorator


def paid_member_required(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        if await request.user.plan != 'PAID':
            raise UserNotPaidMemberError()
        return await f(request, *args, **kwargs)
    return decorator


class UserNotPaidMemberError(Exception):
    pass
