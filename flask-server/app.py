import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from api.admin_api import admin_api
from api.customer_api import customer_api

app = Flask(__name__, static_folder='../client-customer/build', static_url_path='/')
CORS(app)

# JSON size limit workaround
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 # 10MB

# API Registration
app.register_blueprint(admin_api, url_prefix='/api/admin')
app.register_blueprint(customer_api, url_prefix='/api/customer')

@app.route('/hello')
def hello():
    return {'message': 'Hello from Flask server!'}

# Serve admin build
@app.route('/admin/', defaults={'path': ''})
@app.route('/admin/<path:path>')
def serve_admin(path):
    admin_build_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../client-admin/build'))
    
    if path != "" and os.path.exists(os.path.join(admin_build_path, path)):
        return send_from_directory(admin_build_path, path)
    else:
        return send_from_directory(admin_build_path, 'index.html')

# Serve customer build for all other routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_customer(path):
    customer_build_path = app.static_folder
    
    if path != "" and os.path.exists(os.path.join(customer_build_path, path)):
        return send_from_directory(customer_build_path, path)
    else:
        return send_from_directory(customer_build_path, 'index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"Flask Server listening on {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
