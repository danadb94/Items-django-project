from core.models import Item, Tag
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', ]


class ItemSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)  # to display not only user id
    tags = TagSerializer(many=True)

    class Meta:
        model = Item
        fields = ['id', 'user', 'description', 'price', 'tags', ]
        read_only_fields = ('user',)

    def create(self, validated_data):
        tags = validated_data.pop('tags')

        # iterate over all tags, make sure which are existing tags in the database. create new tags otherwise
        tag_names = []
        for tag in tags:
            tag_names.append(tag['name'])

        existing_tags = Tag.objects.filter(name__in=tag_names)

        new_tag_names = list(tag_names)
        if existing_tags:
            for tag in existing_tags:
                new_tag_names.remove(tag.name)

        new_tags = []
        for tag in new_tag_names:
            new_tags.append(Tag(name=tag))

        Tag.objects.bulk_create(new_tags)

        item = Item.objects.create(**validated_data)

        tags = Tag.objects.filter(name__in=tag_names)
        for tag in tags:
            item.tags.add(tag.id)

        item.save()
        return item


class AddTagInputSerializer(serializers.Serializer):
    tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
