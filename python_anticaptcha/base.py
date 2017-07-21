import requests
import time

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from .exceptions import AnticatpchaException

SLEEP_EVERY_CHECK_FINISHED = 3
MAXIMUM_JOIN_TIME = 60*5


class Job(object):
    client = None
    task_id = None
    _last_result = None

    def __init__(self, client, task_id):
        self.client = client
        self.task_id = task_id

    def _update(self):
        self._last_result = self.client.getTaskResult(self.task_id)

    def check_is_ready(self):
        self._update()
        return self._last_result['status'] == 'ready'

    def get_solution_response(self):  # TODO: Support different captcha solutions
        return self._last_result['solution']['gRecaptchaResponse']

    def get_captcha_text(self):
        return self._last_result['solution']['text']

    def join(self, maximum_time=None):
        elapsed_time = 0
        while not self.check_is_ready():
            time.sleep(SLEEP_EVERY_CHECK_FINISHED)
            elapsed_time += SLEEP_EVERY_CHECK_FINISHED
            if elapsed_time is not None and elapsed_time > MAXIMUM_JOIN_TIME:
                raise AnticatpchaException(None, 250, "The maximum execution time of the task has been reached.")


class AnticaptchaClient(object):
    client_key = None
    CREATE_TASK_URL = "/createTask"
    TASK_RESULT_URL = "/getTaskResult"
    BALANCE_URL = "/getBalance"
    SOFT_ID = 847
    language_pool = "en"

    def __init__(self, client_key, language_pool="en", host="api.anti-captcha.com", use_ssl=True):
        self.client_key = client_key
        self.language_pool = language_pool
        self.base_url = "{proto}://{host}/".format(proto="https" if use_ssl else "http",
                                                   host=host)
        self.session = requests.Session()

    def _check_response(self, response):
        if response.get('errorId', False):
            raise AnticatpchaException(response['errorId'],
                                       response['errorCode'],
                                       response['errorDescription'])

    def createTask(self, task):
        request = {"clientKey": self.client_key,
                   "task": task.serialize(),
                   "softId": self.SOFT_ID,
                   "languagePool": self.language_pool,
                   }
        response = self.session.post(urljoin(self.base_url, self.CREATE_TASK_URL), json=request).json()
        self._check_response(response)
        return Job(self, response['taskId'])

    def getTaskResult(self, task_id):
        request = {"clientKey": self.client_key,
                   "taskId": task_id}
        response = self.session.post(urljoin(self.base_url, self.TASK_RESULT_URL), json=request).json()
        self._check_response(response)
        return response

    def getBalance(self):
        request = {"clientKey": self.client_key}
        response = self.session.post(urljoin(self.base_url, self.BALANCE_URL), json=request).json()
        self._check_response(response)
        return response['balance']
