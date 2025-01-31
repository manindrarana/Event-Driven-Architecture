from django.db import models

class Notification(models.Model):
    MESSAGE_TYPES = (
        ('welcome', 'Welcome'),
        ('reminder', 'Reminder'),
        ('alert', 'Alert'),
    )
    user_id = models.IntegerField()
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message_type} - {self.user_id}"
