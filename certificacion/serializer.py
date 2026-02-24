from rest_framework import serializers
from .models import CertificadoDescendencia, Descendiente
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Funcionario
from .models import Administrador

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

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    rol = serializers.CharField(write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)

        rol = attrs.get("rol")
        user = self.user

        token = self.get_token(user)

        # VALIDACIÓN POR ROL
        if rol == "funcionario":
            try:
                funcionario = Funcionario.objects.select_related(
                    "oficina"
                ).get(user=user)

                token["rol"] = "funcionario"
                token["funcionario_id"] = funcionario.id

                if funcionario.oficina:
                    token["oficina_id"] = funcionario.oficina.id

            except Funcionario.DoesNotExist:
                raise serializers.ValidationError(
                    {"detail": "El usuario no pertenece al rol FUNCIONARIO"}
                )

        elif rol == "administrador":
            try:
                administrador = Administrador.objects.get(user=user)
                token["rol"] = "administrador"
                token["administrador_id"] = administrador.id

            except Administrador.DoesNotExist:
                raise serializers.ValidationError(
                    {"detail": "El usuario no pertenece al rol ADMINISTRADOR"}
                )

        else:
            raise serializers.ValidationError(
                {"detail": "Rol inválido"}
            )

        # devolver tokens
        data["access"] = str(token.access_token)
        data["refresh"] = str(token)

        return data
