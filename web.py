import os
import requests
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "CLAVE_SECRETA_FERRETERIA"

# --- CREDENCIALES SUPABASE ---
SUPABASE_URL = "https://hvwckeoykzvntqgdbjq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2d3dja2VveWt6dm50cWdkYmpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwMDIwMDQsImV4cCI6MjA1MjU3ODAwNH0.w9pHZZI-L36qQYlH5-K3dIvlWVFQ7uegTjxVT3q7JLQ"

def consultar_supabase(tabla, query_params={}):
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, params=query_params, timeout=10)
        # Si hay error 400/500, esto lanzará excepción
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error Conexión: {e}")
        return None

# --- RUTAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalogo/todo')
def catalogo_completo():
    data = consultar_supabase('productos', {"select": "*"})
    # Si devuelve None o error, enviamos lista vacía
    lista_productos = data if data else []
    return render_template('category.html', productos=lista_productos, titulo="CATÁLOGO COMPLETO", categoria_id="todo")

@app.route('/categoria/<tipo>')
def categoria(tipo):
    params = {"select": "*", "categoria": f"eq.{tipo}"}
    data = consultar_supabase('productos', params)
    lista_productos = data if data else []
    
    titulo = tipo.upper().replace('_', ' ')
    return render_template('category.html', productos=lista_productos, titulo=titulo, categoria_id=tipo)

# --- LOGIN MEJORADO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # 1. Limpiamos espacios en blanco accidentales (.strip())
        usuario = request.form['username'].strip()
        contra = request.form['password'].strip()
        
        # 2. Consultamos SOLO por usuario primero
        params = {
            "select": "*",
            "username": f"eq.{usuario}"
        }
        
        try:
            data = consultar_supabase('usuarios', params)
            
            if data and len(data) > 0:
                # El usuario EXISTE, ahora verificamos la contraseña en Python
                user_data = data[0]
                
                # Comparamos contraseña (Exacta)
                if user_data['password'] == contra:
                    # ¡ÉXITO!
                    session['user'] = user_data['username']
                    session['rol'] = user_data['rol']
                    return render_template('login_success.html', nombre_usuario=user_data['username'])
                else:
                    error = "Contraseña incorrecta."
            else:
                error = "El usuario no existe en la base de datos."
                
        except Exception as e:
            error = f"Error de sistema: {e}"

    return render_template('login.html', error=error)

@app.route('/admin')
def admin_panel():
    if 'user' not in session:
        return redirect(url_for('login'))
    return f"<h1>PANEL DE GESTIÓN</h1><p>Bienvenido: {session['user']}</p>"

if __name__ == '__main__':
    app.run(debug=True)
