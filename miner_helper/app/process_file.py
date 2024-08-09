import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib

matplotlib.use('Agg')
OUTPUT_DIRS = {
    'histograms': 'static/histograms',
    'box_plots': 'static/box_plots',
    'correlation_matrix': 'static/correlation_matrix',
    'bar_plots': 'static/bar_plots'
}
def save_plot(figure, output_dir, filename):
    """Guarda una figura en el directorio de salida especificado."""
    print (output_dir)
    file_path = os.path.join(output_dir, filename)
    figure.savefig(file_path)
    plt.close(figure)
    return file_path

def obtain_histograms(data):
    output_dir = OUTPUT_DIRS['histograms']  # Ruta donde se guardarán los histogramas
    histogram_paths = []
    for column in data.columns:
        if pd.api.types.is_numeric_dtype(data[column]):
            plt.figure()
            sns.histplot(data[column], kde=False, bins=30, color='green')
            plt.title(f'Histograma de {column}')
            plt.xlabel(column)
            plt.ylabel('Frecuencia')
            plt.grid(True)
            filename = f'histogram_{column}.png'
            histogram_paths.append(save_plot(plt.gcf(), output_dir, filename))
    return histogram_paths

def obtain_box_plots(data):
    output_dir = OUTPUT_DIRS['box_plots']  # Ruta donde se guardarán los histogramas
    box_plots_paths = []
    for column in data.columns:
        if pd.api.types.is_numeric_dtype(data[column]):
            plt.subplot(1, 2, 1)  # Crea un subplot para el boxplot
            plt.boxplot(data[column].dropna(), vert=False)
            plt.title(f'Diagrama de Caja de {column}')
            plt.xlabel(column)
            plt.grid(True)
            plt.tight_layout()
            filename = f'box_plots_{column}.png'
            box_plots_paths.append(save_plot(plt.gcf(), output_dir, filename))
    return box_plots_paths

def obtain_correlation_matrix(data):
    output_dir = OUTPUT_DIRS['correlation_matrix']
    
    # Seleccionar solo las columnas numéricas
    numeric_data = data.select_dtypes(include=['number'])
    
    # Calcular la matriz de correlación
    correlation_matrix = numeric_data.corr()
    
    plt.figure(figsize=(8, 6))
    # Crear el mapa de calor
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, linecolor='black')
    plt.title('Matriz de Correlación')
    
    filename = 'correlation_matrix.png'
    return save_plot(plt.gcf(), output_dir, filename)

def create_bar_plots(data):
    output_dir = OUTPUT_DIRS['bar_plots']
    bar_plot_paths = []    
    for column in data.columns:
        if data[column].dtype == 'object':  # Verifica si la columna es categórica
            plt.figure(figsize=(10, 6))
            sns.countplot(data=data, x=column, palette='viridis')
            plt.title(f'Frecuencia de Categorías en {column}')
            plt.xlabel(column)
            plt.ylabel('Frecuencia')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            filename = f'bar_plots_{column}.png'
            bar_plot_paths.append(save_plot(plt.gcf(), output_dir, filename))
    return bar_plot_paths

def process_file(original_data,name):
    data = {}
    data['name'] = name
    # Mostrar Header
    data['header'] = original_data.columns.tolist()
        # Mostrar las primeras 10 filas como ejemplo
    data['head'] = original_data.head(10).to_html(classes='table table-striped')
        # Dimensiones del DataFrame
    data['shape'] = (int(original_data.shape[0]), int(original_data.shape[1]))
    data['describe'] = original_data.describe().to_html(classes='table table-striped')
    column_details = {col: str(original_data[col].dtype) for col in original_data.columns}
    data['info'] = column_details
    missing_data = original_data.isnull().sum()
    missing_data = missing_data[missing_data > 0]
    if not missing_data.empty:
        data['missing'] = missing_data.to_frame(name='Missing Values').to_html(classes='table table-striped')
    else:
        data['missing'] = "No hay datos faltantes."
        # Duplicados
    data['duplicates'] = int(original_data.duplicated().sum())
        
    return data

