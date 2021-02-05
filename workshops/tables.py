import django_filters
import django_tables2 as tables
from django.db.models import Q

from workshops.models import Workshop


class WorkshopListTable(tables.Table):
    title = tables.TemplateColumn(
        "<a href='{% url 'workshop_detail' record.id %}'>{{ record.title }}</a> ")
    # starts = tables.DateTimeColumn(accessor='get_time_slot', verbose_name='Starts', format='d/m G:i')
    start = tables.TemplateColumn(
        "{{ record.get_time_slot.start }}",
        orderable=False
    )
    end = tables.TemplateColumn(
        "{{ record.get_time_slot.end }}",
        orderable=False,
    )
    update = tables.TemplateColumn(
        "<a href='{% url 'workshop_update' record.id %}'>Modify</a> ",
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
        # order_by = "-start"


class WorkshopListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    open = django_filters.BooleanFilter()

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(title__icontains=value) | Q(location__icontains=value) | Q(host__icontains=value)))

    class Meta:
        model = Workshop
        fields = ['search', 'open']
