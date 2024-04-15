from django.db import models
from django.utils import timezone


class StatusMixinManager(models.Manager):
    def all(self, *args, **kwargs):
        return super(StatusMixinManager, self).filter(is_deleted=False)

    def filter(self, *args, **kwargs):
        return (
            super(StatusMixinManager, self)
            .filter(is_active=True, is_deleted=False)
            .filter(*args, **kwargs)
        )

    def active(self, *args, **kwargs):
        return super(StatusMixinManager, self).filter(is_active=True, is_deleted=False)


class PostMixinQuerySet(models.QuerySet):
    def remove_empty(self):
        return self
        # return self.exclude(image__exact='').exclude(categories=None).exclude(image__isnull=True).exclude(
        # short_description__isnull=True).exclude(short_description__exact='')


class PostMixinManager(models.Manager):
    def all(self, *args, **kwargs):
        return super(PostMixinManager, self).filter(
            is_active=True, publish__lte=timezone.now(), is_deleted=False
        )

    def active(self, *args, **kwargs):
        return super(PostMixinManager, self).filter(is_active=True, is_deleted=False)

    def filter(self, *args, **kwargs):
        return (
            super(PostMixinManager, self)
            .filter(is_active=True, is_deleted=False)
            .filter(*args, **kwargs)
        )

    def get_queryset(self):
        return PostMixinQuerySet(self.model, using=self._db)

    def remove_empty(self):
        return self.get_queryset().remove_empty()
