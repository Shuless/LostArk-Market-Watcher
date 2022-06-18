from datetime import datetime
from threading import Lock
import requests
from modules.common.singleton import Singleton
from modules.config import Config
from modules.errors import NoTokenError
from modules.logging import AppLogger
from sentry_sdk import capture_exception, set_user

api_key = 'AIzaSyBMTA0A2fy-dh4jWidbAtYseC7ZZssnsmk'

class Auth(metaclass=Singleton):
    last_refresh: datetime = None 
    lock = Lock()

    def refresh_token(self):
        try:
            self.lock.acquire()
            res = requests.post(f'https://securetoken.googleapis.com/v1/token?key={api_key}', json={
                'refresh_token': Config().refresh_token,
                'grant_type': 'refresh_token'
            })
            tokens = res.json()
            if 'error' in tokens:
                raise NoTokenError()
            Config().update_token({
                "id_token": tokens['id_token'],
                "refresh_token": tokens['refresh_token'],
                "uid": tokens['user_id'],
            })
            set_user({"id":tokens["user_id"]})
            self.last_refresh = datetime.now()
            self.lock.release()
        except Exception as ex:
            AppLogger().exception(ex)
            capture_exception(ex)
            self.lock.release()

