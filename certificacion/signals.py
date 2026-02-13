from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Funcionario

@receiver(post_save, sender=User)
def create_funcionario(sender, instance, created, **kwargs):
    if created:
        grupo_funcionario = Group.objects.filter(name="Funcionario").first()

        # si el usuario se creo con el grupo asignado Funcionario
        if grupo_funcionario and grupo_funcionario in instance.groups.all():
            Funcionario.objects.get_or_create(user=instance)

@receiver(m2m_changed, sender=User.groups.through)
def asignacion_grupo_funcionario(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        grupo_funcionario = Group.objects.filter(name="Funcionario").first()

        # si el grupo agregado es el de Funcionario
        if grupo_funcionario and grupo_funcionario.pk in pk_set:
            Funcionario.objects.get_or_create(user=instance)