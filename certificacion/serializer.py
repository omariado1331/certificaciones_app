from rest_framework import serializers
from .models import CertificadoDescendencia, Descendiente
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Funcionario, Administrador, CertificadoDescendencia

class DescendienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descendiente
        exclude = ('certificado_descendencia',)


class CertificadoDescendenciaSerializer(serializers.ModelSerializer):

    descendientes = DescendienteSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = CertificadoDescendencia
        fields = '__all__'
        read_only_fields = (
            'codigo_seguridad',
            'correlativo',
            'fecha_emision',
            'fecha_vencimiento',
            'estado_certificado',
            'certificado',
            'codigo_qr'
        )

    def create(self, validated_data):
        descendientes_data = validated_data.pop('descendientes', [])

        with transaction.atomic():
            # creacion del certificado de descendencia
            certificado = CertificadoDescendencia.objects.create(**validated_data)

            # creacion de los descendientes asociados
            descendientes_obj = [
                Descendiente(
                    certificado_descendencia=certificado,
                    **desc
                )
                for desc in descendientes_data
            ]

            Descendiente.objects.bulk_create(descendientes_obj)

            from certificacion.services.certificado_service import (
                generar_documentos_certificado
            )
            generar_documentos_certificado(certificado)
               
        return certificado

class CertificadoDescendenciaListSerializer(serializers.ModelSerializer):

    certificado = serializers.SerializerMethodField()
    nombre_oficina = serializers.CharField(source='oficina.nombre')
    numero_certificado = serializers.ReadOnlyField()

    class Meta:
        model= CertificadoDescendencia
        fields = [
            "certificado",
            "ci_solicitante",
            "nombres_solicitante",
            "estado_certificado",
            "numero_certificado",
            "nombre_oficina",
            "fecha_emision",
        ]

    def get_certificado(self, obj):
        request = self.context.get('request')
        if obj.certificado:
            return request.build_absolute_uri(obj.certificado.url)
        return None

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        token = self.get_token(user)

        try:
            funcionario = Funcionario.objects.select_related("oficina").get(user=user)

            token["rol"] = "funcionario"
            token["funcionario_id"] = funcionario.id

            if funcionario.oficina:
                token["oficina_id"] = funcionario.oficina.id
        
        except Funcionario.DoesNotExist:
            try:
                administrador = Administrador.objects.get(user=user)

                token["rol"] = "administrador"
                token["administrador_id"] = administrador.id
            except Administrador.DoesNotExist:
                raise serializers.ValidationError(
                    { "detail": "El usuario no tiene un rol asignado" }
                )
            
        data["access"] = str(token.access_token)
        data["refresh"] = str(token)

        return data


class FuncionarioInformacionSerializer(serializers.ModelSerializer):

    oficina_nombre = serializers.SerializerMethodField()
    oficina_direccion = serializers.SerializerMethodField()

    class Meta:
        model = Funcionario
        fields = [
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "ci",
            "telefono",
            "oficina_nombre",
            "oficina_direccion",
        ]

    def get_oficina_nombre(self, obj):
        return obj.oficina.nombre if obj.oficina else None

    def get_oficina_direccion(self, obj):
        return obj.oficina.direccion if obj.oficina else None


class FuncionarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcionario
        fields = [
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "ci",
            "telefono",
        ]
