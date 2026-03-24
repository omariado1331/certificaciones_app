from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .models import AuditoriaSistema

signer = TimestampSigner()

def generar_token_preview(certificado_id, funcionario_id):
    value = f"{certificado_id}:{funcionario_id}"
    return signer.sign(value)

def validar_token_preview(token, max_age=60):
    try:
        value = signer.unsign(token, max_age=max_age)
        certificado_id, funcionario_id = value.split(":")
        print(int(certificado_id))
        print (int(funcionario_id))
        return int(certificado_id), int(funcionario_id)
    except SignatureExpired:
        return None
    except BadSignature:
        return None

def registrar_auditoria(request, accion, tramite=None, tramite_id=None, descripcion=None, user=None):

    if not user:
        user = request.user if request.user.is_authenticated else None

    funcionario = None
    
    try:
        funcionario = user.funcionario
    except:
        pass
    
    ip = request.META.get("REMOTE_ADDR")

    user_agent = request.META.get("HTTP_USER_AGENT")

    AuditoriaSistema.objects.create(
        user=user,
        funcionario=funcionario,
        accion=accion,
        tramite=tramite,
        tramite_id=tramite_id,
        descripcion=descripcion,
        ip=ip,
        user_agent=user_agent
    )
