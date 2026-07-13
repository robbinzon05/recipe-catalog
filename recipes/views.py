from django.shortcuts import render
from django.core.paginator import Paginator

from .models import Category, Recipe


def home(request):
    categories = Category.objects.all()
    featured_recipes = Recipe.objects.select_related('category')[:6]

    context = {
        'categories': categories,
        'featured_recipes': featured_recipes,
        'recipe_count': Recipe.objects.count(),
    }
    return render(request, 'recipes/home.html', context)


def recipe_list(request):
    recipes = Recipe.objects.select_related('category')
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'recipes': page_obj.object_list,
    }
    return render(request, 'recipes/recipe_list.html', context)
