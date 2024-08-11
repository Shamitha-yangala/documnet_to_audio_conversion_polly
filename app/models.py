from django.db import models

# Create your models here.

class Language(models.Model):
    name = models.CharField(max_length=100)
    language_code = models.CharField(max_length=20)

    def __str__(self):
        return self.name
class Gender(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)  # Corrected the foreign key reference
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Voice(models.Model):
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
