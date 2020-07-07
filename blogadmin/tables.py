import django_filters
import django_tables2 as tables
from django.db.models import Q

from blog.models import Blog


class BlogAdminTable(tables.Table):
    tags = tables.TemplateColumn(
        "{{ record.tags_as_str }}"
    )

    approve = tables.TemplateColumn(
        "<a href='{% url 'blogadmin:blog_admin_detail' record.id %}'>View and Approve</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = Blog
        template = 'templates/blog_admin_home.html'
        fields = ['title', 'publication_date', 'author', 'tags', 'approved']

class BlogAdminFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    approved = django_filters.ChoiceFilter(choices=((1,'Yes'), (0,'No')))

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(title__icontains=value)))


    class Meta:
        model = Blog
        fields = ['approved']
