from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# 🚨 Imports para la CORRECCIÓN DE RUTA (TemplateNotFound Fix)
import os
from pathlib import Path

# --- Configuración Inicial ---

# 🛠️ Solución para TemplateNotFound: Define la ruta absoluta de la carpeta 'templates'
BASE_DIR = Path(__file__).parent
TEMPLATES_FOLDER = BASE_DIR / "templates"

app = Flask(__name__,
            instance_relative_config=True,
            template_folder=TEMPLATES_FOLDER) # <-- ¡Aquí se fuerza la ruta!

# Configuración de la Base de Datos SQLite (dentro de la carpeta 'instance')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///el_receso.db'
app.config['SECRET_KEY'] = 'la_clave_secreta_de_el_receso_es_super_segura' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'

# --- Modelo de Usuario (Database Model) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='estudiante')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"

# --- Modelo de Menú (Database Model) ---
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Snacks') 
    
    def __repr__(self):
        return f"<Menu {self.name}>"


# --- Modelo de Pedidos (Order) ---
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pendiente') 
    
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

# --- Modelo de Ítems del Pedido (OrderItem) ---
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False) 
    
    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    menu_item = db.relationship('Menu')


# --- Callbacks de Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Rutas Públicas (Home) ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Rutas de Autenticación (Login, Registro, Logout) ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('El nombre de usuario o email ya están registrados.', 'warning')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        if User.query.count() == 0:
            new_user.role = 'admin' 
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user) 
            flash('¡Bienvenido de vuelta!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required 
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))

# --- Rutas Protegidas (Dashboard) ---
@app.route('/dashboard')
@login_required 
def dashboard():
    return render_template('dashboard.html')

# --- Rutas de Menú y Administración ---

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required 
def add_product():
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo los administradores pueden añadir productos.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price')) 
            category = request.form.get('category')

            new_item = Menu(
                name=name,
                description=description,
                price=price,
                category=category
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            flash(f'Producto "{name}" añadido al menú exitosamente.', 'success')
            return redirect(url_for('view_menu')) 
        
        except ValueError:
            flash('Error: El precio debe ser un número válido.', 'danger')
        except Exception as e:
            flash(f'Ocurrió un error al guardar: {e}', 'danger')

    return render_template('add_product.html', title='Añadir Producto')


@app.route('/menu')
def view_menu():
    productos = Menu.query.order_by(Menu.category, Menu.name).all()
    
    menu_por_categoria = {}
    for producto in productos:
        if producto.category not in menu_por_categoria:
            menu_por_categoria[producto.category] = []
        menu_por_categoria[producto.category].append(producto)

    return render_template('menu.html', 
                           menu_por_categoria=menu_por_categoria,
                           title='Menú de El Receso')


# --- Rutas de Carrito y Pedidos ---

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item = Menu.query.get_or_404(item_id)
    
    if 'cart' not in session:
        session['cart'] = {}
        
    cart = session['cart']
    item_key = str(item.id) 

    if item_key in cart:
        cart[item_key]['qty'] += 1
    else:
        cart[item_key] = {
            'name': item.name,
            'price': item.price,
            'qty': 1
        }
        
    session['cart'] = cart 
    flash(f'¡"{item.name}" añadido al carrito!', 'success')
    return redirect(url_for('view_menu'))


@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    
    total = sum(item['price'] * item['qty'] for item in cart.values())
    
    return render_template('cart.html', cart_items=cart.values(), total=total)


@app.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Tu carrito está vacío, no puedes hacer un pedido.', 'warning')
        return redirect(url_for('view_menu'))

    total_amount = sum(item['price'] * item['qty'] for item in cart.values())

    try:
        # 1. Crear el nuevo pedido (Order)
        new_order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status='Pendiente' 
        )
        db.session.add(new_order)
        db.session.flush() 

        # 2. Agregar los ítems del carrito como OrderItem
        for item_id, item_data in cart.items():
            order_item = OrderItem(
                order_id=new_order.id,
                menu_id=int(item_id),
                quantity=item_data['qty'],
                price_at_time=item_data['price'] 
            )
            db.session.add(order_item)

        db.session.commit()
        
        # 3. Limpiar el carrito después de un checkout exitoso
        session.pop('cart', None) 
        
        flash(f'🎉 ¡Pedido #{new_order.id} realizado con éxito! Por favor, espera a que esté listo.', 'success')
        return redirect(url_for('dashboard')) 

    except Exception as e:
        db.session.rollback() 
        flash(f'Ocurrió un error al procesar el pedido: {e}', 'danger')
        return redirect(url_for('view_cart'))


@app.route('/admin/orders')
@login_required
def view_orders():
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    orders = Order.query.order_by(Order.order_date.desc()).all()
    
    # 💥 Esta llamada ya no fallará gracias a la corrección de la ruta al inicio.
    return render_template('admin_orders.html', orders=orders)

# --- Ruta para ver los detalles de un pedido ---
@app.route('/admin/order/<int:order_id>')
@login_required
def view_order_detail(order_id):
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))

    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    return render_template('admin_order_detail.html', order=order, order_items=order_items)

# --- Ruta para marcar un pedido como entregado ---
@app.route('/admin/order/<int:order_id>/mark_delivered', methods=['POST'])
@login_required
def mark_order_delivered(order_id):
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    order = Order.query.get_or_404(order_id)
    order.status = 'Entregado'
    db.session.commit()
    flash(f'✅ Pedido #{order.id} marcado como ENTREGADO.', 'success')
    return redirect(url_for('view_order_detail', order_id=order.id))


# --- Ruta para que el usuario vea sus pedidos ---
@app.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('my_orders.html', orders=orders)

@app.route('/admin/orders/delivered/<int:order_id>')
@login_required
def mark_delivered(order_id):
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    order = Orders.query.get(order_id)
    if order:
        order.status = 'Entregado'
        db.session.commit()
    return redirect(url_for('admin_orders'))

@app.route('/admin/order/<int:order_id>/mark_not_delivered', methods=['POST'])
@login_required
def mark_not_delivered(order_id):
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard'))
    
    order = Order.query.get_or_404(order_id)  # <-- aquí estaba el error
    order.status = 'No entregado'
    db.session.commit()
    flash(f'❌ Pedido #{order.id} marcado como NO ENTREGADO.', 'danger')
    return redirect(url_for('view_order_detail', order_id=order.id))




# --- Inicialización de la App ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)