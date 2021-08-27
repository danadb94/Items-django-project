from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="username")
    description = models.CharField(max_length=256, help_text="description of an item")
    price = models.FloatField()
    tags = models.ManyToManyField(Tag, null=True, blank=True)

    def __str__(self):
        return f'{self.user.email}- {self.price}'
