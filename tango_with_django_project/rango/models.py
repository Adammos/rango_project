from django.db import models
from django.contrib.auth.models import User 
from django.template.defaultfilters import slugify 

class Category(models.Model):
	name = models.CharField(max_length=128, unique=True)
	views = models.IntegerField(default=0)
	likes = models.IntegerField(default=0)
	slug = models.SlugField(unique=True)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		self.views = self.views if self.views >= 0 else 0
		super(Category, self).save(*args, **kwargs)

	class Meta:
		verbose_name_plural = 'Categories'

	def __str__(self):
		return self.name 

class Page(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	title = models.CharField(max_length=128)
	url = models.URLField()
	views = models.IntegerField(default=0)

	def __str__(self):
		return self.title 

class Comment(models.Model):
	author = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
	body = models.TextField()
	created_on = models.DateTimeField(auto_now_add=True)

	# Only one way relationship with Category (many to one)
	# Many comments can be assigned to one Category
	category = models.ForeignKey('Category', on_delete=models.CASCADE)


class UserProfile(models.Model):
	# This line is required. Links UserProfile to a User model instance.
	user = models.OneToOneField(User, on_delete=models.CASCADE)

	# The additional attributes we wish to include
	website = models.URLField(blank=True)
	picture = models.ImageField(upload_to='profile_images', blank=True)

	def __str__(self):
		return self.user.username 