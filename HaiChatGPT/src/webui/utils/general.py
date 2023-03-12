from flask import request, session
import damei as dm
import itertools

logger = dm.get_logger('general')


def get_user_from_session(**kwargs):
    """
    旧的读取用户的方法，可能会导致注入
    """
    msg = kwargs.get('msg', '')
    session_id = request.cookies.get('session', None)
    if session_id:
        username = session.get('username', None)  # 从服务器端读取
        # logger.debug(f'Session_id: {session_id[:4]}**{session_id[-4::]}. session: {session}. {msg}')
    else:
        username = None
    username = 'public' if username is None else username
    # logger.debug(f'Username: {username}')
    return username


def is_generator_empty(iterable):
    peekable = itertools.peekable(iterable)
    try:
        next(peekable)
    except StopIteration:
        return True
    else:
        return False