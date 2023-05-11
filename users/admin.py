from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = CustomUser
    list_display = ("username", "is_staff", "is_active",)
    list_filter = ("username", "is_staff", "is_active",)
    fieldsets = (

        ("User Info",{ 
         
            "fields": (
                "username", 
                "email", 
                # "password",
                # "fp_token",
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