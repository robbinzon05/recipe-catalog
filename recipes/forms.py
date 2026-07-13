from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import Comment


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Напишите комментарий к рецепту',
                }
            ),
        }
        labels = {
            'text': 'Комментарий',
        }
