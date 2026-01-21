import os
from flask import Flask, render_template
from supabase import create_client, Client

app = Flask(__name__)

# --- CONFIGURACIÓN SUPABASE ---
# NOTA: Todo texto debe ir entre comillas " "
SUPABASE_URL = "https://hvwckeoykzvntqgdbjq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2d3dja2VveWt6dm50cWdkYmpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwMDIwMDQsImV4cCI6MjA1MjU3ODAwNH0.w9pHZZI-L36qQYlH5-K3dIvlWVFQ7uegTjxVT3q7JLQ"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- RUTAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/categoria/<tipo>')
def categoria(tipo):
    # 1. Consultamos a Supabase (Select * from productos where categoria = tipo)
    response = supabase.table('productos').select("*").eq('categoria', tipo).execute()
    
    # 2. Obtenemos la lista de datos
    lista_productos = response.data
    
    # 3. Formateamos título
    titulo = tipo.upper().replace('_', ' ')
    
    return render_template('category.html', productos=lista_productos, titulo=titulo, categoria_id=tipo)

if __name__ == '__main__':
    app.run(debug=True)

