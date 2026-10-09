# Configuración de Google (una sola vez)

Esta guía conecta la app "Mis Gastos" con tu Google Sheet usando una
**Service Account** (cuenta de servicio). Es gratis y solo se hace la primera vez.

---

## 1. Crear el proyecto en Google Cloud

1. Entra a <https://console.cloud.google.com/crear-proyecto> (o a la consola y crea uno nuevo).
2. Ponle un nombre, por ejemplo `mis-gastos`, y créalo.
3. Arriba, selecciona ese proyecto como proyecto activo.

## 2. Habilitar la Google Sheets API

1. Ve a **APIs y servicios → Biblioteca**:
   <https://console.cloud.google.com/apis/library/sheets.googleapis.com>
2. Pulsa **Habilitar**.

## 3. Crear la Service Account y descargar el JSON

1. Ve a **APIs y servicios → Credenciales**:
   <https://console.cloud.google.com/apis/credentials>
2. **Crear credenciales → Cuenta de servicio**.
3. Nombre: `mis-gastos` (el ID se genera solo). Pulsa **Crear y continuar**.
4. En "Otorga acceso a este proyecto" puedes dejarlo sin roles y pulsar **Continuar**.
5. Pulsa **Listo**.
6. En la lista, haz clic en la cuenta de servicio recién creada.
7. Ve a la pestaña **Claves → Agregar clave → Crear clave nueva → JSON**.
8. Se descargará un archivo `.json`. **Renómbralo a `credentials.json`** y
   colócalo en la carpeta `assets/` del proyecto:

   ```
   Proyecto de gastos/
   └── assets/
       └── credentials.json
   ```

> Importante: NO compartas este archivo ni lo subas a repositorios públicos.
> Ya está incluido en `.gitignore`.

## 4. Compartir la hoja con la Service Account

1. Abre el archivo `credentials.json` y copia el valor de **`client_email`**.
   Se parece a: `mis-gastos@mis-gastos-123456.iam.gserviceaccount.com`
2. Abre tu hoja de cálculo en Google Sheets.
3. Pulsa **Compartir**, pega ese correo y dale permisos de **Editor**.
4. Copia el **ID de la hoja** desde la URL:

   ```
   https://docs.google.com/spreadsheets/d/  <AQUÍ_ESTÁ_EL_ID>  /edit
   ```

## 5. Pegar el ID en el proyecto

1. Abre `.streamlit/secrets.toml`.
2. Reemplaza el marcador por tu ID real:

   ```toml
   spreadsheet_key = "1AbC...el-id-largo-de-tu-hoja..."
   ```

## 6. Listo

La primera vez que ejecutes la app, se crearán automáticamente las pestañas
**Movimientos**, **Categorias** y **Config** dentro de tu hoja.

---

### Errores comunes

| Mensaje | Causa probable | Solución |
|---|---|---|
| `No se encontró 'assets/credentials.json'` | Falta el archivo | Repite los pasos 3 y colócalo en `assets/` |
| `No se encontró la hoja` | ID incorrecto o sin compartir | Revisa el ID y comparte con el `client_email` |
| `Falta el ID de la hoja` | `secrets.toml` sin pegar | Completa el paso 5 |
| `The caller does not have permission` | La hoja no está compartida | Compártela como Editor con el `client_email` |
