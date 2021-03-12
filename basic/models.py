from django.db import models
from django.contrib.auth.models import User
from PIL import Image
# Create your models here.

import os

from uuid import uuid4

def path_and_rename(instance, filename):
    upload_to = 'photos'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)



class UserProfileInfo(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)

    name = models.CharField(max_length=500,null=True)

    profile_pic = models.ImageField(upload_to=path_and_rename,blank=True)
    blob = models.BinaryField(blank=True,null=True)


    def __str__(self):
        return self.user.username

    def save(self):
        super().save()  # saving image first
        if self.profile_pic:
            img = Image.open(self.profile_pic.path) # Open image using self

            if img.height > 300 or img.width > 300:
                new_img = (300, 300)
                img.thumbnail(new_img)
                img.save(self.profile_pic.path)  # saving image at the same path
