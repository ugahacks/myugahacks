import django_filters
import django_tables2 as tables
from django.db.models import Q
from workshops.models import Workshop, Timeslot

class WorkshopListTable(tables.Table):

    title = tables.TemplateColumn(
        "<a href='{% url 'workshop_detail' record.id %}'>{{ record.title }}</a> ")
    starts = tables.DateTimeColumn(accessor='start', verbose_name='Starts', format='d/m G:i')
    ends = tables.DateTimeColumn(accessor='end', verbose_name='Ends', format='m/d G:i')
    update = tables.TemplateColumn(
        "<a href='{% url 'admin:workshops_workshop_change' record.id %}'>Modify</a> ",
        verbose_name='Actions', orderable=False)

    def before_render(self, request):
        if not request.user.is_organizer:
            self.columns.hide('update')

    class Meta:
        model = Workshop
        attrs = {'class': 'table table-hover'}
        template = 'templates/workshop_list.html'
        fields = ['title', 'location', 'host', 'open']
        empty_text = 'No workshops available'
        order_by = '-starts'

class WorkshopListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(title__icontains=value) | Q(location__icontains=value)))

    class Meta:
        model = Workshop
        fields = ['search',]
