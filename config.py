from dotenv import load_dotenv
import os

# Carga el .env desde la ruta ABSOLUTA
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class COnfig:
    # Usa los valores directamente (sin depender de os.getenv)
    SECRET_KEY = "7a4ed3c0beb44b29d9946bfaea6b5de2709a324f219283e981e2761c70dc3322"
    SQLALCHEMY_DATABASE_URI = "postgresql://admin_med:Cf6PKGCYdW32Kkbg3AjnysHs74Q7dUj9@dpg-d0lkt5be5dus73cmcnj0-a.oregon-postgres.render.com/medical_inventory_euie?sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Debug: Verifica que todo está bien
print("[DEBUG] DATABASE_URL:", COnfig.SQLALCHEMY_DATABASE_URI)
print("[DEBUG] SECRET_KEY:", COnfig.SECRET_KEY)