from myapp.models import Utilisateur, Formateur, Apprenant, Formation, FormationFormateur, Contenu, InscriptionsProgress, Progression, Quiz
from django.contrib.auth.hashers import make_password
from django.utils import timezone

# Création d'un formateur
formateur_user, _ = Utilisateur.objects.get_or_create(username='formateur_demo', defaults={
    'email': 'formateur@demo.com',
    'password': make_password('demo1234'),
    'is_staff': True
})
formateur, _ = Formateur.objects.get_or_create(utilisateur=formateur_user)

# Création d'un apprenant
apprenant_user, _ = Utilisateur.objects.get_or_create(username='apprenant_demo', defaults={
    'email': 'apprenant@demo.com',
    'password': make_password('demo1234')
})
apprenant, _ = Apprenant.objects.get_or_create(utilisateur=apprenant_user, defaults={'nom': 'Apprenant Démo', 'attribut1': 'Test'})

# Création d'une formation
formation, _ = Formation.objects.get_or_create(titre='Formation Démo', defaults={'description': 'Formation de test', 'date_creation': timezone.now().date()})

# Lier la formation au formateur
FormationFormateur.objects.get_or_create(formation=formation, formateur=formateur)

# Création de contenus
contenu1, _ = Contenu.objects.get_or_create(formation=formation, titre='Introduction', defaults={'description': 'Intro', 'fichier': ''})
contenu2, _ = Contenu.objects.get_or_create(formation=formation, titre='Chapitre 1', defaults={'description': 'Chapitre 1', 'fichier': ''})
contenu3, _ = Contenu.objects.get_or_create(formation=formation, titre='Conclusion', defaults={'description': 'Fin', 'fichier': ''})

# Inscription de l'apprenant à la formation
inscription, _ = InscriptionsProgress.objects.get_or_create(apprenant=apprenant, formation=formation, defaults={'date_inscription': timezone.now().date(), 'is_online': True})

# Progression : l'apprenant a validé le premier contenu
Progression.objects.get_or_create(apprenant=apprenant, contenu=contenu1, defaults={'est_complete': True})
Progression.objects.get_or_create(apprenant=apprenant, contenu=contenu2, defaults={'est_complete': False})
Progression.objects.get_or_create(apprenant=apprenant, contenu=contenu3, defaults={'est_complete': False})

# Création d'un quiz pour la formation
demo_quiz, _ = Quiz.objects.get_or_create(
    formation=formation,
    question="Quel est le langage utilisé dans cette formation ?",
    defaults={
        'choix_1': 'Python',
        'choix_2': 'Java',
        'choix_3': 'C++',
        'reponse_correcte': 'Python'
    }
)

print('Données de démonstration créées !')
print('Formateur : formateur_demo / demo1234')
print('Apprenant : apprenant_demo / demo1234')
print('Formation : Formation Démo')
print('Quiz créé pour la formation !') 