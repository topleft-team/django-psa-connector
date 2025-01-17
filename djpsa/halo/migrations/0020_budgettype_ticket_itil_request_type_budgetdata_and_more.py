# Generated by Django 4.2.11 on 2025-01-17 13:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('halo', '0019_alter_ticket_team'),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('default_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
            options={
                'verbose_name_plural': 'Budget Types',
            },
        ),
        migrations.AddField(
            model_name='ticket',
            name='itil_request_type',
            field=models.IntegerField(choices=[(1, 'Incident'), (2, 'Change Request'), (3, 'Service Request'), (4, 'Problem'), (20, 'Request For Quote'), (21, 'Advice Other'), (22, 'Projects'), (23, 'Tasks')], default=1),
        ),
        migrations.CreateModel(
            name='BudgetData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hours', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('money', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('estimated_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('estimated_money', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('actual_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('actual_money', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('scheduled_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('scheduled_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('toschedule_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('toschedule_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('remaining_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('remaining_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('budget_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='halo.budgettype')),
                ('ticket', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='halo.ticket')),
            ],
        ),
        migrations.CreateModel(
            name='BudgetDataTracker',
            fields=[
            ],
            options={
                'db_table': 'halo_budgetdata',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('halo.budgetdata',),
        ),
        migrations.CreateModel(
            name='BudgetTypeTracker',
            fields=[
            ],
            options={
                'db_table': 'halo_budgettype',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('halo.budgettype',),
        ),
    ]