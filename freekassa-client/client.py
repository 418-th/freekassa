import hashlib
import hmac
import requests
from urllib.parse import urlencode
from decimal import Decimal


class FreeKassaClient:
    '''
    client for FreeKassa API
    supports:
     - payment link generation
     - check sign for notify
     - create the order via API
     - status check
    '''

    def __init__(
        self,
        merchant_id: int,
        secret_word_1: str,
        secret_word_2: str,
        api_key: str = None,
        success_url: str = None,
        fail_url: str = None,
        notify_url: str = None,
        api_url: str = None,
        ui_url: str = None,
        nonce: int = 1,
    ):
        self._merchant_id = merchant_id
        self._secret1 = secret_word_1
        self._secret2 = secret_word_2
        self._api_key = api_key
        self._success_url = success_url
        self._fail_url = fail_url
        self._notify_url = notify_url
        self._api_url = 'https://api.fk.life/v1/'
        self._ui_url = 'https://pay.fk.money/'
        self._nonce = nonce

        if api_url:
            self._api_url = api_url
        if ui_url:
            self._ui_url = ui_url

    @staticmethod
    def __md5hex(data: str) -> str:
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    @staticmethod
    def __hmac_sha256_hex(message: str, key: str) -> str:
        return hmac.new(key.encode('utf-8'), message.encode('utf-8'), 'sha256').hexdigest()

    def verify_notify(self, amount: str, order_id: str, sign: str) -> bool:
        '''
        checks SIGN from Freekassa notify.
        '''

        expected = self.__md5hex(
            f'{self._merchant_id}:{amount}:{self._secret2}:{order_id}'
        )

        return expected.lower() == sign.lower()

    def ui_create_order(
        self,
        amount: Decimal,
        currency: str,
        payment_id: str,
        payment_method_id: int,
    ):
        '''
        Creates a payment URL for redirecting the user to FreeKassa UI.
        '''

        amount_str = f'{amount:.2f}'

        sign_str = f'{self._merchant_id}:{amount_str}:{self._secret1}:{currency}:{payment_id}'
        signature = hashlib.md5(sign_str.encode()).hexdigest()

        payload = {
            'm': self._merchant_id,
            'oa': amount_str,
            'currency': currency,
            'o': payment_id,
            's': signature,
            'i': payment_method_id,
        }

        return f'{self._ui_url}?{urlencode(payload)}'

    def api_create_order(
            self,
            nonce: int,
            i: int,
            user_email: str,
            user_ip: str,
            payment_id: str,
            amount: Decimal,
            currency: str,
    ):
        '''
        :keyword amount: required for API calls | amount to be paid
        :keyword currency: required for API calls | currency code
        :keyword i: required for API calls | payment system ID
        :return: response from API
        '''
        if not self._api_key:
            raise RuntimeError('API key is not set')

        payload = {
            'shopId': self._merchant_id,
            'nonce': nonce,
            'amount': f'{amount:.2f}',
            'currency': currency,
            'paymentId': payment_id,
            'ip': user_ip,
            'email': user_email,
            'i': i,
        }

        keys = sorted(payload.keys())
        message = '|'.join(str(payload[k]) for k in keys)

        payload['signature'] = self.__hmac_sha256_hex(message, self._api_key)

        r = requests.post(self._api_url + 'orders/create', json=payload, timeout=10)

        return r.json()

    def api_get_order(self, payment_id: str):
        if not self._api_key:
            raise RuntimeError('API key is not set')

        payload = {
            'shopId': self._merchant_id,
            'nonce': self._nonce,
            'paymentId': payment_id,
        }

        keys = sorted(payload.keys())
        message = '|'.join(str(payload[k]) for k in keys)

        payload['signature'] = self.__hmac_sha256_hex(message, self._api_key)

        r = requests.post(self._api_url + 'orders', json=payload, timeout=10)
        r.raise_for_status()
        return r.json()

client = FreeKassaClient(
    merchant_id=66058,
    secret_word_1='2aJ0hR?0Z-[=VJ6',
    secret_word_2='Hs)D3l&hb4(?xFf',
    api_key='962c879ce9be06f9d34a556872869220',
)
