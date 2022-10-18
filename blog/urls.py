from django.urls import path
from blog.views import PostCommentsListView, PostListView, PostDetailView, PostRecentView, PostSimilarView

urlpatterns = [
    path('posts/', PostListView.as_view(), name="post_list"),
    path('posts/recent/', PostRecentView.as_view(), name="post_recent"),
    path('posts/<slug>/', PostDetailView.as_view(), name="post_detail"),
    path('posts/<slug>/comments/', PostCommentsListView.as_view(), name="post_comments"),
    path('posts/<slug>/similar/', PostSimilarView.as_view(), name="post_similar"),
]
