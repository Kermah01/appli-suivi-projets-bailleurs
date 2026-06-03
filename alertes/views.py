from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from accounts.decorators import login_required_custom, edit_permission_required
from .models import CritereRetard
from .forms import CritereRetardForm


@login_required_custom
def criteres_liste(request):
    criteres = CritereRetard.objects.all()
    return render(request, 'alertes/criteres.html', {'criteres': criteres})


@edit_permission_required
def critere_creer(request):
    if request.method == 'POST':
        form = CritereRetardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Critère de retard créé avec succès.")
            return redirect('alertes:criteres')
    else:
        form = CritereRetardForm()
    return render(request, 'alertes/critere_form.html', {'form': form, 'titre': 'Nouveau critère de retard'})


@edit_permission_required
def critere_modifier(request, pk):
    critere = get_object_or_404(CritereRetard, pk=pk)
    if request.method == 'POST':
        form = CritereRetardForm(request.POST, instance=critere)
        if form.is_valid():
            form.save()
            messages.success(request, "Critère mis à jour.")
            return redirect('alertes:criteres')
    else:
        form = CritereRetardForm(instance=critere)
    return render(request, 'alertes/critere_form.html', {
        'form': form,
        'titre': 'Modifier le critère',
        'critere': critere,
    })


@edit_permission_required
def critere_supprimer(request, pk):
    critere = get_object_or_404(CritereRetard, pk=pk)
    if request.method == 'POST':
        critere.delete()
        messages.success(request, "Critère supprimé.")
        return redirect('alertes:criteres')
    return render(request, 'alertes/critere_confirmer_suppression.html', {'critere': critere})


@edit_permission_required
def critere_toggle(request, pk):
    if request.method == 'POST':
        critere = get_object_or_404(CritereRetard, pk=pk)
        critere.actif = not critere.actif
        critere.save()
        etat = "activé" if critere.actif else "désactivé"
        messages.success(request, f"Critère « {critere.nom} » {etat}.")
    return redirect('alertes:criteres')
