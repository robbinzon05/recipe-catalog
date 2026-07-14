from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, RegisterForm
from .models import Category, Comment, Recipe


def filter_recipes_by_query(recipes, query):
    if not query:
        return recipes

    normalized_query = query.casefold()
    matching_ids = [
        recipe.pk
        for recipe in recipes
        if normalized_query in recipe.title.casefold()
        or normalized_query in recipe.description.casefold()
        or normalized_query in recipe.ingredients.casefold()
    ]
    return recipes.filter(pk__in=matching_ids)


def user_can_change_comment(user, comment):
    return user.is_staff or comment.author == user


def home(request):
    categories = Category.objects.all()
    featured_recipes = Recipe.objects.select_related('category')[:6]

    context = {
        'categories': categories,
        'featured_recipes': featured_recipes,
        'recipe_count': Recipe.objects.count(),
    }
    return render(request, 'recipes/home.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    saved_recipes = request.user.saved_recipes.select_related('category').order_by('-created_at')
    return render(request, 'recipes/profile.html', {'saved_recipes': saved_recipes})


def recipe_list(request):
    query = request.GET.get('q', '').strip()
    recipes = Recipe.objects.select_related('category')
    recipes = filter_recipes_by_query(recipes, query)
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': Category.objects.all(),
        'page_obj': page_obj,
        'query': query,
        'recipes': page_obj.object_list,
    }
    return render(request, 'recipes/recipe_list.html', context)


def recipe_category(request, slug):
    query = request.GET.get('q', '').strip()
    category = get_object_or_404(Category, slug=slug)
    recipes = Recipe.objects.select_related('category').filter(category=category)
    recipes = filter_recipes_by_query(recipes, query)
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': Category.objects.all(),
        'current_category': category,
        'page_obj': page_obj,
        'query': query,
        'recipes': page_obj.object_list,
    }
    return render(request, 'recipes/recipe_list.html', context)


def recipe_detail(request, slug):
    recipe = get_object_or_404(
        Recipe.objects.select_related('category').prefetch_related('comments__author'),
        slug=slug,
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Войдите в систему, чтобы оставить комментарий.')
            return redirect('login')

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен.')
            return redirect(recipe.get_absolute_url())
    else:
        comment_form = CommentForm()

    context = {
        'comment_form': comment_form,
        'recipe': recipe,
        'ingredients': recipe.ingredients.splitlines(),
        'cooking_steps': recipe.cooking_steps.splitlines(),
        'comments': recipe.comments.all(),
    }
    return render(request, 'recipes/recipe_detail.html', context)


@login_required
def toggle_saved_recipe(request, slug):
    if request.method != 'POST':
        return redirect('recipe_detail', slug=slug)

    recipe = get_object_or_404(Recipe, slug=slug)
    if recipe.saved_by.filter(pk=request.user.pk).exists():
        recipe.saved_by.remove(request.user)
        messages.success(request, 'Рецепт удален из сохраненных.')
    else:
        recipe.saved_by.add(request.user)
        messages.success(request, 'Рецепт сохранен в личном кабинете.')
    return redirect(recipe.get_absolute_url())


@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment.objects.select_related('recipe', 'author'), pk=pk)
    if not user_can_change_comment(request.user, comment):
        return HttpResponseForbidden('Недостаточно прав для редактирования комментария.')

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий обновлен.')
            return redirect(comment.recipe.get_absolute_url())
    else:
        form = CommentForm(instance=comment)

    context = {
        'comment': comment,
        'form': form,
    }
    return render(request, 'recipes/comment_form.html', context)


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment.objects.select_related('recipe', 'author'), pk=pk)
    if not user_can_change_comment(request.user, comment):
        return HttpResponseForbidden('Недостаточно прав для удаления комментария.')

    recipe_url = comment.recipe.get_absolute_url()
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удален.')
        return redirect(recipe_url)

    return render(request, 'recipes/comment_confirm_delete.html', {'comment': comment})
