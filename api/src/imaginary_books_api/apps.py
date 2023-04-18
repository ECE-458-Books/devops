import requests, os
import json
from dotenv import dotenv_values
from pathlib import Path

class Postman:
    """
    [API Endpoint, Content-Type, Need Authorization]
    """
    METHOD_TO_ENDPOINT = {
        'login'     : ['/auth/users/login', 'application/json', False],
        'book_add'  : ['/books', 'application/json', True]
    }

    def __init__(
        self,
    ):
        self.load_envvars()
        self.login()
    
    def load_envvars(self):
        self._env = dotenv_values(".env")
        self._endpoint = f"https://{self._env.get('HOST')}/api/v1"

    def login(self):
        login_data = {
            "username" : self._env['USERNAME'],
            "password" : self._env['PASSWORD']
        }
        response = self.post('login', login_data)

        self._refresh_token = response['refresh']
        self._access_token = response['access']

    def post(
        self,
        method: str,
        data,
    ):
        url = self.create_url(method)
        payload, image = self.create_payload(method, data)
        files = self.create_files(method, data, image)
        headers = self.create_headers(method, image)
        # response = requests.request("POST", url, headers=headers, data=payload, files=files)
        response = requests.request("POST", url, headers=headers, data=payload)

        return json.loads(response.text)
    
    def create_files(
        self,
        method: str,
        data,
        image,
    ):
        download_abs_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..', 'images'))
        if (method == 'book_add') and (image != ''):
            image_file = [('image', (image, open(f"{download_abs_path}/{image}", "rb")))]
            return image_file
        return ''
    
    def create_payload(
        self,
        method: str,
        data: dict,
    ):
        image = ''
        if(method == 'book_add'):
            if 'image' in data:
                image = data.pop('image')
                return data, image

        return json.dumps(data), image

    def create_url(
        self,
        method: str,
    ):
        return self._endpoint + self.METHOD_TO_ENDPOINT.get(method)[0]

    def create_headers(
        self,
        method: str,
        image: str
    ):
        headers = {}
        if(self.METHOD_TO_ENDPOINT.get(method)[1] != ''):
            if image == '':
                headers['Content-Type'] = self.METHOD_TO_ENDPOINT.get(method)[1]
        if(self.METHOD_TO_ENDPOINT.get(method)[2]):
            headers['Authorization'] = f'Bearer {self.get_access_token()}'
        
        return headers

    def get_access_token(
        self,
    ):
        return self._access_token