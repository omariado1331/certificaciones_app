from rest_framework import serializers
from .models import CertificadoDescendencia, Descendiente
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Funcionario

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


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Credenciales inválidas")
        
        try:
            funcionario = Funcionario.objects.select_related('oficina').get(user=user)
        except Funcionario.DoesNotExist:
            raise serializers.ValidationError("El usuario no es un funcionario")
        
        # generar JWT
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "funcionario": {
                "id": funcionario.id,
                "nombres": funcionario.nombres,
                "apellido_paterno": funcionario.apellido_paterno,
                "apellido_materno": funcionario.apellido_materno,
                "ci": funcionario.ci,
                "telefono": funcionario.telefono,
                "oficina": funcionario.oficina.nombre if funcionario.oficina else None,
            }
        }
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agregar información adicional al token
        try:
            funcionario = Funcionario.objects.select_related('oficina').get(user=user)
            token['funcionario_id'] = funcionario.id
            token['ci'] = funcionario.ci
            if funcionario.oficina:
                token['oficina_id'] = funcionario.oficina.id
            
        except Funcionario.DoesNotExist:
            pass

        return token
