from django.urls import path
from . import views

# Les encargo que despues de cada path SIEMPRE pongan una coma --> path(),
urlpatterns = [
    path('multilayer/<int:id>/', views.multilayer_HTML, name = 'multilayer'),
    path('acceso/<int:id>', views.access_HTML, name='access'),
    path('', views.index_HTML, name='index'),
    
    # Envio de formularios
    path('form/<int:id>/create-vlan/', views.create_vlan, name='create_vlan'),
    path('form/<int:id>/delete-vlan/', views.delete_vlan, name='delete_vlan'),
    path('form/<int:id>/hub/<str:mode>/', views.hub_form_access, name = 'hub'),
    
    # Polling de JS
    path('poll/interfaces/<int:id>/', views.polling_interfaces, name='polling_interfaces'),
]