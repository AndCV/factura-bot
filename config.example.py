# ============================================================
#  CONFIGURATION — factura_bot
#  Copy this file to config.py and fill in your credentials
# ============================================================

# --- Gmail IMAP ---
EMAIL_ADDRESS  = "your_email@gmail.com"
APP_PASSWORD   = "xxxx xxxx xxxx xxxx"    # Gmail App Password

# --- Claude API (optional, not currently used) ---
ANTHROPIC_API_KEY = ""

# --- Folders ---
DOWNLOAD_FOLDER = r"C:\facturas\adjuntos"
EXCEL_FOLDER    = r"C:\facturas"
EXCEL_BASE_NAME = "facturas"

# --- Optional subject filter ---
SUBJECT_FILTER = []   # e.g. ["factura", "comprobante"]

# --- Invoice categories ---
TIPOS_VALIDOS = ["Combustible", "Compra", "GPS", "Diésel", "Servicio", "Otro"]
