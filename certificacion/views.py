from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, View
from rest_framework.generics import ListAPIView
from urllib.parse import urlencode
from .models import (
    Funcionario, CertificadoDescendencia
)
from .serializer import CertificadoDescendenciaSerializer, CustomTokenObtainPairSerializer, FuncionarioInformacionSerializer, FuncionarioUpdateSerializer, CertificadoDescendenciaListSerializer
from .services.pagination_service import StandardResultsSetPagination
from .security.permissions import IsFuncionario
from .utils import generar_token_preview, validar_token_preview, registrar_auditoria

class CertificadoDescendenciaViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, IsFuncionario]
    
    serializer_class = CertificadoDescendenciaSerializer

    def get_queryset(self):

        funcionario = self.request.user.funcionario

        return ( 
        CertificadoDescendencia.objects
            .filter(funcionario=funcionario)
            .select_related("oficina")
            .prefetch_related("descendientes")
        )

    def perform_create(self, serializer):
        funcionario = self.request.user.funcionario
        oficina = funcionario.oficina
        serializer.save(
            funcionario=funcionario,
            oficina=oficina
        )


class LoginJWTView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [] # Permitir acceso sin autenticación


class FuncionarioInformacionView(APIView):
    
    permission_classes = [IsAuthenticated, IsFuncionario]

    def get(self, request):

        funcionario_id = request.auth.get("funcionario_id")
        
        funcionario = get_object_or_404(
            Funcionario.objects.select_related("oficina"),
            id = funcionario_id
        )

        serializer = FuncionarioInformacionSerializer(funcionario)

        return Response(serializer.data)

class FuncionarioUpdateView(APIView):

    permission_classes = [IsAuthenticated, IsFuncionario]

    def put(self, request):
        funcionario_id = request.auth.get("funcionario_id")

        funcionario = get_object_or_404(
            Funcionario,
            id=funcionario_id
        )

        serializer = FuncionarioUpdateSerializer(
            funcionario,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                { 'message': 'Información actualizada correctamente' },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CertificadosFuncionarioView(ListAPIView):
    serializer_class = CertificadoDescendenciaListSerializer
    permission_classes = [IsAuthenticated, IsFuncionario]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        
        funcionario_id = self.request.auth.get("funcionario_id")

        return (
            CertificadoDescendencia.objects
            .select_related("oficina")
            .filter(funcionario_id=funcionario_id)
            .order_by("-fecha_emision")
        ) 


class CertificadoPreviewURLView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        funcionario_id = request.auth.get("funcionario_id")

        certificado = get_object_or_404(
            CertificadoDescendencia,
            id=pk,
            funcionario_id=funcionario_id
        )

        token = generar_token_preview(certificado.id, funcionario_id)

        query = urlencode({ "token": token })
        preview_url = request.build_absolute_uri(
            f"/api/certificados-descendencia/preview-file/?{query}"
        )

        return Response({
            "preview_url": preview_url,
            "expires_in": 60
        })

class CertificadoPreviewFileView(View):

    def get (self, request):
        token = request.GET.get("token")

        if not token:
            raise Http404("Token no activo")
        
        data = validar_token_preview(token, max_age=60)

        if not data:
            raise Http404("Token invalido / expirado")
        
        certificado_id, funcionario_id = data

        funcionario = Funcionario.objects.get(id=funcionario_id)

        try:
            certificado = CertificadoDescendencia.objects.get(
                id=certificado_id,
                funcionario_id=funcionario_id
            )
        except CertificadoDescendencia.DoesNotExist:
            raise Http404("Certificado no encontrado")

        if not certificado.certificado:
            raise Http404("El registro no tiene certificado")
        
        registrar_auditoria(
            request,
            accion="VIEW",
            descripcion=f"Vista del certificado {certificado.numero_certificado}",
            user=funcionario.user
        )
        
        return FileResponse(
            certificado.certificado.open('rb'),
            content_type='application/pdf',
            filename=f"certificado_descendencia_{certificado.numero_certificado}.pdf"
        )
    
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

class DescargaCertificadoDescendenciaView(APIView):
    permission_classes = [IsAuthenticated, IsFuncionario]

    def get(self, request, pk):

        funcionario_id=request.auth.get('funcionario_id')

        try:
            certificado = CertificadoDescendencia.objects.get(
                id=pk,
                funcionario_id=funcionario_id
            )
        except CertificadoDescendencia.DoesNotExist:
            raise Http404("El certificado no encontrado")
        
        if not certificado.certificado:
            raise Http404("El certificado no existe")

        registrar_auditoria(
            request,
            accion="DOWNLOAD",
            tramite="CertificadoDescendencia",
            tramite_id=certificado.id,
            descripcion=f"Descarga del certificado {certificado.numero_certificado}",
            user=request.user
        )

        return FileResponse(
            certificado.certificado.open('rb'),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"certificado_descendencia_{certificado.numero_certificado}.pdf"
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, IsFuncionario]

    def post(self, request):
        registrar_auditoria(
            request,
            accion="LOGOUT",
            descripcion=f"Cierre de sesion del usuario {request.user.username}",
            user=request.user
        )

        return Response({
            "message": "Sesion cerrada exitosamente"
        })
    