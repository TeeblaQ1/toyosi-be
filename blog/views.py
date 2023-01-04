from rest_framework import generics, status
from rest_framework.response import Response
from blog.models import Post, Comment
from blog.serializers import CommentsSerializer, PostSerializer
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.db import transaction
# Create your views here.
class PostListView(generics.ListAPIView):
    # queryset = Post.published.all()
    serializer_class = PostSerializer

    def get_queryset(self):

        queryset = Post.published.all()
        query = self.request.query_params.get("search")

        if query is not None:
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            queryset = Post.published.annotate(rank=SearchRank(search_vector, search_query)
            ).filter(rank__gt=0.2).order_by('-rank')

        return queryset

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.published.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'

    # def get_queryset(self):
    #     slug = self.kwargs.get('slug')
    #     return Post.published.filter(slug=slug).first()

class PostRecentView(generics.ListAPIView):
    queryset = Post.published.all()[:3]
    serializer_class = PostSerializer

class PostSimilarView(generics.GenericAPIView):
    serializer_class = PostSerializer

    def get(self, request, slug):
        post = Post.published.filter(slug=slug).first()
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = list(similar_posts.annotate(same_tags=Count('tags')).values('title', 'description', 'image').order_by('-same_tags', '-publish'))[:4]
        return Response({
            'status': 'Success', 
            'message': 'List Similar Posts', 
            'data': similar_posts
            }, status=status.HTTP_200_OK)

class PostCommentsListView(generics.GenericAPIView):
    
    serializer_class = CommentsSerializer

    def get(self, request, slug):
        post = Post.published.filter(slug=slug).first()
        comments = list(Comment.objects.filter(active=True, post=post).values('name', 'body', 'parent', 'id'))
        return Response({
            'status': 'Success', 
            'message': 'List Comments Successful', 
            'data': comments
            }, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, slug):
        user = request.user
        data = request.data
        if 'parent' in data.keys():
            try:
                data['parent'] = Comment.objects.get(id=data['parent'])
            except Comment.DoesNotExist:
                return Response({
                    'status': 'Fail', 
                    'message': 'Comment you"re trying to reply does not or no longer exists', 
                    'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = Post.published.filter(slug=slug).first()
        if user.is_anonymous:
            comment = Comment(**data, post=post)
            comment.save()
        else:
            comment = Comment.objects.create(
                name=f'{user.first_name} {user.last_name}',
                email=user.email,
                body=request.data.get('body'),
                parent=data.get('parent'),
                post=post
            )
        return Response({
            'status': 'Success', 
            'message': 'Comment Posted Successfully', 
            'data': []
            }, status=status.HTTP_201_CREATED)