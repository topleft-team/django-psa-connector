from django.db import models

# Ticket
    # id
    # summary
    # details
    # status_id
    # priority_id
    # client_id (company)
    # client_name
    # user_id (contact)
    # user_name
    # agent_id (member/resource)
    # estimate
    # estimatedays
    # lastactiondate
    # last_update
    # starttime
    # targetdate
    # targettime


# priority
    # id (weird alphanumeric)
    # priorityid (actual ID)
    # name
    # ishidden
    # colour


# Status
    # id
    # name
    # colour


# Agent
    # id
    # name
    # isdisabled
    # email
    # initials
    # firstname
    # surname
    # colour

# Client (company)
    # id
    # inactive
    # name

class Priority(models.Model):
    # priorityid is actual ID for sync
    name = models.CharField(max_length=255, blank=True, null=True)
    is_hidden = models.BooleanField(default=False)
    colour = models.CharField(max_length=255, blank=True, null=True)


class Status(models.Model):
    name = models.CharField(max_length=255)
    colour = models.CharField(max_length=255, blank=True, null=True)


class Agent(models.Model):
    name = models.CharField(max_length=255)
    is_disabled = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)
    initials = models.CharField(max_length=10, blank=True, null=True)
    firstname = models.CharField(max_length=255, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    colour = models.CharField(max_length=255, blank=True, null=True)


class Client(models.Model):
    inactive = models.BooleanField(default=False)
    name = models.CharField(max_length=255)


class Ticket(models.Model):
    summary = models.CharField(blank=True, null=True, max_length=255)
    details = models.TextField(
        blank=True, null=True, max_length=8000
    )
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    priority = models.ForeignKey(Priority, blank=True, null=True, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, blank=True, null=True, on_delete=models.CASCADE)
    last_action_date = models.DateField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    target_time = models.TimeField(blank=True, null=True)
