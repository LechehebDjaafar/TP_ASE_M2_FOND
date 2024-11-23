# views.py
from .models import FrequentlyAskedQuestion, ChatMessage, ChatCategory
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Reservation, Reclamation, Ponderation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def reservation_status(request):
    reservations = Reservation.objects.filter(
        user=request.user).order_by('-created_at')
    context = {
        'reservations': reservations,
    }
    return render(request, 'customer_service/reservation_status.html', context)


@login_required
def submit_reclamation(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        reservation_id = request.POST.get('reservation_id')

        reclamation = Reclamation.objects.create(
            user=request.user,
            title=title,
            description=description,
            reservation_id=reservation_id,
            status='NEW',
            priority='MEDIUM'
        )

        return JsonResponse({'status': 'success', 'reclamation_id': reclamation.id})

    reservations = Reservation.objects.filter(user=request.user)
    context = {
        'reservations': reservations,
    }
    return render(request, 'customer_service/submit_reclamation.html', context)


@login_required
def view_ponderation(request):
    points = Ponderation.objects.filter(
        user=request.user).order_by('-created_at')
    total_points = sum(point.points for point in points)

    # Query all ponderations for the current user only
    ponderations = points  # We already have the filtered queryset

    points_data = []
    for ponderation in ponderations:
        subscription_type = "Regular"
        if ponderation.reservation:
            subscription_type = ponderation.reservation.get_subscription_type_display()

        points_data.append({
            'points': ponderation.points,
            'reason': ponderation.reason,
            'subscription_type': subscription_type,
            'created_at': ponderation.created_at.strftime('%Y-%m-%d')
        })

    context = {
        'points': points,
        'total_points': total_points,
        'points_data': points_data
    }
    return render(request, 'customer_service/ponderation.html', context)


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def chat_room(request):
    """
    Main chat room view with FAQ and chat interface
    """
    
    faqs = FrequentlyAskedQuestion.objects.filter(is_active=True)

    context = {
        'faqs': faqs
    }
    return render(request, 'customer_service/chat_room.html', context)


@login_required
@csrf_protect
@require_http_methods(["POST"])
def get_faq_answer(request):
    """
    Retrieve answer for a specific FAQ and log the interaction
    """
    try:
        data = json.loads(request.body)
        faq_id = data.get('question_id')

        # Retrieve FAQ
        try:
            faq = FrequentlyAskedQuestion.objects.get(
                id=faq_id, is_active=True)
        except FrequentlyAskedQuestion.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Question not found'
            }, status=404)

        # Log chat message
        ChatMessage.objects.create(
            user=request.user,
            sender='user',
            message=faq.question,
           
        )

        # Log bot response
        ChatMessage.objects.create(
            user=request.user,
            sender='bot',
            message=faq.answer,
           
        )

        return JsonResponse({
            'status': 'success',
            'answer': faq.answer
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)


@login_required
def chat_history(request):
    """
    Retrieve paginated chat history for the current user
    """
    messages = ChatMessage.objects.filter(
        user=request.user).order_by('-timestamp')

    # Pagination
    paginator = Paginator(messages, 10)  # Show 10 messages per page
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'customer_service/chat_history.html', {
        'messages': page_obj
    })
