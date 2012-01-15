from django.contrib import admin
from link5app.models import Link, Author, Category, Comment


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

    
admin.site.register(Link)
admin.site.register(Author)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment)