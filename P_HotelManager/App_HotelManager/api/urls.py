from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ganancias_mensuales,
    login,
    UsuarioViewSet,
    PerfilHotelViewSet,
    ClienteViewSet,
    HabitacionViewSet,
    AsignacionViewSet,
    PagoViewSet,
    dashboard_resumen,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'perfil-hotel', PerfilHotelViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'habitaciones', HabitacionViewSet)
router.register(r'asignaciones', AsignacionViewSet)
router.register(r'pagos', PagoViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', login, name='login'),
    path('dashboard/resumen/', dashboard_resumen, name='dashboard_resumen'),
    path('dashboard/ganancias-mensuales/', ganancias_mensuales, name='ganancias_mensuales'),
]