from django.contrib import admin
from link5app.models import Link, Author, Category, Comment

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    
class LinkAdmin(admin.ModelAdmin):
    list_display = ["post_ttl", "status", "created_at", "author"]
    ordering = ["-created_at"]
    list_filter = ["status","category"]

class AuthorAdmin(admin.ModelAdmin):
    list_display = ["user", "author_email", "author_date_joined", "author_last_login"]
    ordering = ["-user"]
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ["link", "status", "author", "created_at"] 
    ordering = ["-created_at"]   
    
admin.site.register(Link, LinkAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)