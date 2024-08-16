from django.db import models


class Priority(models.Model):
    # priorityid is actual ID for sync
    name = models.CharField(max_length=255, blank=True, null=True)
    is_hidden = models.BooleanField(default=False)
    colour = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Priorities"

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=255)
    colour = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Statuses"

    def __str__(self):
        return self.name


class Agent(models.Model):
    name = models.CharField(max_length=255)
    is_disabled = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)
    initials = models.CharField(max_length=10, blank=True, null=True)
    firstname = models.CharField(max_length=255, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    colour = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Agents"

    def __str__(self):
        return f"{self.firstname} {self.surname}"


class Client(models.Model):
    inactive = models.BooleanField(default=False)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name


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

    class Meta:
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"Ticket {self.id} - {self.summary}"