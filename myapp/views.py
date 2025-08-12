
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import ApprenantRegisterForm, FormateurRegisterForm, ContenuForm
from .models import FormationFormateur
from .models import Apprenant, Formateur
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from .models import Formation
from .forms import FormationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Contenu, Formation
from django.http import HttpResponse, HttpResponseForbidden
from .forms import QuizForm
from django.shortcuts import render, get_object_or_404
from .models import Contenu, Quiz
from .forms import QuizReponseForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.units import cm
from .models import Commentaire
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Formation, InscriptionsProgress, Contenu, Progression
from datetime import date
from .models import Message, Utilisateur
from .models import Formation, Contenu

from collections import defaultdict
from .models import Progression, InscriptionsProgress
from django.db.models import Q
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os


def accueil(request):
    return render(request, 'accueil.html')

@login_required
def ajouter_quiz(request, contenu_id):
    contenu = get_object_or_404(Contenu, pk=contenu_id)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.contenu = contenu
            quiz.save()
            return redirect('voir_contenus', formation_id=contenu.formation.id)
    else:
        form = QuizForm()
    return render(request, 'formateur/ajouter_quiz.html', {'form': form, 'contenu': contenu})

@login_required
def passer_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    formation = quiz.contenu.formation

    if 'quiz_notes' not in request.session:
        request.session['quiz_notes'] = {}
    quiz_notes = request.session['quiz_notes']

    all_quiz = list(Quiz.objects.filter(contenu__formation=formation).order_by('id'))
    current_index = [q.id for q in all_quiz].index(quiz.id)

    questions = [quiz]

    if request.method == 'POST':
        if 'next' in request.POST:
            if current_index + 1 < len(all_quiz):
                next_quiz = all_quiz[current_index + 1]
                return redirect('passer_quiz', quiz_id=next_quiz.id)
            else:
                total = sum(quiz_notes.get(str(q.id), 0) for q in all_quiz)
                max_total = len(all_quiz) * 5
                pourcentage = int((total / max_total) * 100) if max_total > 0 else 0
                request.session['quiz_notes'] = {}
                return render(request, 'apprenant/resultat_global.html', {
                    'note': total,
                    'max_note': max_total,
                    'pourcentage': pourcentage,
                    'formation': formation,
                    'certificat': pourcentage >= 60
                })
        else:
            form = QuizReponseForm(questions, request.POST)
            if form.is_valid():
                user_answer = list(form.cleaned_data.values())[0]
                is_correct = user_answer == quiz.reponse_correcte  
                note = 5 if is_correct else 0
                quiz_notes[str(quiz.id)] = note
                request.session['quiz_notes'] = quiz_notes
                feedback = 'Bonne réponse !' if is_correct else f"Mauvaise réponse. La bonne réponse était : {quiz.reponse_correcte}"
                is_last = (current_index + 1 == len(all_quiz))
                return render(request, 'apprenant/passer_quiz.html', {
                    'quiz': quiz,
                    'form': form,
                    'user_answer': user_answer,
                    'feedback': feedback,
                    'is_last': is_last,
                    'show_feedback': True
                })
    else:
        form = QuizReponseForm(questions)

    return render(request, 'apprenant/passer_quiz.html', {
        'quiz': quiz,
        'form': form,
        'feedback_type': 'success'
    })




def apprenant_register(request):
    if request.method == 'POST':
        form = ApprenantRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Apprenant.objects.create(
                utilisateur=user,
                nom=form.cleaned_data['nom'],
                attribut1=form.cleaned_data['attribut1']
            )
            login(request, user)
            return redirect('accueil')
    else:
        form = ApprenantRegisterForm()
    return render(request, 'auth/apprenant_register.html', {'form': form})

