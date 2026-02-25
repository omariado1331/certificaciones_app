from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CertificadoDescendenciaViewSet, LoginJWTView, FuncionarioInformacionView, FuncionarioUpdateView

router = DefaultRouter()
router.register(r'certificados-descendencia', CertificadoDescendenciaViewSet, basename='certificados-descendencia')

urlpatterns = router.urls + [
    path('login/', LoginJWTView.as_view(), name='login'),
    path('funcionario/me/informacion', FuncionarioInformacionView.as_view()),
    path('funcionario/me', FuncionarioUpdateView.as_view()),
]