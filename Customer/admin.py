from django.contrib import admin
from .models import Admin, EventCategory, EventTheme, Customer, Event, Payment, Review, SpecialRequest, Plan, PlanImage

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'username', 'password_hash', 'email', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('created_at',)

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name', 'image')
    search_fields = ('category_name',)

@admin.register(EventTheme)
class EventThemeAdmin(admin.ModelAdmin):
    list_display = ('theme_id', 'theme_name', 'category', 'caste_based')
    search_fields = ('theme_name',)
    list_filter = ('caste_based',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'username', 'email', 'registration_date')
    search_fields = ('username', 'email')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'event_name', 'category', 'theme', 'status', 'customer']
    list_filter = ['status', 'category', 'theme']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
    'customer_first_name', 'customer_last_name', 'event_name', 'event_start_date', 'event_end_date','amount', 'payment_date')
    search_fields = ('customer_first_name', 'customer_last_name', 'event_name', 'customer_email')


# Optionally, you can create a custom admin interface for the Review model
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'venue', 'phone', 'message')
    search_fields = ('name', 'email')

# Register the Review model with the custom admin interface
admin.site.register(Review, ReviewAdmin)

@admin.register(SpecialRequest)
class SpecialRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'customer', 'event', 'request_text', 'request_date')
    search_fields = ('customer__username', 'event__event_name')
    list_filter = ('request_date',)


class PlanImageInline(admin.TabularInline):
    model = PlanImage
    extra = 1  # Allows adding multiple images while creating a plan

class PlanAdmin(admin.ModelAdmin):
    inlines = [PlanImageInline]

admin.site.register(Plan, PlanAdmin)
admin.site.register(PlanImage)