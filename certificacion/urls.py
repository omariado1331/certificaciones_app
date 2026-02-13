from rest_framework.routers import DefaultRouter
from .views import CertificadoDescendenciaViewSet

router = DefaultRouter()
router.register(r'certificados-descendencia', CertificadoDescendenciaViewSet, basename='certificados-descendencia')

urlpatterns = router.urls