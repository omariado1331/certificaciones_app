from .utils import registrar_auditoria

class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwds):
        response = self.get_response(request)

        if request.user.is_authenticated:

            metodo = request.method

            if metodo == "POST":
                accion = "CREATE"
            elif metodo == "PUT":
                accion = "UPDATE"
            elif metodo == "DELETE":
                accion = "DELETE"
            else:
                return response

            registrar_auditoria(
                request,
                accion=accion,
                descripcion=f"Metodo {metodo} - {request.path}"
            )
            
        return response