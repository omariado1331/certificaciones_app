import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import lightgrey # Importar color
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph, Frame
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics


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
    buffer.close()

def generar_pdf(certificado):

    buffer = BytesIO()
    page_width, page_height = A4
    width, height = A4
    margin = 60  
    margin_left = 75
    margin_right = 50 
    c = canvas.Canvas(buffer, pagesize=A4)
    dibujar_encabezado(c, page_width, page_height, margin, margin_left, certificado)
    dibujar_pie_pagina(c, page_width, margin, height, margin_left, certificado)

    # ----- cuerpo del certificado -----

    page_width, page_height = A4
    margin_left = 75
    margin_right = 50
    margin_top = 150
    margin_bottom = 60
    contenido_ancho = page_width - margin_left - margin_right
    contenido_alto = page_height - margin_top - margin_bottom
    # Crear estilo para texto justificado
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.alignment = 4  # Justificación
    style.fontName = "Helvetica"
    style.fontSize = 10
    style.leading = 16  # Espaciado entre líneas

    # Texto a justificar
    texto = (
        f"  El Servicio de Registro Cívico de LA PAZ a solicitud expresa de: <b> {certificado.nombres_solicitante}</b> con C.I."
        f":<b>{certificado.ci_solicitante}</b>"
    )
    parrafo = Paragraph(texto, style)

    # Crear un marco (Frame) para colocar el texto
    frame = Frame(
        margin_left,  # X inicial (margen izquierdo)
        margin_bottom,  # Y inicial (margen inferior)
        contenido_ancho,  # Ancho disponible
        contenido_alto,  # Alto disponible
        showBoundary=0,  # Cambiar a 1 para mostrar bordes del marco
    )

    # Dibuja el contenido del Paragraph en el Frame
    frame.addFromList([parrafo], c)

    body_y = height - margin - 145
    c.setFont("Helvetica", 11)
    lines = [
        "  C E R T I F I C A :"
        ]
    for line in lines:
        c.drawString(margin_left, body_y, line)
        body_y -= 18

    page_width, page_height = A4
    margin_left = 75
    margin_right = 50
    margin_top = 210
    margin_bottom = 60
    contenido_ancho = page_width - margin_left - margin_right
    contenido_alto = page_height - margin_top - margin_bottom
    # Crear estilo para texto justificado
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.alignment = 4  # Justificación
    style.fontName = "Helvetica"
    style.fontSize = 10
    style.leading = 16  # Espaciado entre líneas

    # Texto a justificar
    texto = (
        "Que, efectuada la verificación en el archivo histórico del Servicio de Registro Cívico, de filiación en el"
        f" orden de descendencia en primer grado de:  <b>{certificado.nombres_progenitor} {certificado.primer_apellido_progenitor} {certificado.segundo_apellido_progenitor}</b>, conforme a los datos "
        "proporcionados por el/la solicitante en el formulario FOR-02(PRO-GRC-CDC-01) con número correlativo: "
        f"<b>F.C.F./LA PAZ Nº: {certificado.numero_certificado} </b>, se identifica el (los)  siguiente(s)  registro(s) de Nacimiento donde figura como progenitor(a):"

    )
    parrafo = Paragraph(texto, style)

    # Crear un marco (Frame) para colocar el texto
    frame = Frame(
        margin_left,  # X inicial (margen izquierdo)
        margin_bottom,  # Y inicial (margen inferior)
        contenido_ancho,  # Ancho disponible
        contenido_alto,  # Alto disponible
        showBoundary=0,  # Cambiar a 1 para mostrar bordes del marco
    )

    # Dibuja el contenido del Paragraph en el Frame
    frame.addFromList([parrafo], c)

    # tabla de descendientes
    table_data = [
    ["", "Datos del Registro", "", "", "", "Titular del Registro", "", "", "", ""],
    ["No.", "Oficialia", " Libro ", " Partida ", " F. Inscripción ",
     "Nombres", " Ap Paterno ", " Ap Materno ", "Sexo", "F. Nac"]
    ]

    datos_tabla = certificado.descendientes.all()   
    for i, d in enumerate(datos_tabla, start=1):
        table_data.append([
            str(i),
            d.oficialia,
            d.libro,
            d.partida,
            d.fecha_inscripcion.strftime("%d/%m/%Y"),
            d.nombres,
            d.primer_apellido or "",
            d.segundo_apellido or "",
            d.sexo,
            d.fecha_nacimiento.strftime("%d/%m/%Y"),
        ])

    available_width = page_width - margin_left - margin_right
    column_widths = calculate_column_widths(
        table_data,
        available_width
    )
    total_table_width = sum(column_widths)
    x_start = 12 + (page_width - total_table_width) / 2

    # llamada a funcion de dibujar la tabla con los registros de
    draw_table_multipage(
        c,
        certificado,
        table_data,
        column_widths,
        x_start,
        y_start=page_height - margin - 240,
        page_width=page_width,
        page_height=page_height,
        margin_top=150,
        margin_bottom=70,
    )

    # Ultima parte del documento guarda el certificado y le asigna nombre
    c.save()

    buffer.seek(0)

    certificado.certificado.save(
        f"cert_{certificado.numero_certificado}.pdf",
        ContentFile(buffer.read()),
        save=False
    )

