import sqlite3

def inicializar_db():
    """Crea la base de datos y las tablas si no existen"""
    conn = sqlite3.connect('recompensas.db')
    cursor = conn.cursor()
    
    # Tabla de clientes con cédula
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            puntos INTEGER DEFAULT 0
        )
    ''')
    
    # Tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio INTEGER NOT NULL
        )
    ''')
    
    # Insertar productos iniciales si no existen
    cursor.execute('SELECT COUNT(*) FROM productos')
    if cursor.fetchone()[0] == 0:
        productos_iniciales = [
            ('Laptop Dell Inspiron 15', 2500000),
            ('Mouse Logitech MX Master', 250000),
            ('Teclado Mecánico Razer', 450000),
            ('Monitor Samsung 24"', 800000),
            ('Auriculares Sony WH-1000XM5', 1200000),
            ('Tablet Samsung Galaxy Tab', 1500000),
            ('Webcam Logitech C920', 350000),
            ('Disco Duro Externo 2TB', 300000),
            ('Impresora HP LaserJet', 900000),
            ('Router WiFi 6 TP-Link', 400000)
        ]
        cursor.executemany('INSERT INTO productos (nombre, precio) VALUES (?, ?)', productos_iniciales)
    
    conn.commit()
    conn.close()

def obtener_cliente_por_cedula(cedula):
    """Busca un cliente por cédula"""
    conn = sqlite3.connect('recompensas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM clientes WHERE cedula = ?', (cedula,))
    cliente = cursor.fetchone()
    
    conn.close()
    return cliente

def crear_cliente(nombre, cedula):
    """Crea un nuevo cliente con 0 puntos"""
    conn = sqlite3.connect('recompensas.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO clientes (nombre, cedula, puntos) VALUES (?, ?, 0)', (nombre, cedula))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # La cédula ya existe

def actualizar_puntos(cedula, puntos):
    """Actualiza los puntos de un cliente"""
    conn = sqlite3.connect('recompensas.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE clientes SET puntos = ? WHERE cedula = ?', (puntos, cedula))
    
    conn.commit()
    conn.close()

def listar_clientes():
    """Obtiene todos los clientes"""
    conn = sqlite3.connect('recompensas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()
    
    conn.close()
    return clientes

def listar_productos():
    """Obtiene todos los productos"""
    conn = sqlite3.connect('recompensas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    
    conn.close()
    return productos

def obtener_producto(producto_id):
    """Obtiene un producto por ID"""
    conn = sqlite3.connect('recompensas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
    producto = cursor.fetchone()
    
    conn.close()
    return producto