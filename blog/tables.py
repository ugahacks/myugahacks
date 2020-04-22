import django_filters
import django_tables2 as tables
from django.db.models import Q
from blog.models import Blog

class BlogPostsListTable(tables.Table):

    title = tables.Column(accessor='title', verbose_name='Title')
    description = tables.Column(accessor='description', verbose_name='Description')
    author = tables.Column(accessor='author.name', verbose_name='Author')
    # update = tables.TemplateColumn(
    #     "<a href='{% url 'blog_update' record.id %}'>Modify</a> ",
    #     verbose_name='Actions', orderable=False)

    class Meta:
        model = Blog
        attrs = {'class': 'table table-hover'}
        template = 'templates/blog_list.html'
        fields = ['title', 'description', 'author']
        empty_text = 'No blog posts created...Why not create one?'


class BlogPostsListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(title__icontains=value) | Q(description__icontains=value) | Q(author__icontains=value)))

    class Meta:
        model = Blog
        fields = ['search']
