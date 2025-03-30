import json
import os

import requests
from hamcrest import assert_that, is_


class Client:

    def __init__(self):
        self.port = os.getenv("PORT", 8080)
        self.endpoint = os.getenv("ENDPOINT", 'localhost')
        self.root = f'http://{self.endpoint}:{self.port}'

    def is_healthy(self):
        response = requests.get(f"{self.root}/health", verify=False)
        assert_that(response.status_code, is_(200))
        return response

    def submit_statement(self, statement):
        response = requests.post(f"{self.root}/api/statements",
                                 json=json.loads(statement))
        assert_that(response.status_code, is_(201))
        return response.json()

    def get_statement_by_id(self, statement_id, user_id):
        response = requests.get(
            f"{self.root}/api/statements",
            params={
                "id": statement_id,
                "user_id": user_id
            },
            verify=False
        )

        if response.status_code != 200:
            response.raise_for_status()

        assert_that(response.status_code, is_(200))
        return response.json()

    def get_rating_by_id(self, statement_id, user_id):
        response = requests.get(
            f"{self.root}/api/ratings",
            params={
                "report_id": statement_id,
                "user_id": user_id
            },
            verify=False
        )

        if response.status_code != 200:
            response.raise_for_status()

        assert_that(response.status_code, is_(200))
        return response.json()

    def get_rating_period(self, user_id, start_date, end_date):

        response = requests.get(
            f"{self.root}/api/ratings",
            params={
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            },
            verify=False
        )
        if response.status_code != 200:
            response.raise_for_status()

        assert_that(response.status_code, is_(200))
        return response.json()
