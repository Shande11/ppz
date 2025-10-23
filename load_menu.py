# load_menu.py
from app import app, db, Menu

def load_sample_menu():
    """Carga productos dominicanos de ejemplo en la base de datos."""
    
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        print("Error: La configuración de la app no está cargada. Asegúrate de que 'app.py' esté completo.")
        return

    # Menú Dominicano de Muestra (AQUÍ ESTÁ LA CORRECCIÓN DE LAS COMILLAS)
    sample_items = [
        # Desayuno
        {'name': 'Mangú con Queso', 'description': 'Plátanos verdes majados con mantequilla y queso frito.', 'price': 120.00, 'category': 'Desayuno'},
        {'name': 'Sandwich de Huevo', 'description': 'Pan, huevo revuelto y mayonesa.', 'price': 75.00, 'category': 'Desayuno'},
        
        # Almuerzo (Comida Fuerte)
        {'name': 'Arroz con Pollo Guisado', 'description': "El famoso 'la bandera' sin habichuelas.", 'price': 180.00, 'category': 'Almuerzo'},
        {'name': 'Mofongo', 'description': 'Plátano frito con ajo y chicharrón.', 'price': 250.00, 'category': 'Almuerzo'},
        
        # Snacks
        {'name': 'Empanada de Pollo', 'description': 'Masa frita rellena de pollo.', 'price': 50.00, 'category': 'Snacks'},
        {'name': 'Quipes', 'description': 'Trigo molido relleno de carne de res.', 'price': 45.00, 'category': 'Snacks'},
        {'name': 'Pastel en Hoja', 'description': 'Masa de plátano con carne, envuelto en hoja de plátano.', 'price': 100.00, 'category': 'Snacks'},
        
        # Bebidas
        {'name': 'Jugo de Chinola (Maracuyá)', 'description': 'Jugo natural, hecho en casa.', 'price': 70.00, 'category': 'Bebidas'},
        {'name': 'Agua', 'description': 'Botella de agua (16oz).', 'price': 25.00, 'category': 'Bebidas'},
    ]

    with app.app_context():
        # ... (el resto del código sigue igual) ...
        print("Cargando Menú de Muestra (El Receso)...")
        
        for item_data in sample_items:
            # Revisa si el producto ya existe para no duplicarlo
            existing_item = Menu.query.filter_by(name=item_data['name']).first()
            if not existing_item:
                item = Menu(**item_data)
                db.session.add(item)
                print(f"✅ Añadido: {item.name}")
            else:
                print(f"➡️ Ya existe: {existing_item.name} (Saltado)")

        db.session.commit()
        print("\n🎉 Menú de muestra cargado exitosamente en la base de datos 'el_receso.db'.")

if __name__ == '__main__':
    load_sample_menu()