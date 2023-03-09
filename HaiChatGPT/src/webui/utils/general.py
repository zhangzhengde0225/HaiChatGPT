from flask import request, session
import damei as dm
import itertools

logger = dm.get_logger('general')

def get_user_from_session():
    session_id = request.cookies.get('session')
    # logger.debug(f'Session_id: {session_id}')
    if session_id:
        user_name = session.get('username')
        if user_name is None:
            # logger.warn(f'User not login.')
            return None
        else:
            # logger.debug(f'User login: {user_name}.')
            return user_name


def is_generator_empty(iterable):
    peekable = itertools.peekable(iterable)
    try:
        next(peekable)
    except StopIteration:
        return True
    else:
        return False