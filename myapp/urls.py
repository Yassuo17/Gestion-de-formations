from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    
    path('', views.accueil, name='accueil'),
    path('login/apprenant/', views.apprenant_login, name='apprenant_login'),
    path('register/apprenant/', views.apprenant_register, name='apprenant_register'),

    path('login/formateur/', views.formateur_login, name='formateur_login'),
    path('register/formateur/', views.formateur_register, name='formateur_register'),

    path('dashboard/apprenant/', views.dashboard_apprenant, name='dashboard_apprenant'),
    path('dashboard/formateur/', views.dashboard_formateur, name='dashboard_formateur'),
    

     path('formateur/formations/', views.gerer_formations, name='gerer_formations'),
    path('formateur/formations/modifier/<int:pk>/', views.modifier_formation, name='modifier_formation'),
    path('formateur/formations/supprimer/<int:pk>/', views.supprimer_formation, name='supprimer_formation'),

    path('formateur/formations/<int:formation_id>/contenus/ajouter/', views.ajouter_contenu, name='ajouter_contenu'),

path('apprenant/formations/<int:formation_id>/contenus/', views.contenus_apprenant, name='contenus_apprenant'),
path('apprenant/mes-formations/', views.mes_formations, name='mes_formations'),
path('apprenant/formations-disponibles/', views.formations_disponibles, name='formations_disponibles'),
path('apprenant/formations/<int:formation_id>/inscription/', views.s_inscrire_formation, name='s_inscrire_formation'),

path('formateur/formations/<int:formation_id>/contenus/', views.voir_contenus, name='voir_contenus'),
path('formateur/contenus/<int:contenu_id>/modifier/', views.modifier_contenu, name='modifier_contenu'),
path('formateur/contenus/<int:contenu_id>/supprimer/', views.supprimer_contenu, name='supprimer_contenu'),
path('formateur/contenus/<int:contenu_id>/quiz/ajouter/', views.ajouter_quiz, name='ajouter_quiz'),
path(
    'apprenant/formations/<int:formation_id>/contenus/',
    views.progression_contenus,
    name='progression_contenus'
), path(
  'apprenant/formations/<int:formation_id>/contenus/',
  views.contenus_apprenant,
  name='contenus_apprenant'
),

path('apprenant/quiz/<int:quiz_id>/passer/', views.passer_quiz, name='passer_quiz'),
path('apprenant/formation/<int:formation_id>/certificat/', views.telecharger_certificat, name='telecharger_certificat'),
path('apprenant/commentaire/ajouter/', views.ajouter_commentaire, name='ajouter_commentaire'),

path('formateur/messagerie/', views.messagerie_formateur, name='messagerie_formateur'),
path('formateur/conversation/<int:apprenant_id>/', views.conversation, name='conversation'),
            path('formateur/dashboard/', views.dashboard_formateur, name='dashboard_formateur'),
            path('formateur/suivi-apprenants/', views.suivi_apprenants_global, name='suivi_apprenants_global'),
    # Si tu as besoin aussi du suivi par formation (optionnel)
            #path('formateur/suivi-apprenants/<int:formation_id>/', views.suivi_apprenants, name='suivi_apprenants'),
        path('admin/utilisateurs/', views.admin_dashboard_utilisateurs, name='admin_dashboard_utilisateurs'),
path('admin/', admin.site.urls),
path('accounts/', include('django.contrib.auth.urls')), 
path('formateur/messagerie/', views.messagerie_formateur, name='messagerie_formateur'),
# myapp/urls.py
path('formateur/messagerie/',       views.messagerie_formateur, name='messagerie_formateur'),
path('apprenant/messagerie/', views.messagerie_apprenant, name='messagerie_apprenant'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
