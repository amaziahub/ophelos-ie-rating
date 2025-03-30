import os
import subprocess
from busypie import wait as busy_wait, SECOND
from tests.support.client import Client


class AppDriver:

    def __init__(self):
        self._app_p = None
        self.app_client = None

    def start(self):
        self.app_client = Client()
        self._start_app()

    def _start_app(self):
        app_file = os.getcwd().split('tests')[0] + 'service/app.py'
        if not os.path.exists(app_file):
            app_file = 'service/app.py'

        self._app_p = subprocess.Popen(
            ['python', app_file], env=(os.environ.copy())
        )

        busy_wait().at_most(30, SECOND).ignore_exceptions().until(self.is_healthy)

    def stop(self):
        self._app_p.terminate()
        self._app_p.wait()

    def is_healthy(self):
        return self.app_client.is_healthy()

    def submit_statement(self, statement):
        return self.app_client.submit_statement(statement)

    def get_statement(self, statement_id, user_id):
        return self.app_client.get_statement_by_id(statement_id, user_id)

    def get_rating(self, statement_id, user_id):
        return self.app_client.get_rating_by_id(statement_id, user_id)

    def get_rating_period(self, user_id, start_date, end_date):
        return self.app_client.get_rating_period(user_id, start_date, end_date)
