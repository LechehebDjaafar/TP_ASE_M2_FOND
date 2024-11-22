# urls.py
from django.urls import path
from . import views

app_name = 'customer_service'

urlpatterns = [
    path('reservation-status/', views.reservation_status,
         name='reservation_status'),
    path('submit-reclamation/', views.submit_reclamation,
         name='submit_reclamation'),
    path('ponderation/', views.view_ponderation, name='ponderation'),
    path('chat/', views.chat_room, name='chat_room'),
    path('get-answer/', views.get_faq_answer, name='get_answer'),
    path('chat-history/', views.chat_history, name='chat_history'),


]
