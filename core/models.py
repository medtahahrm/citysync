from django.contrib.auth.models import AbstractUser, User
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('citizen', 'Citoyen'),
        ('institution', 'Institution'),
        ('admin', 'Administrateur'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='citizen')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class CitizenProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    cni_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)

    profile_picture = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True
    )

    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class InstitutionProfile(models.Model):
    INSTITUTION_TYPES = (
        ('mairie', 'Mairie/Commune'),
        ('police', 'Police'),
        ('pompiers', 'Pompiers'),
        ('sante', 'Santé'),
        ('education', 'Éducation'),
        ('environnement', 'Environnement'),
        ('transport', 'Transport'),
        ('autre', 'Autre'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='institution_profile')
    institution_type = models.CharField(max_length=100, choices=INSTITUTION_TYPES)
    official_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50)
    department = models.CharField(max_length=100, blank=True)
    jurisdiction_area = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='institution_logos/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.official_name} ({self.get_institution_type_display()})"
    

class UserNotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    incident_alerts = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification settings for {self.user.username}"