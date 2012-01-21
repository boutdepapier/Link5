# -*- coding: utf-8 -*- 
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _

from annoying.fields import AutoOneToOneField


class Author(models.Model):
    user = AutoOneToOneField(User, primary_key=True, related_name="link5_profile")
    newsletter = models.BooleanField(_("Accept newsletter if it exist one day?"), default = False)
    avatar = models.FileField(upload_to='avatars')
    
    @property
    def author_email(self):
        return self.user.email
    
    def __unicode__(self):
        return "%s - %s" % (self.user.username, self.author_email)
            

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    
    class Meta:
        ordering = ["name"]
    
    def __unicode__(self):
        return self.name

class Link(models.Model):
    post_ttl  = models.CharField(max_length=155)
    post_txt  = models.TextField(max_length=255, help_text=_("Post Descripiton"), blank=True, null=True)
    post_url  = models.URLField(max_length=2000, help_text=_("Foreign URL"))
    post_img  = models.URLField(max_length=2000, help_text=_("Illustration"), blank=True, null=True)
    post_html = models.CharField(max_length=2000, help_text=_("Media"), blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.CharField(
        choices = (
            ("publish", _("Published")),
            ("draft", _("Draft")),
            ("deleted", _("Deleted")),
            ),
        default="draft", max_length=20)
        
    link_type = models.CharField(
        choices = (
            ("photo", _("Photo")),
            ("video", _("Video")),
            ("rich", _("Rich")),
            ("link", _("Link")),
            ("error", _("Error")),
            ),
        default="link", max_length=20)
        
    positive = models.PositiveIntegerField(_("Link number of positive votes"), default = 0)
    negative = models.PositiveIntegerField(_("Link number of negative votes"), default = 0)
    
    author = models.OneToOneField('Author')
    category = AutoOneToOneField('Category')
    
    def __unicode__(self):
        return self.post_ttl

class Comment(models.Model):
    status = models.CharField(
        choices = (
            ("publish", _("Published")),
            ("draft", _("Draft")),
            ("deleted", _("Deleted")),
            ),
        default="publish", max_length=20)
    text = models.TextField(max_length=1000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    author = models.ForeignKey(Author)
    link = models.OneToOneField(Link)
    
    def __unicode__(self):
        return "%s - %s - %s" % (self.author, self.link, self.created_at)
    
class Like(models.Model):
    link = models.OneToOneField(Link)
    author = models.OneToOneField('Author')
    created_at = models.DateTimeField(auto_now_add=True)
    point = models.BooleanField(default = True)
    
class Follow(models.Model):
    author = models.ForeignKey('Author')
    #author_to = models.ForeignKey('Author')
    created_at = models.DateTimeField(auto_now_add=True)