# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PENDING', 'Pending'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]

    SUBSCRIPTION_TYPE_CHOICES = [
        ('MONTHLY', 'Monthly'),
        ('ANNUAL', 'Annual'),
        ('CARDS', 'Cards Package'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    subscription_type = models.CharField(
        max_length=20, choices=SUBSCRIPTION_TYPE_CHOICES, default='MONTHLY')
    # Only used when subscription_type is CARDS
    number_of_cards = models.IntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    tickets_remaining = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_points(self):
        if self.subscription_type == 'MONTHLY':
            return 10
        elif self.subscription_type == 'ANNUAL':
            return 120
        elif self.subscription_type == 'CARDS':
            # Calculate points for cards (3 points per 10 cards)
            return (self.number_of_cards // 10) * 3
        return 0


class Reclamation(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Ponderation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    reason = models.CharField(max_length=200)
    reservation = models.ForeignKey(
        Reservation, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'

    def __str__(self):
        return f"{self.user.username} - {self.points} points"


@receiver(post_save, sender=Reservation)
def create_ponderation_on_reservation(sender, instance, created, **kwargs):
    if created and instance.status == 'ACTIVE':
        points = instance.calculate_points()
        if points > 0:
            Ponderation.objects.create(
                user=instance.user,
                points=points,
                reason=f"Points for {
                    instance.get_subscription_type_display()} subscription",
                reservation=instance
            )


class ChatCategory(models.Model):
    """
    Categories for chat topics or departments
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Chat Categories"


class FrequentlyAskedQuestion(models.Model):
    """
    Frequently Asked Questions model
    """
    # category = models.ForeignKey(
    #     ChatCategory,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     related_name='faqs'
    # )
    question = models.CharField(max_length=500)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['-created_at']


class ChatMessage(models.Model):
    """
    Model to store individual chat messages
    """
    SENDER_CHOICES = (
        ('user', 'User'),
        ('bot', 'Bot'),
        ('agent', 'Support Agent')
    )

    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    category = models.ForeignKey(
        ChatCategory,
        on_delete=models.SET_NULL,
        null=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"

    class Meta:
        ordering = ['timestamp']
