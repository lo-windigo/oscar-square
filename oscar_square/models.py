from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models


class SquareSettings(models.Model):
    """
    Account details and settings for the Square payment API
    """
    access_token = models.CharField('Access Token',
            max_length=50,
            blank=True,
            null=True)
    application_id = models.CharField('Application ID',
            max_length=50,
            blank=True,
            null=True)
    location_id = models.CharField('Location ID',
            max_length=50,
            blank=True,
            null=True)
    # Prevent more than one setting object by associating it with the site
    site = models.ForeignKey(Site,
            blank=True,
            null=True)

    def save(self, *args, **kwargs):
        """
        Manually assign the site to the settings object
        """
        self.site = Site.objects.get(pk=settings.SITE_ID)

        super().save(*args, **kwargs)


    @classmethod
    def get_settings(cls):
        """
        Retrieve the settings object for the current site
        """
        settings_singleton,_ = cls.objects.get_or_create(
                site__pk=settings.SITE_ID)

        return settings_singleton

