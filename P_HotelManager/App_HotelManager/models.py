from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class Usuario(AbstractUser):
    ROL_CHOICES = (
        ('admin', 'Administrador'),
        ('usuario', 'Usuario'),
    )

    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='usuario')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class PerfilHotel(models.Model):
    nombre = models.CharField(max_length=150, default='HotelManager')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    rfc = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=30)
    nacionalidad = models.CharField(max_length=80, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
    Usuario,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='clientes_creados'
)

    class Meta:
        ordering = ['nombre', 'apellido']

    def __str__(self):
        return f'{self.nombre} {self.apellido}'


class Habitacion(models.Model):
    ESTADO_CHOICES = (
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('limpieza', 'En limpieza'),
    )
    
    TIPO_COBRO_CHOICES = (
        ('noche', 'Por noche'),
        ('mensual', 'Mensual'),
    )

    MONEDA_CHOICES = (
        ('NIO', 'Córdobas'),
        ('USD', 'Dólares'),
    )

    nombre = models.CharField(max_length=50)
    piso = models.PositiveIntegerField(default=1)
    capacidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_cobro = models.CharField(max_length=20, choices=TIPO_COBRO_CHOICES, default='noche')
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='NIO')
    aire_acondicionado = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['piso', 'nombre']

    def __str__(self):
        return self.nombre

    @property
    def esta_disponible(self):
        return self.estado == 'disponible'


class Asignacion(models.Model):
    ESTADO_CHOICES = (
        ('activa', 'Activa'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    )

    habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT, related_name='asignaciones')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='asignaciones')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='asignaciones_creadas')
    fecha_inicio = models.DateField(default=timezone.localdate)
    fecha_fin = models.DateField(null=True, blank=True)
    meses = models.PositiveIntegerField(default=0)
    noches = models.PositiveIntegerField(default=0)
    persona_adicional = models.BooleanField(default=False)
    cantidad_personas_adicionales = models.PositiveIntegerField(default=0)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cargo_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f'{self.cliente} - {self.habitacion}'
    
    def calcular_fecha_fin(self):
        """Calcula la fecha de fin basada en la fecha de inicio y los meses/noches"""
        if self.habitacion.tipo_cobro == 'mensual' and self.meses > 0:
            return self.fecha_inicio + timedelta(days=30 * self.meses)
        elif self.noches > 0:
            return self.fecha_inicio + timedelta(days=self.noches)
        return self.fecha_inicio

    def calcular_total(self):
        """Calcula el total basado en el precio de la habitación"""
        precio = self.habitacion.precio
        if self.habitacion.tipo_cobro == 'mensual':
            subtotal = precio * self.meses
        else:
            subtotal = precio * self.noches
        return subtotal + self.cargo_adicional

    def save(self, *args, **kwargs):
        # Guardar precio base
        if not self.precio_base:
            self.precio_base = self.habitacion.precio
        
        # Calcular fecha fin si no tiene
        if not self.fecha_fin:
            self.fecha_fin = self.calcular_fecha_fin()
        
        # Calcular total
        self.total = self.calcular_total()
        
        super().save(*args, **kwargs)


class Pago(models.Model):
    METODO_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
    )

    asignacion = models.ForeignKey(Asignacion, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=30, choices=METODO_CHOICES, default='efectivo')
    referencia = models.CharField(max_length=100, blank=True, null=True)
    fecha_pago = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Pago {self.monto} - {self.asignacion}'