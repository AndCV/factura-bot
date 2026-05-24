"""
main.py — Orquesta la descarga y procesamiento de facturas del día.

Uso:
    python main.py                  # Procesa correos del día
    python main.py --carpeta ./pdfs # Procesa archivos locales sin conectar Gmail
"""
import sys
import os

import gmail_reader
import factura_parser
import excel_writer


def procesar_archivos(archivos: list[str]) -> list[dict]:
    facturas = []
    for path in archivos:
        print(f"  → Procesando: {os.path.basename(path)}")
        datos = factura_parser.parsear(path)
        if datos:
            facturas.append(datos)
            print(f"     Fecha: {datos['fecha']}  |  Monto: {datos['monto']}  |  Tipo: {datos['tipo']}")
        else:
            print(f"     ⚠ No se pudo leer.")
    return facturas


def main():
    # ── Modo local: leer archivos de una carpeta ──────────────────────────────
    if "--carpeta" in sys.argv:
        idx = sys.argv.index("--carpeta")
        carpeta = sys.argv[idx + 1]
        archivos = [
            os.path.join(carpeta, f)
            for f in os.listdir(carpeta)
            if f.lower().endswith((".pdf", ".xml"))
        ]
        print(f"Archivos encontrados en '{carpeta}': {len(archivos)}")
        facturas = procesar_archivos(archivos)

    # ── Modo Gmail: descargar y procesar correos del día ─────────────────────
    else:
        print("Conectando a Gmail…")
        try:
            mail = gmail_reader.conectar()
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            print("   Verificá el correo y el App Password en config.py")
            sys.exit(1)

        emails = gmail_reader.obtener_emails_del_dia(mail)
        mail.logout()

        if not emails:
            print("No hay facturas para procesar hoy.")
            sys.exit(0)

        todos_los_archivos = []
        for em in emails:
            print(f"\nCorreo: {em['asunto'][:60]}")
            todos_los_archivos.extend(em["adjuntos"])

        facturas = procesar_archivos(todos_los_archivos)

    # ── Guardar en Excel ─────────────────────────────────────────────────────
    if facturas:
        excel_writer.guardar_facturas(facturas)
    else:
        print("No se encontraron facturas válidas.")


if __name__ == "__main__":
    main()
