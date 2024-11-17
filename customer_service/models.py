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
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPE_CHOICES,default='MONTHLY')
    number_of_cards = models.IntegerField(default=0)  # Only used when subscription_type is CARDS
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
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, null=True, blank=True)
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
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True)
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
                reason=f"Points for {instance.get_subscription_type_display()} subscription",
                reservation=instance
            )