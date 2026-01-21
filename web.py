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
        usuario = request.form['username']
        contra = request.form['password']
        
        try:
            # Buscamos en Supabase si existe el usuario y contraseña
            response = supabase.table('usuarios').select("*").eq('username', usuario).eq('password', contra).execute()
            
            if len(response.data) > 0:
                # Login Exitoso
                user_data = response.data[0]
                session['user'] = user_data['username']
                session['rol'] = user_data['rol']
                # Redireccionamos a una ruta intermedia para mostrar el splash screen de éxito
                return render_template('login_success.html')
            else:
                error = "Usuario o contraseña incorrectos"
        except Exception as e:
            error = f"Error de conexión: {e}"

    return render_template('login.html', error=error)
