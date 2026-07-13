from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('categories/<slug:slug>/', views.recipe_category, name='recipe_category'),
    path('recipes/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
]
