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


class SLA(models.Model):

    name = models.CharField(max_length=255)
    hours_are_techs_local_time = models.BooleanField(default=False)
    response_reset = models.BooleanField(default=False)
    response_reset_approval = models.BooleanField(default=False)
    track_sla_fix_by_time = models.BooleanField(default=False)
    track_sla_response_time = models.BooleanField(default=False)
    workday_id = models.IntegerField(blank=True, null=True)
    auto_release_limit = models.IntegerField(blank=True, null=True)
    auto_release_option = models.BooleanField(default=False)
    status_after_first_warning = models.IntegerField(blank=True, null=True)
    status_after_second_warning = models.IntegerField(blank=True, null=True)
    status_after_auto_release = models.IntegerField(blank=True, null=True)


class Site(models.Model):

    name = models.CharField(max_length=255)
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.CASCADE)
    colour = models.CharField(max_length=50, null=True, blank=True)
    active = models.BooleanField(default=True)
    phone_number = models.CharField(blank=True, null=True, max_length=250)
    sla = models.ForeignKey(SLA, blank=True, null=True, on_delete=models.CASCADE)
    use = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=1000)


class HaloUser(models.Model):

    name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    initials = models.CharField(max_length=10)
    surname = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True, max_length=250)
    colour = models.CharField(max_length=50, null=True, blank=True)
    active = models.BooleanField(default=True)
    login = models.CharField(max_length=255)
    use = models.CharField(max_length=255)
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, blank=True, null=True, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE)
    never_send_emails = models.BooleanField(default=False)
    phone_number = models.CharField(blank=True, null=True, max_length=250)
    mobile_number = models.CharField(blank=True, null=True, max_length=250)
    mobile_number_2 = models.CharField(blank=True, null=True, max_length=250)
    home_number = models.CharField(blank=True, null=True, max_length=250)
    tel_pref = models.IntegerField(blank=True, null=True)
    is_service_account = models.BooleanField(default=False)
    is_important_contact = models.BooleanField(default=False)
    is_important_contact_2 = models.BooleanField(default=False)


class Ticket(models.Model):
    summary = models.CharField(blank=True, null=True, max_length=255)
    details = models.TextField(
        blank=True, null=True, max_length=8000
    )
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    priority = models.ForeignKey(Priority, blank=True, null=True, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, blank=True, null=True, on_delete=models.CASCADE)
    sla = models.ForeignKey(SLA, blank=True, null=True, on_delete=models.CASCADE)
    last_action_date = models.DateField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    target_time = models.TimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"Ticket {self.id} - {self.summary}"
