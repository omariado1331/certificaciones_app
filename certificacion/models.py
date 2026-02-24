from django.db import models, transaction
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from django.utils import timezone
from datetime import timedelta
import uuid

# Create your models here.

class Oficina(models.Model):
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} ({self.sigla})"

class CorrelativoDescendencia(models.Model):
    nro_correlativo = models.IntegerField(default=0)
    oficina = models.OneToOneField(Oficina, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nro_correlativo}-{self.oficina.sigla}"

class Funcionario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=100, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    ci = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno} - CI: {self.ci}"

class CertificadoDescendencia(models.Model):
    ESTADOS_CERTIFICADO = [
        ('VIGENTE', 'Vigente'),
        ('VENCIDO', 'Vencido'),
        ('ANULADO', 'Anulado'),
    ]
    certificado = models.FileField(upload_to='certificados/', null=True, blank=True)
    ci_solicitante = models.CharField(max_length=20, db_index=True)
    nombres_solicitante = models.CharField(max_length=100)
    # progenitor(a) fields
    nombres_progenitor = models.CharField(max_length=100)
    primer_apellido_progenitor = models.CharField(max_length=100, blank=True, null=True)
    segundo_apellido_progenitor = models.CharField(max_length=100, blank=True, null=True)

    # estos campos se llenan desde el formulario de solicitud
    correlativo_formulario = models.CharField(max_length=50, unique=True, null=True, blank=True)
    texto_certificado = models.TextField(null=True, blank=True)

    # codigo qr y codigo de seguridad para validación del certificado
    codigo_qr = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    codigo_seguridad = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )
    estado_certificado = models.CharField(
        max_length=20,
        choices=ESTADOS_CERTIFICADO,
        default='VIGENTE'
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    correlativo = models.IntegerField()
    oficina = models.ForeignKey(Oficina, on_delete=models.PROTECT)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, null=True, blank=True)
    fecha_vencimiento = models.DateTimeField()

    # property to generate the certificate number based on the correlativo and office sigla
    @property
    def numero_certificado(self):
        return f"{self.correlativo}-{self.oficina.sigla}"
    
    # historical records for tracking changes
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # Normalize the CI by stripping whitespace and converting to uppercase
        self.ci_solicitante = self.ci_solicitante.strip().upper()
        # if the certificate is being created for the first time, set the correlativo and expiration date
        if not self.pk:
            with transaction.atomic():
                # lock the correlativo record for this office
                correlativo_obj, created = CorrelativoDescendencia.objects.select_for_update().get_or_create(
                    oficina=self.oficina,
                    defaults={'nro_correlativo': 0}
                )

                # increment the correlativo and save it back to the database
                correlativo_obj.nro_correlativo += 1
                correlativo_obj.save()

                self.correlativo = correlativo_obj.nro_correlativo

                # set expiration date to 1 year from now
                self.fecha_vencimiento = timezone.now() + timedelta(days=60)
        
        # refresh the state of the certificate based on the expiration date
        if self.fecha_vencimiento and timezone.now() > self.fecha_vencimiento:
            self.estado_certificado = 'VENCIDO'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificado: {self.certificado} - Solicitante: {self.nombres_solicitante} {self.estado_certificado}"

class Descendiente(models.Model):
    nombres = models.CharField(max_length=100)
    primer_apellido = models.CharField(max_length=100, blank=True, null=True)
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    oficialia = models.CharField(max_length=100)
    libro = models.CharField(max_length=20)
    partida = models.CharField(max_length=20)
    fecha_inscripcion = models.DateField()
    sexo = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    certificado_descendencia = models.ForeignKey(
        CertificadoDescendencia, 
        on_delete=models.CASCADE, 
        related_name='descendientes'
    )

    def __str__(self):
        return f"{self.nombres} {self.primer_apellido} {self.segundo_apellido} - Nacido el {self.fecha_nacimiento}"
    

class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=100, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    ci = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno} - CI: {self.ci}"