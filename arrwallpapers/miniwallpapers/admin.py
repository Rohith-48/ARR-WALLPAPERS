from django.contrib import admin
from .models import UserProfileDoc

admin.site.register(UserProfileDoc)


from .models import WallpaperCollection, Tag, Category

@admin.register(WallpaperCollection)
class WallpaperCollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'price', 'upload_date')
    list_filter = ('category', 'tags', 'price')
    search_fields = ('title', 'user__username', 'category__name')
    filter_horizontal = ('tags',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
