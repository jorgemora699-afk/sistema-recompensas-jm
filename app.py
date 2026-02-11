from flask import Flask, render_template, request, redirect, url_for, flash, session
import database

app = Flask(__name__)
app.secret_key = 'clave_secreta_123'

# Inicializar la base de datos
database.inicializar_db()

# Reglas de negocio
PESOS_POR_PUNTO = 1000  # Por cada $1.000 pesos = 1 punto
PESOS_POR_REDENCION = 100  # 1 punto = $100 pesos

def calcular_puntos(monto_compra):
    """Calcula cuántos puntos se ganan por una compra"""
    puntos = int(monto_compra / PESOS_POR_PUNTO)
    return puntos

@app.route('/')
def index():
    """Página principal - Tienda"""
    productos = database.listar_productos()
    cliente_logueado = None
    
    if 'cedula' in session:
        cliente_logueado = database.obtener_cliente_por_cedula(session['cedula'])
    
    return render_template('index.html', productos=productos, cliente=cliente_logueado)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Iniciar sesión"""
    if request.method == 'POST':
        cedula = request.form['cedula']
        cliente = database.obtener_cliente_por_cedula(cedula)
        
        if cliente:
            session['cedula'] = cedula
            flash(f'¡Bienvenido {cliente[1]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Cliente no encontrado. Por favor regístrese.', 'error')
            return redirect(url_for('registrar_cliente'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.pop('cedula', None)
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('index'))

@app.route('/registrar_cliente', methods=['GET', 'POST'])
def registrar_cliente():
    """Registrar un nuevo cliente"""
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        
        if database.crear_cliente(nombre, cedula):
            session['cedula'] = cedula
            flash(f'¡Bienvenido {nombre}! Tu cuenta ha sido creada.', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Error: La cédula {cedula} ya está registrada', 'error')
    
    return render_template('registrar_cliente.html')

@app.route('/comprar/<int:producto_id>', methods=['GET', 'POST'])
def comprar(producto_id):
    """Página de compra con opción de redimir puntos"""
    if 'cedula' not in session:
        flash('Debes iniciar sesión para comprar', 'error')
        return redirect(url_for('login'))
    
    cliente = database.obtener_cliente_por_cedula(session['cedula'])
    producto = database.obtener_producto(producto_id)
    
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        puntos_a_usar = int(request.form.get('puntos_usar', 0))
        
        puntos_disponibles = cliente[3]
        precio_producto = producto[2]
        
        # Validar puntos
        if puntos_a_usar > puntos_disponibles:
            flash(f'Error: Solo tienes {puntos_disponibles} puntos disponibles', 'error')
            return redirect(url_for('comprar', producto_id=producto_id))
        
        # Calcular descuento
        descuento = puntos_a_usar * PESOS_POR_REDENCION
        
        if descuento > precio_producto:
            flash('Error: El descuento no puede ser mayor al precio del producto', 'error')
            return redirect(url_for('comprar', producto_id=producto_id))
        
        # Calcular precio final
        precio_final = precio_producto - descuento
        
        # Calcular puntos ganados por la compra
        puntos_ganados = calcular_puntos(precio_final)
        
        # Actualizar puntos: restar los usados y sumar los ganados
        nuevos_puntos = puntos_disponibles - puntos_a_usar + puntos_ganados
        
        database.actualizar_puntos(session['cedula'], nuevos_puntos)
        
        flash(f'¡Compra exitosa! Compraste {producto[1]} por ${precio_final:,}. Usaste {puntos_a_usar} puntos y ganaste {puntos_ganados} puntos nuevos. Total de puntos: {nuevos_puntos}', 'success')
        return redirect(url_for('index'))
    
    return render_template('comprar.html', producto=producto, cliente=cliente)

@app.route('/mis_puntos')
def mis_puntos():
    """Ver mis puntos"""
    if 'cedula' not in session:
        flash('Debes iniciar sesión', 'error')
        return redirect(url_for('login'))
    
    cliente = database.obtener_cliente_por_cedula(session['cedula'])
    return render_template('mis_puntos.html', cliente=cliente)

if __name__ == '__main__':
    app.run(debug=True)