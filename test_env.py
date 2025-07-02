import os
from pathlib import Path
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

db_name = os.getenv("DB_NAME")

print(f"Valor de DB_NAME leído del .env: '{db_name}'")
print(f"Tipo de DB_NAME: {type(db_name)}")
print(f"Longitud de DB_NAME: {len(db_name) if db_name else 'None'}")

if db_name and '#' in db_name:
    print("¡ADVERTENCIA! El nombre de la base de datos aún contiene un '#'.")
elif db_name:
    print("¡ÉXITO! El nombre de la base de datos parece correcto.")
else:
    print("¡ERROR! DB_NAME no se pudo leer o está vacío.")