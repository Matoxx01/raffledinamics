import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar .env
load_dotenv()
host     = os.getenv('host')
user     = os.getenv('user')
password = os.getenv('password')
port     = int(os.getenv('port', 3306))
database = os.getenv('database')

try:
    conexion = mysql.connector.connect(
        host=host,
        user=user,
        port=port,
        password=password,
        database=database
    )

    if conexion.is_connected():
        cursor = conexion.cursor(dictionary=True)

        # Obtener todas las tablas
        cursor.execute("""
            SELECT TABLE_NAME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s
        """, (database,))
        resultados = cursor.fetchall()
        tablas = [row['TABLE_NAME'] for row in resultados]

        with open("schema_report.txt", "w", encoding="utf-8") as f:
            for tabla in tablas:
                f.write(f"Tabla: {tabla}\n")
                f.write("-" * (7 + len(tabla)) + "\n")

                # Obtener columnas
                cursor.execute("""
                    SELECT 
                        COLUMN_NAME,
                        COLUMN_TYPE,
                        IS_NULLABLE,
                        COLUMN_DEFAULT,
                        COLUMN_KEY
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = %s
                      AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """, (database, tabla))
                columnas = cursor.fetchall()

                for col in columnas:
                    nombre   = col['COLUMN_NAME']
                    tipo     = col['COLUMN_TYPE']
                    nullable = col['IS_NULLABLE']
                    default  = col['COLUMN_DEFAULT']
                    key      = col['COLUMN_KEY']

                    marcadores = []
                    if key == 'PRI':
                        marcadores.append('PK')
                    if key == 'MUL':
                        marcadores.append('FK?')  # Se confirma más abajo

                    f.write(f"  - {nombre}{' [' + ', '.join(marcadores) + ']' if marcadores else ''}\n")
                    f.write(f"      Tipo: {tipo}\n")
                    f.write(f"      Nullable: {nullable}\n")
                    f.write(f"      Default: {default}\n")

                # Obtener claves foráneas
                cursor.execute("""
                    SELECT
                        kcu.COLUMN_NAME,
                        kcu.REFERENCED_TABLE_NAME,
                        kcu.REFERENCED_COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE kcu
                    JOIN information_schema.TABLE_CONSTRAINTS tc
                      ON kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                     AND kcu.TABLE_SCHEMA = tc.TABLE_SCHEMA
                     AND kcu.TABLE_NAME = tc.TABLE_NAME
                    WHERE tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
                      AND kcu.TABLE_SCHEMA = %s
                      AND kcu.TABLE_NAME = %s
                """, (database, tabla))
                fks = cursor.fetchall()

                if fks:
                    f.write("  Foreign Keys:\n")
                    for fk in fks:
                        f.write(f"    * {fk['COLUMN_NAME']} → {fk['REFERENCED_TABLE_NAME']}({fk['REFERENCED_COLUMN_NAME']})\n")

                f.write("\n\n")

        print("✅ Reporte generado: schema_report.txt")

except Error as e:
    print(f"❌ Error de conexión: {e}")

finally:
    if 'conexion' in locals() and conexion.is_connected():
        cursor.close()
        conexion.close()
        print("🔌 Conexión cerrada")
