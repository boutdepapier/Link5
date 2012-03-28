# -*- coding: utf-8 -*- 
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _

from django.template.defaultfilters import slugify, urlencode

from annoying.fields import AutoOneToOneField


class Author(models.Model):
    user = AutoOneToOneField(User, primary_key=True, related_name="link5_profile")
    newsletter = models.BooleanField(_("Accept newsletter if it exist one day?"), default = False)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
    conditions = models.BooleanField(_("Term and conditions?"), default = False)
    
    @property
    def author_email(self):
        return self.user.email 
        
    @property
    def author_date_joined(self):
        return self.user.date_joined
        
    @property
    def author_last_login(self):
        return self.user.last_login
    
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
            ("denied", _("Denied")),
            ),
        default="draft", max_length=20)
        
    link_type = models.CharField(
        choices = (
            ("photo", _("Photo")),
            ("video", _("Video")),
            ("rich", _("Rich")),
            ("link", _("Link")),
            ),
        default="link", max_length=20)
        
    positive = models.IntegerField(_("Link number of positive votes"), default = 0)
    negative = models.IntegerField(_("Link number of negative votes"), default = 0)
    
    author = models.ForeignKey('Author')
    category = models.ForeignKey('Category')
    
    @property
    def source(self):
        from urlparse import urlparse
        return urlparse(self.post_url)
    
    @property
    def title_for_url(self):
        return slugify(self.post_ttl.encode("ascii", "xmlcharrefreplace"))
        
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    @property
    def id_b62(self):
        """Encode a number in Base X
    
        `num`: The number to encode
        `alphabet`: The alphabet to use for encoding
        """
        arr = []
        base = len(self.ALPHABET)
        url_id = self.id
        while url_id:
            rem = url_id % base
            url_id = url_id // base
            arr.append(self.ALPHABET[rem])
        arr.reverse()
        return ''.join(arr)
    
    def b62_id(self, url_id):
        """Decode a Base X encoded string into the number
    
        Arguments:
        - `string`: The encoded string
        - `alphabet`: The alphabet to use for encoding
        """
        base = len(self.ALPHABET)
        strlen = len(url_id)
        num = 0
    
        idx = 0
        for char in url_id:
            power = (strlen - (idx + 1))
            num += self.ALPHABET.index(char) * (base ** power)
            idx += 1
    
        return num
    
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
    link = models.ForeignKey(Link)
    
    def __unicode__(self):
        return "%s - %s - %s" % (self.author, self.link.post_ttl, self.created_at)
    
class Like(models.Model):
    link = models.ForeignKey(Link)
    author = models.ForeignKey('Author')
    created_at = models.DateTimeField(auto_now_add=True)
    point = models.BooleanField(default = True)
    
class Follow(models.Model):
    author_from = models.ForeignKey('Author', related_name="author_from")
    author_to = models.ForeignKey('Author', related_name="author_to")
    created_at = models.DateTimeField(auto_now_add=True)