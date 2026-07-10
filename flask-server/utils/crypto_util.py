import hashlib

class CryptoUtil:
    @staticmethod
    def md5(input_string):
        return hashlib.md5(input_string.encode('utf-8')).hexdigest()
