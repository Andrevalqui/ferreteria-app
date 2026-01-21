import os
import requests # Usamos requests en lugar de la librería supabase para evitar Errno 16
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "CLAVE_SECRETA_FERRETERIA"

# --- TUS CREDENCIALES (Tal cual las tenías) ---
SUPABASE_URL = "https://hvwckeoykzvntqgdbjq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2d3dja2VveWt6dm50cWdkYmpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwMDIwMDQsImV4cCI6MjA1MjU3ODAwNH0.w9pHZZI-L36qQYlH5-K3dIvlWVFQ7uegTjxVT3q7JLQ"

# --- FUNCIÓN AUXILIAR PARA PEDIR DATOS (SIN ERRORES) ---
def consultar_supabase(tabla, query_params={}):
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, params=query_params, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error API: {e}")
        return []

# --- RUTAS PÚBLICAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalogo/todo')
def catalogo_completo():
    # Traemos todo (select=*)
    lista_productos = consultar_supabase('productos', {"select": "*"})
    return render_template('category.html', productos=lista_productos, titulo="CATÁLOGO COMPLETO", categoria_id="todo")

@app.route('/categoria/<tipo>')
def categoria(tipo):
    # Filtramos por categoría (categoria=eq.VALOR)
    params = {
        "select": "*",
        "categoria": f"eq.{tipo}"
    }
    lista_productos = consultar_supabase('productos', params)
    
    titulo = tipo.upper().replace('_', ' ')
    return render_template('category.html', productos=lista_productos, titulo=titulo, categoria_id=tipo)

# --- LOGIN (SOLUCIÓN ERROR 16) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['username']
        contra = request.form['password']
        
        # Filtramos usuarios donde username=usuario AND password=contra
        params = {
            "select": "*",
            "username": f"eq.{usuario}",
            "password": f"eq.{contra}"
        }
        
        try:
            # Consulta HTTP directa (No usa sockets persistentes -> No Error 16)
            data = consultar_supabase('usuarios', params)
            
            if len(data) > 0:
                user_data = data[0]
                session['user'] = user_data['username']
                session['rol'] = user_data['rol']
                
                # ÉXITO
                return render_template('login_success.html', nombre_usuario=user_data['username'])
            else:
                error = "Credenciales incorrectas, contáctese con el administrador de la plataforma."
        
        except Exception as e:
            error = "Ocurrió un error de conexión con el servidor."

    return render_template('login.html', error=error)

@app.route('/admin')
def admin_panel():
    if 'user' not in session:
        return redirect(url_for('login'))
    return f"<h1>PANEL DE GESTIÓN (Próximamente)</h1><p>Usuario: {session['user']}</p>"

if __name__ == '__main__':
    app.run(debug=True)
