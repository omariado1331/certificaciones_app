from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CertificadoDescendenciaViewSet, LoginView, LoginJWTView, DebugHeaders

router = DefaultRouter()
router.register(r'certificados-descendencia', CertificadoDescendenciaViewSet, basename='certificados-descendencia')

urlpatterns = router.urls + [
    path('login-jwt/', LoginJWTView.as_view(), name='login-jwt'),
    # Ruta para probar los headers en la solicitud y respuesta (verificar conectividad con token)
    # path('debug-headers/', DebugHeaders.as_view(), name='debug-headers'),
]