def dibujar_encabezado(c, page_width, page_height, margin, margin_left, certificado):

    BASE_DIR = Path(__file__).resolve().parent.parent
    logo_path = str(BASE_DIR / "static" / "images" / "logo.png")
    marca_agua_path = str(BASE_DIR / "static" / "images" / "marca.png")

    pdfmetrics.registerFont(TTFont("Bookman-Bold", "BOOKOSB.TTF")) # Negrita

    # ----- marca de agua -----
    if os.path.exists(marca_agua_path):
        c.saveState()
        c.setFillColorRGB(0.9, 0.9, 0.9)  # Gris claro
        c.setFillAlpha(0.4)  # Transparencia
        c.drawImage(marca_agua_path, x=0, y=0, width=600, height=850, mask="auto")
        c.restoreState()

    # ----- texto lateral --------
    c.saveState()
    c.setFont('Helvetica-Bold', 6)
    c.translate(40, page_height / 2)
    c.rotate(90)
    c.drawCentredString(
        0, 
        0, 
        "El presente certificado no tiene valor legal si no está firmado y será nulo si contiene enmiendas, borrones, raspaduras o superposiciones."
    )
    c.restoreState()

    # ----- logo -----
    if os.path.exists(logo_path):
        logo_width = 150
        logo_height = 50
        logo_x = (page_width - logo_width) / 2
        logo_y = page_height - margin - 20
        c.drawImage(
            logo_path,
            logo_x,
            logo_y,
            width=logo_width,
            height=logo_height,
            mask="auto"
        )
    
    # ----- titulo -----
    c.setFont('Helvetica-Bold', 6)
    c.setStrokeColor(lightgrey) 
    c.line(margin_left, page_height - margin - 40, page_width - margin, page_height - margin - 40)
    c.line(margin_left, page_height - margin - 40, margin_left, page_height - margin - 90)
    c.line(page_width - margin - 160, page_height - margin - 40, page_width - margin - 160, page_height - margin - 90)
    c.line(page_width - margin, page_height - margin - 40, page_width - margin, page_height - margin - 90)
    c.line(margin_left, page_height - margin - 90, page_width - margin, page_height - margin - 90)

    c.setFont("Bookman-Bold", 16)
    c.drawString(margin_left, page_height - margin - 55,
                 " CERTIFICACIÓN DE FILIACIÓN")
    c.drawString(margin_left, page_height - margin - 70,
                 " DESCENDENCIA")
    
    c.setFont("Bookman-Bold", 10)
    c.drawRightString(page_width - margin, page_height - margin - 36, f"Código de seguridad: {certificado.codigo_seguridad}")

    c.setFont("Helvetica-BoldOblique", 12)
    c.drawRightString(page_width - margin, page_height - margin - 52, "SERECÍ LA PAZ   ")
    c.drawRightString(page_width - margin, page_height - margin - 68,  f"DESC. N°:{certificado.numero_certificado}/2026 ")

def dibujar_pie_pagina(c, page_width, margin, page_height, margin_left, certificado):

    # QR y Normativa
    body_y = page_height - margin - 727
    c.setFont("Helvetica", 7)
    lines = [
        "Cc.Arch.", 
        f"{certificado.primer_apellido_progenitor[0]}{certificado.segundo_apellido_progenitor[0]}-{certificado.correlativo}"
        ]
    for line in lines:
        c.drawString(margin_left + 10, body_y, line, charSpace=0.09)
        body_y -= 8
    
    body_y = page_height - margin - 680
    lines_normativa = [
        "La presente certificación es otorgada en cumplimiento de la Ley Nº 018 del Órgano Electoral Plurinacional,",
        "Reglamento de Acceso a la información de Datos del Servicio de Registro Cívico (SERECÍ)  aprobada por ",
        "Sala Plena del  T.S.E.  mediante  R.A. N.º 263/2011."
    ]
    for line in lines_normativa:
        c.drawString(margin_left + 90, body_y, line, charSpace=0.09)
        body_y -= 10

    # Añade el código QR
    qr_path = certificado.codigo_qr.path
    body_y = page_height - margin - 300
    qr_x = margin_left
    qr_y = body_y - 420
    c.drawImage(qr_path, qr_x, qr_y, width=75, height=75)

    # parte final del documento
    c.setFont("Helvetica-Oblique", 6)
    c.drawCentredString(page_width / 2, 50, "VÁLIDO POR 60 DÍAS")
    c.drawString(margin, 45, "               ........................................................................................................................................................................................................................................................................")
    c.drawCentredString(page_width / 2, 34,"Av. 16 de Julio N° 23 frente a la plaza Venezuela, El Prado")
    c.drawCentredString(page_width / 2, 27, "Teléfonos: 2316226 • 2311535 Fax: 2311555")
    c.drawCentredString(page_width / 2, 20, "Servicio de Registro Cívico La Paz")
    c.drawRightString(page_width - margin, 20, "© 2026 CD_OA")

