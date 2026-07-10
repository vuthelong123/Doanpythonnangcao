from database import execute_query

class CategoryDAO:
    @staticmethod
    def select_all():
        query = "SELECT * FROM category"
        return execute_query(query, fetchall=True)

    @staticmethod
    def select_by_id(_id):
        query = "SELECT * FROM category WHERE id=%s"
        return execute_query(query, (_id,), fetchone=True)

    @staticmethod
    def insert(category):
        query = "INSERT INTO category (name) VALUES (%s)"
        new_id = execute_query(query, (category['name'],), insert=True)
        if new_id:
            category['_id'] = new_id
            return category
        return None

    @staticmethod
    def update(category):
        query = "UPDATE category SET name=%s WHERE id=%s"
        execute_query(query, (category['name'], category['_id']))
        return category

    @staticmethod
    def delete(_id):
        query = "DELETE FROM category WHERE id=%s"
        execute_query(query, (_id,))
        return True
