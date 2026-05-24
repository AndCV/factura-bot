"""
gmail_reader.py — Conexión IMAP a Gmail y descarga de adjuntos por fecha
"""
import imaplib
import email
import os
from datetime import date
from email.header import decode_header

import config


def _decode_str(value):
    if not value:
        return ""
    parts = decode_header(value)
    decoded = []
    for part, enc in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def conectar():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(config.EMAIL_ADDRESS, config.APP_PASSWORD)
    return mail


def obtener_emails_del_dia(mail, fecha: date = None):
    if fecha is None:
        fecha = date.today()

    mail.select("INBOX")
    fecha_imap = fecha.strftime("%d-%b-%Y")
    status, data = mail.search(None, f'(ON {fecha_imap})')

    if status != "OK" or not data[0]:
        print(f"No hay correos para el {fecha.strftime('%d/%m/%Y')}.")
        return []

    ids = data[0].split()
    print(f"Correos encontrados: {len(ids)}")

    os.makedirs(config.DOWNLOAD_FOLDER, exist_ok=True)
    resultados = []

    for num in ids:
        status, msg_data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            continue

        raw_bytes = msg_data[0][1]
        msg = email.message_from_bytes(raw_bytes)
        asunto = _decode_str(msg.get("Subject", ""))
        remite = _decode_str(msg.get("From", ""))

        if config.SUBJECT_FILTER:
            if not any(f.lower() in asunto.lower() for f in config.SUBJECT_FILTER):
                continue

        adjuntos = []
        for part in msg.walk():
            content_disp = part.get("Content-Disposition", "")
            content_type = part.get_content_type()

            es_adjunto = "attachment" in content_disp
            es_factura = content_type in ("application/pdf", "text/xml",
                                          "application/xml", "application/octet-stream")

            if es_adjunto and es_factura:
                filename = part.get_filename()
                if not filename:
                    ext = "pdf" if "pdf" in content_type else "xml"
                    filename = f"factura_{num.decode()}_{len(adjuntos)}.{ext}"
                else:
                    filename = _decode_str(filename)

                filepath = os.path.join(config.DOWNLOAD_FOLDER, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                adjuntos.append(filepath)
                print(f"  ✔ Descargado: {filename}")

        if adjuntos:
            resultados.append({
                "asunto":    asunto,
                "remite":    remite,
                "raw_bytes": raw_bytes,  # correo original completo
                "adjuntos":  adjuntos,
            })

    return resultados
