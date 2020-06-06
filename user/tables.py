import django_tables2 as tables

from .models import User


class OnDutyListTable(tables.Table):
    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['name', 'email', 'on_duty', 'is_volunteer', 'is_organizer', 'duty_update_time']
        empty_text = 'No one is on-duty'
        order_by = '-user.name'
