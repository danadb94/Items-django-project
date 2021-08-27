from core.models import Item,Tag
from django.contrib import admin


@admin.register(Item)
class Itemadmin(admin.ModelAdmin):
    list_display = ('id','user','description','price',)
    autocomplete_fields = ('tags',)


@admin.register(Tag)
class Tagadmin(admin.ModelAdmin):
    list_display = ('id','name')
    search_fields = ('name',)

