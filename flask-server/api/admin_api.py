from flask import Blueprint, request, jsonify
import time
import math

from utils.jwt_util import gen_token, check_token
from utils.email_util import EmailUtil

from models.admin_dao import AdminDAO
from models.category_dao import CategoryDAO
from models.product_dao import ProductDAO
from models.order_dao import OrderDAO
from models.customer_dao import CustomerDAO

admin_api = Blueprint('admin_api', __name__)

# ================= LOGIN =================
@admin_api.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if username and password:
        admin = AdminDAO.select_by_username_and_password(username, password)
        if admin:
            token = gen_token(username, password)
            return jsonify({'success': True, 'message': 'Xác thực thành công', 'token': token})
        else:
            return jsonify({'success': False, 'message': 'Sai tài khoản hoặc mật khẩu'})
    else:
        return jsonify({'success': False, 'message': 'Vui lòng nhập tài khoản và mật khẩu'})

@admin_api.route('/token', methods=['GET'])
@check_token
def token():
    token_val = request.headers.get('x-access-token') or request.headers.get('authorization')
    return jsonify({'success': True, 'message': 'Token hợp lệ', 'token': token_val})

# ================= CATEGORY =================
@admin_api.route('/categories', methods=['GET'])
@check_token
def get_categories():
    categories = CategoryDAO.select_all()
    return jsonify(categories)

@admin_api.route('/categories', methods=['POST'])
@check_token
def add_category():
    data = request.json or {}
    result = CategoryDAO.insert({'name': data.get('name')})
    return jsonify(result if result else {})

@admin_api.route('/categories/<int:id>', methods=['PUT'])
@check_token
def update_category(id):
    data = request.json or {}
    category = {'_id': id, 'name': data.get('name')}
    result = CategoryDAO.update(category)
    return jsonify(result)

@admin_api.route('/categories/<int:id>', methods=['DELETE'])
@check_token
def delete_category(id):
    result = CategoryDAO.delete(id)
    return jsonify({'success': result})

# ================= PRODUCT =================
@admin_api.route('/products', methods=['GET'])
@check_token
def get_products():
    products = ProductDAO.select_all()
    sizePage = 4
    noPages = math.ceil(len(products) / sizePage)
    
    curPage = 1
    if request.args.get('page'):
        curPage = int(request.args.get('page'))
        
    offset = (curPage - 1) * sizePage
    paged_products = products[offset : offset + sizePage]
    
    return jsonify({'products': paged_products, 'noPages': noPages, 'curPage': curPage})

@admin_api.route('/products', methods=['POST'])
@check_token
def add_product():
    data = request.json or {}
    category = CategoryDAO.select_by_id(data.get('category'))
    
    product = {
        'name': data.get('name'),
        'price': data.get('price'),
        'image': data.get('image'),
        'description': data.get('description'),
        'cdate': int(time.time() * 1000),
        'category': category
    }
    result = ProductDAO.insert(product)
    return jsonify(result if result else {})

@admin_api.route('/products/<int:id>', methods=['PUT'])
@check_token
def update_product(id):
    data = request.json or {}
    category = CategoryDAO.select_by_id(data.get('category'))
    
    product = {
        '_id': id,
        'name': data.get('name'),
        'price': data.get('price'),
        'image': data.get('image'),
        'description': data.get('description'),
        'category': category
    }
    result = ProductDAO.update(product)
    return jsonify(result)

@admin_api.route('/products/<int:id>', methods=['DELETE'])
@check_token
def delete_product(id):
    result = ProductDAO.delete(id)
    return jsonify({'success': result})

# ================= CUSTOMER =================
@admin_api.route('/customers', methods=['GET'])
@check_token
def get_customers():
    customers = CustomerDAO.select_all()
    return jsonify(customers)

@admin_api.route('/customers/sendmail/<int:id>', methods=['GET'])
@check_token
def sendmail(id):
    cust = CustomerDAO.select_by_id(id)
    if cust:
        try:
            EmailUtil.send(cust['email'], str(cust.get('otp', '')))
            return jsonify({'success': True, 'message': 'Vui lòng kiểm tra email'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Lỗi gửi email'})
    else:
        return jsonify({'success': False, 'message': 'Khách hàng không tồn tại'})

@admin_api.route('/customers/deactive/<int:id>', methods=['PUT'])
@check_token
def deactive_customer(id):
    data = request.json or {}
    token = data.get('token')
    result = CustomerDAO.active(id, token, 0)
    return jsonify({'success': result})

# ================= ORDER =================
@admin_api.route('/orders', methods=['GET'])
@check_token
def get_orders():
    orders = OrderDAO.select_all()
    return jsonify(orders)

@admin_api.route('/orders/customer/<int:cid>', methods=['GET'])
@check_token
def get_customer_orders(cid):
    orders = OrderDAO.select_by_cust_id(cid)
    return jsonify(orders)

@admin_api.route('/orders/status/<int:id>', methods=['PUT'])
@check_token
def update_order_status(id):
    data = request.json or {}
    result = OrderDAO.update(id, data.get('status'))
    return jsonify(result)
