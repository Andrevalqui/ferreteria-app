import os
import requests
import json
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "CLAVE_SECRETA_FERRETERIA"

# --- CREDENCIALES ---
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
        # Si falla, devolvemos el error crudo para verlo en pantalla
        if response.status_code != 200:
            return {"error_debug": f"Status: {response.status_code}, Msg: {response.text}"}
        return response.json()
    except Exception as e:
        return {"error_debug": f"Excepción Python: {str(e)}"}

# --- RUTAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalogo/todo')
def catalogo_completo():
    data = consultar_supabase('productos', {"select": "*"})
    lista_productos = data if isinstance(data, list) else []
    return render_template('category.html', productos=lista_productos, titulo="CATÁLOGO COMPLETO", categoria_id="todo")

@app.route('/categoria/<tipo>')
def categoria(tipo):
    params = {"select": "*", "categoria": f"eq.{tipo}"}
    data = consultar_supabase('productos', params)
    lista_productos = data if isinstance(data, list) else []
    
    titulo = tipo.upper().replace('_', ' ')
    return render_template('category.html', productos=lista_productos, titulo=titulo, categoria_id=tipo)

# --- LOGIN MODO DETECTIVE ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['username'].strip()
        contra = request.form['password'].strip()
        
        # Consultamos a Supabase
        params = {
            "select": "*",
            "username": f"eq.{usuario}"
        }
        
        data = consultar_supabase('usuarios', params)
        
        # --- BLOQUE DE DIAGNÓSTICO ---
        if isinstance(data, dict) and "error_debug" in data:
            # Si hubo error técnico, LO MOSTRAMOS EN PANTALLA
            error = f"Error Técnico: {data['error_debug']}"
        elif isinstance(data, list):
            if len(data) > 0:
                user_data = data[0]
                # Verificamos contraseña
                if user_data['password'] == contra:
                    session['user'] = user_data['username']
                    session['rol'] = user_data['rol']
                    return render_template('login_success.html', nombre_usuario=user_data['username'])
                else:
                    error = f"Contraseña incorrecta. (Tu pusiste: '{contra}', en BD es: '{user_data['password']}')"
            else:
                error = f"Usuario no encontrado. (Buscamos: '{usuario}' y la BD devolvió lista vacía [])"
        else:
            error = "Error desconocido en formato de respuesta."

    return render_template('login.html', error=error)

@app.route('/admin')
def admin_panel():
    if 'user' not in session:
        return redirect(url_for('login'))
    return f"<h1>PANEL DE GESTIÓN</h1><p>Bienvenido: {session['user']}</p>"

if __name__ == '__main__':
    app.run(debug=True)
