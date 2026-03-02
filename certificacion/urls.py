from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    CertificadoDescendenciaViewSet, LoginJWTView, FuncionarioInformacionView, 
    FuncionarioUpdateView, CertificadosFuncionarioView, CertificadoPreviewURLView,
    CertificadoPreviewFileView)

router = DefaultRouter()
router.register(r'certificados-descendencia', CertificadoDescendenciaViewSet, basename='certificados-descendencia')

urlpatterns = [
    path('certificados-descendencia/preview-file/', CertificadoPreviewFileView.as_view()),
    path('login/', LoginJWTView.as_view(), name='login'),
    path('funcionario/me/informacion/', FuncionarioInformacionView.as_view()),
    path('funcionario/me/', FuncionarioUpdateView.as_view()),
    path('funcionario/me/certificados/', CertificadosFuncionarioView.as_view()),
    path('certificados-descendencia/<int:pk>/preview/', CertificadoPreviewURLView.as_view()),
] + router.urls