from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import BlacklistToken, CustomUser


class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = CustomUser
    list_display = ("username", "is_staff", "is_active",)
    list_filter = ("username", "is_staff", "is_active",)
    fieldsets = (

        ("User Info",{ 
         
            "fields": (
                "acceptation",
                "username", 
                "email", 
                "ip_address",
                # "password",
                "fp_token",
                "token_expiration",
                "birthday",
                "birthplace",
                "workplace",
                "religion",
                "insurance_number",
                "tax_number",
                "adress_pl",
                "adress_de",
                "profession",
                "position",
                "internal_tax_number",
                "nfz_name",
                "nfz_adress",
                "phone_number",
                "bank",
                "bic_swift",
                "bank_account",
                "health_insurance_de",
                "health_insurance_de_number",
                "shoe_size",
                "growth",
                "work_clothes",
                "rights",
                "payment",
                # 'vacations_days_quantity',
                'vacations_days_quantity_de',
                # 'last_year_vacations_days_quantity',
                'last_year_vacations_days_quantity_de',
                # 'days_to_use_in_current_year',
                'days_to_use_in_current_year_de',
                # 'vacacions_on_demand',
                # 'cares_vacations',
                # 'force_majeure_vacations',
                # 'compassionate_vacations',
            )
        }),

        ("Permissions", {
            "fields": (
                "is_staff", 
                "is_active", 
                "date_joined",
                # "groups", 
                # "user_permissions"
            )}
        ),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email", 
                "password1", 
                "password2", 
                "is_staff",
                "is_active", 
            )}
        ),
    )

    search_fields = ("username",)
    ordering = ("username",)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BlacklistToken)