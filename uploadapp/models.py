from django.db import models


class User(models.Model):
   pic =models.ImageField(upload_to="images/")
# Create your models here.
