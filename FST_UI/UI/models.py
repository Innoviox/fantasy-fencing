from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    pass

class Fencer(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    WEAPONS = (
        ('E', 'Epee'),
        ('S', 'Sabre'),
        ('F', 'Foil')
    )
    weapon = models.CharField(max_length=1, choices=WEAPONS)
    rating = models.CharField(max_length=1, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rating})"