import requests
from requests.auth import HTTPBasicAuth


class MpesaBase:
    def __init__(self, env="sandbox", app_key=None, app_secret=None, sandbox_url="https://sandbox.safaricom.co.ke",
                 live_url="https://api.safaricom.co.ke"):
        self.env = env
        self.app_key = app_key
        self.app_secret = app_secret
        self.sandbox_url = sandbox_url
        self.live_url = live_url
        self.token = None
        self.headers = {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-Type': 'application/json'
        }
        self.validate_credentials()
        self.base_url = self.sandbox_url if self.env == "sandbox" else self.live_url
        self.api_version = "v1"
        self.api_endpoint = f"{self.base_url}/{self.api_version}"
        self.api_path = {}
        self.endpoint_path = {}
        self.response = None
        self.status_code = None
        self.error_message = None
        self.transaction_id = None

    def validate_credentials(self):
        if not self.app_key or not self.app_secret:
            raise ValueError("App Key and App Secret are required")
        if self.env == "sandbox" and not self.sandbox_url:
            raise ValueError("Sandbox URL is required for sandbox environment")
        if self.env == "production" and not self.live_url:
            raise ValueError("Live URL is required for production environment")
        return True
    
    def get_token(self):
        if not self.token or self.token_expired():
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            response = requests.get(url, auth=HTTPBasicAuth(self.app_key, self.app_secret))
            self.status_code = response.status_code
            self.response = response.json()
            if self.status_code == 200:
                self.token = self.response['access_token']
            else:
                raise ValueError(f"Error fetching token: {self.response['error_description']}")
        return self.token
