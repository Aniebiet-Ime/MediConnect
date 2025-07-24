from django.contrib.auth.models import AbstractUser 
from django.db import models
from django.utils import timezone
from PIL import Image
from .managers import CustomUserManager  # Import the custom user manager

class User(AbstractUser):
    #Custom User model extending Django's AbstractUser
    USER_TYPES = (
        ('patient', 'Patient'),
        ('provider', 'Healthcare Provider'),
        ('admin', 'Administrator'),
    )
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=15, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()  #Add this line
    
    # Required fields for registration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        #Resize profile picture
        if self.profile_picture and hasattr(self.profile_picture, 'path'):
            try:
                img = Image.open(self.profile_picture.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.profile_picture.path)
            except Exception:
                pass
                
                
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return (today - self.date_of_birth).days // 365
        return None
        
class Profile(models.Model):
    #Extended profile information for users
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class ProviderProfile(models.Model):
    #Additional profile information for healthcare providers 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    years_of_experience = models.IntegerField(default=0)
    hospital_affiliation = models.CharField(max_length=200, blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    availability_hours = models.JSONField(default=dict)  #Store schedule as JSON
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"

