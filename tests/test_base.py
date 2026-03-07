from unittest.mock import patch, MagicMock
import pytest

from python_anticaptcha.base import AnticaptchaClient, Job, SLEEP_EVERY_CHECK_FINISHED
from python_anticaptcha.exceptions import AnticaptchaException


class TestAnticaptchaClientInit:
    def test_https_url(self):
        client = AnticaptchaClient("key123")
        assert client.base_url == "https://api.anti-captcha.com/"
        assert client.client_key == "key123"

    def test_http_url(self):
        client = AnticaptchaClient("key123", use_ssl=False)
        assert client.base_url == "http://api.anti-captcha.com/"

    def test_custom_host(self):
        client = AnticaptchaClient("key123", host="custom.host.com")
        assert client.base_url == "https://custom.host.com/"

    def test_language_pool(self):
        client = AnticaptchaClient("key123", language_pool="rn")
        assert client.language_pool == "rn"


class TestCheckResponse:
    def setup_method(self):
        self.client = AnticaptchaClient("key123")

    def test_success_passthrough(self):
        response = {"errorId": 0, "taskId": 42}
        self.client._check_response(response)

    def test_error_raises(self):
        response = {
            "errorId": 1,
            "errorCode": "ERROR_KEY_DOES_NOT_EXIST",
            "errorDescription": "Account authorization key not found",
        }
        with pytest.raises(AnticaptchaException) as exc_info:
            self.client._check_response(response)
        assert exc_info.value.error_id == 1
        assert exc_info.value.error_code == "ERROR_KEY_DOES_NOT_EXIST"

    def test_error_id_11_appends_ip(self):
        response = {
            "errorId": 11,
            "errorCode": "ERROR_IP_NOT_ALLOWED",
            "errorDescription": "IP not allowed",
        }
        with patch.object(
            type(self.client), "client_ip", new_callable=lambda: property(lambda self: "5.6.7.8")
        ):
            with pytest.raises(AnticaptchaException) as exc_info:
                self.client._check_response(response)
            assert "5.6.7.8" in exc_info.value.error_description


class TestCreateTask:
    def test_payload_structure(self):
        client = AnticaptchaClient("key123")
        mock_task = MagicMock()
        mock_task.serialize.return_value = {"type": "NoCaptchaTaskProxyless", "websiteURL": "https://example.com"}

        mock_response = MagicMock()
        mock_response.json.return_value = {"errorId": 0, "taskId": 99}

        with patch.object(client.session, "post", return_value=mock_response) as mock_post:
            job = client.createTask(mock_task)

        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs.kwargs["json"]
        assert payload["clientKey"] == "key123"
        assert payload["task"] == {"type": "NoCaptchaTaskProxyless", "websiteURL": "https://example.com"}
        assert payload["softId"] == 847
        assert payload["languagePool"] == "en"
        assert isinstance(job, Job)
        assert job.task_id == 99


class TestGetBalance:
    def test_returns_balance(self):
        client = AnticaptchaClient("key123")
        mock_response = MagicMock()
        mock_response.json.return_value = {"errorId": 0, "balance": 3.21}

        with patch.object(client.session, "post", return_value=mock_response):
            balance = client.getBalance()
        assert balance == 3.21


class TestJobCheckIsReady:
    def test_ready(self):
        client = MagicMock()
        client.getTaskResult.return_value = {"status": "ready", "solution": {}}
        job = Job(client, task_id=1)
        assert job.check_is_ready() is True

    def test_processing(self):
        client = MagicMock()
        client.getTaskResult.return_value = {"status": "processing"}
        job = Job(client, task_id=1)
        assert job.check_is_ready() is False


class TestJobSolutionGetters:
    def setup_method(self):
        self.client = MagicMock()
        self.job = Job(self.client, task_id=1)
        self.job._last_result = {
            "status": "ready",
            "solution": {
                "gRecaptchaResponse": "recaptcha-token",
                "token": "funcaptcha-token",
                "text": "captcha text",
                "cellNumbers": [1, 3, 5],
                "answers": {"q1": "a1"},
            },
        }

    def test_get_solution_response(self):
        assert self.job.get_solution_response() == "recaptcha-token"

    def test_get_token_response(self):
        assert self.job.get_token_response() == "funcaptcha-token"

    def test_get_captcha_text(self):
        assert self.job.get_captcha_text() == "captcha text"

    def test_get_cells_numbers(self):
        assert self.job.get_cells_numbers() == [1, 3, 5]

    def test_get_answers(self):
        assert self.job.get_answers() == {"q1": "a1"}

    def test_get_solution(self):
        assert self.job.get_solution() == self.job._last_result["solution"]


class TestJobJoinTimeout:
    @patch("python_anticaptcha.base.time.sleep")
    def test_timeout_raises(self, mock_sleep):
        client = MagicMock()
        client.getTaskResult.return_value = {"status": "processing"}
        job = Job(client, task_id=1)
        with pytest.raises(AnticaptchaException) as exc_info:
            job.join(maximum_time=SLEEP_EVERY_CHECK_FINISHED)
        assert "exceeded" in str(exc_info.value).lower()


class TestSnakeCaseAliases:
    def test_create_task_alias(self):
        assert AnticaptchaClient.create_task is AnticaptchaClient.createTask

    def test_create_task_smee_alias(self):
        assert AnticaptchaClient.create_task_smee is AnticaptchaClient.createTaskSmee

    def test_get_task_result_alias(self):
        assert AnticaptchaClient.get_task_result is AnticaptchaClient.getTaskResult

    def test_get_balance_alias(self):
        assert AnticaptchaClient.get_balance is AnticaptchaClient.getBalance

    def test_get_app_stats_alias(self):
        assert AnticaptchaClient.get_app_stats is AnticaptchaClient.getAppStats

    def test_report_incorrect_image_alias(self):
        assert AnticaptchaClient.report_incorrect_image is AnticaptchaClient.reportIncorrectImage

    def test_report_incorrect_recaptcha_alias(self):
        assert AnticaptchaClient.report_incorrect_recaptcha is AnticaptchaClient.reportIncorrectRecaptcha

    def test_alias_works_on_instance(self):
        client = AnticaptchaClient("key123")
        mock_response = MagicMock()
        mock_response.json.return_value = {"errorId": 0, "balance": 5.0}
        with patch.object(client.session, "post", return_value=mock_response):
            balance = client.get_balance()
        assert balance == 5.0
