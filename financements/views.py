from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum
from .models import Financement, Decaissement
from .forms import FinancementForm, DecaissementForm
from accounts.decorators import login_required_custom, edit_permission_required


@login_required_custom
def liste(request):
    query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    financements = Financement.objects.select_related('projet', 'bailleur').all()

    if query:
        financements = financements.filter(
            Q(projet__titre__icontains=query) | Q(bailleur__nom__icontains=query) | Q(reference__icontains=query)
        )
    if type_filter:
        financements = financements.filter(type_financement=type_filter)

    total_engage = financements.aggregate(total=Sum('montant_engage'))['total'] or 0

    context = {
        'financements': financements,
        'query': query,
        'type_filter': type_filter,
        'types': Financement.TYPE_CHOICES,
        'total_engage': total_engage,
    }
    return render(request, 'financements/liste.html', context)


@login_required_custom
def detail(request, pk):
    financement = get_object_or_404(
        Financement.objects.select_related('projet', 'bailleur').prefetch_related('decaissements'),
        pk=pk
    )
    context = {'financement': financement}
    return render(request, 'financements/detail.html', context)


@edit_permission_required
def creer(request):
    if request.method == 'POST':
        form = FinancementForm(request.POST)
        if form.is_valid():
            financement = form.save()
            messages.success(request, 'Financement créé avec succès.')
            return redirect('financements:detail', pk=financement.pk)
    else:
        form = FinancementForm()
    return render(request, 'financements/form.html', {'form': form, 'titre': 'Nouveau financement'})


@edit_permission_required
def modifier(request, pk):
    financement = get_object_or_404(Financement, pk=pk)
    profile = getattr(request.user, 'profile', None)
    if profile and not profile.can_edit_financement(financement):
        messages.error(request, "Vous n'êtes pas point focal de ce bailleur.")
        return redirect('financements:detail', pk=financement.pk)
    if request.method == 'POST':
        form = FinancementForm(request.POST, instance=financement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Financement modifié avec succès.')
            return redirect('financements:detail', pk=financement.pk)
    else:
        form = FinancementForm(instance=financement)
    return render(request, 'financements/form.html', {'form': form, 'titre': 'Modifier le financement', 'financement': financement})


@edit_permission_required
def creer_decaissement(request, financement_pk):
    financement = get_object_or_404(Financement, pk=financement_pk)
    profile = getattr(request.user, 'profile', None)
    if profile and not profile.can_edit_financement(financement):
        messages.error(request, "Vous n'êtes pas point focal de ce bailleur.")
        return redirect('financements:detail', pk=financement.pk)
    if request.method == 'POST':
        form = DecaissementForm(request.POST)
        if form.is_valid():
            decaissement = form.save(commit=False)
            decaissement.financement = financement
            decaissement.save()
            messages.success(request, 'Décaissement enregistré avec succès.')
            return redirect('financements:detail', pk=financement.pk)
    else:
        form = DecaissementForm()
    return render(request, 'financements/form_decaissement.html', {
        'form': form, 'financement': financement, 'titre': 'Nouveau décaissement'
    })
