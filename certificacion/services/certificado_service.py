import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile

from certificacion.models import CertificadoDescendencia

def generar_qr(certificado):

    url_verificacion = (
        f"https://verificacion{certificado.id}"
    )

    qr = qrcode.make(url_verificacion)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    certificado.codigo_qr.save(
        f"qr_{certificado.id}.png",
        ContentFile(buffer.getvalue()),
        save=False
    )

def generar_pdf(certificado):

    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=A4)

    p.drawString(100, 800, "CERTIFICADO DE DESCENDENCIA")
    p.drawString(100, 770, f"Nro: {certificado.numero_certificado}")
    p.drawString(100, 740, f"Solicitante: {certificado.nombres_solicitante}")

    p.showPage()
    p.save()

    buffer.seek(0)

    certificado.certificado.save(
        f"cert_{certificado.numero_certificado}.pdf",
        ContentFile(buffer.read()),
        save=False
    )

def generar_documentos_certificado(certificado):

    generar_qr(certificado)
    generar_pdf(certificado)

    certificado.save(update_fields=["codigo_qr", "certificado"])
