from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CertificadoDescendenciaViewSet, LoginJWTView, DebugHeaders

router = DefaultRouter()
router.register(r'certificados-descendencia', CertificadoDescendenciaViewSet, basename='certificados-descendencia')

urlpatterns = router.urls + [
    path('login/', LoginJWTView.as_view(), name='login'),
]