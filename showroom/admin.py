from django.contrib import admin
from users.models import ShowroomProfile, Vehicle, VehicleOwnershipHistory

# Register your models here.

@admin.register(ShowroomProfile)
class ShowroomProfileAdmin(admin.ModelAdmin):
    list_display = [
        'showroom_name',
        'registration_number',
        'owner_name',
        'phone',
        'verification_status',
        'created_at'
    ]
    
    list_filter = ['verification_status', 'created_at']
    search_fields = ['showroom_name', 'registration_number', 'owner_name', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    
    fieldsets = (
        ('Business Information', {
            'fields': ('showroom_name', 'registration_number', 'pan_number')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'alternative_phone')
        }),
        ('Owner Information', {
            'fields': ('owner_name', 'owner_citizenship')
        }),
        ('Documents', {
            'fields': (
                'registration_certificate',
                'pan_certificate',
                'owner_citizenship_file',
                'showroom_photo'
            )
        }),
        ('Verification', {
            'fields': (
                'verification_status',
                'verified_by',
                'verification_remarks',
                'verified_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        'chassis_number',
        'make',
        'model',
        'year',
        'showroom',
        'current_owner',
        'verification_status',
        'created_at'
    ]

    list_filter = ['verification_status', 'vehicle_type', 'fuel_type', 'created_at']
    search_fields = [
        'chassis_number',
        'engine_number',
        'make',
        'model',
        'permanent_plate_number',
        'temporary_plate_number'
    ]
    readonly_fields = ['created_at', 'updated_at', 'verified_at', 'temporary_plate_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'showroom',
                'chassis_number',
                'engine_number',
                'make',
                'model',
                'year',
                'color'
            )
        }),
        ('Technical Details', {
            'fields': (
                'vehicle_type',
                'fuel_type',
                'engine_cc',
                'seating_capacity'
            )
        }),
        ('Photos', {
            'fields': (
                'photo_front',
                'photo_back',
                'photo_left',
                'photo_right'
            )
        }),
        ('Ownership', {
            'fields': ('current_owner', 'price', 'payment_receipt')
        }),
        ('Number Plates', {
            'fields': ('temporary_plate_number', 'permanent_plate_number')
        }),
        ('Verification', {
            'fields': (
                'verification_status',
                'verified_by',
                'verification_remarks',
                'verified_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VehicleOwnershipHistory)
class VehicleOwnershipHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'vehicle',
        'owner',
        'is_current_owner',
        'purchase_date',
        'purchase_price'
    ]
    
    list_filter = ['is_current_owner', 'purchase_date']
    search_fields = ['vehicle__chassis_number', 'owner__full_name']
    readonly_fields = ['created_at']