from database import execute_query

class ProductDAO:
    @staticmethod
    def _map_category(product):
        if product and 'category_id' in product:
            query = "SELECT * FROM category WHERE id=%s"
            cat = execute_query(query, (product['category_id'],), fetchone=True)
            product['category'] = cat
        return product

    @staticmethod
    def select_all():
        query = "SELECT * FROM product"
        products = execute_query(query, fetchall=True)
        return [ProductDAO._map_category(p) for p in products]

    @staticmethod
    def select_by_id(_id):
        query = "SELECT * FROM product WHERE id=%s"
        product = execute_query(query, (_id,), fetchone=True)
        return ProductDAO._map_category(product)

    @staticmethod
    def insert(product):
        query = """INSERT INTO product (name, price, image, cdate, description, category_id) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        cat_id = product['category']['_id'] if 'category' in product and product['category'] else None
        
        # fallback for missing description
        desc = product.get('description', '') 
        
        new_id = execute_query(query, (
            product['name'], product['price'], product['image'], 
            product['cdate'], desc, cat_id
        ), insert=True)
        
        if new_id:
            product['_id'] = new_id
            return product
        return None

    @staticmethod
    def update(product):
        query = """UPDATE product SET name=%s, price=%s, image=%s, cdate=%s, description=%s, category_id=%s
                   WHERE id=%s"""
        cat_id = product['category']['_id'] if 'category' in product and product['category'] else None
        desc = product.get('description', '')
        
        execute_query(query, (
            product['name'], product['price'], product['image'], 
            product.get('cdate', 0), desc, cat_id, product['_id']
        ))
        return product

    @staticmethod
    def delete(_id):
        query = "DELETE FROM product WHERE id=%s"
        execute_query(query, (_id,))
        return True

    @staticmethod
    def select_top_new(top):
        query = "SELECT * FROM product ORDER BY cdate DESC LIMIT %s"
        products = execute_query(query, (top,), fetchall=True)
        return [ProductDAO._map_category(p) for p in products]

    @staticmethod
    def select_top_hot(top):
        query = """
            SELECT product_id as id, SUM(quantity) as sum 
            FROM order_items 
            JOIN orders ON order_items.order_id = orders.id 
            WHERE orders.status = 'APPROVED' 
            GROUP BY product_id 
            ORDER BY sum DESC 
            LIMIT %s
        """
        top_items = execute_query(query, (top,), fetchall=True)
        products = []
        for item in top_items:
            product = ProductDAO.select_by_id(item['id'])
            if product:
                products.append(product)
        return products

    @staticmethod
    def select_by_cat_id(_cid):
        query = "SELECT * FROM product WHERE category_id = %s"
        products = execute_query(query, (_cid,), fetchall=True)
        return [ProductDAO._map_category(p) for p in products]

    @staticmethod
    def select_by_keyword(keyword):
        query = "SELECT * FROM product WHERE name LIKE %s"
        pattern = f"%{keyword}%"
        products = execute_query(query, (pattern,), fetchall=True)
        return [ProductDAO._map_category(p) for p in products]
