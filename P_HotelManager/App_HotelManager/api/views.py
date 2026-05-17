from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q, Sum
from rest_framework.authtoken.models import Token
from App_HotelManager.models import (
    PerfilHotel,
    Cliente,
    Habitacion,
    Asignacion,
    Pago,
)
from .serializers import (
    UsuarioSerializer,
    PerfilHotelSerializer,
    ClienteSerializer,
    HabitacionSerializer,
    AsignacionSerializer,
    PagoSerializer,
)

Usuario = get_user_model()


from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    usuario = authenticate(username=username, password=password)

    if usuario is None:
        return Response(
            {'error': 'Usuario o contraseña incorrectos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not usuario.activo:
        return Response(
            {'error': 'El usuario está inactivo'},
            status=status.HTTP_403_FORBIDDEN
        )

    token, created = Token.objects.get_or_create(user=usuario)

    return Response({
        'token': token.key,
        'user_id': usuario.id,
        'username': usuario.username,
        'first_name': usuario.first_name,
        'last_name': usuario.last_name,
        'email': usuario.email,
        'rol': usuario.rol,
    })

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Usuario.objects.all().order_by('id')
        buscar = self.request.query_params.get('buscar')

        if buscar:
            queryset = queryset.filter(
                Q(username__icontains=buscar) |
                Q(first_name__icontains=buscar) |
                Q(last_name__icontains=buscar) |
                Q(email__icontains=buscar)
            )

        return queryset


class PerfilHotelViewSet(viewsets.ModelViewSet):
    queryset = PerfilHotel.objects.all()
    serializer_class = PerfilHotelSerializer
    permission_classes = [IsAuthenticated]


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Cliente.objects.all()
        buscar = self.request.query_params.get('buscar')

        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(apellido__icontains=buscar) |
                Q(cedula__icontains=buscar) |
                Q(telefono__icontains=buscar) |
                Q(nacionalidad__icontains=buscar)
            )

        return queryset


class HabitacionViewSet(viewsets.ModelViewSet):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Habitacion.objects.filter(activa=True)

        piso = self.request.query_params.get('piso')
        tipo_cobro = self.request.query_params.get('tipo_cobro')
        disponibles = self.request.query_params.get('disponibles')
        estado = self.request.query_params.get('estado')

        if piso:
            queryset = queryset.filter(piso=piso)

        if tipo_cobro:
            queryset = queryset.filter(tipo_cobro=tipo_cobro)

        if estado:
            queryset = queryset.filter(estado=estado)

        if disponibles == 'true':
            queryset = queryset.filter(estado='disponible')

        return queryset.order_by('piso', 'nombre')

    @action(detail=False, methods=['get'])
    def resumen(self, request):
        habitaciones = Habitacion.objects.filter(activa=True)

        total = habitaciones.count()
        disponibles = habitaciones.filter(estado='disponible').count()
        ocupadas = habitaciones.filter(estado='ocupada').count()
        limpiando = habitaciones.filter(estado='limpieza').count()

        return Response({
            'total': total,
            'disponibles': disponibles,
            'ocupadas': ocupadas,
            'limpiando': limpiando,
        })

    @action(detail=True, methods=['post'])
    def marcar_lista(self, request, pk=None):
        habitacion = self.get_object()
        habitacion.estado = 'disponible'
        habitacion.save()

        return Response({
            'mensaje': 'La habitación ya está disponible.'
        })



class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.select_related(
        'habitacion',
        'cliente',
        'usuario'
    ).all()
    serializer_class = AsignacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Asignacion.objects.select_related(
            'habitacion',
            'cliente',
            'usuario'
        ).all()

        estado = self.request.query_params.get('estado')
        cliente = self.request.query_params.get('cliente')
        habitacion = self.request.query_params.get('habitacion')

        if estado:
            queryset = queryset.filter(estado=estado)

        if cliente:
            queryset = queryset.filter(cliente_id=cliente)

        if habitacion:
            queryset = queryset.filter(habitacion_id=habitacion)

        return queryset.order_by('-creado_en')

    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        asignacion = self.get_object()
        asignacion.estado = 'finalizada'
        asignacion.save()

        habitacion = asignacion.habitacion
        habitacion.estado = 'limpieza'
        habitacion.save()

        return Response({
            'mensaje': 'Asignación finalizada. La habitación pasó a limpieza.'
        })

    @action(detail=False, methods=['get'])
    def activas(self, request):
        asignaciones = self.get_queryset().filter(estado='activa')
        serializer = self.get_serializer(asignaciones, many=True)

        return Response(serializer.data)

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.select_related('asignacion').all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Pago.objects.select_related('asignacion').all()

        asignacion = self.request.query_params.get('asignacion')

        if asignacion:
            queryset = queryset.filter(asignacion_id=asignacion)

        return queryset.order_by('-fecha_pago')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_resumen(request):
    habitaciones = Habitacion.objects.filter(activa=True)

    ids_ocupadas = Asignacion.objects.filter(
        estado='activa'
    ).values_list('habitacion_id', flat=True)

    total_habitaciones = habitaciones.count()
    habitaciones_ocupadas = habitaciones.filter(id__in=ids_ocupadas).count()
    habitaciones_disponibles = total_habitaciones - habitaciones_ocupadas

    total_clientes = Cliente.objects.count()
    asignaciones_activas = Asignacion.objects.filter(estado='activa').count()

    ingresos = Pago.objects.aggregate(
        total=Sum('monto')
    )['total'] or 0

    return Response({
        'habitaciones_total': total_habitaciones,
        'habitaciones_disponibles': habitaciones_disponibles,
        'habitaciones_ocupadas': habitaciones_ocupadas,
        'habitaciones_limpiando': 0,
        'clientes_total': total_clientes,
        'asignaciones_activas': asignaciones_activas,
        'ingresos_totales': ingresos,
    })
    