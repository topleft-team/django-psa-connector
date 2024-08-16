from django.contrib import admin

from djpsa.halo import models


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'summary', 'client', 'status', 'priority', 'agent')
    search_fields = ['id', 'summary']


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'inactive')
    search_fields = ['id', 'name']


@admin.register(models.Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'is_disabled')
    search_fields = ['id', 'name']


@admin.register(models.Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['id', 'name']


@admin.register(models.Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['id', 'name']
