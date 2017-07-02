from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 

# Create your models here.

class UserProfile(models.Model):
   user = models.OneToOneField(User, on_delete = models.CASCADE)
   nickname = models.CharField(max_length=50)
   @property
   def alias(self):
     """restituisce uno pseudonimo: in ordine prova con nickname, nome, username"""
     res = self.user.username
     if (self.nickname != ""):
	res = self.nickname
     elif (self.user.first_name != ""):
	res = self.user.first_name
     return res

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