@csrf_exempt
def apprenant_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                user.apprenant  
                login(request, user)
                return redirect('dashboard_apprenant') 
            except Apprenant.DoesNotExist:
                messages.error(request, "Ce compte n'est pas un Apprenant.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'auth/apprenant_login.html')


def formateur_register(request):
    if request.method == 'POST':
        form = FormateurRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Formateur.objects.create(utilisateur=user)
            login(request, user)
            return redirect('accueil')
    else:
        form = FormateurRegisterForm()
    return render(request, 'auth/formateur_register.html', {'form': form})

def formateur_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                user.formateur
                login(request, user)
                return redirect('dashboard_formateur') 
            except Formateur.DoesNotExist:
                messages.error(request, "Ce compte n'est pas un Formateur.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'auth/formateur_login.html')

@login_required
def dashboard_apprenant(request):
    user = request.user
    from .models import Message
    messages = Message.objects.filter(recipient=user).order_by('-timestamp')
    commentaires = Commentaire.objects.order_by('-date')[:10]
    
    try:
        apprenant = Apprenant.objects.get(utilisateur=request.user)
        formations = [insc.formation for insc in InscriptionsProgress.objects.filter(apprenant=apprenant)]
    except Apprenant.DoesNotExist:
        formations = []
    return render(request, 'dashboard/apprenant.html', {'commentaires': commentaires, 'formations': formations, 'messages': messages,})

from django.contrib.auth.decorators import login_required

@login_required
def dashboard_formateur(request):
    formateur = request.user.formateur

    # Récupère toutes les formations liées à ce formateur
    formations = Formation.objects.filter(
        formationformateur__formateur=formateur
    ).distinct()

    suivi = []
    for formation in formations:
        inscriptions = InscriptionsProgress.objects.filter(formation=formation)
        # Charge toutes les progressions de cette formation
        progressions = Progression.objects.filter(
            contenu__formation=formation
        ).select_related('apprenant', 'contenu')

        # Map apprenant.id → { contenu.id: est_complete }
        prog_map = {}
        for p in progressions:
            prog_map.setdefault(p.apprenant.id, {})[p.contenu.id] = p.est_complete

        # Prépare les données par apprenant
        apprenants_data = []
        for ins in inscriptions:
            appr = ins.apprenant
            apprenants_data.append({
                'apprenant': appr,
                'progression': prog_map.get(appr.id, {}),
            })

        suivi.append({
            'formation': formation,
            'inscriptions': inscriptions,
            'apprenants_data': apprenants_data,
            'modules': formation.modules.all(),
        })

    return render(request, 'dashboard/formateur.html', {
        'suivi': suivi
    })


def logout_view(request):
    user = request.user
    logout(request)

    try:
        if hasattr(user, 'apprenant'):
            return redirect('apprenant_login')
        elif hasattr(user, 'formateur'):
            return redirect('formateur_login')
    except:
        pass

    return redirect('accueil')

@login_required
def gerer_formations(request):
    formateur = request.user.formateur
    formation_formateurs = FormationFormateur.objects.filter(formateur=formateur)
    formations = [ff.formation for ff in formation_formateurs]
    form = FormationForm()

    if request.method == 'POST':
        form = FormationForm(request.POST)
        if form.is_valid():
            formation = form.save()
            FormationFormateur.objects.create(formation=formation, formateur=formateur)
            return redirect('gerer_formations')
    return render(request, 'formateur/gerer_formations.html', {'formations': formations, 'form': form})

@login_required
def modifier_formation(request, pk):
    formation = get_object_or_404(Formation, pk=pk)
    form = FormationForm(request.POST or None, instance=formation)
    if form.is_valid():
        form.save()
        return redirect('gerer_formations')
    return render(request, 'formateur/modifier_formation.html', {'form': form})

@login_required
def supprimer_formation(request, pk):
    formation = get_object_or_404(Formation, pk=pk)
    if request.method == 'POST':
        formation.delete()
        return redirect('gerer_formations')
    return render(request, 'formateur/confirmer_suppression.html', {'formation': formation})

@login_required
def ajouter_contenu(request, formation_id):
    formation = get_object_or_404(Formation, id=formation_id)
    
    if request.method == 'POST':
        form = ContenuForm(request.POST, request.FILES)
        if form.is_valid():
            contenu = form.save(commit=False)
            contenu.formation = formation
            contenu.save()
            return redirect('voir_contenus', formation_id=formation.id)
    else:
        form = ContenuForm()

    return render(request, 'formateur/ajouter_contenu.html', {
        'form': form,
        'formation': formation
    })

from .models import InscriptionsProgress, Progression, Contenu

@login_required
def contenus_apprenant(request, formation_id):
    
    inscription = InscriptionsProgress.objects.filter(
        formation_id=formation_id,
        apprenant__utilisateur=request.user
    ).first()

    if not inscription:
        return redirect('formations_disponibles')

    formation = get_object_or_404(Formation, id=formation_id)
    contenus = Contenu.objects.filter(formation=formation)
    apprenant = inscription.apprenant

    # Associe chaque contenu à son quiz
    contenus_et_quiz = []
    for contenu in contenus:
        quiz = Quiz.objects.filter(contenu=contenu).first()
        contenus_et_quiz.append((contenu, quiz))

    # Récupère les progressions existantes
    progressions = Progression.objects.filter(contenu__in=contenus, apprenant=apprenant)
    progression_map = {p.contenu.id: p for p in progressions}

    if request.method == 'POST':
        contenus_completes = request.POST.getlist('contenus_completes')

        for contenu in contenus:
            est_complete = str(contenu.id) in contenus_completes
            progression = progression_map.get(contenu.id)

            if progression:
                progression.est_complete = est_complete
                progression.save()
            else:
                Progression.objects.create(
                    apprenant=apprenant,
                    contenu=contenu,
                    est_complete=est_complete
                )

        messages.success(request, "✅ Votre progression a été mise à jour.")
        return redirect('contenus_apprenant', formation_id=formation.id)

    return render(request, 'apprenant/contenus.html', {
        'formation': formation,
        'contenus_et_quiz': contenus_et_quiz,
        'progression_map': progression_map,
    })
@login_required
def mes_formations(request):
    try:
        apprenant = Apprenant.objects.get(utilisateur=request.user)
    except Apprenant.DoesNotExist:
        return HttpResponseForbidden("Vous n'êtes pas un apprenant.")

    for formation in Formation.objects.all():
        InscriptionsProgress.objects.get_or_create(
            apprenant=apprenant,
            formation=formation,
            defaults={
                'date_inscription': timezone.now().date(),
                'is_online': True
            }
        )
    inscriptions = InscriptionsProgress.objects.filter(apprenant=apprenant)
    for inscription in inscriptions:
        inscription.progression = calculer_progression(inscription)
    return render(request, 'apprenant/mes_formations.html', {'inscriptions': inscriptions})

from django.db.models import Q
@login_required
def formations_disponibles(request):
    try:
        apprenant = Apprenant.objects.get(utilisateur=request.user)
    except Apprenant.DoesNotExist:
        return HttpResponseForbidden("Vous n'êtes pas un apprenant.")
    inscrits_ids = InscriptionsProgress.objects.filter(apprenant=apprenant).values_list('formation_id', flat=True)
    formations = Formation.objects.exclude(id__in=inscrits_ids)

    return render(request, 'apprenant/formations_disponibles.html', {
        'formations': formations
    })

@login_required
def s_inscrire_formation(request, formation_id):
    formation = get_object_or_404(Formation, id=formation_id)

    try:
        apprenant = Apprenant.objects.get(utilisateur=request.user)
    except Apprenant.DoesNotExist:
        return HttpResponseForbidden("Vous n'êtes pas un apprenant.")

    InscriptionsProgress.objects.get_or_create(
        apprenant=apprenant,
        formation=formation,
        defaults={
            'is_online': True,
            'date_inscription': timezone.now().date()
        }
    )

    return redirect('mes_formations')

from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Formation, Contenu, InscriptionsProgress, Progression

@login_required
def suivi_apprenants(request, formation_id):

    formation  = get_object_or_404(Formation, id=formation_id)
    contenus   = Contenu.objects.filter(formation=formation)
    inscriptions = InscriptionsProgress.objects.filter(
        formation=formation
    ).select_related('apprenant')
    if not inscriptions:
        return render(request, 'formateur/suivi_apprenants.html', {
            'formation': formation,
            'contenus': contenus,
            'apprenants_data': []
        })
    prog_map = defaultdict(dict)
    for p in Progression.objects.filter(contenu__formation=formation)\
                               .select_related('apprenant','contenu'):
        prog_map[p.apprenant.id][p.contenu.id] = p.est_complete

    
    total = contenus.count()
    apprenants_data = []
    for ins in inscriptions:
        a = ins.apprenant
        done = sum(1 for cid, ok in prog_map[a.id].items() if ok)
        pct  = round((done/total)*100) if total else 0
        apprenants_data.append({
            'apprenant': a,
            'progression': prog_map[a.id],
            'pourcentage': pct,
        })

    return render(request, 'formateur/suivi_apprenants.html', {
        'formation': formation,
        'contenus': contenus,
        'apprenants_data': apprenants_data,
    })

@login_required
def voir_contenus(request, formation_id):
    formation = get_object_or_404(Formation, id=formation_id)
    contenus = Contenu.objects.filter(formation=formation)


    contenus_et_quiz = []
    for contenu in contenus:
        quiz = contenu.quiz_set.first() if hasattr(contenu, 'quiz_set') else None
        contenus_et_quiz.append((contenu, quiz))

    return render(request, 'formateur/voir_contenus.html', {
        'formation': formation,
        'contenus_et_quiz': contenus_et_quiz
    })

@login_required
def modifier_contenu(request, contenu_id):
    contenu = get_object_or_404(Contenu, id=contenu_id)
    if request.method == 'POST':
        form = ContenuForm(request.POST, request.FILES, instance=contenu)
        if form.is_valid():
            form.save()
            return redirect('voir_contenus', formation_id=contenu.formation.id)
    else:
        form = ContenuForm(instance=contenu)
    return render(request, 'formateur/modifier_contenu.html', {'form': form})

@login_required
def supprimer_contenu(request, contenu_id):
    contenu = get_object_or_404(Contenu, id=contenu_id)
    if request.method == 'POST':
        formation_id = contenu.formation.id
        contenu.delete()
        return redirect('voir_contenus', formation_id=formation_id)
    return render(request, 'formateur/supprimer_contenu.html', {'contenu': contenu})

@login_required
def telecharger_certificat(request, formation_id):
    user = request.user
    formation = get_object_or_404(Formation, id=formation_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificat_{formation.titre}.pdf"'

    PAGE_WIDTH = 21 * cm
    PAGE_HEIGHT = 12 * cm
    p = canvas.Canvas(response, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    width, height = PAGE_WIDTH, PAGE_HEIGHT

    # Fond dégradé
    for i in range(20):
        color = colors.linearlyInterpolatedColor(colors.HexColor('#a8edea'), colors.HexColor('#fed6e3'), 0, 20, i)
        p.setFillColor(color)
        p.rect(0, (height/20)*i, width, height/20, fill=1, stroke=0)

    # Cadre extérieur arrondi
    p.setStrokeColor(colors.HexColor('#0984e3'))
    p.setLineWidth(5)
    p.roundRect(1*cm, 1*cm, width-2*cm, height-2*cm, 20, fill=0)

    # Logo EduConnect (assure-toi qu’il existe dans static/img)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'educonnect_logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, width/2 - 2.5*cm, height - 3.5*cm, width=5*cm, height=2*cm, mask='auto')

    # Titre principal
    p.setFont("Helvetica-Bold", 28)
    p.setFillColor(colors.HexColor('#2d3436'))
    p.drawCentredString(width / 2, height - 5*cm, "🏆 CERTIFICAT DE RÉUSSITE")

    # Message personnalisé
    p.setFont("Helvetica", 16)
    p.setFillColor(colors.HexColor('#636e72'))
    p.drawCentredString(width / 2, height - 7*cm, "Ce certificat est décerné à")

    p.setFont("Helvetica-Bold", 22)
    p.setFillColor(colors.HexColor('#00b894'))
    p.drawCentredString(width / 2, height - 8.2*cm, user.get_full_name() or user.username)

    p.setFont("Helvetica", 14)
    p.setFillColor(colors.HexColor('#636e72'))
    p.drawCentredString(width / 2, height - 9.5*cm, "Pour avoir complété avec succès la formation :")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 10.5*cm, f"“{formation.titre}”")

    # Date et signature
    p.setFont("Helvetica-Oblique", 11)
    p.setFillColor(colors.HexColor('#636e72'))
    p.drawString(2*cm, 1.5*cm, f"Délivré le : {timezone.now().date()}")

    p.setFont("Helvetica-Oblique", 13)
    p.setFillColor(colors.HexColor('#0984e3'))
    p.drawString(width - 7*cm, 1.5*cm, "Signature du formateur")

    p.showPage()
    p.save()
    return response
@login_required
def ajouter_commentaire(request):
    if request.method == 'POST':
        texte = request.POST.get('commentaire')
        if texte:
            Commentaire.objects.create(utilisateur=request.user, commentaire=texte)
    return redirect('dashboard_apprenant')

from django.core.mail import send_mass_mail

from .models import Message

 
@login_required
def messagerie_formateur(request):
    if request.method == 'POST':
        content = request.POST.get('corps') 
        sender = request.user  
        apprenants = Apprenant.objects.select_related('utilisateur').all()
        for appr in apprenants:
            Message.objects.create(
                content=content,
                sender=sender,
                recipient=appr.utilisateur
            )
        return redirect('dashboard_formateur')

    return render(request, 'formateur/messagerie_formateur.html')

@login_required
def conversation(request, apprenant_id):
    formateur = request.user
    apprenant = get_object_or_404(Utilisateur, id=apprenant_id)
    messages = Message.objects.filter(
        (Q(sender=formateur) & Q(recipient=apprenant)) |
        (Q(sender=apprenant) & Q(recipient=formateur))
    ).order_by('timestamp')
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=formateur, recipient=apprenant, content=content)
            return redirect('conversation', apprenant_id=apprenant.id)
    return render(request, 'formateur/conversation.html', {'apprenant': apprenant, 'messages': messages})
def calculer_progression(inscription):
    formation = inscription.formation
    apprenant = inscription.apprenant

    total_contenus = Contenu.objects.filter(formation=formation).count()
    if total_contenus == 0:
        return 0

    contenus_termines = Progression.objects.filter(
        contenu__formation=formation,
        apprenant=apprenant,
        est_complete=True  
    ).count()

    progression = int((contenus_termines / total_contenus) * 100)
    return progression

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Formation, Progression, InscriptionsProgress

@login_required
def suivi_apprenants_global(request):
    formateur = request.user.formateur
    formations = Formation.objects.filter(formationformateur__formateur=formateur).distinct()

    suivi = []
    cours_finis = []

    for formation in formations:
        modules = formation.modules.all()
        contenus = [c for m in modules for c in m.contenus.all()]
        inscriptions = InscriptionsProgress.objects.filter(formation=formation)
        progressions = Progression.objects.filter(contenu__formation=formation)

        prog_map = {}
        for p in progressions:
            prog_map.setdefault(p.apprenant.id, {})[p.contenu.id] = p.est_complete

        apprenants_data = []
        for ins in inscriptions:
            apprenant = ins.apprenant
            total = len(contenus)
            done = sum(1 for c in contenus if prog_map.get(apprenant.id, {}).get(c.id, False))
            pourcentage = int((done / total) * 100) if total > 0 else 0

            apprenants_data.append({
                'apprenant': apprenant,
                'progression': prog_map.get(apprenant.id, {}),
                'pourcentage': pourcentage
            })

            if pourcentage == 100:
                cours_finis.append({'apprenant': apprenant, 'formation': formation})

        suivi.append({
            'formation': formation,
            'apprenants': apprenants_data,
        })

    return render(request, 'formateur/suivi_apprenants.html', {
    'suivi': suivi,
    'cours_finis': cours_finis
})
from .models import Contenu, Progression


@login_required
def progression_contenus(request, formation_id):
    formation = get_object_or_404(Formation, id=formation_id)
    contenus = Contenu.objects.filter(formation=formation)
    apprenant = request.user.apprenant

    progressions = Progression.objects.filter(apprenant=apprenant, contenu__formation=formation)
    progression_map = {p.contenu.id: p for p in progressions}

    if request.method == 'POST':
        ids = request.POST.getlist('contenus_completes')
        for contenu in contenus:
            est_complete = str(contenu.id) in ids
            progression = progression_map.get(contenu.id)
            if progression:
                progression.est_complete = est_complete
                progression.save()
            else:
                Progression.objects.create(apprenant=apprenant, contenu=contenu, est_complete=est_complete)

        return redirect('progression_contenus', formation_id=formation.id)

    return render(request, 'apprenant/progression_contenus.html', {
        'formation': formation,
        'contenus_et_quiz': [(c, None) for c in contenus],
        'progression_map': progression_map
    })
def est_admin(user):
    return user.is_authenticated and user.is_superuser  
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.contrib.auth.models import User
@login_required
@user_passes_test(est_admin)
def admin_dashboard_utilisateurs(request):
    utilisateurs = User.objects.all().order_by('-date_joined')  
    return render(request, 'admin_dashboard.html', {'utilisateurs': utilisateurs})



@login_required
def messagerie_apprenant(request):
    user = request.user
    messages = Message.objects.filter(destinataires=user).order_by('-date_envoi')
    return render(request, 'apprenant/messagerie_apprenant.html', {
        'messages': messages
    })
