import os
import re
from datetime import datetime
from random import choice

import openai

from inv_aki_flask.model.secret_client import SecretClient

MAX_QUESTIONS = 10


class ChatGPT:
    SELECT_MAX_RETRY = 5
    ANSWER_MAX_RETRY = 3

    def __init__(self, api_key=None):
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

    def parse_select(self, res):
        output = {}
        for line in res.split("\n"):
            if line.startswith("対象の名称: "):
                output["keyword"] = line.strip()[len("対象の名称: ") :]
        return output

    def parse_answer(self, res):
        output = {}
        for line in res.split("\n"):
            if line.startswith("理由1: "):
                output["reason1"] = line.strip()[len("理由1: ") :]
            if line.startswith("理由2: "):
                output["reason2"] = line.strip()[len("理由2: ") :]
            if line.startswith("理由3: "):
                output["reason3"] = line.strip()[len("理由3: ") :]
            if line.startswith("返答: "):
                output["answer"] = line.strip()[len("返答: ") :]
        return output

    def parse_judge(self, res):
        output = {}
        for line in res.split("\n"):
            if line.startswith("返答: "):
                output["judge"] = line.strip()[len("返答: ") :]
        return output

    def select_category(self):
        category_list = [
            "実在する動物",
            "実在する日本人",
            "実在する食べ物や料理",
            "実在する文房具",
            "実在する漫画やアニメのキャラクター",
            "実在するディズニーキャラクター",
        ]

        return choice(category_list)

    def select_keyword(self):
        category = self.select_category()
        text = self.prompt_select.format(category=category)
        for _ in range(ChatGPT.SELECT_MAX_RETRY):
            res = self.request_to_chatgpt(text)
            res = self.parse_select(res)
            keyword = res.get("keyword", "")
            if keyword != "":
                return category, keyword
        raise Exception("キーワードの選択に失敗しました")

    def ask_answer(self, question, category, keyword):
        self.logging("----------")
        self.logging("question: " + question)

        text = self.prompt_answer.format(
            category=category, keyword=keyword, question=question
        )

        for _ in range(ChatGPT.ANSWER_MAX_RETRY):
            res = self.request_to_chatgpt(text)
            res = self.parse_answer(res)
            res["question"] = question
            answer = res.get("answer", "")
            if answer != "":
                break
        else:
            answer = "分からない"

        self.logging("answer: " + answer)

        return answer, res

    def judge(self, question, category, keyword):
        self.logging("----------")
        self.logging("question: " + question)
        text = self.prompt_judge.format(
            category=category, keyword1=keyword, keyword2=question
        )

        res = self.request_to_chatgpt(text)
        res = self.parse_judge(res)
        answer = res["judge"]
        if "同じものである" in answer:
            judge = "正解！"
        else:
            judge = "残念！"
        answer = "\n".join(
            [
                judge,
                "私が考えていたのは",
                keyword,
                f"({category})",
                "でした！",
            ]
        )

        self.logging(answer)

        return answer, (judge == "正解！")

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

        system_content, user_content = content.split("------")

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_content.strip(),
                },
                {
                    "role": "user",
                    "content": user_content.strip(),
                },
            ],
        )
        res = completion.choices[0].message.content
        self.logging(res)
        return res
