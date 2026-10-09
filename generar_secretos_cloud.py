"""
generar_secretos_cloud.py
=========================
Genera el archivo de secretos con el formato que espera Streamlit Community
Cloud, combinando:
- el ID de la hoja (leído de .streamlit/secrets.toml), y
- la service account (leída de assets/credentials.json).

Resultado: .streamlit/secrets_cloud.toml

Uso:
    python generar_secretos_cloud.py

Luego abre ese archivo, copia TODO su contenido y pégalo en el panel de
Secrets de Streamlit Cloud.
"""

import json
import os
import tomllib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_FILE = os.path.join(BASE_DIR, "assets", "credentials.json")
SECRETS_FILE = os.path.join(BASE_DIR, ".streamlit", "secrets.toml")
OUT_FILE = os.path.join(BASE_DIR, ".streamlit", "secrets_cloud.toml")


def main() -> None:
    if not os.path.exists(CRED_FILE):
        raise SystemExit(
            f"No se encontró {CRED_FILE}. Coloca primero el credentials.json."
        )
    if not os.path.exists(SECRETS_FILE):
        raise SystemExit(f"No se encontró {SECRETS_FILE}.")

    with open(CRED_FILE, encoding="utf-8") as f:
        cred = json.load(f)

    with open(SECRETS_FILE, "rb") as f:
        spreadsheet_key = tomllib.load(f).get("spreadsheet_key", "")

    if not spreadsheet_key or str(spreadsheet_key).upper().startswith("PEGA"):
        raise SystemExit("El 'spreadsheet_key' en secrets.toml no es válido.")

    lineas = [f'spreadsheet_key = {json.dumps(spreadsheet_key)}', ""]
    lineas.append("[gcp_service_account]")
    for clave, valor in cred.items():
        lineas.append(f"{clave} = {json.dumps(valor)}")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Listo. Archivo generado en: {OUT_FILE}")
    print("Copia TODO su contenido en el panel 'Secrets' de Streamlit Cloud.")


if __name__ == "__main__":
    main()
