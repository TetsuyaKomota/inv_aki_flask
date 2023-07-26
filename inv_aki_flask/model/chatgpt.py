import os
import re
from datetime import datetime

import openai

from inv_aki_flask.model.secret_client import SecretClient

MAX_QUESTIONS = 3


class ChatGPT:
    SELECT_MAX_RETRY = 5
    ANSWER_MAX_RETRY = 3

    def __init__(self, api_key=None, work_preserve=""):
        self.secret_client = SecretClient(project_id="inv-aki")
        self.set_api_key(api_key)

        if "LOG_DIR_PATH" in os.environ:
            log_dir_path = os.environ["LOG_DIR_PATH"]
        else:
            log_dir_path = "tmp/log"

        os.makedirs(log_dir_path, exist_ok=True)
        self.log_path = os.path.join(
            log_dir_path, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        )
        self.work_preserve = work_preserve
        self.prompt_select = self.load_prompt("template_select.txt")
        self.prompt_answer = self.load_prompt("template_answer.txt")
        self.prompt_judge = self.load_prompt("template_judge.txt")

    def set_api_key(self, api_key=None):
        self.is_active = False

        if not api_key:
            api_key = self.secret_client.get_secret("openai_api_key")

        if api_key:
            openai.api_key = api_key
            self.is_active = True

    def logging(self, text):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(str(text) + "\n")

    def load_prompt(self, filename):
        with open(f"inv_aki_flask/lib/prompt/{filename}", "r", encoding="utf-8") as f:
            text = f.read()
        return text

    def select_keyword(self):
        text = self.prompt_select.format(work_preserve=self.work_preserve)
        keywords = []
        for _ in range(ChatGPT.SELECT_MAX_RETRY):
            res = self.request_to_chatgpt(text)
            work = res.strip().split("\n")[0]
            keyword = res.strip().split("\n")[-1]
            keywords.append(keyword)
            if "代表作: " in work and "キャラクター名: " in keyword:
                work = re.sub("代表作: ", "", work)
                keyword = re.sub("キャラクター名: ", "", keyword)
                return work, keyword
        raise Exception(f"キーワードの選択に失敗しました: {keywords}")

    def ask_answer(self, question, work, keyword):
        self.logging("----------")
        self.logging("question: " + question)

        text = self.prompt_answer.format(work=work, keyword=keyword, question=question)

        for _ in range(ChatGPT.ANSWER_MAX_RETRY):
            res = self.request_to_chatgpt(text)
            answer = res.strip().split("\n")[-1]
            if "返答: " in answer:
                answer = re.sub("返答: ", "", answer)
                break
        else:
            answer = "分からない"

        self.logging("answer: " + answer)

        return answer

    def judge(self, question, work, keyword):
        self.logging("----------")
        self.logging("question: " + question)
        text = self.prompt_judge.format(work=work, keyword1=keyword, keyword2=question)

        res = self.request_to_chatgpt(text)
        answer = res.strip().split("\n")[-1]
        if "同じものである" in answer:
            judge = "正解！"
        else:
            judge = "残念！"
        answer = "\n".join(
            [
                judge,
                "私が考えていたのは",
                keyword,
                "でした！",
            ]
        )

        self.logging(answer)

        return answer

    def request_to_chatgpt_mock(self, content):
        if content.startswith("アニメのキャラクターの名前を"):
            return "\n".join(
                [
                    "代表作: ドラゴンボール",
                    "作中での代表的なエピソード: ピッコロとの激闘",
                    "キャラクター名: 孫悟空",
                ]
            )
        if content.startswith("私はあなたに以下に指定する"):
            return "\n".join(
                [
                    "理由1: ほげほげ",
                    "理由2: ほげほげ",
                    "理由3: ほげほげ",
                    "返答: 部分的に当てはまる，たぶん当てはまる",
                ]
            )
        if content.startswith("以下のキーワード1とキーワード2は"):
            return "\n".join(
                [
                    "キーワード1の説明: ほげほげ",
                    "キーワード2の説明: ほげほげ",
                    "2つが同じものか判断した理由: ほげほげ",
                    "返答: 同じものである",
                ]
            )

    def request_to_chatgpt(self, content):
        # API KEY が与えられていない場合，モック関数を使う
        if not self.is_active:
            return self.request_to_chatgpt_mock(content)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )
        res = completion.choices[0].message.content
        self.logging(res)
        return res
