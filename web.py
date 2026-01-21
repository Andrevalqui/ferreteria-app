import os
import requests
import time # Para generar nombres únicos de imágenes
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "CLAVE_SECRETA_FERRETERIA"

# --- CREDENCIALES SUPABASE ---
SUPABASE_URL = "https://hvwckeoykzvntqgdbjq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2d3dja2VveWt6dm50cWdkYmpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwMTQ3OTMsImV4cCI6MjA4NDU5MDc5M30.w9pHZZi-L36qQYIH5-K3dIvlWVFQ7uegTjXVT3q7JLQ"

# --- FUNCIONES AUXILIARES ---
def consultar_supabase(tabla, query_params={}):
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    headers = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json" }
    try:
        response = requests.get(url, headers=headers, params=query_params, timeout=10)
        if response.status_code == 200: return response.json()
    except: pass
    return []

def insertar_supabase(tabla, datos):
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    headers = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal" }
    requests.post(url, headers=headers, json=datos)

def actualizar_supabase(tabla, id_fila, datos):
    url = f"{SUPABASE_URL}/rest/v1/{tabla}?id=eq.{id_fila}"
    headers = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json" }
    requests.patch(url, headers=headers, json=datos)

def eliminar_supabase(tabla, id_fila):
    url = f"{SUPABASE_URL}/rest/v1/{tabla}?id=eq.{id_fila}"
    headers = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}" }
    requests.delete(url, headers=headers)

# --- RUTAS PÚBLICAS ---
@app.route('/')
def home():
    return render_template('index.html', user=session.get('user'))

@app.route('/catalogo/todo')
def catalogo_completo():
    lista = consultar_supabase('productos', {"select": "*", "order": "id.desc"}) # Ordenado por más nuevo
    return render_template('category.html', productos=lista, titulo="CATÁLOGO COMPLETO", categoria_id="todo")

@app.route('/categoria/<tipo>')
def categoria(tipo):
    params = {"select": "*", "categoria": f"eq.{tipo}"}
    lista = consultar_supabase('productos', params)
    return render_template('category.html', productos=lista, titulo=tipo.upper().replace('_', ' '), categoria_id=tipo)

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session: return redirect(url_for('admin_panel'))
    error = None
    if request.method == 'POST':
        usuario = request.form['username'].strip()
        contra = request.form['password'].strip()
        params = {"select": "*", "username": f"eq.{usuario}"}
        data = consultar_supabase('usuarios', params)
        if data and len(data) > 0 and data[0]['password'] == contra:
            session['user'] = data[0]['username']
            session['rol'] = data[0]['rol']
            return render_template('login_success.html', nombre_usuario=data[0]['username'])
        else:
            error = "Credenciales incorrectas, contáctese con el administrador de la plataforma."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# --- PANEL ADMIN Y PRODUCTOS ---
@app.route('/admin')
def admin_panel():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('admin.html', user=session['user'])

@app.route('/admin/productos')
def admin_productos():
    if 'user' not in session: return redirect(url_for('login'))
    # Traemos todos los productos para la tabla
    lista = consultar_supabase('productos', {"select": "*", "order": "id.desc"})
    return render_template('admin_productos.html', user=session['user'], productos=lista)

@app.route('/admin/producto/guardar', methods=['POST'])
def guardar_producto():
    if 'user' not in session: return redirect(url_for('login'))
    
    # Recibimos datos del formulario
    nombre = request.form['nombre']
    categoria = request.form['categoria']
    precio = float(request.form['precio'])
    stock = int(request.form['stock'])
    desc = request.form['desc']
    img_nombre = request.form.get('img_url', '') # Por ahora URL manual o vacía

    datos = {
        "nombre": nombre, "categoria": categoria, "precio": precio, 
        "stock": stock, "desc": desc, "img": img_nombre
    }

    # Si viene ID es EDICIÓN, si no es CREACIÓN
    id_prod = request.form.get('id')
    if id_prod:
        actualizar_supabase('productos', id_prod, datos)
    else:
        insertar_supabase('productos', datos)
    
    return redirect(url_for('admin_productos'))

@app.route('/admin/producto/eliminar/<id>')
def eliminar_producto(id):
    if 'user' not in session: return redirect(url_for('login'))
    eliminar_supabase('productos', id)
    return redirect(url_for('admin_productos'))

if __name__ == '__main__':
    app.run(debug=True)
