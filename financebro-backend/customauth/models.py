from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    pass

    @cached_property
    async def plan(self):
        user_subscriptions = UserSubscription.objects.filter(user=self)
        if await user_subscriptions.acount() == 0:
            return 'FREE_TRIAL'
        active_user_subscriptions = user_subscriptions.filter(stripe_subscription_ends_at__gt = timezone.now())
        return (
            'PAID'
            if await active_user_subscriptions.acount() > 0
            else 'FREE_TRIAL'
        )


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    stripe_id = models.CharField(max_length=255, primary_key=True)
    stripe_amount_total = models.PositiveBigIntegerField()
    stripe_customer_id = models.CharField(max_length=255)
    stripe_customer_email = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_subscription_starts_at = models.DateTimeField()
    stripe_subscription_ends_at = models.DateTimeField()
    stripe_subscription_plan_name = models.CharField(max_length=255)
    stripe_subscription_plan_id = models.CharField(max_length=255)
    stripe_subscription_product_id = models.CharField(max_length=255)

    created_date = models.DateTimeField(verbose_name='Created At', auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name='Updated At', auto_now=True)


class UserAutoFillProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(_("middle name"), max_length=150, blank=True, null=True)
    middle_name = models.CharField(_("middle name"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("middle name"), max_length=150, blank=True, null=True)
    email = models.CharField(_("email"), max_length=150, blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=20, blank=True, null=True)
    address1 = models.CharField(_("Address 1"), max_length=255, blank=True, null=True)
    address2 = models.CharField(_("Address 2"), max_length=255, blank=True, null=True)
    city = models.CharField(_("City"), max_length=100, blank=True, null=True)
    country = models.CharField(_("Country"), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True, null=True)
    education1 = models.TextField(_("Education 1"), max_length=20, blank=True, null=True)
    education2 = models.TextField(_("Education 2"), max_length=20, blank=True, null=True)
    education3 = models.TextField(_("Education 3"), max_length=20, blank=True, null=True)
    employment1 = models.TextField(_("Employment 1"), max_length=20, blank=True, null=True)
    employment2 = models.TextField(_("Employment 2"), max_length=20, blank=True, null=True)
    employment3 = models.TextField(_("Employment 3"), max_length=20, blank=True, null=True)

    created_date = models.DateTimeField(verbose_name='Created At', auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name='Updated At', auto_now=True)
