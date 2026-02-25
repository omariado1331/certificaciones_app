from .models import CertificadoDescendencia
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import Funcionario
from .serializer import CertificadoDescendenciaSerializer, CustomTokenObtainPairSerializer, FuncionarioInformacionSerializer, FuncionarioUpdateSerializer, CertificadoDescendenciaListSerializer
from .services.pagination_service import StandardResultsSetPagination
from .security.permissions import IsFuncionario

class CertificadoDescendenciaViewSet(viewsets.ModelViewSet):
    queryset = CertificadoDescendencia.objects.all().select_related(
        'oficina'
    ).prefetch_related('descendientes')

    permission_classes = [IsAuthenticated, IsFuncionario]
    
    serializer_class = CertificadoDescendenciaSerializer

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

