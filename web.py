import os
import requests
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "CLAVE_SECRETA_FERRETERIA"

# --- CONFIGURACIÓN SUPABASE ---
# ⚠️ IMPORTANTE: Borra la URL de abajo y pega la que acabas de copiar de Supabase (Ctrl+V)
SUPABASE_URL = "https://hvwwckeoykzvntqgdbjq.supabase.co"

# Tu llave (Esta parece estar bien, pero si quieres cópiala de nuevo por si acaso)
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2d3dja2VveWt6dm50cWdkYmpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwMTQ3OTMsImV4cCI6MjA4NDU5MDc5M30.w9pHZZi-L36qQYIH5-K3dIvlWVFQ7uegTjXVT3q7JLQ"

def consultar_supabase(tabla, query_params={}):
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, params=query_params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

# --- RUTAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalogo/todo')
def catalogo_completo():
    lista_productos = consultar_supabase('productos', {"select": "*"})
    return render_template('category.html', productos=lista_productos, titulo="CATÁLOGO COMPLETO", categoria_id="todo")

@app.route('/categoria/<tipo>')
def categoria(tipo):
    params = {"select": "*", "categoria": f"eq.{tipo}"}
    lista_productos = consultar_supabase('productos', params)
    
    titulo = tipo.upper().replace('_', ' ')
    return render_template('category.html', productos=lista_productos, titulo=titulo, categoria_id=tipo)

# --- LOGIN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['username'].strip()
        contra = request.form['password'].strip()
        
        # 1. Buscamos usuario
        params = {"select": "*", "username": f"eq.{usuario}"}
        data = consultar_supabase('usuarios', params)
        
        if data and len(data) > 0:
            user_data = data[0]
            # 2. Verificamos contraseña
            if user_data['password'] == contra:
                session['user'] = user_data['username']
                session['rol'] = user_data['rol']
                return render_template('login_success.html', nombre_usuario=user_data['username'])
            else:
                error = "Credenciales incorrectas, contáctese con el administrador de la plataforma."
        else:
            error = "Credenciales incorrectas, contáctese con el administrador de la plataforma."

    return render_template('login.html', error=error)

@app.route('/admin')
def admin_panel():
    if 'user' not in session:
        return redirect(url_for('login'))
    return f"<h1>BIENVENIDO AL PANEL</h1><p>Usuario: {session['user']}</p>"

if __name__ == '__main__':
    app.run(debug=True)


