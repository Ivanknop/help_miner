from flask import Flask, request, redirect, render_template
import pandas as pd
import os,chardet
from process_file import *
from pathlib import Path

# Variable global para almacenar el DataFrame
global_data = None
def detect_encoding(file_path):
    """Detecta el encoding de un archivo."""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(100000))  # Analiza los primeros 100KB del archivo
    return result['encoding']

def clean_dir(path):
    """Limpia todos los archivos en el directorio especificado."""
    print(path)
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                # Recursivamente limpiar subdirectorios
                clean_dir(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configura la ruta del directorio para guardar los archivos
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'tmp')

@app.route('/')
def index(): 
       
    clean_dir(app.config['UPLOAD_FOLDER'])
    clean_dir('static/histograms')
    clean_dir('static/box_plots')
    clean_dir('static/bar_plots')
    clean_dir('static/correlation_matrix')
    return render_template('index.html',page_title='Inicio')

@app.route('/process')
def process():    
    return render_template('process.html',page_title='Procesamiento')

@app.route('/details')
def details():  
    global global_data
    if global_data is not None:
        data = global_data['data']
        # Preparar datos para el template
        results = {
            'name': global_data['name'],
            'info': data.dtypes.to_dict(),
            'shape': data.shape,
            'describe': data.describe(include='all').to_html(classes='table table-striped'),
            'missing': data.isnull().sum().reset_index().rename(columns={0: 'Missing Values', 'index': 'Column'}).to_html(classes='table table-striped', index=False),
            'duplicates': data.duplicated().sum()
        }
        return render_template('details.html', results=results, page_title='Detalles')
    else:
        return render_template('details.html', page_title='Detalles')

@app.route('/process_file', methods=['POST', 'GET'])
def upload_file():
    global global_data
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.csv'):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Detectar encoding automáticamente
        encoding = detect_encoding(file_path)
        try:
            # Intentar leer el archivo en UTF-8
            data = pd.read_csv(
                file_path, 
                encoding=encoding, 
                on_bad_lines='skip',  # Saltar líneas problemáticas
                skip_blank_lines=True,   # Ignorar líneas en blanco
                sep=None                # Detectar delimitador automáticamente          
            )
        except UnicodeDecodeError:
            return f"Error cargando el csv", 400
        # Procesar el archivo
        file_name = Path(file_path).stem
        process_file(data,file_name)
        obtain_box_plots(data)
        obtain_histograms(data)
        obtain_correlation_matrix(data)
        create_bar_plots(data)
        global_data = {'name': filename, 'data': data}
        return render_template('process_file.html', global_data=global_data['data'].describe(include='all').to_html(classes='table table-striped'), page_title='Descripción General')

    return "Archivo no válido. Por favor, sube un archivo CSV."

@app.route('/histograms')
def histograms():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    histograms_path = os.path.join(base_dir, 'static', 'histograms')    
    try:
        # Obtener todos los archivos en el directorio de histogramas
        histograms = [f for f in os.listdir(histograms_path) if os.path.isfile(os.path.join(histograms_path, f))]
        
        # Si no se encuentran histogramas
        if not histograms:
            return render_template('histograms.html',page_title='Histogramas')
        return render_template('histograms.html', histograms=histograms, page_title='Histogramas')
    except Exception as e:
        return f"Error al obtener los histogramas: {e}"
        
@app.route('/box_plots')
def box_plots():  
    base_dir = os.path.abspath(os.path.dirname(__file__))
    box_plots_path = os.path.join(base_dir, 'static', 'box_plots')    
    try:
        if not os.path.exists(box_plots_path):
            return "El directorio de diagramas de caja no existe."
        box_plots = [f for f in os.listdir(box_plots_path) if os.path.isfile(os.path.join(box_plots_path, f))]
        
        if not box_plots:
            return render_template('box_plots.html', page_title='Diagramas de Caja')
        return render_template('box_plots.html', box_plots=box_plots, page_title='Diagramas de Caja')
    except Exception as e:
        return f"Error al obtener los diagramas de caja: {e}"
    
@app.route('/correlation_matrix')
def correlation_matrix():  
    base_dir = os.path.abspath(os.path.dirname(__file__))
    correlation_matrix_path = os.path.join(base_dir, 'static', 'correlation_matrix')    
    try:
        if not os.path.exists(correlation_matrix_path):
            return "El directorio de la matriz de correlación no existe."
        correlation_matrix = [f for f in os.listdir(correlation_matrix_path) if os.path.isfile(os.path.join(correlation_matrix_path, f))]
        
        if not correlation_matrix:
            return render_template('correlation_matrix.html', page_title='Matriz de Correlación') 
        return render_template('correlation_matrix.html', correlation_matrix=correlation_matrix, page_title='Matriz de Correlación')
    except Exception as e:
        return f"Error al obtener la matriz de correlación: {e}"

@app.route('/bar_plots')
def bar_plots():  
    base_dir = os.path.abspath(os.path.dirname(__file__))
    bar_plots_path = os.path.join(base_dir, 'static', 'bar_plots')    
    try:
        if not os.path.exists(bar_plots_path):
            return "El directorio de diagramas de barra no existe."
        bar_plots = [f for f in os.listdir(bar_plots_path) if os.path.isfile(os.path.join(bar_plots_path, f))]
        
        if not bar_plots:            
            return render_template('bar_plots.html', page_title='Diagramas de Barra')
        return render_template('bar_plots.html', bar_plots=bar_plots, page_title='Diagramas de Barra')
    except Exception as e:
        return f"Error al obtener los diagramas de barra: {e}"

if __name__ == '__main__':
    app.run(debug=True)
