from django.contrib import admin

from .models import Post, Group , Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description")
    search_fields = ("title",)
    empty_value_display = "-пусто-"

class FolloADM(admin.ModelAdmin):
    list_display = ("user", 'author')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FolloADM)
# Register your models here.
