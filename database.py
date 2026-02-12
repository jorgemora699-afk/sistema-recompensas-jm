import sqlite3

def initialize_database():
    """Creates the database and tables if they don't exist"""
    conn = sqlite3.connect('rewards.db')
    cursor = conn.cursor()
    
    # Customers table with ID card
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            id_card TEXT UNIQUE NOT NULL,
            points INTEGER DEFAULT 0
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            image_url TEXT DEFAULT '/static/images/default-product.jpg'
        )
    ''')
    
    # Insert initial products if none exist
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        initial_products = [
            ('Dell Inspiron 15 Laptop', 2500000, '/static/images/inspirion.jpg'),
            ('Logitech MX Master Mouse', 250000, '/static/images/mouse.jpg'),
            ('Razer Mechanical Keyboard', 450000, '/static/images/keyboard.jpg'),
            ('Samsung 24" Monitor', 800000, '/static/images/monitor 24.jpg'),
            ('Sony WH-1000XM5 Headphones', 1200000, '/static/images/headphones.jpg'),
            ('Samsung Galaxy Tab Tablet', 1500000, '/static/images/tab.jpg'),
            ('Logitech C920 Webcam', 350000, '/static/images/cam.jpg'),
            ('2TB External Hard Drive', 300000, '/static/images/hard drive.jpg'),
            ('HP LaserJet Printer', 900000, '/static/images/print.jpg'),
            ('TP-Link WiFi 6 Router', 400000, '/static/images/router.jpg')
        ]
        cursor.executemany('INSERT INTO products (name, price, image_url) VALUES (?, ?, ?)', initial_products)
    
    conn.commit()
    conn.close()

def get_customer_by_id_card(id_card):
    """Finds a customer by ID card"""
    conn = sqlite3.connect('rewards.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers WHERE id_card = ?', (id_card,))
    customer = cursor.fetchone()
    
    conn.close()
    return customer

def create_customer(name, id_card):
    """Creates a new customer with 0 points"""
    conn = sqlite3.connect('rewards.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO customers (name, id_card, points) VALUES (?, ?, 0)', (name, id_card))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # ID card already exists

def update_points(id_card, points):
    """Updates customer points"""
    conn = sqlite3.connect('rewards.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE customers SET points = ? WHERE id_card = ?', (points, id_card))
    
    conn.commit()
    conn.close()

def list_all_customers():
    """Gets all customers"""
    conn = sqlite3.connect('rewards.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    
    conn.close()
    return customers

def list_all_products():
    """Gets all products"""
    conn = sqlite3.connect('rewards.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    conn.close()
    return products

def get_product_by_id(product_id):
    """Gets a product by ID"""
    conn = sqlite3.connect('rewards.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    
    conn.close()
    return product