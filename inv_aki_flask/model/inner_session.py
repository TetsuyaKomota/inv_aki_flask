from datetime import datetime
from hashlib import md5

from flask import session

from inv_aki_flask.model.dialog import DialogData


def generate_sessionid(name: str) -> str:
    text = f"{name}_{datetime.now()}"
    return md5(text.encode("utf-8"), usedforsecurity=False).hexdigest()


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


def init_sessionid(session):
    session["sessionid"] = generate_sessionid(session["name"])


def get_sessionid(session):
    return session.get("sessionid", "")


def set_keyword(session, category, keyword):
    session["category"] = category
    session["keyword"] = keyword


def get_keyword(session):
    category = session.get("category", "")
    keyword = session.get("keyword", "")
    return category, keyword


def get_messages(session):
    if "messages" not in session:
        session["messages"] = init_message(session["name"]).to_args()
    return DialogData(*session["messages"])


def set_message(session, msg, ans):
    message_data = get_messages(session)
    message_data.add(msg, ans)
    session["messages"] = message_data.to_args()


def get_messageid(session):
    message_data = get_messages(session)
    return len(message_data)


def get_message_count(session):
    message_data = get_messages(session)
    return len(message_data) - 1  # 最初のセリフ分


def judged_in_session(session):
    session["judged"] = True


def is_judged_in_session(session):
    return "judged" in session


def view_ad_in_session(session):
    session["viewad"] = True


def had_view_ad_in_session(session):
    return "viewad" in session


def get_name(session):
    return session.get("name", "ネイター")


def set_name(session, name):
    session["name"] = name


def get_notice(session):
    return session.get("notice", "")


def set_notice(session, notice):
    session["notice"] = notice


def reset_sessionid(session):
    if "sessionid" in session:
        del session["sessionid"]


def init_session(session, category, keyword):
    for k in ["messages", "category", "keyword", "judged", "notice", "viewad"]:
        if k in session:
            del session[k]
    init_sessionid(session)
    set_keyword(session, category, keyword)
    return get_sessionid(session)


def is_login(session):
    return "login" in session and "name" in session


def set_login(session):
    session["login"] = True


def set_logout(session):
    if "login" in session:
        del session["login"]


def had_init_session(session):
    return "sessionid" in session
