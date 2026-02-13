from flask import Flask, render_template, request, redirect, url_for, flash, session
import database
import re

app = Flask(__name__)
app.secret_key = 'pb202602'

# Initialize database
database.initialize_database()

# Business rules
PESOS_PER_POINT = 1000  # $1,000 pesos = 1 point
PESOS_PER_REDEMPTION = 100  # 1 point = $100 pesos

def calculate_points(purchase_amount):
    """Calculates how many points are earned from a purchase"""
    points = int(purchase_amount / PESOS_PER_POINT)
    return points

def validate_id_card(id_card):
    """Validates ID card format (only numbers, 6-12 digits)"""
    if not id_card:
        return False, "ID card is required"
    if not re.match(r'^\d{6,12}$', id_card):
        return False, "ID card must contain only numbers (6-12 digits)"
    return True, ""

def validate_name(name):
    """Validates customer name (letters and spaces only, 3-50 characters)"""
    if not name:
        return False, "Name is required"
    if len(name.strip()) < 3:
        return False, "Name must be at least 3 characters"
    if len(name.strip()) > 50:
        return False, "Name cannot exceed 50 characters"
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', name):
        return False, "Name must contain only letters and spaces"
    return True, ""

def validate_points(points_str, available_points):
    """Validates points to redeem"""
    try:
        points = int(points_str)
        if points < 0:
            return False, "Points cannot be negative", 0
        if points > available_points:
            return False, f"You only have {available_points} points available", 0
        return True, "", points
    except ValueError:
        return False, "Points must be a valid number", 0

@app.route('/')
def index():
    """Main page - Store"""
    products = database.list_all_products()
    logged_customer = None
    
    if 'id_card' in session:
        logged_customer = database.get_customer_by_id_card(session['id_card'])
    
    return render_template('index.html', products=products, customer=logged_customer)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login"""
    if request.method == 'POST':
        id_card = request.form.get('id_card', '').strip()
        
        # Validate ID card
        is_valid, error_message = validate_id_card(id_card)
        if not is_valid:
            flash(error_message, 'error')
            return render_template('login.html')
        
        customer = database.get_customer_by_id_card(id_card)
        
        if customer:
            session['id_card'] = id_card
            flash(f'Welcome {customer[1]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Customer not found. Please register.', 'error')
            return redirect(url_for('register_customer'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('id_card', None)
    flash('Session closed successfully', 'success')
    return redirect(url_for('index'))

@app.route('/register_customer', methods=['GET', 'POST'])
def register_customer():
    """Register a new customer"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        id_card = request.form.get('id_card', '').strip()
        
        # Validate name
        is_valid, error_message = validate_name(name)
        if not is_valid:
            flash(error_message, 'error')
            return render_template('register_customer.html')
        
        # Validate ID card
        is_valid, error_message = validate_id_card(id_card)
        if not is_valid:
            flash(error_message, 'error.')
            return render_template('register_customer.html')
        
        # Create customer
        if database.create_customer(name, id_card):
            session['id_card'] = id_card
            flash(f'Welcome {name}! Your account has been created successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Error: ID card {id_card} is already registered', 'error')
    
    return render_template('register_customer.html')

@app.route('/purchase/<int:product_id>', methods=['GET', 'POST'])
def purchase(product_id):
    """Purchase page with option to redeem points"""
    if 'id_card' not in session:
        flash('You must login to purchase', 'error')
        return redirect(url_for('login'))
    
    customer = database.get_customer_by_id_card(session['id_card'])
    product = database.get_product_by_id(product_id)
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        points_to_use_str = request.form.get('points_to_use', '0')
        
        available_points = customer[3]
        product_price = product[2]
        
        # Validate points
        is_valid, error_message, points_to_use = validate_points(points_to_use_str, available_points)
        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('purchase', product_id=product_id))
        
        # Calculate discount
        discount = points_to_use * PESOS_PER_REDEMPTION
        
        # Validate discount doesn't exceed product price
        if discount > product_price:
            flash('Error: Discount cannot exceed product price', 'error')
            return redirect(url_for('purchase', product_id=product_id))
        
        # Calculate final price
        final_price = product_price - discount
        
        # Calculate points earned from purchase
        points_earned = calculate_points(final_price)
        
        # Update points: subtract used and add earned
        new_points = available_points - points_to_use + points_earned
        
        database.update_points(session['id_card'], new_points)
        
        flash(f'Purchase successful! You bought {product[1]} for ${final_price:,}. You used {points_to_use} points and earned {points_earned} new points. Total points: {new_points}', 'success')
        return redirect(url_for('index'))
    
    return render_template('purchase.html', product=product, customer=customer)

@app.route('/my_points')
def my_points():
    """View my points"""
    if 'id_card' not in session:
        flash('You must login', 'error')
        return redirect(url_for('login'))
    
    customer = database.get_customer_by_id_card(session['id_card'])
    return render_template('my_points.html', customer=customer)

if __name__ == '__main__':
    app.run(debug=True)