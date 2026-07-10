import os

class Config:
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASS = os.environ.get('DB_PASSWORD', '123456') # Sửa lại thành mật khẩu MySQL của bạn nếu có
    DB_DATABASE = os.environ.get('DB_NAME', 'shoppingonline')
    JWT_SECRET = '70addbf370449269b7685058e81215444314830c3b28783ce0a1551277b647391e14832be3610ffb17cc5ab91470de9ff385a63ee0523128a72455a6d1d7941e'
    JWT_EXPIRES_MINUTES = 600 # 10 hours
    # Hãy lấy api-key từ file .env ở NodeJS cũ (hoặc tài khoản Brevo) và dán vào đây:
    BREVO_API_KEY = "ĐIỀN-KEY-CỦA-BẠN-VÀO-ĐÂY"
