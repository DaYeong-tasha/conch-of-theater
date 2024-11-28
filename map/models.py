from django.db import models

class Theater(models.Model):
    mt10id = models.CharField(max_length=100, primary_key=True)
    fcltynm = models.CharField(max_length=100)
    adres = models.CharField(max_length=200)

    def __str__(self):
        return self.fcltynm