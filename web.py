import os
from flask import Flask, render_template, request, session, redirect, url_for
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = "CLAVE_SECRETA_FERRETERIA" # Necesario para el login

# --- CONFIGURACIÓN SUPABASE ---
SUPABASE_URL = "https://hvwckeoykzvntqgdbjq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2d3dja2VveWt6dm50cWdkYmpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwMDIwMDQsImV4cCI6MjA1MjU3ODAwNH0.w9pHZZI-L36qQYlH5-K3dIvlWVFQ7uegTjxVT3q7JLQ"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error iniciando Supabase: {e}")

# --- RUTAS PÚBLICAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalogo/todo')
def catalogo_completo():
    try:
        # Traemos TODO sin filtrar por categoría
        response = supabase.table('productos').select("*").execute()
        lista_productos = response.data
    except Exception as e:
        lista_productos = []
    
    return render_template('category.html', productos=lista_productos, titulo="CATÁLOGO COMPLETO", categoria_id="todo")

@app.route('/categoria/<tipo>')
def categoria(tipo):
    try:
        response = supabase.table('productos').select("*").eq('categoria', tipo).execute()
        lista_productos = response.data
    except Exception as e:
        lista_productos = []
    
    titulo = tipo.upper().replace('_', ' ')
    return render_template('category.html', productos=lista_productos, titulo=titulo, categoria_id=tipo)

# --- RUTAS DE EMPLEADO (LOGIN) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # CONTRASEÑA SIMPLE PARA EL CLIENTE
        if request.form['password'] == 'admin2025': 
            session['user'] = 'empleado'
            return redirect(url_for('admin_panel'))
        else:
            error = "Contraseña incorrecta"
    return render_template('login.html', error=error)

@app.route('/admin')
def admin_panel():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Aquí cargaremos el inventario para editar
    return "<h1>BIENVENIDO AL PANEL (En construcción...)</h1>"

if __name__ == '__main__':
    app.run(debug=True)
