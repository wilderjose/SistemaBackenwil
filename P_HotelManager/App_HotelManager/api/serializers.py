from rest_framework import serializers
from django.contrib.auth import get_user_model
from App_HotelManager.models import (
    PerfilHotel,
    Cliente,
    Habitacion,
    Asignacion,
    Pago,
)

Usuario = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'rol',
            'activo',
            'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        usuario = Usuario(**validated_data)

        if password:
            usuario.set_password(password)
        else:
            usuario.set_password('123456')

        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class PerfilHotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilHotel
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = [
            'id',
            'nombre',
            'apellido',
            'nombre_completo',
            'cedula',
            'telefono',
            'nacionalidad',
            'creado_en',
        ]

    def get_nombre_completo(self, obj):
        return f'{obj.nombre} {obj.apellido}'


class HabitacionSerializer(serializers.ModelSerializer):
    disponible = serializers.SerializerMethodField()
    estado_texto = serializers.SerializerMethodField()

    class Meta:
        model = Habitacion
        fields = [
        'id',
        'nombre',
        'piso',
        'capacidad',
        'precio',
        'tipo_cobro',
        'moneda',
        'aire_acondicionado',
        'estado',
        'activa',
        'disponible',
        'estado_texto',
    ]


    def get_disponible(self, obj):
        return obj.estado == 'disponible'

    def get_estado_texto(self, obj):
        if obj.estado == 'disponible':
            return 'Disponible'
        if obj.estado == 'ocupada':
            return 'Ocupada'
        if obj.estado == 'limpieza':
            return 'En limpieza'
        return obj.estado

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'


class AsignacionSerializer(serializers.ModelSerializer):
    cliente_data = ClienteSerializer(source='cliente', read_only=True)
    habitacion_data = HabitacionSerializer(source='habitacion', read_only=True)
    pagos = PagoSerializer(many=True, read_only=True)

    cliente_nombre = serializers.SerializerMethodField()
    habitacion_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Asignacion
        fields = [
            'id',
            'habitacion',
            'habitacion_data',
            'habitacion_nombre',
            'cliente',
            'cliente_data',
            'cliente_nombre',
            'usuario',
            'fecha_inicio',
            'fecha_fin',
            'meses',
            'noches',
            'persona_adicional',
            'cantidad_personas_adicionales',
            'precio_base',
            'cargo_adicional',
            'total',
            'estado',
            'pagos',
            'creado_en',
        ]
        read_only_fields = ['precio_base', 'total', 'fecha_fin', 'usuario']

    def get_cliente_nombre(self, obj):
        return f'{obj.cliente.nombre} {obj.cliente.apellido}'

    def get_habitacion_nombre(self, obj):
        return obj.habitacion.nombre

    def validate(self, data):
        habitacion = data.get('habitacion')
        cliente = data.get('cliente')
        meses = data.get('meses', 0)
        noches = data.get('noches', 0)

        if self.instance is None:
            if habitacion and habitacion.estado != 'disponible':
                raise serializers.ValidationError(
                    'Esta habitación no está disponible.'
                )

            if cliente and Asignacion.objects.filter(cliente=cliente, estado='activa').exists():
                raise serializers.ValidationError(
                    'Este cliente ya tiene una habitación asignada actualmente.'
                )

        if habitacion.tipo_cobro == 'mensual':
            if meses <= 0:
                raise serializers.ValidationError(
                    'Debe indicar la cantidad de meses para una habitación mensual.'
                )

        if habitacion.tipo_cobro == 'noche':
            if noches <= 0:
                raise serializers.ValidationError(
                    'Debe indicar la cantidad de noches.'
                )

        return data

    def create(self, validated_data):
        from datetime import timedelta
        from django.utils import timezone
        
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['usuario'] = request.user

        habitacion = validated_data['habitacion']
       
        
        # 🔥 ACTUALIZAR EL ESTADO DE LA HABITACIÓN A OCUPADA 🔥
        habitacion.estado = 'ocupada'
        habitacion.save()

        meses = validated_data.get('meses', 0)
        noches = validated_data.get('noches', 0)
        cargo_adicional = validated_data.get('cargo_adicional', 0)
        
        # Obtener fecha_inicio, si no viene usar la fecha actual
        fecha_inicio = validated_data.get('fecha_inicio')
        if fecha_inicio is None:
            fecha_inicio = timezone.now().date()
            validated_data['fecha_inicio'] = fecha_inicio
        
        # Calcular precio base
        validated_data['precio_base'] = habitacion.precio
        
        # Calcular total
        if habitacion.tipo_cobro == 'mensual':
            total = float(habitacion.precio) * meses
        else:
            total = float(habitacion.precio) * noches
        validated_data['total'] = total + float(cargo_adicional)
        
        # Calcular fecha fin
        if habitacion.tipo_cobro == 'mensual' and meses > 0:
            validated_data['fecha_fin'] = fecha_inicio + timedelta(days=30 * meses)
        elif noches > 0:
            validated_data['fecha_fin'] = fecha_inicio + timedelta(days=noches)
        else:
            validated_data['fecha_fin'] = fecha_inicio
        
        return super().create(validated_data)