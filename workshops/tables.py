import django_filters
import django_tables2 as tables
from workshops.models import Workshop
from django.db.models import Q

class WorkshopsListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    class Meta:
        model = Workshop
        fields = ['search']

class WorkshopsListTable(tables.Table):
    change = tables.TemplateColumn(
        "<a href='{% url 'workshop_detail' record.id %}'>Modify</a> ",
        verbose_name='Actions', orderable=False)
    checkin = tables.TemplateColumn(
        "<a href='{% url 'workshop_checkin' record.id %}'>Check-in hacker</a> ",
        verbose_name='Check-in', orderable=False)
    starts = tables.DateColumn(accessor='starts', verbose_name='Starts', format='d/m G:i')
    ends = tables.DateTimeColumn(accessor='ends', verbose_name='Ends', format='d/m G:i')
    attended = tables.Column(accessor='attended', verbose_name='Total workshops attended')
    opened = tables.Column(accessor='opened', verbose_name='Active')

    def before_render(self, request):
    	if not request.user.is_organizer:
            self.columns.hide('opened')
            self.columns.hide('change')
            self.columns.hide('ends')
            self.columns.hide('starts')

    class Meta:
        model = Workshop
        attrs = {'class': 'table table-hover'}
        template = 'templates/workshops_list.html'
        fields = ['title', 'location', 'host', 'starts', 'ends', 'opened',]
        empty_text = 'No workshops available'
        order_by = '-starts'

class WorkshopsUsersFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(workshop__title__icontains=value) | Q(user__name__icontains=value) |
                                Q(user__email__icontains=value)))

    class Meta:
        model = Workshop
        fields = ['search']



class WorkshopsUsersTable(tables.Table):
    time2 = tables.DateTimeColumn(accessor='time', verbose_name='Time', format='d/m/Y G:i')

    class Meta:
        model = Workshop
        attrs = {'class': 'table table-hover'}
        template = 'templates/workshops_users.html'
        fields = ['id', 'workshop', 'user', 'time2']
        empty_text = 'No hacker has attended yet'
        order_by = 'time'