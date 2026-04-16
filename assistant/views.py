import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from accounts.decorators import login_required_custom

from .gemini_service import ask_gemini


@login_required_custom
def assistant_index(request):
    """Page principale de l'assistant IA."""
    context = {
        'gemini_enabled': bool(settings.GEMINI_API_KEY)
    }
    return render(request, 'assistant/index.html', context)


@require_POST
@login_required_custom
def assistant_ask(request):
    """Endpoint API pour poser une question à l'IA."""
    if not settings.GEMINI_API_KEY:
        return JsonResponse({
            'error': 'L\'assistant IA n\'est pas configuré. Veuillez ajouter une clé API Gemini.'
        }, status=503)
    
    try:
        body = json.loads(request.body)
        question = body.get('question', '').strip()
        history = body.get('history', [])

        if not question:
            return JsonResponse({'error': 'Veuillez poser une question.'}, status=400)

        result = ask_gemini(question, conversation_history=history)
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
