from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
from django.contrib.auth import get_user_model

User = get_user_model()

class Reservation(models.Model):
    """Table reservation for customers."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    people = models.PositiveIntegerField()
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.date} at {self.time}"

class Store(models.Model):
    """Farm products available in the store."""
    CATEGORY_CHOICES = [
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('grains', 'Grains'),
        ('dairy', 'Dairy'),
        ('livestock', 'Livestock'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='farm_products/', blank=True, null=True)
    tag = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    """Shopping cart for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    items = models.ManyToManyField(Store, through='CartItem')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username} (Created: {self.created_at.strftime('%Y-%m-%d')})"

class CartItem(models.Model):
    """Item and quantity in a cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in cart of {self.cart.user.username}"

class Wishlist(models.Model):
    """Wishlist of items for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    items = models.ManyToManyField(Store)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.username} (Created: {self.created_at.strftime('%Y-%m-%d')})"

class Carousel(models.Model):
    """Images for homepage carousel."""
    image = models.ImageField(upload_to='carousel/')
    alt_text = models.CharField(max_length=150)

    def __str__(self):
        return self.alt_text

class TeamMember(models.Model):
    """Team members' information."""
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    details = models.TextField()
    image = models.ImageField(upload_to='team/')
    social_instagram = models.URLField(blank=True)
    social_twitter = models.URLField(blank=True)
    social_facebook = models.URLField(blank=True)
    social_tiktok = models.URLField(blank=True)
    is_highlight = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Feature(models.Model):
    """Key features of the farm/business."""
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class (e.g. 'bi-leaf')")
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

class FarmStatistic(models.Model):
    """Farm statistics to display."""
    label = models.CharField(max_length=100)
    number = models.PositiveIntegerField()
    suffix = models.CharField(max_length=10, blank=True, help_text="e.g. '+', '%'")

    def __str__(self):
        return self.label

class Event(models.Model):
    """Upcoming and past events."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/', blank=True, null=True)

    def __str__(self):
        return self.title

class HeroSlide(models.Model):
    """Hero slides for homepage."""
    image = models.ImageField(upload_to='hero_slides/')
    alt_text = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.alt_text or f"Hero Slide {self.pk}"



class OTP(models.Model):
    PURPOSE_CHOICES = (
        ('reset', 'Password Reset'),
        ('2fa', 'Two-Factor Authentication'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='reset')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # ✅ Add this field

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.username} | {self.purpose} | {self.code}"
