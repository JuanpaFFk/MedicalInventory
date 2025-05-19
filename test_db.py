import psycopg2

conn = psycopg2.connect(
    dbname="medical_inventory_euie",
    user="admin_med",
    password="Cf6PKGCYdW32Kkbg3AjnysHs74Q7dUj9",
    host="dpg-d0lkt5be5dus73cmcnj0-a.oregon-postgres.render.com",
    port=5432,
    sslmode="require"  # ← Obligatorio para Render
)
print("¡Conectado exitosamente!")
conn.close()