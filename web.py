from flask import Flask, render_template

app = Flask(__name__)

# --- BASE DE DATOS SIMULADA (Para empezar gratis y rápido) ---
# En el futuro, esto vendrá de una base de datos real o un Excel.
PRODUCTOS = {
    "materiales": [
        {"id": 1, "nombre": "Cemento Sol Tipo I", "precio": 28.50, "stock": 50, "img": "cemento.jpg", "desc": "Alta resistencia, ideal para columnas."},
        {"id": 2, "nombre": "Fierro Corrugado 1/2", "precio": 45.00, "stock": 120, "img": "fierro.jpg", "desc": "Acero Arequipa legítimo."}
    ],
    "seguridad": [
        {"id": 3, "nombre": "Casco de Seguridad 3M", "precio": 35.00, "stock": 20, "img": "casco.jpg", "desc": "Norma ANSI, color amarillo."},
        {"id": 4, "nombre": "Botas Punta de Acero", "precio": 85.00, "stock": 15, "img": "botas.jpg", "desc": "Cuero legítimo, suela antideslizante."}
    ],
    "herramientas": [],
    "accesorios": [],
    "electricos": []
}

# --- RUTAS ---

@app.route('/')
def home():
    # Renderiza la portada
    return render_template('index.html')

@app.route('/categoria/<tipo>')
def categoria(tipo):
    # Busca los productos según la tarjeta que clickearon
    lista_productos = PRODUCTOS.get(tipo, [])
    # Formateamos el título para que se vea bien (ej: materiales -> MATERIALES)
    titulo = tipo.upper().replace('_', ' ')
    return render_template('category.html', productos=lista_productos, titulo=titulo, categoria_id=tipo)

if __name__ == '__main__':
    app.run(debug=True)