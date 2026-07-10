from flask import Blueprint, request, jsonify
import time
import random
import os
import google.generativeai as genai

from utils.jwt_util import gen_token, check_token
from utils.email_util import EmailUtil

from models.category_dao import CategoryDAO
from models.product_dao import ProductDAO
from models.customer_dao import CustomerDAO
from models.order_dao import OrderDAO

customer_api = Blueprint('customer_api', __name__)

# --- CATEGORY API ---
@customer_api.route('/categories', methods=['GET'])
def get_categories():
    categories = CategoryDAO.select_all()
    return jsonify(categories)

# --- PRODUCT API ---
@customer_api.route('/products/new', methods=['GET'])
def get_new_products():
    products = ProductDAO.select_top_new(8)
    return jsonify(products)

@customer_api.route('/products/hot', methods=['GET'])
def get_hot_products():
    products = ProductDAO.select_top_hot(8)
    return jsonify(products)

@customer_api.route('/products/category/<int:cid>', methods=['GET'])
def get_category_products(cid):
    products = ProductDAO.select_by_cat_id(cid)
    return jsonify(products)

@customer_api.route('/products/search/<keyword>', methods=['GET'])
def search_products(keyword):
    products = ProductDAO.select_by_keyword(keyword)
    return jsonify(products)

@customer_api.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = ProductDAO.select_by_id(id)
    return jsonify(product)

# --- CUSTOMER API ---
@customer_api.route('/signup', methods=['POST'])
def signup():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')

    db_cust = CustomerDAO.select_by_username_or_email(username, email)
    if db_cust:
        return jsonify({'success': False, 'message': 'Tài khoản hoặc email đã tồn tại'})
    else:
        otp = str(random.randint(100000, 999999))
        otp_expire = int(time.time()*1000) + 5 * 60 * 1000 # 5 mins

        new_cust = {
            'username': username,
            'password': password,
            'name': name,
            'phone': phone,
            'email': email,
            'active': 0,
            'token': '',
            'otp': otp,
            'otp_expire': otp_expire
        }

        result = CustomerDAO.insert(new_cust)
        if result:
            try:
                EmailUtil.send(email, otp)
                return jsonify({'success': True, 'message': 'Thành công, vui lòng kiểm tra email để lấy mã OTP.'})
            except Exception as e:
                print(f"Lỗi gửi email API. MÃ OTP CỦA BẠN LÀ: {otp}")
                # Vẫn trả về True để cho phép web nhảy sang màn hình nhập OTP
                return jsonify({'success': True, 'message': 'Để xem mã OTP, vui lòng mở Terminal!'})
        else:
            return jsonify({'success': False, 'message': 'Thêm thất bại'})

@customer_api.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json or {}
    email = data.get('email')
    otp = data.get('otp')

    customer = CustomerDAO.select_by_email(email)
    if customer:
        if str(customer.get('otp')) == str(otp):
            if int(time.time()*1000) < customer.get('otp_expire', 0):
                CustomerDAO.active_by_otp(customer['_id'])
                return jsonify({'success': True, 'message': 'Thành công'})
            else:
                return jsonify({'success': False, 'message': 'Mã xác thực đã hết hạn'})
        else:
            return jsonify({'success': False, 'message': 'Mã xác thực không đúng'})
    else:
        return jsonify({'success': False, 'message': 'Tài khoản không tồn tại'})

@customer_api.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if username and password:
        customer = CustomerDAO.select_by_username_and_password(username, password)
        if customer:
            if customer.get('active') == 1:
                token = gen_token(username, password)
                return jsonify({'success': True, 'message': 'Thành công', 'token': token, 'customer': customer})
            else:
                return jsonify({'success': False, 'message': 'Tài khoản chưa được xác thực'})
        else:
            return jsonify({'success': False, 'message': 'Sai tài khoản hoặc mật khẩu'})
    else:
        return jsonify({'success': False, 'message': 'Vui lòng nhập tài khoản và mật khẩu'})

@customer_api.route('/token', methods=['GET'])
@check_token
def token():
    token_val = request.headers.get('x-access-token') or request.headers.get('authorization')
    return jsonify({'success': True, 'message': 'Token hợp lệ', 'token': token_val})

@customer_api.route('/customers/<int:id>', methods=['PUT'])
@check_token
def update_profile(id):
    data = request.json or {}
    customer = {
        '_id': id,
        'username': data.get('username'),
        'password': data.get('password'),
        'name': data.get('name'),
        'phone': data.get('phone'),
        'email': data.get('email')
    }
    result = CustomerDAO.update(customer)
    return jsonify(result)

# --- CHECKOUT ---
@customer_api.route('/checkout', methods=['POST'])
@check_token
def checkout():
    data = request.json or {}
    now = int(time.time()*1000)
    total = data.get('total')
    items = data.get('items')
    customer = data.get('customer')

    order = {
        'cdate': now,
        'total': total,
        'status': 'PENDING',
        'customer': customer,
        'items': items
    }

    result = OrderDAO.insert(order)
    return jsonify(result if result else {})

# --- MY ORDERS ---
@customer_api.route('/orders/customer/<int:cid>', methods=['GET'])
@check_token
def my_orders(cid):
    orders = OrderDAO.select_by_cust_id(cid)
    return jsonify(orders)

# --- CHATBOT API ---
@customer_api.route('/chat', methods=['POST'])
def chat_with_bot():
    data = request.json or {}
    user_message = data.get('message', '')
    
    if not user_message:
         return jsonify({'reply': 'Xin chào, tôi có thể giúp gì cho bạn?'})

    try:
        if not os.environ.get("GEMINI_API_KEY"):
            # Set this using an environment variable if possible, or paste the key to try locally
            # genai.configure(api_key="PASTE_YOUR_API_KEY_HERE_FOR_TESTING")
            pass
            
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyBevXx1IboO3jdUuxkx4OXCIf9o48QNpZs"))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        products = ProductDAO.select_all()
        products_info = ""
        for p in products:
            cat_name = p['category']['name'] if 'category' in p and p['category'] else 'Khác'
            products_info += f"- {p['name']} (Giá: {p['price']} đ, Danh mục: {cat_name}). Mô tả: {p.get('description', '')}\n"
            
        system_prompt = f"""
Bạn là một trợ lý ảo tư vấn bán hàng của một cửa hàng Laptop.
Dưới đây là danh sách các sản phẩm đang có của cửa hàng:
{products_info}

Hãy tư vấn cho khách hàng bằng tiếng Việt một cách thân thiện, nhiệt tình.
Lưu ý:
- Chỉ gợi ý các sản phẩm có trong danh sách trên.
- Nếu khách hàng hỏi sản phẩm mà cửa hàng không có, hãy lịch sự thông báo và gợi ý các sản phẩm tương tự.
- Trả lời ngắn gọn, tự nhiên, không liệt kê toàn bộ danh sách trừ khi được yêu cầu.

Câu hỏi của khách hàng: {user_message}
"""
        
        response = model.generate_content(system_prompt)
        reply_text = response.text
        
        return jsonify({'reply': reply_text})
    except Exception as e:
        print("Chatbot Error:", e)
        return jsonify({'reply': 'Xin lỗi, hiện tại tôi đang gặp sự cố. Vui lòng liên hệ trực tiếp với nhân viên qua hotline!'})
