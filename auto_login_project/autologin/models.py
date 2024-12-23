from django.db import models

class WebsiteCredentials(models.Model):
    url = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    username_field_id = models.CharField(max_length=100, null=True, blank=True)
    password_field_id = models.CharField(max_length=100, null=True, blank=True)
    login_button_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.url
