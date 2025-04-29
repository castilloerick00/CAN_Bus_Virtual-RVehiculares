# 🚗 Análisis de Datos Vehiculares OBD-II

Herramienta para procesar y visualizar datos de vehículos obtenidos a través del protocolo OBD-II desde archivos MF4.

---

## 📁 Estructura del proyecto

```
📁 CAN Bus Virtual
├── 📂 Archivos
│   ├── 00000001.MF4
│   ├── output.log
├── 📂 Imagenes
│   ├── Combustible_plot.png
│   ├── RPM_plot.png
│   ├── Temperatura_plot.png
│   └── Velocidad_plot.png
├── 📂 Script
│   └── OBD2_Data_Analyzer.py
└── README.md
```



---

## 📋 Descripción del Proyecto
Herramienta de análisis que convierte registros CAN vehiculares (MF4) en datos procesables, extrayendo parámetros clave como:
- Temperatura del motor
- RPM
- Velocidad
- Nivel de combustible

Ideal para:
- Diagnóstico vehicular
- Análisis de rendimiento
- Proyectos de telemetría
- Investigación en sistemas embebidos

## ✨ Características Principales
- **Conversión MF4 a LOG**: Utiliza `can_logconvert` para procesar archivos brutos
- **Extracción de parámetros OBD-II**: Decodificación de PIDs específicos
- **Visualización profesional**: Gráficas temporales configurables
- **Gestión automática de directorios**: 
  - `Archivos/`: Datos brutos y logs procesados
  - `Imagenes/`: Gráficas generadas automáticamente

## 🛠 Instalación
```bash
# Clonar repositorio
git clone https://github.com/castilloerick00/CAN_Bus_Virtual-RVehiculares

# Instalar dependencias
pip install matplotlib python-can

# Instalar herramienta de conversión (requiere permisos)
sudo pip install can-logconvert
```


## 🎓 Créditos académicos

**Universidad de Cuenca**  
Facultad de Ingeniería  
Ingeniería en Telecomunicaciones  
Asignatura: Redes Vehiculares  

**Autores:**  
- Erick Castillo  
- Sebastián Chalco  
- Felipe Palaguachi
