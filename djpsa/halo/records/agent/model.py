from django.db import models
from model_utils import FieldTracker

UNASSIGNED_AGENT_ID = 1  # The Agent with id 1 represents the concept of being unassigned.
# Apparently the designer of this API dropped out before the lesson on NULLs.


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


class AgentTracker(Agent):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_agent'
