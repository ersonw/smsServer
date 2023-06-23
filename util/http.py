import json
import logging
import os

import requests

env_dist = os.environ


class HttpApi:
    token = None

    def __init__(self):
        http_url = env_dist.get('CENTER_URL') or "http://127.0.0.1:8080"
        if not f"{http_url}".endswith("/"):
            http_url = f"{http_url}/"
        self.http_url = http_url

    def auth(self):
        self.get(f"{self.http_url}api/authSms")
        return self.get(f"{self.http_url}api/authSms")

    def get(self, url, params=None, ):
        Headers = {}
        if self.token:
            Headers = {"X-Token": f"{self.token}"}

        return self.handler(requests.get(url, params=params, headers=Headers))

    def post(self, url, data=None):
        Headers = {}
        if self.token:
            Headers = {"X-Token": f"{self.token}"}
        return self.handler(requests.post(url, data=data, headers=Headers))

    @classmethod
    def test(cls):
        print(cls)

    @staticmethod
    def handler(response):
        if response.status_code == 200:
            # print(response.status_code)
            result = response.json()
            # print(result)
            if result["code"] == 200:
                if result["message"]:
                    logging.info(result["message"])
                return result["data"]
            logging.error(result["message"])
            raise Exception(result["code"], result["message"])
        raise Exception(f"连接服务器失败： {response.status_code}")


Http = HttpApi()
