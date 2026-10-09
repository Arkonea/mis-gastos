# Mis Gastos

App personal de finanzas (Streamlit + Python) que guarda todo en Google Sheets.

## Requisitos

- Python 3.10+ (probado con 3.11)
- Una cuenta de Google

## Instalación

```bash
# 1. (Opcional) Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate      # Windows PowerShell

# 2. Instalar dependencias
pip install -r requirements.txt
```

## Configuración de Google

Sigue **CONFIGURACION_GOOGLE.md** para:

1. Crear la Service Account y descargar `assets/credentials.json`.
2. Compartir tu hoja "Mis Gastos" con el `client_email`.
3. Pegar el ID de la hoja en `.streamlit/secrets.toml`.

## Ejecutar

```bash
streamlit run app.py
```

Se abre en <http://localhost:8501>.

## Usar desde el celular (misma red WiFi)

1. Al iniciar, Streamlit muestra una **Network URL** parecida a
   `http://192.168.1.15:8501`.
2. Abre esa dirección en Chrome desde tu celular (misma red WiFi).

Para acceso desde fuera de casa necesitarías desplegar en un hosting
(por ejemplo Railway o Render).

## Estructura

```
Proyecto de gastos/
├── .streamlit/
│   ├── config.toml          # Tema oscuro minimalista
│   └── secrets.toml         # ID de la hoja (NO compartir)
├── assets/
│   ├── credentials.json     # Service account (NO compartir)
│   └── credentials.example.json
├── sheets.py                # Capa de datos + utilidades
├── app.py                   # Entrada + navegación + selector de mes
├── requirements.txt
├── CONFIGURACION_GOOGLE.md
└── pages/
    ├── 1_Dashboard.py
    ├── 2_Registrar_Ingreso.py
    ├── 3_Registrar_Gasto.py
    ├── 4_Historial.py
    └── 5_Ajustes.py
```

## Estructura de la hoja

- **Movimientos**: `fecha_hora | tipo | categoria | nombre | monto`
- **Categorias**: una categoría por fila (columna A)
- **Config**: pares `clave | valor` (usuario, moneda)

Las pestañas se crean automáticamente si no existen.
