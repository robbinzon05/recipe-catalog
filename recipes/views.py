from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

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
        'categories': Category.objects.all(),
        'page_obj': page_obj,
        'recipes': page_obj.object_list,
    }
    return render(request, 'recipes/recipe_list.html', context)


def recipe_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    recipes = Recipe.objects.select_related('category').filter(category=category)
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': Category.objects.all(),
        'current_category': category,
        'page_obj': page_obj,
        'recipes': page_obj.object_list,
    }
    return render(request, 'recipes/recipe_list.html', context)


def recipe_detail(request, slug):
    recipe = get_object_or_404(
        Recipe.objects.select_related('category').prefetch_related('comments__author'),
        slug=slug,
    )

    context = {
        'recipe': recipe,
        'ingredients': recipe.ingredients.splitlines(),
        'cooking_steps': recipe.cooking_steps.splitlines(),
        'comments': recipe.comments.all(),
    }
    return render(request, 'recipes/recipe_detail.html', context)
