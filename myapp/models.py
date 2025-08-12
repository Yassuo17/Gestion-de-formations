from django.db import models
from django.contrib.auth.models import AbstractUser

# models.py
from django.db import models

class Utilisateur(AbstractUser):
    
    def __str__(self):
        return self.username

class Apprenant(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    attribut1 = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

class Formateur(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)

    def __str__(self):
        return self.utilisateur.username

class Administrateur(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)

    def __str__(self):
        return self.utilisateur.username

class Formation(models.Model):
    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_creation = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titre

class FormationFormateur(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    formateur = models.ForeignKey(Formateur, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.formation} par {self.formateur}"

class InscriptionsProgress(models.Model):
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.apprenant} inscrit à {self.formation}"

class ModuleFormation(models.Model):
    id_module = models.AutoField(primary_key=True)
    checked = models.BooleanField(default=False)
    titre = models.CharField(max_length=255)
    description = models.TextField()
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="modules")

    def __str__(self):
        return self.titre

class Contenu(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='contenus')
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to='contenus/', blank=True, null=True)
    checked = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.titre} ({self.formation.titre})"

class Quiz(models.Model):
    contenu = models.ForeignKey(Contenu, on_delete=models.CASCADE, related_name="quizz")
    question = models.CharField(max_length=255)
    reponse_correcte = models.CharField(max_length=255)
    choix_1 = models.CharField(max_length=255)
    choix_2 = models.CharField(max_length=255)
    choix_3 = models.CharField(max_length=255)

    def __str__(self):
        return f"Quiz pour {self.contenu.titre}"

class Commentaire(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    commentaire = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur} : {self.commentaire[:30]}..."

class Progression(models.Model):
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    contenu = models.ForeignKey(Contenu, on_delete=models.CASCADE)
    est_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.apprenant.nom} - {self.contenu.titre} : {'✅' if self.est_complete else '❌'}"

class Message(models.Model):
    sender = models.ForeignKey(Utilisateur, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(Utilisateur, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.sender.username} à {self.recipient.username} : {self.content[:30]}..."
    