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

    def greet(self, name, msg):
        return self.app_client.greet(name, msg)

    def login(self, username, password):
        return self.app_client.login(username, password)
