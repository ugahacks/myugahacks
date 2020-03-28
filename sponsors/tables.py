import django_tables2 as tables

from applications.models import Application

class ApplicationsListSponsor(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail_sponsor' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)
    origin = tables.Column(accessor='origin', verbose_name='Origin')

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'user.email', 'university','degree','class_status', 'origin']
        empty_text = 'No applications available'
        order_by = '-user.name'