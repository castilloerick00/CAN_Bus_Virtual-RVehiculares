import re
import os
import subprocess
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, SecondLocator, AutoDateLocator
from datetime import datetime
from collections import defaultdict

# =============================================================================
# CONFIGURACIÓN DE RUTAS
# =============================================================================
# Directorio base del proyecto (donde están Script, Archivos e Imagenes)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Rutas completas
INPUT_DIR = os.path.join(BASE_DIR, "Archivos")
IMAGES_DIR = os.path.join(BASE_DIR, "Imagenes")
INPUT_FILE = os.path.join(INPUT_DIR, "00000001.MF4")
OUTPUT_FILE = os.path.join(INPUT_DIR, "output.log")

# Crear directorios si no existen
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)
# =============================================================================
# CONFIGURACIÓN (MODIFICABLE)
# =============================================================================
TICK_INTERVAL = 60                   # Intervalo de marcas en segundos (eje X)
LOG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"  # Formato fecha+hora para logs
PLOT_TIME_FORMAT = "%H:%M:%S"        # Formato hora para gráficas
PLOT_STYLE = "ggplot"                # Estilo de gráficas (prueba: 'ggplot', 'seaborn', 'default')
LINE_COLOR = "#2ca02c"               # Color de las líneas (formato HEX)
FIG_SIZE = (12, 5)                   # Tamaño de gráficas (ancho, alto)
# =============================================================================
# FUNCIONES DE PROCESAMIENTO
# =============================================================================
def decode_obd_param(pid, data_bytes):
    try:
        if pid == "05":  # Temperatura del refrigerante
            value = int(data_bytes[0], 16) - 40
            return "Temperatura", value, "°C"
        
        elif pid == "0C":  # RPM
            a = int(data_bytes[0], 16)
            b = int(data_bytes[1], 16)
            value = (256 * a + b) / 4
            return "RPM", value, ""
        
        elif pid == "0D":  # Velocidad
            value = int(data_bytes[0], 16)
            return "Velocidad", value, "km/h"
        
        elif pid == "2F":  # Combustible
            value = int(data_bytes[0], 16) * 100 / 255
            return "Combustible", value, "%"
            
        else:
            return None, None, None
            
    except (IndexError, ValueError, TypeError) as e:
        print(f"Error decodificando: {str(e)}")
        return None, None, None

def parse_line(line):
    match = re.match(r"\(([\d.]+)\) can\d (\w+)#(\w+)", line)
    if not match:
        return None
        
    timestamp, can_id, payload = match.groups()
    try:
        can_id_int = int(can_id, 16)
        
        # Filtrar IDs 0x7E8 a 0x7EF
        if 0x7E8 <= can_id_int <= 0x7EF:
            payload_bytes = [payload[i:i+2] for i in range(0, len(payload), 2)]
            
            # Validar formato OBD-II
            if len(payload_bytes) < 3 or payload_bytes[1] != "41":
                return None
                
            pid = payload_bytes[2]
            data_length = int(payload_bytes[0], 16)
            data = payload_bytes[3:3 + (data_length - 2)]
            
            nombre, valor, unidad = decode_obd_param(pid, data)
            if nombre and valor is not None:
                return float(timestamp), nombre, valor, unidad
                
    except ValueError as e:
        print(f"Línea corrupta: {line}\nError: {str(e)}")
    
    return None

# =============================================================================
# FUNCIONES DE GRAFICACIÓN
# =============================================================================
def plot_individual(data, parameter, unit):
    if not data[parameter]['timestamps']:
        print(f"\n⚠️ Sin datos para: {parameter}")
        return
    
    plt.style.use(PLOT_STYLE)
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    
    times = [datetime.fromtimestamp(ts) for ts in data[parameter]['timestamps']]
    values = data[parameter]['values']
    
    ax.plot(times, values, 
            marker='o', 
            linestyle='-', 
            linewidth=1.5,
            color=LINE_COLOR,
            markersize=5,
            alpha=0.8)
    
    # Configuración del eje X
    ax.xaxis.set_major_formatter(DateFormatter(PLOT_TIME_FORMAT))
    time_span = max(times) - min(times)
    locator = AutoDateLocator() if time_span.total_seconds() > 3600 else SecondLocator(interval=TICK_INTERVAL)
    ax.xaxis.set_major_locator(locator)
    
    # Ajustes estéticos
    ax.set_title(f'Monitoreo: {parameter}', fontsize=14, pad=15)
    ax.set_xlabel('Hora', fontsize=10)
    ax.set_ylabel(unit if unit else 'Valor', fontsize=10)
    plt.xticks(rotation=35, ha='right', fontsize=9)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    # Guardar en la carpeta Imagenes
    plot_path = os.path.join(IMAGES_DIR, f'{parameter}_plot.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfica guardada en: {plot_path}")

# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================
def main():
    data = defaultdict(lambda: {'timestamps': [], 'values': []})
    
    # Generar output.log si no existe
    if not os.path.exists(OUTPUT_FILE):
        command = f"~/.local/bin/can_logconvert {INPUT_FILE} {OUTPUT_FILE}"
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"✅ Archivo convertido: {OUTPUT_FILE}")
        except Exception as e:
            print(f"❌ Error en conversión: {str(e)}")
            return
    else:
        print(f"ℹ Archivo ya existe: {OUTPUT_FILE}")
    
    # Procesar el archivo de log
    try:
        with open(OUTPUT_FILE, "r") as f:
            print("\nProcesando datos...")
            for line_number, line in enumerate(f, 1):
                result = parse_line(line.strip())
                if result:
                    timestamp, nombre, valor, unidad = result
                    print(f"[Línea {line_number}] {datetime.fromtimestamp(timestamp):{LOG_TIME_FORMAT}} | {nombre}: {valor:.2f}{unidad}")
                    data[nombre]['timestamps'].append(timestamp)
                    data[nombre]['values'].append(valor)
    
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {OUTPUT_FILE}")
        return
    
    # Generar gráficas
    print("\nGenerando gráficas...")
    for param, unit in [('Temperatura', '°C'), ('RPM', 'RPM'), 
                       ('Velocidad', 'km/h'), ('Combustible', '%')]:
        plot_individual(data, param, unit)
    
    print("\nProceso completado ✅")

if __name__ == "__main__":
    main()
