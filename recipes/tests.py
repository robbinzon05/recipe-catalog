from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Comment, Recipe
from .views import filter_recipes_by_query


class RecipeCatalogTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Супы',
            slug='supy',
            description='Домашние супы.',
        )
        self.other_category = Category.objects.create(
            name='Десерты',
            slug='deserty',
            description='Сладкие блюда.',
        )
        self.recipe = Recipe.objects.create(
            title='Куриный суп',
            slug='kurinyy-sup',
            description='Легкий домашний суп с курицей.',
            ingredients='Курица\nСоль\nКартофель',
            cooking_steps='Сварить курицу\nДобавить овощи',
            category=self.category,
        )
        self.other_recipe = Recipe.objects.create(
            title='Шоколадный кекс',
            slug='shokoladnyy-keks',
            description='Кекс к чаю.',
            ingredients='Мука\nСахар\nКакао',
            cooking_steps='Смешать\nИспечь',
            category=self.other_category,
        )
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='user',
            password='StrongPass12345',
        )
        self.other_user = user_model.objects.create_user(
            username='other',
            password='StrongPass12345',
        )
        self.admin = user_model.objects.create_superuser(
            username='admin',
            password='StrongPass12345',
        )

    def test_public_pages_are_available(self):
        urls = [
            reverse('home'),
            reverse('recipe_list'),
            self.category.get_absolute_url(),
            self.recipe.get_absolute_url(),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_search_checks_title_description_and_ingredients_case_insensitive(self):
        recipes = Recipe.objects.all()

        self.assertIn(self.recipe, filter_recipes_by_query(recipes, 'КУР'))
        self.assertIn(self.recipe, filter_recipes_by_query(recipes, 'соль'))
        self.assertIn(self.other_recipe, filter_recipes_by_query(recipes, 'САХАР'))
        self.assertIn(self.recipe, filter_recipes_by_query(recipes, 'домашний'))

    def test_category_page_only_shows_category_recipes(self):
        response = self.client.get(self.category.get_absolute_url())

        self.assertContains(response, self.recipe.title)
        self.assertNotContains(response, self.other_recipe.title)

    def test_guest_cannot_create_comment(self):
        response = self.client.post(
            self.recipe.get_absolute_url(),
            {'text': 'Гостевой комментарий'},
        )

        self.assertRedirects(response, reverse('login'))
        self.assertEqual(Comment.objects.count(), 0)

    def test_authenticated_user_can_create_comment(self):
        self.client.login(username='user', password='StrongPass12345')
        response = self.client.post(
            self.recipe.get_absolute_url(),
            {'text': 'Отличный рецепт'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Comment.objects.filter(
                recipe=self.recipe,
                author=self.user,
                text='Отличный рецепт',
            ).exists()
        )

    def test_user_can_edit_own_comment_but_not_other_users_comment(self):
        comment = Comment.objects.create(
            recipe=self.recipe,
            author=self.user,
            text='Первый текст',
        )

        self.client.login(username='user', password='StrongPass12345')
        response = self.client.post(
            reverse('comment_edit', kwargs={'pk': comment.pk}),
            {'text': 'Новый текст'},
        )
        comment.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(comment.text, 'Новый текст')

        self.client.logout()
        self.client.login(username='other', password='StrongPass12345')
        response = self.client.post(
            reverse('comment_edit', kwargs={'pk': comment.pk}),
            {'text': 'Чужая правка'},
        )
        comment.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(comment.text, 'Новый текст')

    def test_admin_can_delete_any_comment(self):
        comment = Comment.objects.create(
            recipe=self.recipe,
            author=self.user,
            text='Удалить администратором',
        )

        self.client.login(username='admin', password='StrongPass12345')
        response = self.client.post(reverse('comment_delete', kwargs={'pk': comment.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
