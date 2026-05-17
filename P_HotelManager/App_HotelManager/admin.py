from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Usuario,
    PerfilHotel,
    Cliente,
    Habitacion,
    Asignacion,
    Pago,
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'rol', 'activo', 'is_staff')
    list_filter = ('rol', 'activo', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('Datos del sistema', {
            'fields': ('rol', 'activo')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos del sistema', {
            'fields': ('rol', 'activo')
        }),
    )


@admin.register(PerfilHotel)
class PerfilHotelAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'cedula', 'telefono', 'nacionalidad')
    search_fields = ('nombre', 'apellido', 'cedula', 'telefono')


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'piso',
        'capacidad',
        'precio',
        'tipo_cobro',
        'aire_acondicionado',
        'activa',
    )
    list_filter = ('piso', 'tipo_cobro', 'aire_acondicionado', 'activa')
    search_fields = ('nombre',)


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'habitacion',
        'cliente',
        'fecha_inicio',
        'fecha_fin',
        'meses',
        'noches',
        'total',
        'estado',
    )
    list_filter = ('estado', 'fecha_inicio')
    search_fields = (
        'habitacion__nombre',
        'cliente__nombre',
        'cliente__apellido',
        'cliente__cedula',
    )


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'asignacion', 'monto', 'metodo', 'referencia', 'fecha_pago')
    list_filter = ('metodo', 'fecha_pago')
    search_fields = (
        'asignacion__cliente__nombre',
        'asignacion__cliente__apellido',
        'referencia',
    )