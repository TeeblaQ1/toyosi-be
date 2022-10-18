from rest_framework import serializers
from blog.models import Comment, Post
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        fields = ('id','slug', 'title', 'description', 'body', 'image', 'publish', 'tags')
        model = Post
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CommentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
    
    def validate(self, attrs):
        return super().validate(attrs)

