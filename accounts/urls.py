from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import login_view, register , activate_email,logout_view
from . import views

urlpatterns = [
   # usuario
   path('login/' , login_view , name="login" ),
   path('register/' , register , name="register"),
   path('activate/<email_token>/' , activate_email , name="activate"),
   path('logout/' , logout_view , name="logout"),   
   path('password_change/', auth_views.PasswordChangeView.as_view(template_name='/password_change.html', success_url='/password_change/done/'), name='password_change'),
   path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
   path('change_password/', views.change_password, name='change_password'),
   path('forgot_password/', views.forgot_password, name='forgot_password'),
   path('reset_password/<email_token>/', views.reset_password, name='reset_password'),
   
   # Dashboard cliente
   path('dashboard/', views.dashboard_cliente, name='dashboard_cliente'),
   path('perfil/', views.perfil_cliente, name='perfil_cliente'),
   path('mis-proformas/', views.mis_proformas_cliente, name='mis_proformas_cliente'),
   path('mis-contratos/', views.mis_contratos_cliente, name='mis_contratos_cliente'),
   path('contrato/<str:contrato_num>/', views.ver_contrato_cliente, name='ver_contrato_cliente'),
   path('generar-contrato/<str:proforma_num>/', views.generar_contrato_cliente, name='generar_contrato_cliente'),
]
