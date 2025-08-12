from django import template
import random

register = template.Library()

@register.filter
def get_random_choices(quiz):
    choices = [quiz.choix_1, quiz.choix_2, quiz.choix_3, quiz.reponse_correcte]
    random.shuffle(choices)
    return choices 