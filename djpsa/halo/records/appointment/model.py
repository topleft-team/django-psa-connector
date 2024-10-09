from django.db import models
from model_utils import FieldTracker


class Appointment(models.Model):
    subject = models.CharField(max_length=1000, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    appointment_type = models.CharField(max_length=255, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    # Appointments have two types: appointment and task. Task
    # in this context does NOT mean a project task.
    is_task = models.BooleanField(default=False)
    complete_status = models.IntegerField(blank=True, null=True)
    colour = models.CharField(max_length=50, null=True, blank=True)
    # Not using URLField because I don't trust API data.
    online_meeting_url = models.CharField(max_length=2000, blank=True, null=True)
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, blank=True, null=True)
    site = models.ForeignKey('Site', on_delete=models.CASCADE, blank=True, null=True)
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey('HaloUser', on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Appointments"

    def __str__(self):
        return f"Appointment {self.id} - {self.subject}"


class AppointmentTracker(Appointment):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_appointment'
