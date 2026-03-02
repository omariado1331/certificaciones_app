from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

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