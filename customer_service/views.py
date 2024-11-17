# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Reservation, Reclamation, Ponderation

@login_required
def reservation_status(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
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
    points = Ponderation.objects.filter(user=request.user).order_by('-created_at')
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