from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Oficina,
    CorrelativoDescendencia,
    CertificadoDescendencia,
    Descendiente,
    Funcionario
)
# Register your models here.
@admin.register(Oficina)
class OficinaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "sigla", "telefono")
    search_fields = ("nombre", "sigla")

@admin.register(CorrelativoDescendencia)
class CorrelativoDescendenciaAdmin(admin.ModelAdmin):
    list_display = ("nro_correlativo", "oficina")
    search_fields = ("oficina__nombre", "oficina__sigla")

@admin.register(CertificadoDescendencia)
class CertificadoDescendenciaAdmin(SimpleHistoryAdmin):
    list_display = (
        "ci_solicitante",
        "nombres_solicitante",
        "codigo_seguridad",
        "correlativo",
        "oficina",
        "estado_certificado",
        "fecha_emision",
        "fecha_vencimiento"
    )
    search_fields = ("ci_solicitante", "nombres_solicitante", "correlativo")
    list_filter = ("estado_certificado", "oficina")

@admin.register(Descendiente)
class DescendienteAdmin(admin.ModelAdmin):
    list_display = ("nombres", "primer_apellido", "segundo_apellido", "fecha_nacimiento", "oficialia")
    search_fields = ("nombres", "primer_apellido", "segundo_apellido", "oficialia")

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ("oficina", "nombres", "apellido_paterno", "apellido_materno")
    search_fields = ("user__username",)