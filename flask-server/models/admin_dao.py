from database import execute_query

class AdminDAO:
    @staticmethod
    def select_by_username_and_password(username, password):
        query = "SELECT * FROM admin WHERE username=%s AND password=%s"
        return execute_query(query, (username, password), fetchone=True)
