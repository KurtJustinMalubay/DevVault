from django.contrib import admin

from .models import Comment, Entry, Membership, Tag, Workspace


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'member_count', 'created_at')
    inlines = [MembershipInline]


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'entry_type', 'status', 'workspace', 'author', 'created_at')
    list_filter = ('entry_type', 'status', 'workspace')
    search_fields = ('title', 'description')
    filter_horizontal = ('tags',)


admin.site.register(Tag)
admin.site.register(Comment)
