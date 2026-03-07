from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from python_anticaptcha.async_client import (
    SLEEP_EVERY_CHECK_FINISHED,
    AsyncAnticaptchaClient,
    AsyncJob,
)
from python_anticaptcha.exceptions import AnticaptchaException


class TestAsyncAnticaptchaClientInit:
    def test_https_url(self):
        client = AsyncAnticaptchaClient("key123")
        assert client.base_url == "https://api.anti-captcha.com/"
        assert client.client_key == "key123"

    def test_http_url(self):
        client = AsyncAnticaptchaClient("key123", use_ssl=False)
        assert client.base_url == "http://api.anti-captcha.com/"

    def test_custom_host(self):
        client = AsyncAnticaptchaClient("key123", host="custom.host.com")
        assert client.base_url == "https://custom.host.com/"

    def test_language_pool(self):
        client = AsyncAnticaptchaClient("key123", language_pool="rn")
        assert client.language_pool == "rn"

    def test_env_var_fallback(self, monkeypatch):
        monkeypatch.setenv("ANTICAPTCHA_API_KEY", "env-key-456")
        client = AsyncAnticaptchaClient()
        assert client.client_key == "env-key-456"

    def test_explicit_key_over_env(self, monkeypatch):
        monkeypatch.setenv("ANTICAPTCHA_API_KEY", "env-key-456")
        client = AsyncAnticaptchaClient("explicit-key-789")
        assert client.client_key == "explicit-key-789"

    def test_no_key_raises(self, monkeypatch):
        monkeypatch.delenv("ANTICAPTCHA_API_KEY", raising=False)
        with pytest.raises(AnticaptchaException) as exc_info:
            AsyncAnticaptchaClient()
        assert exc_info.value.error_code == "CONFIG_ERROR"


class TestAsyncCheckResponse:
    def setup_method(self):
        self.client = AsyncAnticaptchaClient("key123")

    @pytest.mark.asyncio
    async def test_success_passthrough(self):
        response = {"errorId": 0, "taskId": 42}
        await self.client._check_response(response)

    @pytest.mark.asyncio
    async def test_error_raises(self):
        response = {
            "errorId": 1,
            "errorCode": "ERROR_KEY_DOES_NOT_EXIST",
            "errorDescription": "Account authorization key not found",
        }
        with pytest.raises(AnticaptchaException) as exc_info:
            await self.client._check_response(response)
        assert exc_info.value.error_id == 1
        assert exc_info.value.error_code == "ERROR_KEY_DOES_NOT_EXIST"

    @pytest.mark.asyncio
    async def test_error_id_11_appends_ip(self):
        response = {
            "errorId": 11,
            "errorCode": "ERROR_IP_NOT_ALLOWED",
            "errorDescription": "IP not allowed",
        }
        self.client._get_client_ip = AsyncMock(return_value="5.6.7.8")
        with pytest.raises(AnticaptchaException) as exc_info:
            await self.client._check_response(response)
        assert "5.6.7.8" in exc_info.value.error_description


class TestAsyncCreateTask:
    @pytest.mark.asyncio
    async def test_payload_structure(self):
        client = AsyncAnticaptchaClient("key123")
        mock_task = MagicMock()
        mock_task.serialize.return_value = {"type": "NoCaptchaTaskProxyless", "websiteURL": "https://example.com"}

        mock_response = MagicMock()
        mock_response.json.return_value = {"errorId": 0, "taskId": 99}

        client.session.post = AsyncMock(return_value=mock_response)
        job = await client.createTask(mock_task)

        call_kwargs = client.session.post.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs.kwargs["json"]
        assert payload["clientKey"] == "key123"
        assert payload["task"] == {"type": "NoCaptchaTaskProxyless", "websiteURL": "https://example.com"}
        assert payload["softId"] == 847
        assert payload["languagePool"] == "en"
        assert isinstance(job, AsyncJob)
        assert job.task_id == 99


class TestAsyncGetBalance:
    @pytest.mark.asyncio
    async def test_returns_balance(self):
        client = AsyncAnticaptchaClient("key123")
        mock_response = MagicMock()
        mock_response.json.return_value = {"errorId": 0, "balance": 3.21}

        client.session.post = AsyncMock(return_value=mock_response)
        balance = await client.getBalance()
        assert balance == 3.21


class TestAsyncJobCheckIsReady:
    @pytest.mark.asyncio
    async def test_ready(self):
        client = MagicMock()
        client.getTaskResult = AsyncMock(return_value={"status": "ready", "solution": {}})
        job = AsyncJob(client, task_id=1)
        assert await job.check_is_ready() is True

    @pytest.mark.asyncio
    async def test_processing(self):
        client = MagicMock()
        client.getTaskResult = AsyncMock(return_value={"status": "processing"})
        job = AsyncJob(client, task_id=1)
        assert await job.check_is_ready() is False


class TestAsyncJobSolutionGetters:
    def setup_method(self):
        self.client = MagicMock()
        self.job = AsyncJob(self.client, task_id=1)
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


