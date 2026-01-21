import os
import requests
import time
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "CLAVE_SECRETA_FERRETERIA"

# --- CONFIGURACIÓN SUPABASE ---
SUPABASE_URL = "https://hvwckeoykzvntqgdbjq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2d3dja2VveWt6dm50cWdkYmpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwMDIwMDQsImV4cCI6MjA1MjU3ODAwNH0.w9pHZZI-L36qQYlH5-K3dIvlWVFQ7uegTjxVT3q7JLQ"

# --- FUNCIONES AUXILIARES ---
def consultar_supabase(tabla, query_params={}):
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    headers = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}" }
    try:
        response = requests.get(url, headers=headers, params=query_params, timeout=10)
        if response.status_code == 200: return response.json()
    except: pass
    return []

def subir_imagen_supabase(archivo):
    if not archivo: return None
    try:
        filename = secure_filename(str(int(time.time())) + "_" + archivo.filename)
        url = f"{SUPABASE_URL}/storage/v1/object/imagenes/{filename}"
        headers = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": archivo.content_type }
        
        # Enviamos los bytes del archivo
        response = requests.post(url, headers=headers, data=archivo.read())
        
        if response.status_code == 200:
            return filename
        else:
            print(f"Error subiendo imagen: {response.text}")
            return None
    except Exception as e:
        print(f"Excepción subida: {e}")
        return None

def upsert_producto(datos, id_prod=None):
    headers = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal" }
    
    if id_prod: # ACTUALIZAR
        url = f"{SUPABASE_URL}/rest/v1/productos?id=eq.{id_prod}"
        requests.patch(url, headers=headers, json=datos)
    else: # CREAR
        url = f"{SUPABASE_URL}/rest/v1/productos"
        requests.post(url, headers=headers, json=datos)

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
    lista = consultar_supabase('productos', {"select": "*", "order": "id.desc"})
    return render_template('category.html', productos=lista, titulo="CATÁLOGO COMPLETO", categoria_id="todo")

@app.route('/categoria/<tipo>')
def categoria(tipo):
    params = {"select": "*", "categoria": f"eq.{tipo}"}
    lista = consultar_supabase('productos', params)
    return render_template('category.html', productos=lista, titulo=tipo.upper().replace('_', ' '), categoria_id=tipo)

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
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

# --- ADMINISTRACIÓN ---
@app.route('/admin')
def admin_panel():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('admin.html', user=session['user'])

@app.route('/admin/productos')
def admin_productos():
    if 'user' not in session: return redirect(url_for('login'))
    lista = consultar_supabase('productos', {"select": "*", "order": "id.desc"})
    return render_template('admin_productos.html', user=session['user'], productos=lista, supabase_url=SUPABASE_URL)

@app.route('/admin/producto/guardar', methods=['POST'])
def guardar_producto():
    if 'user' not in session: return redirect(url_for('login'))
    
    try:
        # Datos del formulario
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        desc = request.form['desc']
        
        # Manejo de Imagen
        archivo = request.files.get('img_archivo')
        img_nombre = request.form.get('img_actual') # Mantener la que ya tenía si no sube nueva
        
        if archivo and archivo.filename != '':
            nuevo_nombre = subir_imagen_supabase(archivo)
            if nuevo_nombre:
                img_nombre = nuevo_nombre

        datos = {
            "nombre": nombre, "categoria": categoria, 
            "precio": precio, "stock": stock, 
            "desc": desc, "img": img_nombre
        }

        id_prod = request.form.get('id')
        upsert_producto(datos, id_prod)
        
        return redirect(url_for('admin_productos'))
        
    except Exception as e:
        return f"Error en el servidor: {str(e)}"

@app.route('/admin/producto/eliminar/<id>')
def eliminar_producto(id):
    if 'user' not in session: return redirect(url_for('login'))
    eliminar_supabase('productos', id)
    return redirect(url_for('admin_productos'))

if __name__ == '__main__':
    app.run(debug=True)
