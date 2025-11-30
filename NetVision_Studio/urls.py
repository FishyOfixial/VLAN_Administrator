from django.urls import path
from . import views

# Les encargo que despues de cada path SIEMPRE pongan una coma --> path(),
urlpatterns = [
    path('<int:id>/', views.multilayer_HTML, name = 'multilayer'),
    path('acceso/', views.access_HTML, name='access'),
    
    # Envio de formularios
    path('form/<int:id>/create-vlan/', views.create_vlan, name='create_vlan'),
    path('form/<int:id>/delete-vlan/', views.delete_vlan, name='delete_vlan'),

    # Polling de JS
    path('api/switches/status/', views.switches_status, name='switches_status'),
]