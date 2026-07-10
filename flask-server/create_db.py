import mysql.connector
from config import Config

def create_database():
    try:
        # Connect to MySQL server without selecting a database first
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASS
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_DATABASE} CHARACTER SET utf8mb4")
        cursor.execute(f"USE {Config.DB_DATABASE}")
        
        # Create tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS admin (
              id INT AUTO_INCREMENT PRIMARY KEY,
              username VARCHAR(100) NOT NULL UNIQUE,
              password VARCHAR(255) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS category (
              id INT AUTO_INCREMENT PRIMARY KEY,
              name VARCHAR(255) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS product (
              id INT AUTO_INCREMENT PRIMARY KEY,
              name VARCHAR(255) NOT NULL,
              price DECIMAL(15,2) NOT NULL,
              image TEXT,
              cdate BIGINT,
              description TEXT,
              category_id INT,
              FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS customer (
              id INT AUTO_INCREMENT PRIMARY KEY,
              username VARCHAR(100) NOT NULL,
              password VARCHAR(255) NOT NULL,
              name VARCHAR(255),
              phone VARCHAR(20),
              email VARCHAR(255) NOT NULL UNIQUE,
              active TINYINT DEFAULT 0,
              token VARCHAR(500),
              otp VARCHAR(10),
              otp_expire BIGINT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS orders (
              id INT AUTO_INCREMENT PRIMARY KEY,
              cdate BIGINT,
              total DECIMAL(15,2),
              status VARCHAR(50) DEFAULT 'PENDING',
              customer_id INT,
              FOREIGN KEY (customer_id) REFERENCES customer(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS order_items (
              id INT AUTO_INCREMENT PRIMARY KEY,
              order_id INT,
              product_id INT,
              quantity INT,
              product_name VARCHAR(255),
              product_price DECIMAL(15,2),
              product_image TEXT,
              category_id INT,
              category_name VARCHAR(255),
              FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
              FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE SET NULL
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
            
        # Insert default admin user if not exists
        cursor.execute("SELECT COUNT(*) as cnt FROM admin WHERE username='admin'")
        res = cursor.fetchone()
        if res[0] == 0:
            cursor.execute("INSERT INTO admin (username, password) VALUES ('admin', '123')")
            print("Đã tạo tài khoản admin/123")
            
        conn.commit()
        print("Tạo database và bảng thành công!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    create_database()
