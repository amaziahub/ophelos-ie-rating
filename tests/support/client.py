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

    def greet(self, name, msg):
        response = requests.post(f"{self.root}/greet",
                                 json={
                                     "user_id": 1,
                                     "name": f"{name}",
                                     "greet_msg": f"{msg}"
                                 })
        assert_that(response.status_code, is_(201))

    def submit_statement(self, statement):
        response = requests.post(f"{self.root}/api/statements",
                                 json={
                                     "expenditures": [
                                         {
                                             "amount": 1500.0,
                                             "category": "Rent"
                                         }],
                                     "incomes": [
                                         {
                                             "amount": 5000.0,
                                             "category": "Salary"
                                         }],
                                     "user_id": 1})
        assert_that(response.status_code, is_(201))
        return response.json()
