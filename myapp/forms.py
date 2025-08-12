from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur, Apprenant, Formateur
from .models import Formation
from .models import Contenu
from .models import Quiz

class ApprenantRegisterForm(UserCreationForm):
    nom = forms.CharField(max_length=100)
    attribut1 = forms.CharField(max_length=255)

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password1', 'password2', 'nom', 'attribut1']

class FormateurRegisterForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password1', 'password2']

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['titre', 'description']
        widgets = {
            'date_creation': forms.DateInput(attrs={'type': 'date'})
        }
        
class ContenuForm(forms.ModelForm):
    class Meta:
        model = Contenu
        fields = ['titre', 'description', 'fichier']


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['question', 'choix_1', 'choix_2', 'choix_3', 'reponse_correcte']

from django import forms

class QuizReponseForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for question in questions:
            choices = [
                (question.reponse_correcte, question.reponse_correcte),
                (question.choix_1, question.choix_1),
                (question.choix_2, question.choix_2),
                (question.choix_3, question.choix_3),
            ] 
            import random
            random.shuffle(choices)
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                label=question.question,
                choices=choices,
                widget=forms.RadioSelect
            )
