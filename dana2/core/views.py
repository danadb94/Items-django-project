from core.models import Item, Tag
from django.contrib.auth.models import User
from core.serializers import ItemSerializer, UserSerializer, TagSerializer,\
    AddTagInputSerializer
from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response


class UserView(mixins.CreateModelMixin, mixins.DestroyModelMixin,
               mixins.ListModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.values_list('id', 'email', 'first_name', 'last_name').all()


class TagView(mixins.CreateModelMixin, mixins.DestroyModelMixin,
              mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(methods=["post"], detail=False)
    def update_tags(self, request, pk=None):
        tags = request.data
        responses = []

        # verify if there is data
        if len(tags) < 1:
            return Response(data={"Tags list is missing"}, status=status.HTTP_400_BAD_REQUEST)

        for tag in tags:
            tag_name = tag['tag']
            remove = tag['remove']

            # Validate if inputs are good
            if type(tag_name) != str or type(remove) != bool:
                responses.append(f"For {tag_name} inputs are wrong. Tag should be string, remove should be boolean")
                return Response(data={str(responses)},
                                status=status.HTTP_400_BAD_REQUEST)

            # Validate if tag exist
            existing_tag = Tag.objects.filter(name__in=[tag_name])

            # raise error when tag not exist and user wants to delete it,
            # when tag exist and user wants to add it again
            if (remove and not existing_tag) or (existing_tag and not remove):
                responses.append(f"For {tag_name} remove is {remove} but tag existence: {existing_tag}")
                return Response(data={str(responses)},
                                status=status.HTTP_400_BAD_REQUEST)

            elif remove:
                Tag.objects.filter(name=tag_name).delete()
                responses.append(f'{tag_name} delete')
            else:
                Tag.objects.create(name=tag_name)
                responses.append(f'{tag_name} created')

        return Response(data={str(responses)}, status=status.HTTP_200_OK)


class ItemView(mixins.CreateModelMixin, mixins.DestroyModelMixin,
               mixins.ListModelMixin, GenericViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["post"], detail=True)
    def add_tag(self, request, pk=None):
        input_serializer = AddTagInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        item = self.get_object()
        item.tags.add(input_serializer.validated_data['tag'])
        item.save()

        serializer = ItemSerializer(item, many=False)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