def new_page(c, page_width, page_height, margin, margin_left, certificado):

    c.showPage()

    # Redibujar automáticamente
    dibujar_encabezado(c, page_width, page_height, margin, margin_left, certificado)
    dibujar_pie_pagina(c, page_width, margin, page_height, margin_left, certificado)

def calculate_column_widths(table_data, available_width, font_name="Helvetica", font_size=8, padding=7):
    max_columns = max(len(row) for row in table_data)
    table_data = [row + [""] * (max_columns - len(row)) for row in table_data]

    column_widths = []

    for col in zip(*table_data):
        max_width = max(
            pdfmetrics.stringWidth(str(cell), font_name, font_size) + padding
            for cell in col
        )
        column_widths.append(max_width)

    total_width = sum(column_widths)

    if total_width > available_width:
        scale = available_width / total_width
        column_widths = [w * scale for w in column_widths]

    return column_widths

def draw_table_multipage(canvas_obj, certificado, table_data, column_widths, x_start, y_start, page_width, page_height, margin_top, margin_bottom):
    """
    Dibuja una tabla que automáticamente continúa en nuevas páginas.
    """
    PRIMERA_PAGINA = 10
    PAGINAS_SIGUIENTES = 28

    header_rows = table_data[:2]
    data_rows = table_data[2:]

    paginas = []

    # primera hoja 
    paginas.append(data_rows[:PRIMERA_PAGINA])

    restantes = data_rows[PRIMERA_PAGINA:]

    # siguientes hojas

    for i in range (0, len(restantes), PAGINAS_SIGUIENTES):
        paginas.append(restantes[i:i + PAGINAS_SIGUIENTES])
    
    total_paginas = len(paginas)

    for page_index, registros in enumerate(paginas):

        table_pagina = header_rows + registros

        table = Table(
            table_pagina,
            colWidths=column_widths,
            repeatRows=2  # ← repite encabezados automáticamente
        )

        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),

            ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-BoldOblique'),
            ('FONTSIZE', (0, 0), (-1, 1), 8),

            ('SPAN', (1, 0), (4, 0)),
            ('SPAN', (5, 0), (9, 0)),
        ]))

        table_width, table_height = table.wrap(page_width, page_height)

        table.drawOn(canvas_obj, x_start, y_start - table_height)

        dibujar_nota_final(canvas_obj, certificado, y_start, table_height, page_width, page_height)

        # paginacion
        numeracion = f"Página {page_index + 1} de {total_paginas}"
        canvas_obj.setFont("Helvetica-Bold", 10)
        canvas_obj.drawRightString(
            540,   # X 
            780,    # Y
            numeracion,
        )


        if page_index < total_paginas - 1:
            new_page(
                canvas_obj,
                page_width,
                page_height,
                margin=60,
                margin_left=75,
                
                certificado=certificado
            )
            y_start = page_height - margin_top - 5


def dibujar_nota_final(c, certificado, y_start, table_height, page_width, page_height):
    margin_left = 75
    margin_right = 50
    margin_bottom = 70

    # posición debajo de la tabla
    body_y = y_start - table_height + margin_bottom - 7

    line_height = 45
    body_y -= line_height + 20

    contenido_ancho = page_width - margin_left - margin_right

    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.alignment = 4
    style.fontName = "Helvetica"
    style.fontSize = 10
    style.leading = 16

    # fecha en español (ejemplo simple)
    fecha = certificado.fecha_emision.strftime("%d/%m/%Y")

    texto = (
        "<b>NOTA:</b> La verificación efectuada en la base de datos del Servicio actualizada a la fecha "
        "de emisión del presente certificado, fue realizada usando los datos proporcionados por el/la solicitante, "
        "razón por la que si se omite algún registro, se debe a que éste no incluye los datos exactos utilizados "
        "en la búsqueda.<br/><br/>"
        "Asimismo, se hace notar que el resultado de la búsqueda practicada para la emisión de la presente "
        "certificación, no excluye la posibilidad de homónimos del progenitor.<br/><br/>"
        "Es cuanto certifico en honor a la verdad para fines consiguientes.<br/><br/>"
        f"La Paz, {fecha}"
    )

    parrafo = Paragraph(texto, style)

    w, h = parrafo.wrap(contenido_ancho, page_height)

    parrafo.drawOn(c, margin_left, body_y - h)

def generar_documentos_certificado(certificado):

    generar_qr(certificado)
    certificado.save(update_fields=["codigo_qr"])

    generar_pdf(certificado)
    certificado.save(update_fields=["certificado"])
