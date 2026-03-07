# Backward compatibility — canonical location is sync_client.py
from .sync_client import *  # noqa: F401,F403
from .sync_client import Job, AnticaptchaClient
