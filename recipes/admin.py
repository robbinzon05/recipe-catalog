from django.contrib import admin

from .models import Category, Comment, Recipe


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('author', 'text', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'ingredients')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = (CommentInline,)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'author', 'created_at')
    list_filter = ('created_at', 'recipe__category')
    search_fields = ('text', 'author__username', 'recipe__title')
    readonly_fields = ('created_at', 'updated_at')
