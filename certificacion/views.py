from django.shortcuts import render
from .models import CertificadoDescendencia
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from .serializer import CertificadoDescendenciaSerializer, CustomTokenObtainPairSerializer

class CertificadoDescendenciaViewSet(viewsets.ModelViewSet):
    queryset = CertificadoDescendencia.objects.all().select_related(
        'oficina'
    ).prefetch_related('descendientes')

    permission_classes = [IsAuthenticated]
    
    serializer_class = CertificadoDescendenciaSerializer

class LoginJWTView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [] # Permitir acceso sin autenticación

class DebugHeaders(APIView):

    permission_classes = []

    def get(self, request):
        return Response({
            "headers": dict(request.headers)
        })
        
        
