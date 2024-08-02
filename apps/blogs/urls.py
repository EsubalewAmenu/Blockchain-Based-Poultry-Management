from django.urls import path, re_path
from .views import BlogDetailView, BlogListView, BlogTagListView

urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list_view'),
    re_path(r'^tag/(?P<tag>[\w ]+)/$', BlogTagListView.as_view(), name='blog_tag_list_view'),
    re_path(r'^(?P<slug>[\w-]+)/$', BlogDetailView.as_view(), name='blog_detail_view'),
]
