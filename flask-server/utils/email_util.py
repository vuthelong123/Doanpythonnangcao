import requests
from config import Config

class EmailUtil:
    @staticmethod
    def send(email, otp):
        try:
            payload = {
                "sender": {
                    "name": "ShopOnline",
                    "email": "vuthelong1009@gmail.com"
                },
                "to": [
                    {
                        "email": email
                    }
                ],
                "subject": "Signup | Verification (OTP)",
                "textContent": f"Your verification code is: {otp}"
            }
            
            headers = {
                "api-key": Config.BREVO_API_KEY,
                "Content-Type": "application/json"
            }
            
            response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
            response.raise_for_status()
            return True
        except Exception as err:
            print("Email Error:", err)
            raise err
