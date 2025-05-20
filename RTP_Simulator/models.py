from django.db import models
from django.utils import timezone


class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(primary_key=True)
    password = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.email

class Instructor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    is_approved = models.BooleanField(default=False)  # NEW

    def __str__(self):
        return self.username

class Visitor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=100)  # Consider hashing
    contact = models.CharField(max_length=15)
    is_approved = models.BooleanField(default=False)  

    def __str__(self):
        return self.username

class AdminNote(models.Model):
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note created at {self.created_at}"

class LabVIEWPanel(models.Model):
    class Meta:
        verbose_name = "RTPSimulator Panel"
        verbose_name_plural = "RTPSimulator Panel"

class RequestCert(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    instructor = models.ForeignKey('Instructor', on_delete=models.CASCADE)
    student_name = models.CharField(max_length=100)
    university_name = models.CharField(max_length=100)
    date_completed = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Certificate for {self.student_name} ({self.university_name})"

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class VisitorSlot(models.Model):
    slot_number = models.IntegerField(unique=True)
    session_key = models.CharField(max_length=100, blank=True, null=True)
    last_active = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Visitor {self.slot_number} - {self.session_key}"
