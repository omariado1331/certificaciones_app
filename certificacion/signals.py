from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Funcionario, Administrador

# signals para crear funcionario cuando se asigna el grupo de Funcionario a un usuario
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


# signals para crear administrador cuando se asigna el grupo de Administrador a un usuario
@receiver(post_save, sender=User)
def create_admin(sender, instance, created, **kwargs):
    if created:
        grupo_admin = Group.objects.filter(name="Administrador").first()

        # si el usuario se creo con el grupo asignado Administrador
        if grupo_admin and grupo_admin in instance.groups.all():
            Administrador.objects.get_or_create(user=instance)

@receiver(m2m_changed, sender=User.groups.through)
def asignacion_grupo_administrador(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        grupo_admin = Group.objects.filter(name="Administrador").first()

        # si el grupo agregado es el de Administrador
        if grupo_admin and grupo_admin.pk in pk_set:
            Administrador.objects.get_or_create(user=instance)