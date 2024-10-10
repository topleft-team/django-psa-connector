from django.db import models
from model_utils import FieldTracker


class Site(models.Model):

    name = models.CharField(max_length=255)
    client = models.ForeignKey(
        'Client', blank=True, null=True, on_delete=models.CASCADE)
    colour = models.CharField(max_length=50, null=True, blank=True)
    active = models.BooleanField(default=True)
    phone_number = models.CharField(blank=True, null=True, max_length=250)
    sla = models.ForeignKey(
        'SLA', blank=True, null=True, on_delete=models.CASCADE)
    use = models.CharField(max_length=255, blank=True, null=True)
    delivery_address = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Sites"

    def __str__(self):
        return f"Site {self.id} - {self.name}"


class SiteTracker(Site):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_site'