class TestAsyncJobJoinTimeout:
    @pytest.mark.asyncio
    @patch("python_anticaptcha.async_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_timeout_raises(self, mock_sleep):
        client = MagicMock()
        client.getTaskResult = AsyncMock(return_value={"status": "processing"})
        job = AsyncJob(client, task_id=1)
        with pytest.raises(AnticaptchaException) as exc_info:
            await job.join(maximum_time=SLEEP_EVERY_CHECK_FINISHED)
        assert "exceeded" in str(exc_info.value).lower()


class TestAsyncJobJoinOnCheck:
    @pytest.mark.asyncio
    @patch("python_anticaptcha.async_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_on_check_called_each_iteration(self, mock_sleep):
        client = MagicMock()
        client.getTaskResult = AsyncMock(
            side_effect=[
                {"status": "processing"},
                {"status": "processing"},
                {"status": "ready", "solution": {}},
            ]
        )
        job = AsyncJob(client, task_id=1)
        callback = MagicMock()
        await job.join(on_check=callback)
        assert callback.call_count == 2
        callback.assert_any_call(SLEEP_EVERY_CHECK_FINISHED, "processing")
        callback.assert_any_call(SLEEP_EVERY_CHECK_FINISHED * 2, "processing")

    @pytest.mark.asyncio
    @patch("python_anticaptcha.async_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_on_check_none_by_default(self, mock_sleep):
        client = MagicMock()
        client.getTaskResult = AsyncMock(return_value={"status": "ready", "solution": {}})
        job = AsyncJob(client, task_id=1)
        await job.join()

    @pytest.mark.asyncio
    @patch("python_anticaptcha.async_client.asyncio.sleep", new_callable=AsyncMock)
    async def test_on_check_not_called_when_immediately_ready(self, mock_sleep):
        client = MagicMock()
        client.getTaskResult = AsyncMock(return_value={"status": "ready", "solution": {}})
        job = AsyncJob(client, task_id=1)
        callback = MagicMock()
        await job.join(on_check=callback)
        callback.assert_not_called()


class TestAsyncContextManager:
    @pytest.mark.asyncio
    async def test_aenter_returns_self(self):
        client = AsyncAnticaptchaClient("key123")
        assert await client.__aenter__() is client

    @pytest.mark.asyncio
    async def test_aexit_closes_session(self):
        client = AsyncAnticaptchaClient("key123")
        client.session.aclose = AsyncMock()
        await client.__aexit__(None, None, None)
        client.session.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_closes_session(self):
        client = AsyncAnticaptchaClient("key123")
        client.session.aclose = AsyncMock()
        await client.close()
        client.session.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_with_statement(self):
        async with AsyncAnticaptchaClient("key123") as client:
            assert isinstance(client, AsyncAnticaptchaClient)

    @pytest.mark.asyncio
    async def test_aexit_returns_false(self):
        client = AsyncAnticaptchaClient("key123")
        client.session.aclose = AsyncMock()
        result = await client.__aexit__(None, None, None)
        assert result is False


class TestAsyncSnakeCaseAliases:
    def test_create_task_alias(self):
        assert AsyncAnticaptchaClient.create_task is AsyncAnticaptchaClient.createTask

    def test_get_task_result_alias(self):
        assert AsyncAnticaptchaClient.get_task_result is AsyncAnticaptchaClient.getTaskResult

    def test_get_balance_alias(self):
        assert AsyncAnticaptchaClient.get_balance is AsyncAnticaptchaClient.getBalance

    def test_get_app_stats_alias(self):
        assert AsyncAnticaptchaClient.get_app_stats is AsyncAnticaptchaClient.getAppStats

    def test_report_incorrect_image_alias(self):
        assert AsyncAnticaptchaClient.report_incorrect_image is AsyncAnticaptchaClient.reportIncorrectImage

    def test_report_incorrect_recaptcha_alias(self):
        assert AsyncAnticaptchaClient.report_incorrect_recaptcha is AsyncAnticaptchaClient.reportIncorrectRecaptcha

    @pytest.mark.asyncio
    async def test_alias_works_on_instance(self):
        client = AsyncAnticaptchaClient("key123")
        mock_response = MagicMock()
        mock_response.json.return_value = {"errorId": 0, "balance": 5.0}
        client.session.post = AsyncMock(return_value=mock_response)
        balance = await client.get_balance()
        assert balance == 5.0


class TestAsyncRepr:
    def test_client_repr(self):
        client = AsyncAnticaptchaClient("key123")
        assert repr(client) == "<AsyncAnticaptchaClient host='api.anti-captcha.com'>"

    def test_job_repr_no_result(self):
        client = MagicMock()
        job = AsyncJob(client, task_id=42)
        assert repr(job) == "<AsyncJob task_id=42>"

    def test_job_repr_with_status(self):
        client = MagicMock()
        job = AsyncJob(client, task_id=42)
        job._last_result = {"status": "ready"}
        assert repr(job) == "<AsyncJob task_id=42 status='ready'>"
