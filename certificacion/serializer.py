from rest_framework import serializers
from .models import CertificadoDescendencia, Descendiente
from django.db import transaction

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

            return certificado
        