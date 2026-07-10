import time
from database import execute_query
from models.customer_dao import CustomerDAO

class OrderDAO:
    @staticmethod
    def _map_order_items(order):
        if not order: return order
        
        # Lấy customer
        cust = CustomerDAO.select_by_id(order['customer_id'])
        order['customer'] = cust
        
        # Lấy items
        query = "SELECT * FROM order_items WHERE order_id=%s"
        items = execute_query(query, (order['_id'],), fetchall=True)
        
        mapped_items = []
        for it in items:
            mapped_items.append({
                'product': {
                    '_id': it['product_id'],
                    'name': it['product_name'],
                    'price': float(it['product_price']) if it['product_price'] else 0,
                    'image': it['product_image'],
                    'category': {
                        '_id': it['category_id'],
                        'name': it['category_name']
                    } if it['category_id'] else None
                },
                'quantity': it['quantity']
            })
            
        order['items'] = mapped_items
        return order

    @staticmethod
    def insert(order):
        query_order = """INSERT INTO orders (cdate, total, status, customer_id) 
                         VALUES (%s, %s, %s, %s)"""
        order_id = execute_query(query_order, (
            order.get('cdate', int(time.time()*1000)), 
            order.get('total', 0), 
            order.get('status', 'PENDING'), 
            order['customer']['_id']
        ), insert=True)
        
        if order_id:
            order['_id'] = order_id
            query_item = """INSERT INTO order_items (order_id, product_id, quantity, 
                            product_name, product_price, product_image, category_id, category_name) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            for item in order.get('items', []):
                prod = item.get('product', {})
                cat = prod.get('category', {})
                execute_query(query_item, (
                    order_id, 
                    prod.get('_id'), 
                    item.get('quantity', 1),
                    prod.get('name'), 
                    prod.get('price'), 
                    prod.get('image'),
                    cat.get('_id') if cat else None,
                    cat.get('name') if cat else None
                ), insert=True)
            return order
        return None

    @staticmethod
    def select_by_cust_id(_cid):
        query = "SELECT * FROM orders WHERE customer_id=%s ORDER BY cdate DESC"
        orders = execute_query(query, (_cid,), fetchall=True)
        return [OrderDAO._map_order_items(o) for o in orders]

    @staticmethod
    def select_all():
        query = "SELECT * FROM orders ORDER BY cdate DESC"
        orders = execute_query(query, fetchall=True)
        return [OrderDAO._map_order_items(o) for o in orders]

    @staticmethod
    def update(_id, new_status):
        query = "UPDATE orders SET status=%s WHERE id=%s"
        execute_query(query, (new_status, _id))
        
        # return updated order
        query_get = "SELECT * FROM orders WHERE id=%s"
        order = execute_query(query_get, (_id,), fetchone=True)
        return OrderDAO._map_order_items(order)
