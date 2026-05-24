"""
interfaz.py — GUI principal del Factura Bot
"""
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from datetime import date
import calendar
import sys
import io
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

import config

CORREO_DESTINO = "facturas-transcarga@outlook.com"


class LogRedirector(io.TextIOBase):
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)
        self.widget.configure(state="disabled")
        self.widget.update()
        return len(text)

    def flush(self):
        pass


class FacturaBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Factura Bot 📄")
        self.root.geometry("640x680")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.selected_date = date.today()
        # Lista de {asunto, adjuntos} por correo
        self.correos_facturas = []
        self._build_ui()

    def _build_ui(self):
        tk.Label(self.root, text="📄 Factura Bot", font=("Arial", 20, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=(20, 4))
        tk.Label(self.root, text="Descarga y registra facturas electrónicas automáticamente",
                 font=("Arial", 10), bg="#1e1e2e", fg="#a6adc8").pack(pady=(0, 12))

        # ── Selector de fecha ────────────────────────────────────────────────
        frame_fecha = tk.Frame(self.root, bg="#313244")
        frame_fecha.pack(padx=30, fill="x", pady=(0, 10))

        tk.Label(frame_fecha, text="Seleccioná la fecha a procesar",
                 font=("Arial", 11, "bold"), bg="#313244", fg="#cdd6f4").pack(pady=(12, 8))

        nav = tk.Frame(frame_fecha, bg="#313244")
        nav.pack()
        tk.Button(nav, text="◀", font=("Arial", 12), bg="#45475a", fg="#cdd6f4",
                  bd=0, padx=10, cursor="hand2",
                  command=self._mes_anterior).grid(row=0, column=0, padx=4)
        self.lbl_mes = tk.Label(nav, text="", font=("Arial", 12, "bold"),
                                bg="#313244", fg="#89b4fa", width=16)
        self.lbl_mes.grid(row=0, column=1)
        tk.Button(nav, text="▶", font=("Arial", 12), bg="#45475a", fg="#cdd6f4",
                  bd=0, padx=10, cursor="hand2",
                  command=self._mes_siguiente).grid(row=0, column=2, padx=4)

        self.cal_frame = tk.Frame(frame_fecha, bg="#313244")
        self.cal_frame.pack(pady=8)
        for i, d in enumerate(["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]):
            tk.Label(self.cal_frame, text=d, font=("Arial", 9, "bold"),
                     bg="#313244", fg="#6c7086", width=4).grid(row=0, column=i, pady=(0, 4))

        self.day_buttons = {}
        self._render_calendario()

        self.lbl_fecha_sel = tk.Label(frame_fecha, text="", font=("Arial", 10),
                                      bg="#313244", fg="#a6e3a1")
        self.lbl_fecha_sel.pack(pady=(0, 8))
        self._actualizar_label_fecha()

        # ── Botones de acción ────────────────────────────────────────────────
        frame_btns = tk.Frame(self.root, bg="#1e1e2e")
        frame_btns.pack(pady=6)
        tk.Button(frame_btns, text="📅 Ir a hoy", font=("Arial", 10),
                  bg="#45475a", fg="#cdd6f4", bd=0, padx=14, pady=6,
                  cursor="hand2", command=self._ir_a_hoy).grid(row=0, column=0, padx=6)
        self.btn_run = tk.Button(frame_btns, text="⚡ Descargar y procesar facturas",
                                 font=("Arial", 11, "bold"), bg="#89b4fa", fg="#1e1e2e",
                                 bd=0, padx=20, pady=8, cursor="hand2",
                                 command=self._correr)
        self.btn_run.grid(row=0, column=1, padx=6)

        # ── Sección de envío ─────────────────────────────────────────────────
        frame_envio = tk.Frame(self.root, bg="#313244")
        frame_envio.pack(padx=30, fill="x", pady=(6, 10))

        tk.Label(frame_envio, text="📧 Reenviar facturas por correo",
                 font=("Arial", 11, "bold"), bg="#313244", fg="#cdd6f4").pack(pady=(12, 4))

        tk.Label(frame_envio,
                 text=f"Para: {CORREO_DESTINO}  •  Un correo por factura con el asunto original",
                 font=("Arial", 9), bg="#313244", fg="#a6adc8").pack()

        self.lbl_adjuntos = tk.Label(frame_envio, text="",
                                     font=("Arial", 9), bg="#313244", fg="#6c7086")
        self.lbl_adjuntos.pack(pady=(4, 6))

        self.btn_enviar = tk.Button(frame_envio, text="✉ Enviar facturas",
                                    font=("Arial", 10, "bold"), bg="#a6e3a1", fg="#1e1e2e",
                                    bd=0, padx=16, pady=6, cursor="hand2",
                                    command=self._enviar, state="disabled")
        self.btn_enviar.pack(pady=(2, 12))

        # ── Log ──────────────────────────────────────────────────────────────
        tk.Label(self.root, text="Registro de actividad",
                 font=("Arial", 10, "bold"), bg="#1e1e2e", fg="#a6adc8").pack(anchor="w", padx=30)
        self.log = scrolledtext.ScrolledText(self.root, height=8, font=("Consolas", 9),
                                             bg="#181825", fg="#cdd6f4", bd=0,
                                             insertbackground="white", state="disabled")
        self.log.pack(padx=30, pady=(4, 16), fill="x")
        sys.stdout = LogRedirector(self.log)

    # ── Calendario ─────────────────────────────────────────────────────────────

    def _render_calendario(self):
        for w in self.day_buttons.values():
            w.destroy()
        self.day_buttons.clear()
        self.lbl_mes.config(text=self.selected_date.strftime("%B %Y").capitalize())
        year, month = self.selected_date.year, self.selected_date.month
        hoy = date.today()
        for r, week in enumerate(calendar.monthcalendar(year, month), start=1):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                d = date(year, month, day)
                es_sel    = (d == self.selected_date)
                es_hoy    = (d == hoy)
                es_futuro = (d > hoy)
                if es_sel:        bg, fg = "#89b4fa", "#1e1e2e"
                elif es_hoy:      bg, fg = "#45475a", "#a6e3a1"
                elif es_futuro:   bg, fg = "#313244", "#585b70"
                else:             bg, fg = "#313244", "#cdd6f4"
                btn = tk.Button(self.cal_frame, text=str(day), font=("Arial", 9),
                                bg=bg, fg=fg, bd=0, width=3, height=1,
                                cursor="hand2" if not es_futuro else "arrow",
                                command=lambda dd=d: self._seleccionar_dia(dd))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.day_buttons[d] = btn

    def _seleccionar_dia(self, d):
        if d > date.today():
            return
        self.selected_date = d
        self._render_calendario()
        self._actualizar_label_fecha()

    def _actualizar_label_fecha(self):
        self.lbl_fecha_sel.config(
            text=f"Fecha seleccionada: {self.selected_date.strftime('%d/%m/%Y')}"
        )

    def _mes_anterior(self):
        d = self.selected_date
        mes = 12 if d.month == 1 else d.month - 1
        año = d.year - 1 if d.month == 1 else d.year
        self.selected_date = d.replace(year=año, month=mes, day=1)
        self._render_calendario()
        self._actualizar_label_fecha()

    def _mes_siguiente(self):
        d = self.selected_date
        mes = 1 if d.month == 12 else d.month + 1
        año = d.year + 1 if d.month == 12 else d.year
        nuevo = d.replace(year=año, month=mes, day=1)
        if nuevo <= date.today():
            self.selected_date = nuevo
            self._render_calendario()
            self._actualizar_label_fecha()

    def _ir_a_hoy(self):
        self.selected_date = date.today()
        self._render_calendario()
        self._actualizar_label_fecha()

    # ── Proceso principal ───────────────────────────────────────────────────────

    def _correr(self):
        self.btn_run.config(state="disabled", text="⏳ Procesando...")
        self.btn_enviar.config(state="disabled")
        self.correos_facturas = []
        self.log.configure(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.configure(state="disabled")
        threading.Thread(target=self._ejecutar, daemon=True).start()

    def _es_factura(self, path):
        nombre = os.path.basename(path).lower()
        return not any(x in nombre for x in
                       ["respuesta", "acuse", "confirmacion", "_respuesta"])

    def _ejecutar(self):
        try:
            import gmail_reader
            import factura_parser
            import excel_writer

            fecha = self.selected_date
            print(f"Conectando a Gmail — {fecha.strftime('%d/%m/%Y')}\n")

            mail = gmail_reader.conectar()
            emails = gmail_reader.obtener_emails_del_dia(mail, fecha)
            mail.logout()

            if not emails:
                print("No se encontraron correos con adjuntos para esa fecha.")
                return

            facturas = []
            for em in emails:
                print(f"\nCorreo: {em['asunto'][:60]}")
                adjuntos_factura = [p for p in em["adjuntos"] if self._es_factura(p)]

                # Si no hay ningún XML entre los adjuntos, descartar el correo completo
                tiene_xml = any(p.lower().endswith(".xml") for p in adjuntos_factura)
                if not tiene_xml:
                    print(f"  ⏭ Sin XML, descartando correo: {em['asunto'][:50]}")
                    continue

                for path in em["adjuntos"]:
                    print(f"  → Procesando: {os.path.basename(path)}")
                    datos = factura_parser.parsear(path)
                    if datos:
                        facturas.append(datos)
                        print(f"     ₡{datos['monto']:,.2f}  |  {datos['emisor'][:30]}  |  {datos['tipo']}")

                # Guardar correo original completo para reenvío
                if adjuntos_factura:
                    self.correos_facturas.append({
                        "asunto":    em["asunto"],
                        "raw_bytes": em.get("raw_bytes", b""),
                        "adjuntos":  adjuntos_factura,
                    })

            if facturas:
                ruta = excel_writer.guardar_facturas(facturas)
                n = len(self.correos_facturas)
                print(f"\n✅ {len(facturas)} factura(s) procesadas.")
                print(f"📁 Excel: {ruta}")
                print(f"📧 {n} correo(s) listos para reenviar.")
                self.lbl_adjuntos.config(
                    text=f"{n} factura(s) listas para enviar individualmente",
                    fg="#89b4fa"
                )
                self.btn_enviar.config(state="normal")
                os.startfile(ruta)
            else:
                print("\n⚠ No se encontraron facturas válidas.")

        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.btn_run.config(state="normal", text="⚡ Descargar y procesar facturas")

    # ── Envío individual por factura ────────────────────────────────────────────

    def _enviar(self):
        if not self.correos_facturas:
            messagebox.showerror("Error", "No hay facturas para enviar.")
            return
        self.btn_enviar.config(state="disabled", text="⏳ Enviando...")
        threading.Thread(target=self._enviar_correos, daemon=True).start()

    def _enviar_correos(self):
        try:
            import email as emaillib
            enviados = 0
            errores  = 0

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(config.EMAIL_ADDRESS, config.APP_PASSWORD)

                for correo in self.correos_facturas:
                    asunto    = correo["asunto"]
                    raw_bytes = correo.get("raw_bytes", b"")

                    if not raw_bytes:
                        continue

                    print(f"\n📧 Reenviando: {asunto[:55]}...")

                    # Parsear el original y cambiar solo el destinatario
                    msg = emaillib.message_from_bytes(raw_bytes)
                    del msg["To"]
                    del msg["Cc"]
                    del msg["Bcc"]
                    msg["To"] = CORREO_DESTINO

                    try:
                        server.sendmail(config.EMAIL_ADDRESS, CORREO_DESTINO, msg.as_bytes())
                        print(f"  ✅ Enviado")
                        enviados += 1
                    except Exception as e:
                        print(f"  ❌ Error: {e}")
                        errores += 1

            resumen = f"✅ {enviados} factura(s) enviadas a {CORREO_DESTINO}"
            if errores:
                resumen += f" | ❌ {errores} error(es)"
            print(f"\n{resumen}")
            messagebox.showinfo("Enviado", resumen)

        except Exception as e:
            print(f"\n❌ Error de conexión: {e}")
            messagebox.showerror("Error", f"No se pudo conectar:\n{e}")
        finally:
            self.btn_enviar.config(state="normal", text="✉ Enviar facturas")


if __name__ == "__main__":
    root = tk.Tk()
    app = FacturaBotApp(root)
    root.mainloop()
