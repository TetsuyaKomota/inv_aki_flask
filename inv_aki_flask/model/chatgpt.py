import os
import re
from datetime import datetime
from random import choice

import openai
import pandas as pd

from inv_aki_flask.model.secret_client import SecretClient

MAX_QUESTIONS = 10


class ChatGPT:
    SELECT_MAX_RETRY = 5
    ANSWER_MAX_RETRY = 3
    JUDGE_MAX_RETRY = 3

    def __init__(self, api_key=None, use_easy_list=True):
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

        # キーワード選択のモード
        # True : 前もって作成したリストから選択
        # False: 毎回プロンプトでChatGPTから取得
        self.is_select_from_list = True
        self.keyword_list = pd.read_csv("inv_aki_flask/lib/keyword_list.tsv", sep="\t")

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

    def parse_response(self, res, kv):
        output = {}
        for line in res.split("\n"):
            for k, v in kv.items():
                if line.startswith(k):
                    output[v] = line.strip()[len(k) :]
        return output

    def parse_select(self, res):
        kv = {
            "対象の名称: ": "keyword",
        }
        return self.parse_response(res, kv)

    def parse_answer(self, res):
        kv = {
            "理由1: ": "reason1",
            "理由2: ": "reason2",
            "理由3: ": "reason3",
            "返答: ": "answer",
        }
        return self.parse_response(res, kv)

    def parse_judge(self, res):
        kv = {
            "キーワード1の説明: ": "explain1",
            "キーワード2の説明: ": "explain2",
            "2つが同じものか判断した理由: ": "reason",
            "返答: ": "judge",
        }
        return self.parse_response(res, kv)

    def select_keyword(self):
        if self.is_select_from_list:
            return self.select_keyword_from_list()
        else:
            return self.select_keyword_from_prompt()

    def select_keyword_from_list(self, use_easy_list=True):
        keyword_list = self.keyword_list
        if use_easy_list:
            keyword_list = keyword_list[keyword_list.is_easy]
        r = keyword_list.sample().iloc[0]
        return r.category, r.keyword

    def select_keyword_from_prompt(self):
        category_list = [
            ("実在する動物", "あまり有名ではない"),
            ("実在する虫", "多くの人が知っている"),
            ("実在する日本人", "多くの人が知っている"),
            ("実在する食べ物や料理", "多くの人が知っている"),
            ("実在する文房具", "あまり有名ではない"),
            ("実在する乗り物", "あまり有名ではない"),
            ("実在する漫画やアニメのキャラクター", "多くの人が知っている"),
            ("実在するゲームのキャラクター", "多くの人が知っている"),
            ("実在するディズニーキャラクター", "多くの人が知っている"),
        ]
        category, difficulty = choice(category_list)
        text = self.prompt_select.format(category=category, difficulty=difficulty)
        for _ in range(ChatGPT.SELECT_MAX_RETRY):
            res = self.request_to_chatgpt(text)
            res = self.parse_select(res)
            keyword = res.get("keyword", "")
            if keyword == "":
                continue
            break
        else:
            raise Exception("キーワードの選択に失敗しました")

        return category, keyword

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
            if res.get("answer", "") == "":
                continue
            if len(res.get("answer", "")) > 11:
                # 選択肢以外の返答をしたらやり直し
                continue
            break
        else:
            res = {"answer": "分からない"}

        answer = res.get("answer", "")
        self.logging("answer: " + answer)

        return answer, res

    def judge(self, question, category, keyword):
        self.logging("----------")
        self.logging("question: " + question)
        text = self.prompt_judge.format(
            category=category, keyword1=keyword, keyword2=question
        )

        for _ in range(ChatGPT.JUDGE_MAX_RETRY):
            res = self.request_to_chatgpt(text)
            res = self.parse_judge(res)
            if res.get("judge", "") == "":
                continue
            break
        else:
            res = {"judge": "分からない"}

        answer = res.get("judge", "")

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

        return answer, res

    def request_to_chatgpt(
        self, content, chatgpt_model_type="gpt-3.5-turbo", temperature=0
    ):
        system_content, user_content = content.split("------")

        completion = openai.ChatCompletion.create(
            model=chatgpt_model_type,
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
            temperature=temperature,
        )
        res = completion.choices[0].message.content
        self.logging(res)
        return res
