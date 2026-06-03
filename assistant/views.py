import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib import messages
from accounts.decorators import login_required_custom

from .gemini_service import ask_gemini, get_gemini_api_key
from .models import GeminiConfig


@login_required_custom
def assistant_index(request):
    """Page principale de l'assistant IA."""
    api_key = get_gemini_api_key()
    has_user_config = hasattr(request.user, 'gemini_config') and request.user.gemini_config.is_active

    context = {
        'gemini_enabled': bool(api_key),
        'has_user_config': has_user_config,
        'api_key_source': 'user' if has_user_config else ('env' if api_key else 'none')
    }
    return render(request, 'assistant/index.html', context)


@login_required_custom
def configure_api_key(request):
    """Page pour configurer sa clé API Gemini."""
    config = None
    try:
        config = request.user.gemini_config
    except GeminiConfig.DoesNotExist:
        pass

    if request.method == 'POST':
        api_key = request.POST.get('api_key', '').strip()
        action = request.POST.get('action', 'save')

        if action == 'delete' and config:
            config.delete()
            messages.success(request, 'Votre clé API a été supprimée.')
            return redirect('assistant:configure')

        if api_key:
            if config:
                config.api_key = api_key
                config.is_active = True
                config.save()
            else:
                GeminiConfig.objects.create(
                    user=request.user,
                    api_key=api_key,
                    is_active=True
                )
            messages.success(request, 'Votre clé API Gemini a été enregistrée avec succès.')
            return redirect('assistant:index')
        else:
            messages.error(request, 'Veuillez saisir une clé API valide.')

    return render(request, 'assistant/configure.html', {'config': config})


@require_POST
@login_required_custom
def assistant_ask(request):
    """Endpoint API pour poser une question à l'IA."""
    api_key = get_gemini_api_key(request.user)
    if not api_key:
        return JsonResponse({
            'error': 'L\'assistant IA n\'est pas configuré. Veuillez ajouter une clé API Gemini dans les paramètres.'
        }, status=503)
    
    try:
        body = json.loads(request.body)
        question = body.get('question', '').strip()
        history = body.get('history', [])

        if not question:
            return JsonResponse({'error': 'Veuillez poser une question.'}, status=400)

        result = ask_gemini(question, conversation_history=history, user=request.user)
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
