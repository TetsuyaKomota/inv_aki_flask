import pytest

from inv_aki_flask.model.chatgpt import ChatGPT


@pytest.fixture()
def chatgpt(mocker):
    mock_openai = mocker.patch("openai.ChatCompletion.create", side_effect=lambda: None)
    return ChatGPT()


def test_sample(chatgpt):
    res = "ほげほげ\n対象の名称: ふがふが"

    expected = {"keyword": "ふがふが"}

    actual = chatgpt.parse_select(res)

    assert expected == actual
