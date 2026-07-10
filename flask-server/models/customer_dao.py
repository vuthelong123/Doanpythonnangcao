from database import execute_query

class CustomerDAO:
    @staticmethod
    def select_by_username_or_email(username, email):
        query = "SELECT * FROM customer WHERE username=%s OR email=%s"
        return execute_query(query, (username, email), fetchone=True)

    @staticmethod
    def insert(customer):
        query = """INSERT INTO customer (username, password, name, phone, email, active, token, otp, otp_expire)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        new_id = execute_query(query, (
            customer['username'], customer['password'], customer.get('name', ''), 
            customer.get('phone', ''), customer['email'], customer.get('active', 0), 
            customer.get('token', ''), customer.get('otp', ''), customer.get('otp_expire', 0)
        ), insert=True)
        
        if new_id:
            customer['_id'] = new_id
            return customer
        return None

    @staticmethod
    def select_by_email(email):
        query = "SELECT * FROM customer WHERE email=%s"
        return execute_query(query, (email,), fetchone=True)

    @staticmethod
    def active_by_otp(_id):
        query = "UPDATE customer SET active=1, otp='', otp_expire=0 WHERE id=%s"
        execute_query(query, (_id,))
        return True

    @staticmethod
    def active(_id, token, active_status):
        # Admin disable/enable customer
        query = "UPDATE customer SET active=%s, token=%s WHERE id=%s"
        execute_query(query, (active_status, token, _id))
        return True

    @staticmethod
    def select_by_username_and_password(username, password):
        query = "SELECT * FROM customer WHERE username=%s AND password=%s"
        return execute_query(query, (username, password), fetchone=True)

    @staticmethod
    def update(customer):
        query = """UPDATE customer SET username=%s, password=%s, name=%s, phone=%s, email=%s 
                   WHERE id=%s"""
        execute_query(query, (
            customer['username'], customer['password'], customer.get('name', ''), 
            customer.get('phone', ''), customer['email'], customer['_id']
        ))
        return customer

    @staticmethod
    def select_all():
        query = "SELECT * FROM customer"
        return execute_query(query, fetchall=True)

    @staticmethod
    def select_by_id(_id):
        query = "SELECT * FROM customer WHERE id=%s"
        return execute_query(query, (_id,), fetchone=True)
