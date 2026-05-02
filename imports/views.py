import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from accounts.decorators import login_required_custom
from accounts.models import ActivityLog

from .template_generator import generate_template
from .engine import analyze_file, execute_import


def _user_can_import(user):
    """Vérifie si l'utilisateur peut exécuter un import (admin ou directeur)."""
    if user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    if not profile or not profile.is_approved:
        return False
    return profile.is_directeur or profile.role in ('superadmin', 'directeur')


@login_required_custom
def import_index(request):
    """Page principale d'import avec upload et preview."""
    can_import = _user_can_import(request.user)
    context = {'report': None, 'step': 'upload', 'can_import': can_import}

    if request.method == 'POST':
        if not can_import:
            messages.error(request, "Vous n'avez pas les droits pour exécuter un import.")
            return render(request, 'imports/index.html', context)

        if 'analyze' in request.POST:
            file = request.FILES.get('excel_file')
            if not file:
                messages.error(request, "Veuillez sélectionner un fichier Excel.")
                return render(request, 'imports/index.html', context)

            if not file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, "Le fichier doit être au format Excel (.xlsx).")
                return render(request, 'imports/index.html', context)

            try:
                report = analyze_file(file)
                file.seek(0)
                request.session['import_file_data'] = file.read().hex()
                request.session['import_file_name'] = file.name
                context['report'] = report
                context['report_json'] = json.dumps(report, default=str)
                context['step'] = 'preview'
                context['file_name'] = file.name
                context['sections'] = [
                    {**report['bailleurs'], 'key': 'bailleurs'},
                    {**report['projets'], 'key': 'projets'},
                    {**report['financements'], 'key': 'financements'},
                    {**report['decaissements'], 'key': 'decaissements'},
                ]
            except Exception as e:
                messages.error(request, f"Erreur lors de l'analyse : {str(e)}")

        elif 'execute' in request.POST:
            file_hex = request.session.get('import_file_data')
            if not file_hex:
                messages.error(request, "Session expirée. Veuillez re-charger le fichier.")
                return render(request, 'imports/index.html', context)

            try:
                from io import BytesIO
                file_bytes = bytes.fromhex(file_hex)
                file_obj = BytesIO(file_bytes)

                counts = execute_import(file_obj)

                total_created = sum(c['created'] for c in counts.values())
                total_updated = sum(c['updated'] for c in counts.values())
                total_errors = sum(len(c['errors']) for c in counts.values())

                msg = f"Import terminé : {total_created} créé(s), {total_updated} mis à jour"
                if total_errors:
                    msg += f", {total_errors} erreur(s)"

                messages.success(request, msg)
                ActivityLog.log(request.user, 'create', 'Import Excel',
                                f'{total_created} créés, {total_updated} mis à jour', details=msg)

                context['counts'] = counts
                context['step'] = 'done'

                del request.session['import_file_data']
                if 'import_file_name' in request.session:
                    del request.session['import_file_name']

            except Exception as e:
                messages.error(request, f"Erreur lors de l'import : {str(e)}")

    return render(request, 'imports/index.html', context)


@login_required_custom
def download_template(request):
    """Télécharge le fichier Excel type."""
    buffer = generate_template()
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Template_Import_Projets_Bailleurs.xlsx"'
    return response
