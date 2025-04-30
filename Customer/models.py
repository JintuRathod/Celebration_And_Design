from django.db import models
from django.utils import timezone
from django.utils.timezone import now
default_date = timezone.now()
# from django.core.exceptions import ValidationError

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class EventCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)

    def __str__(self):
        return self.category_name


class EventTheme(models.Model):
    theme_id = models.AutoField(primary_key=True)
    theme_name = models.CharField(max_length=100)
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    caste_based = models.BooleanField(default=False)

    def __str__(self):
        return self.theme_name

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    registration_date = models.DateTimeField(default=now)
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username

class Event(models.Model):
    EVENT_STATUS_CHOICES = [
        ('Planned', 'Planned'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed')
    ]

    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=100)
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE, null=True, blank=True)
    theme = models.ForeignKey(EventTheme, on_delete=models.CASCADE,null=True, blank=True)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=50, choices=EVENT_STATUS_CHOICES)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")

    def __str__(self):
        return self.event_name


class Payment(models.Model):
    customer_first_name = models.CharField(max_length=100, default="Unknown")
    customer_last_name = models.CharField(max_length=100, default="Unknown")
    customer_email = models.EmailField(null=True)
    customer_phone = models.CharField(max_length=15, null=True, blank=True)
    event_name = models.CharField(max_length=200, null=True)
    event_start_date = models.DateField(null=True, blank=True)
    event_end_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=255, null=True, blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.customer_first_name} {self.customer_last_name} - {self.event_name}"

class Review(models.Model):
    name = models.CharField(max_length=255,default='username')
    email = models.EmailField(null=True,blank =True)
    venue = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15,default='999999999')
    message = models.TextField(default='-')

    def __str__(self):
        return self.name

class SpecialRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    request_text = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Request {self.request_id} - {self.customer.username}"


class Plan(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100)
    max_persons = models.IntegerField()
    features = models.TextField()
    event = models.ForeignKey(EventCategory, on_delete=models.CASCADE,blank=True,null=True)

    def get_features(self):
        return self.features.split(",")

    def __str__(self):
        return self.name

class PlanImage(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="plan_images/")

    def __str__(self):
        return f"Image for {self.plan.name}"




