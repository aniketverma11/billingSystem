from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

# Create your models here.
from .behaviours import UUIDMixin, StatusMixin, UserStampedMixin


class Product(UUIDMixin, StatusMixin, UserStampedMixin):
    name = models.CharField(max_length=100, blank=True)
    price = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = " Products"

class BillingMaster(UUIDMixin, StatusMixin, UserStampedMixin):
    products = models.ManyToManyField(Product)
    totalPrice = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return str(self.uuid)
    
    class Meta:
        verbose_name = "Billing Master"
        verbose_name_plural = " Billing Master"

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the instance is not saved yet
            super().save(*args, **kwargs)  # Save the instance to get an ID
        # Calculate total price based on the prices of associated products
        self.totalPrice = sum(product.price for product in self.products.all())
        super().save(*args, **kwargs)


@receiver(m2m_changed, sender=BillingMaster.products.through)
def update_total_price(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        instance.totalPrice = sum(product.price for product in instance.products.all())
        instance.save()