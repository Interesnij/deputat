from django.contrib import admin
from common.model.other import *
from common.model.comments import *
from common.model.votes import *


class BlogCommentDocInline(admin.TabularInline):
    model = BlogCommentDoc
class BlogCommentPhotoInline(admin.TabularInline):
    model = BlogCommentPhoto

class ElectNewCommentDocInline(admin.TabularInline):
    model = ElectNewCommentDoc
class ElectNewCommentPhotoInline(admin.TabularInline):
    model = ElectNewCommentPhoto


class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['text','commenter','created']
    list_filter = ['created']
    search_fields = ['created','text','commenter']

    inlines = [
        BlogCommentDoc,
        BlogCommentPhotoInline,
    ]

    class Meta:
            model = BlogComment

class ElectNewCommentAdmin(admin.ModelAdmin):
    list_display = ['text','commenter','created']
    list_filter = ['created']
    search_fields = ['created','text','commenter']

    inlines = [
        ElectNewCommentDocInline,
        ElectNewCommentPhotoInline,
    ]

    class Meta:
            model = ElectNewComment


admin.site.register(PhoneCodes)
admin.site.register(BlogComment, BlogCommentAdmin)
admin.site.register(ElectNewComment, ElectNewCommentAdmin)

admin.site.register(BlogVotes)
admin.site.register(ElectNewVotes2)
admin.site.register(ElectNewCommentVotes)
admin.site.register(BlogCommentVotes)
