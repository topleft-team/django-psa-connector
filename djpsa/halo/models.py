from django.db import models
from model_utils import FieldTracker


class Priority(models.Model):
    # priorityid is actual ID for sync
    name = models.CharField(max_length=255, blank=True, null=True)
    is_hidden = models.BooleanField(default=False)
    colour = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Priorities"

    def __str__(self):
        return f"Priority {self.id} - {self.name}"


class Status(models.Model):
    name = models.CharField(max_length=255)
    colour = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Statuses"

    def __str__(self):
        return f"Status {self.id} - {self.name}"


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
        return f"Agent {self.id} - {self.name}"


class Client(models.Model):
    name = models.CharField(max_length=255)
    inactive = models.BooleanField(default=False)
    colour = models.CharField(max_length=255, blank=True, null=True)
    main_site = models.ForeignKey('Site',
                                  blank=True,
                                  null=True,
                                  on_delete=models.CASCADE,
                                  related_name='client_primary'
                                  )
    phone_number = models.CharField(blank=True, null=True, max_length=250)


    class Meta:
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"Client {self.id} - {self.name}"


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

    class Meta:
        verbose_name_plural = "SLAs"

    def __str__(self):
        return f"Site {self.id} - {self.name}"


class Site(models.Model):

    name = models.CharField(max_length=255)
    client = models.ForeignKey('Client', blank=True, null=True, on_delete=models.CASCADE)
    colour = models.CharField(max_length=50, null=True, blank=True)
    active = models.BooleanField(default=True)
    phone_number = models.CharField(blank=True, null=True, max_length=250)
    sla = models.ForeignKey('SLA', blank=True, null=True, on_delete=models.CASCADE)
    use = models.CharField(max_length=255, blank=True, null=True)
    delivery_address = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Sites"

    def __str__(self):
        return f"Site {self.id} - {self.name}"


class HaloUser(models.Model):

    name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    initials = models.CharField(max_length=10, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(null=True, blank=True, max_length=250)
    colour = models.CharField(max_length=50, null=True, blank=True)
    active = models.BooleanField(default=True)
    login = models.CharField(max_length=255, blank=True, null=True)
    use = models.CharField(max_length=255, blank=True, null=True)
    client = models.ForeignKey('Client', blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey('Agent', blank=True, null=True, on_delete=models.CASCADE)
    site = models.ForeignKey('Site', blank=True, null=True, on_delete=models.CASCADE)
    never_send_emails = models.BooleanField(default=False)
    phone_number = models.CharField(blank=True, null=True, max_length=250)
    mobile_number = models.CharField(blank=True, null=True, max_length=250)
    mobile_number_2 = models.CharField(blank=True, null=True, max_length=250)
    home_number = models.CharField(blank=True, null=True, max_length=250)
    tel_pref = models.IntegerField(blank=True, null=True)
    is_service_account = models.BooleanField(default=False)
    is_important_contact = models.BooleanField(default=False)
    is_important_contact_2 = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Halo Users"

    def __str__(self):
        return f"Halo User {self.id} - {self.name}"


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


class TicketType(models.Model):
    name = models.CharField(max_length=255)
    agents_can_select = models.BooleanField(default=False)
    end_users_can_select = models.BooleanField(default=False)
    allow_attachments = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    copy_attachments_to_child = models.BooleanField(default=False)
    copy_attachments_to_related = models.BooleanField(default=False)
    use = models.CharField(max_length=255, blank=True, null=True)


class Ticket(models.Model):
    summary = models.CharField(blank=True, null=True, max_length=255)
    details = models.TextField(
        blank=True, null=True, max_length=8000
    )
    status = models.ForeignKey('Status', on_delete=models.CASCADE)
    priority = models.ForeignKey('Priority', blank=True, null=True, on_delete=models.CASCADE)
    client = models.ForeignKey('Client', blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey('Agent', blank=True, null=True, on_delete=models.CASCADE)
    sla = models.ForeignKey('SLA', blank=True, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey('HaloUser', blank=True, null=True, on_delete=models.CASCADE)
    site = models.ForeignKey('Site', blank=True, null=True, on_delete=models.CASCADE)
    type = models.ForeignKey('TicketType', blank=True, null=True, on_delete=models.CASCADE)
    project = models.ForeignKey('Ticket', blank=True, null=True, on_delete=models.CASCADE)
    user_email = models.EmailField(blank=True, null=True)
    reported_by = models.CharField(max_length=255, blank=True, null=True)
    end_user_status = models.IntegerField(blank=True, null=True)
    category_1 = models.CharField(max_length=255, blank=True, null=True)
    category_2 = models.CharField(max_length=255, blank=True, null=True)
    category_3 = models.CharField(max_length=255, blank=True, null=True)
    category_4 = models.CharField(max_length=255, blank=True, null=True)
    inactive = models.BooleanField(default=False)
    sla_response_state = models.CharField(max_length=255, blank=True, null=True)
    sla_hold_time = models.FloatField(blank=True, null=True)
    date_occurred = models.DateTimeField(blank=True, null=True)
    respond_by_date = models.DateTimeField(blank=True, null=True)
    fix_by_date = models.DateTimeField(blank=True, null=True)
    date_assigned = models.DateTimeField(blank=True, null=True)
    response_date = models.DateTimeField(blank=True, null=True)
    deadline_date = models.DateTimeField(blank=True, null=True)
    last_action_date = models.DateField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    target_time = models.TimeField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    last_incoming_email = models.DateTimeField(blank=True, null=True)
    impact = models.IntegerField(blank=True, null=True)
    impact_level = models.IntegerField(blank=True, null=True)
    flagged = models.BooleanField(default=False)
    on_hold = models.BooleanField(default=False)
    project_time_actual = models.FloatField(blank=True, null=True)
    project_money_actual = models.FloatField(blank=True, null=True)
    cost = models.FloatField(blank=True, null=True)
    estimate = models.FloatField(blank=True, null=True)
    estimated_days = models.FloatField(blank=True, null=True)
    exclude_from_sla = models.BooleanField(default=False)
    team = models.CharField(max_length=255, blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    use = models.CharField(max_length=255, blank=True, null=True)
    email_to_list = models.TextField(max_length=2000, blank=True, null=True)
    urgency = models.IntegerField(blank=True, null=True)
    service_status_note = models.TextField(max_length=2000, blank=True, null=True)
    ticket_tags = models.TextField(max_length=2000, blank=True, null=True)
    appointment_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"Ticket {self.id} - {self.summary}"


class PriorityTracker(Priority):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_priority'


class StatusTracker(Status):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_status'


class AgentTracker(Agent):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_agent'


class ClientTracker(Client):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_client'


class SLATracker(SLA):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_sla'


class SiteTracker(Site):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_site'


class HaloUserTracker(HaloUser):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_halouser'


class AppointmentTracker(Appointment):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_appointment'


class TicketTypeTracker(TicketType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_tickettype'


class TicketTracker(Ticket):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_ticket'

