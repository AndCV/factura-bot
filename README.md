# 📄 Factura Bot

Automated tool for downloading, parsing, and forwarding Costa Rican electronic invoices (facturas electrónicas) from Gmail. Built for businesses that receive XML + PDF invoices from Hacienda CR and need to consolidate them into a monthly Excel report and forward them to an accounting inbox.

---

## ✨ Features

- 📥 **Downloads invoices** from Gmail via IMAP for any selected date
- 📊 **Parses XML** from Hacienda CR (extracts invoice number, date, amount, IVA, issuer)
- 📁 **Generates a monthly Excel report** with all invoice data
- 📧 **Forwards each invoice** as a separate email (with original subject and body) to a destination inbox
- 🗓️ **Date picker UI** to select any past date
- 🚫 **Skips PDF-only emails** and Hacienda acknowledgement XMLs automatically
- 🖥️ **Runs as a standalone `.exe`** on Windows (no Python required on target machine)

---

## 🗂️ Project Structure

```
factura_bot/
├── config.py           # Credentials and settings (edit this first)
├── gmail_reader.py     # Gmail IMAP connection and attachment download
├── factura_parser.py   # XML parser for Hacienda CR invoices
├── excel_writer.py     # Monthly Excel report generator
├── interfaz.py         # Main GUI (tkinter)
├── main.py             # CLI entry point (no GUI)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## ⚙️ Setup

### 1. Install Python
Download Python 3.11+ from https://python.org  
During installation, check **"Add Python to PATH"**.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Enable Gmail IMAP
1. Go to [Gmail Settings → Forwarding and POP/IMAP](https://mail.google.com/mail/u/0/#settings/fwdandpop)
2. Enable **IMAP Access**
3. Save changes

### 4. Create a Gmail App Password
Gmail requires an App Password for IMAP access (your regular password won't work):

1. Go to your [Google Account → Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already active
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Create a new one (name it `factura_bot`)
5. Copy the 16-character code Google gives you

### 5. Configure `config.py`
```python
EMAIL_ADDRESS     = "your_email@gmail.com"
APP_PASSWORD      = "xxxx xxxx xxxx xxxx"   # App Password from step 4
ANTHROPIC_API_KEY = ""                       # Not required (PDF parsing disabled)
DOWNLOAD_FOLDER   = r"C:\facturas\adjuntos"
EXCEL_FOLDER      = r"C:\facturas"
EXCEL_BASE_NAME   = "facturas"              # Output: facturas_2026-05.xlsx
SUBJECT_FILTER    = []                      # Optional: filter emails by subject keyword
TIPOS_VALIDOS     = ["Combustible", "Compra", "GPS", "Diésel", "Servicio", "Otro"]
```

---

## ▶️ Running the App

### GUI mode (recommended)
```bash
python interfaz.py
```

### CLI mode (no GUI)
```bash
python main.py                        # Process today's emails
python main.py --carpeta C:\path\     # Process local XML/PDF files
```

---

## 📊 Excel Output

A file is created per month: `facturas_2026-05.xlsx`

| Column | Description |
|--------|-------------|
| N° Factura | Invoice consecutive number from Hacienda XML |
| Fecha | Invoice date (YYYY-MM-DD) |
| Emisor | Issuing company name |
| Descripción | Product/service description |
| Tipo | Category (Combustible, Compra, GPS, etc.) |
| Otros | Specific detail |
| Monto | Total amount including IVA |
| IVA | Tax amount |
| Fuente | Source type (XML) |

A **Resumen** sheet is also generated with monthly totals.

---

## 📦 Building a Windows Executable

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "FacturaBot" interfaz.py
```

The `.exe` will be in `dist/FacturaBot.exe`. Right-click → **Send to → Desktop** to create a shortcut.

---

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| `[AUTHENTICATIONFAILED]` | Use App Password, not your regular Gmail password |
| `Connection refused` | Enable IMAP in Gmail settings |
| `No emails found` | Emails must exist for that date; use `--carpeta` to test with local files |
| `PermissionError` on Excel | Close the Excel file before running again |
| Only PDF emails skipped | Normal behavior — PDF-only invoices are discarded (no XML = no data) |

---

## 📋 Requirements

- Python 3.11+
- `anthropic>=0.40.0` (installed but not actively used — reserved for future PDF parsing)
- `openpyxl>=3.1.0`
- Gmail account with IMAP enabled and an App Password

---

## 🇨🇷 Notes for Costa Rica

This tool is designed for **comprobantes electrónicos** issued under the Hacienda CR XML schema (v4.3). It reads the following fields directly from XML:
- `NumeroConsecutivo` — invoice number
- `FechaEmision` — issue date
- `Emisor/Nombre` — issuer name
- `ResumenFactura/TotalComprobante` — total amount
- `ResumenFactura/TotalImpuesto` — IVA amount

Acknowledgement files (`Acuse_Recibo`, `RespuestaHacienda`, `xml_confirmacion`) are automatically ignored.

---

## 📄 License

MIT
