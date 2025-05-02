from django.urls import path
from .views import schedule_visit, predict_product_cost

urlpatterns = [
    path('schedule-visit/', schedule_visit, name='schedule_visit'),
    path('predict_product_cost/', predict_product_cost, name='predict_product_cost'),
]