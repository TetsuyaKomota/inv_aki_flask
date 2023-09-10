from datetime import datetime
from hashlib import md5

from flask import session

from inv_aki_flask.model.dialog import DialogData

# リセットごとに初期化が不要な情報
INFO_KEYS = [
    SESSION_ID := "sessionid",
    LOGIN := "login",
    NAME := "name",
]

# リセットごとに初期化が必要な情報
STATUS_KEYS = [
    MESSAGES := "messages",
    CATEGIRY := "category",
    KEYWORD := "keyword",
    JUDGED := "judged",
    NOTICE := "notice",
    VIEW_AD := "viewad",
    THANK := "thank",
]


def get_sessionid(session):
    return session.get(SESSION_ID, "")


def pop_sessionid(session):
    sessionid = get_sessionid(session)
    if SESSION_ID in session:
        del session[SESSION_ID]
    return sessionid


def init_sessionid(session):
    name = get_name(session)
    text = f"{name}_{datetime.now()}".encode("utf-8")
    sessionid = md5(text, usedforsecurity=False).hexdigest()
    session[SESSION_ID] = sessionid


def init_session(session, category, keyword):
    for k in STATUS_KEYS:
        if k in session:
            del session[k]
    init_sessionid(session)
    set_keyword(session, category, keyword)
    return get_sessionid(session)


def had_init_session(session):
    return SESSION_ID in session


def set_name(session, name):
    session[NAME] = name


def get_name(session):
    return session.get(NAME, "ネイター")


def set_login(session):
    session[LOGIN] = True


def set_logout(session):
    if LOGIN in session:
        del session[LOGIN]


def is_login(session):
    return LOGIN in session and NAME in session


def set_keyword(session, category, keyword):
    session[CATEGIRY] = category
    session[KEYWORD] = keyword


def get_keyword(session):
    category = session.get(CATEGIRY, "")
    keyword = session.get(KEYWORD, "")
    return category, keyword


def init_message(name: str) -> DialogData:
    msg = "\n".join(
        [
            "有名な人物やキャラクターを思い浮かべて．",
            "魔人が誰でも当てて見せよう．",
        ]
    )

    ans = "よーし，やってみるぞー"

    message_data = DialogData(player_name=f"アキ{name}", system_name="ChatGPT")
    message_data.add(msg, ans)

    return message_data


def set_message(session, msg, ans):
    message_data = get_messages(session)
    message_data.add(msg, ans)
    session[MESSAGES] = message_data.to_args()


def get_messages(session):
    if MESSAGES not in session:
        session[MESSAGES] = init_message(get_name(session)).to_args()
    return DialogData(*session[MESSAGES])


def get_messageid(session):
    message_data = get_messages(session)
    return len(message_data)


def get_message_count(session):
    message_data = get_messages(session)
    return len(message_data) - 1  # 最初のセリフ分


def judged_in_session(session):
    session[JUDGED] = True


def is_judged_in_session(session):
    return JUDGED in session


def view_ad_in_session(session):
    session[VIEW_AD] = True


def had_view_ad_in_session(session):
    return VIEW_AD in session


def set_notice(session, notice):
    session[NOTICE] = notice


def get_notice(session):
    return session.get(NOTICE, "")


def set_thank(session, message):
    session[THANK] = message


def pop_thank(session):
    thank = session.get(THANK, "")
    if THANK in session:
        del session[THANK]
    return thank
