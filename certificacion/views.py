from django.shortcuts import render
from .models import CertificadoDescendencia
from .serializer import CertificadoDescendenciaSerializer
from rest_framework import viewsets

class CertificadoDescendenciaViewSet(viewsets.ModelViewSet):
    queryset = CertificadoDescendencia.objects.all().select_related(
        'oficina'
    ).prefetch_related('descendientes')
    
    serializer_class = CertificadoDescendenciaSerializer

