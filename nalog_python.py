import os
import json
import requests
from dotenv import load_dotenv

class NalogRuPython:
    HOST = 'irkkt-mobile.nalog.ru:8888'
    DEVICE_OS = 'iOS'
    CLIENT_VERSION = '2.9.0'
    DEVICE_ID = '7C82010F-16CC-446B-8F66-FC4080C66521'
    ACCEPT = '*/*'
    USER_AGENT = 'billchecker/2.9.0 (iPhone; iOS 13.6; Scale/2.00)'
    ACCEPT_LANGUAGE = 'ru-RU;q=1, en-US;q=0.9'
    
    
    def __init__(self):
        load_dotenv('data.env')
        self.__session_id = None
        self.set_session_id()

    def set_session_id(self) -> None:
        if os.getenv('CLIENT_SECRET') is None:
            raise ValueError('OS environments not content "CLIENT_SECRET"')
        if os.getenv('INN') is None:
            raise ValueError('OS environments not content "INN"')
        if os.getenv('PASSWORD') is None:
            raise ValueError('OS environments not content "PASSWORD"')

        url = f'https://{self.HOST}/v2/mobile/users/lkfl/auth'
        payload = {
            'inn': os.getenv('INN'),
            'client_secret': os.getenv('CLIENT_SECRET'),
            'password': os.getenv('PASSWORD')
        }
        headers = {
            'Host': self.HOST,
            'Accept': self.ACCEPT,
            'Device-OS': self.DEVICE_OS,
            'Device-Id': self.DEVICE_ID,
            'clientVersion': self.CLIENT_VERSION,
            'Accept-Language': self.ACCEPT_LANGUAGE,
            'User-Agent': self.USER_AGENT,
        }

        resp = requests.post(url, json=payload, headers=headers)
        self.__session_id = resp.json()['sessionId']


    def _get_ticket_id(self, qr: str) -> str:
        url = f'https://{self.HOST}/v2/ticket'
        payload = {'qr': qr}
        headers = {
            'Host': self.HOST,
            'Accept': self.ACCEPT,
            'Device-OS': self.DEVICE_OS,
            'Device-Id': self.DEVICE_ID,
            'clientVersion': self.CLIENT_VERSION,
            'Accept-Language': self.ACCEPT_LANGUAGE,
            'sessionId': self.__session_id,
            'User-Agent': self.USER_AGENT,
        }
        resp = requests.post(url, json=payload, headers=headers)
        return resp.json()["id"]
    
    def get_ticket(self, qr: str) -> dict:
        ticket_id = self._get_ticket_id(qr)
        url = f'https://{self.HOST}/v2/tickets/{ticket_id}'
        headers = {
            'Host': self.HOST,
            'sessionId': self.__session_id,
            'Device-OS': self.DEVICE_OS,
            'clientVersion': self.CLIENT_VERSION,
            'Device-Id': self.DEVICE_ID,
            'Accept': self.ACCEPT,
            'User-Agent': self.USER_AGENT,
            'Accept-Language': self.ACCEPT_LANGUAGE,
        }
        resp = requests.get(url, headers=headers)
        return resp.json()


if __name__ == '__main__':
    client = NalogRuPython()
    qr_code = "t=20200727T1117&s=4850.00&fn=9287440300634471&i=13571&fp=3730902192&n=1"
    ticket = client.get_ticket(qr_code)
    print(json.dumps(ticket, indent=4))