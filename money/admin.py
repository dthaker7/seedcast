from django.contrib import admin

from .models import FinancialProfile, MonthlyBudget


admin.site.register(FinancialProfile)
admin.site.register(MonthlyBudget)

