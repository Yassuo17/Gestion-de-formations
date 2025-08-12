from django.contrib import admin
from .models import (
    Utilisateur,
    Apprenant,
    Formateur,
    Administrateur,
    Formation,
    FormationFormateur,
    InscriptionsProgress,
    ModuleFormation,
    Contenu,
    Commentaire
)

admin.site.register(Utilisateur)
admin.site.register(Apprenant)
admin.site.register(Formateur)
admin.site.register(Administrateur)
admin.site.register(Formation)
admin.site.register(FormationFormateur)
admin.site.register(InscriptionsProgress)
admin.site.register(ModuleFormation)
admin.site.register(Contenu)
admin.site.register(Commentaire)
from django.contrib import admin

admin.site.site_header  = "📋 Mon Administration"
admin.site.site_title   = "Administration | MonSite"
admin.site.index_title  = "Bienvenue dans l’admin"
