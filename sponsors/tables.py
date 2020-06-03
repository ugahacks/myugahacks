import django_filters
import django_tables2 as tables
from django.db.models import Q

from applications.models import Application
from sponsors.models import Sponsor
from user.models import User


class ApplicationsListSponsor(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'sponsors:app_detail_sponsor' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)
    origin = tables.Column(accessor='origin', verbose_name='Origin')

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'user.email', 'university', 'degree', 'class_status', 'origin']
        empty_text = 'No applications available'
        order_by = '-user.name'

class SponsorListTable(tables.Table):
    update = tables.TemplateColumn(
        "<a href='{% url 'sponsors:sponsor_update' record.id %}'>Modify</a> ",
        verbose_name='Actions', orderable=False)

    def before_render(self, request):
        if not request.user.is_organizer:
            self.columns.hide('update')

    class Meta:
        model = Sponsor
        attrs = {'class': 'table table-hover'}
        template = 'templates/sponsor_list.html'
        fields = ['company', 'email_domain', 'tier']
        empty_text = 'No sponsors are whitelisted.'


class SponsorListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    tier = django_filters.ChoiceFilter(choices=Sponsor.TIERS, empty_label='Any')

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            (Q(company__icontains=value) | Q(email_domain__icontains=value) | Q(tier__icontains=value)))

    class Meta:
        model = Sponsor
        fields = ['search', 'tier']
