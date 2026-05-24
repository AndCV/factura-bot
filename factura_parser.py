"""
factura_parser.py — Lee XML de Hacienda CR.
"""
import xml.etree.ElementTree as ET
import re
import os


def _texto(root, *paths):
    for path in paths:
        ns_uri = re.match(r'\{(.+?)\}', root.tag)
        if ns_uri:
            ns = ns_uri.group(1)
            full_path = path.replace("h:", f"{{{ns}}}")
            node = root.find(full_path)
            if node is not None and node.text:
                return node.text.strip()
        clean_path = path.replace("h:", "")
        node = root.find(clean_path)
        if node is not None and node.text:
            return node.text.strip()
    return ""


def parsear_xml(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError:
        return None

    # Ignorar XMLs de respuesta/acuse de Hacienda
    tag = root.tag.lower()
    if "mensajehacienda" in tag or "acuse" in tag or "respuesta" in tag:
        return None
    nombre = os.path.basename(filepath).lower()
    if "respuesta" in nombre or "acuse" in nombre or "confirmacion" in nombre:
        return None

    fecha_raw = _texto(root, "h:FechaEmision", "FechaEmision")
    fecha = fecha_raw[:10] if fecha_raw else ""

    total_str = _texto(root, "h:ResumenFactura/h:TotalComprobante",
                             "ResumenFactura/TotalComprobante")
    iva_str   = _texto(root, "h:ResumenFactura/h:TotalImpuesto",
                             "ResumenFactura/TotalImpuesto")
    emisor    = _texto(root, "h:Emisor/h:Nombre", "Emisor/Nombre")

    # Número de factura
    numero    = _texto(root, "h:NumeroConsecutivo", "NumeroConsecutivo",
                             "h:Clave", "Clave")

    desc_node = root.find(".//{*}Detalle") or root.find(".//Detalle")
    descripcion = desc_node.text.strip() if desc_node is not None and desc_node.text else ""

    total = float(total_str.replace(",", ".")) if total_str else 0.0
    iva   = float(iva_str.replace(",", "."))   if iva_str   else 0.0

    tipo, otros = _clasificar(emisor, descripcion)

    return {
        "numero":      numero,
        "fecha":       fecha,
        "monto":       total,
        "iva":         iva,
        "tipo":        tipo,
        "otros":       otros,
        "descripcion": descripcion or emisor,
        "emisor":      emisor,
        "fuente":      "XML",
    }


_KEYWORDS = {
    "Combustible": ["gasolinera", "combustible", "gasolina", "bpsr", "delta", "recope"],
    "Diésel":      ["diesel", "diésel", "disel"],
    "GPS":         ["gps", "rastreo", "tracking", "flota"],
    "Compra":      ["supermercado", "ferretería", "farmacia", "tienda", "auto mercado",
                    "walmart", "pricemart", "maxi"],
    "Servicio":    ["servicio", "mantenimiento", "taller", "reparación"],
}

def _clasificar(emisor, descripcion):
    texto = (emisor + " " + descripcion).lower()
    for tipo, kws in _KEYWORDS.items():
        if any(kw in texto for kw in kws):
            return tipo, tipo
    return "Otro", ""


def parsear(filepath):
    ext = filepath.lower().rsplit(".", 1)[-1]
    if ext == "xml":
        return parsear_xml(filepath)
    else:
        print(f"  ⏭ Saltando: {os.path.basename(filepath)}")
        return None
