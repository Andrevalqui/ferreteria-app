import os
from flask import Flask, render_template
from supabase import create_client, Client

app = Flask(__name__)

# --- CONFIGURACIÓN SUPABASE (Tus datos confirmados) ---
SUPABASE_URL = "https://hvwckeoykzvntqgdbjq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2d3dja2VveWt6dm50cWdkYmpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwMDIwMDQsImV4cCI6MjA1MjU3ODAwNH0.w9pHZZI-L36qQYlH5-K3dIvlWVFQ7uegTjxVT3q7JLQ"

# Iniciamos el cliente de base de datos
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error iniciando Supabase: {e}")

# --- RUTAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/categoria/<tipo>')
def categoria(tipo):
    lista_productos = []
    
    try:
        # 1. Consultamos a Supabase de forma segura
        # Trae todos los productos donde la columna 'categoria' coincida con el tipo
        response = supabase.table('productos').select("*").eq('categoria', tipo).execute()
        
        # 2. Guardamos los datos
        lista_productos = response.data
        
    except Exception as e:
        # Si algo falla, imprimimos el error en la consola interna pero NO rompemos la web
        print(f"Error obteniendo productos: {e}")
        # La lista se queda vacía [], así el usuario ve la página aunque sea sin productos
    
    # 3. Formateamos título
    titulo = tipo.upper().replace('_', ' ')
    
    return render_template('category.html', productos=lista_productos, titulo=titulo, categoria_id=tipo)

if __name__ == '__main__':
    app.run(debug=True)
