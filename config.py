import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# =========================================================
# CONFIGURACIÓN DE BASE DE DATOS - XAMPP
# =========================================================
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')  # Por defecto XAMPP no tiene password
MYSQL_DB = os.getenv('MYSQL_DB', 'ComunicacionDatos')

# =========================================================
# CONFIGURACIÓN FLASK
# =========================================================
SECRET_KEY = os.getenv('SECRET_KEY', 'clave_secreta_ucundinamarca_2024')

# =========================================================
# CONFIGURACIÓN SSL/TLS
# =========================================================
SSL_CERT_PATH = os.getenv('SSL_CERT_PATH', 'certificado/cert.pem')
SSL_KEY_PATH = os.getenv('SSL_KEY_PATH', 'certificado/key.pem')
