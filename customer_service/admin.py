from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Reservation, Reclamation, Ponderation, ChatCategory, FrequentlyAskedQuestion, ChatMessage


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subscription_type', 'status', 'number_of_cards',
                    'tickets_remaining', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'subscription_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Subscription Details', {
            'fields': ('subscription_type', 'number_of_cards', 'status', 'tickets_remaining')
        }),
        ('Date Information', {
            'fields': ('start_date', 'end_date')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Recalculate points when subscription type changes
        if change and 'subscription_type' in form.changed_data:
            points = obj.calculate_points()
            Ponderation.objects.create(
                user=obj.user,
                points=points,
                reason=f"Points update for {
                    obj.get_subscription_type_display()} subscription",
                reservation=obj
            )


@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'title', 'priority', 'status', 'created_at',
                    'view_reservation_link')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Complaint Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Details', {
            'fields': ('reservation', 'priority', 'status')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_user(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.email})"
    get_user.short_description = 'User'

    def view_reservation_link(self, obj):
        if obj.reservation:
            url = reverse('admin:customer_service_reservation_change', args=[
                          obj.reservation.id])
            return format_html('<a href="{}">View Reservation</a>', url)
        return "No Reservation"
    view_reservation_link.short_description = 'Associated Reservation'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'reservation')


@admin.register(Ponderation)
class PonderationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'points', 'reason',
                    'get_reservation_info', 'created_at')
    list_filter = ('created_at', 'points')
    search_fields = ('user__username', 'user__email',
                     'reason', 'reservation__subscription_type')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Rating Information', {
            'fields': ('user', 'points', 'reason', 'reservation')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_reservation_info(self, obj):
        if obj.reservation:
            url = reverse('admin:customer_service_reservation_change', args=[
                          obj.reservation.id])
            return format_html(
                '{} - {} ({})<br><a href="{}">View Reservation</a>',
                obj.reservation.get_subscription_type_display(),
                obj.reservation.status,
                obj.reservation.created_at.strftime('%Y-%m-%d'),
                url
            )
        return "No Reservation"
    get_reservation_info.short_description = 'Reservation Details'
    get_reservation_info.allow_tags = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'reservation')

# Custom Date Range Filter


class DateRangeFilter(admin.SimpleListFilter):
    title = 'Date Range'
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('week', 'This week'),
            ('month', 'This month'),
            ('year', 'This year'),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta

        if self.value() == 'today':
            today = timezone.now().date()
            return queryset.filter(created_at__date=today)
        if self.value() == 'week':
            week_ago = timezone.now().date() - timedelta(days=7)
            return queryset.filter(created_at__date__gte=week_ago)
        if self.value() == 'month':
            month_ago = timezone.now().date() - timedelta(days=30)
            return queryset.filter(created_at__date__gte=month_ago)
        if self.value() == 'year':
            year_ago = timezone.now().date() - timedelta(days=365)
            return queryset.filter(created_at__date__gte=year_ago)


@admin.register(ChatCategory)
class ChatCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(FrequentlyAskedQuestion)
class FrequentlyAskedQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'created_at')
    list_filter = ( 'is_active', 'created_at')
    search_fields = ('question', 'answer')


# FrequentlyAskedQuestion.objects.create(
#     question="How can I recharge my tram card?",
#     answer="You can recharge your tram card via our website or at any tram station."
# )
# FrequentlyAskedQuestion.objects.create(
#     question="What should I do if I lose my tram card?",
#     answer="Please contact customer service immediately to block your card."
# )
# FrequentlyAskedQuestion.objects.create(
#     question="Where can I find tram schedules?",
#     answer="You can find tram schedules on our website or the SETRAM mobile app."
# )
# FrequentlyAskedQuestion.objects.create(
#     question="Is there a discount for students?",
#     answer="Yes, we offer discounted subscriptions for students with a valid ID."
# )
# FrequentlyAskedQuestion.objects.create(
#     question="Can I transfer my balance to another card?",
#     answer="No, balance transfers between cards are not allowed."
# )
# FrequentlyAskedQuestion.objects.create(
#     question="What payment methods are accepted?",
#     answer="We accept cash, credit cards, and mobile payment options at stations."
# )
# FrequentlyAskedQuestion.objects.create(
#     question="Are trams accessible for disabled passengers?",
#     answer="Yes, all trams are equipped with facilities for disabled passengers."
# )
# FrequentlyAskedQuestion.objects.create(
#     question="How can I report an issue or complaint?",
#     answer="You can report issues through our website or contact customer service directly."
# )
# FrequentlyAskedQuestion.objects.create(
#     question="Is there a mobile app for SETRAM?",
#     answer="Yes, the SETRAM app is available on Android and iOS for schedules and card management."
# )

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'message_preview',
                    'timestamp', 'is_read')
    list_filter = ('sender', 'timestamp', 'is_read')
    search_fields = ('message',)

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'


ReservationAdmin.list_filter += (DateRangeFilter,)
ReclamationAdmin.list_filter += (DateRangeFilter,)
PonderationAdmin.list_filter += (DateRangeFilter,)
