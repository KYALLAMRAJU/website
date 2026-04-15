from django.contrib import admin
from webapp.models import *  # change this line according to your company (update to your app name)

# Register your models here.


class contacusAdmin(admin.ModelAdmin):  # change this line according to your company (rename to match your model)
    list_display = ["name", "email", "subject", "message", "created_date"]  # change this line according to your company (update fields to display)
    list_filter = ["name"]        # change this line according to your company (update filter fields)
    search_fields = ("name", "email")  # change this line according to your company (update search fields)
    date_hierarchy = "created_date"  # change this line according to your company (update date field)


admin.site.register(contacus, contacusAdmin)  # change this line according to your company (update model and admin class names)


class aboutDetailsAdmin(admin.ModelAdmin):  # change this line according to your company (rename/remove if not needed)
    list_display = ["id", "title", "phase", "body"]  # change this line according to your company (update fields to display)
    prepopulated_fields = {"slug": ("title",)}  # change this line according to your company (update slug source field)
    list_filter = ["phase"]       # change this line according to your company (update filter fields)
    search_fields = ("title",)    # change this line according to your company (update search fields)


admin.site.register(aboutdetails, aboutDetailsAdmin)  # change this line according to your company (update model and admin class names)


"""------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

# THE BELOW MODEL IS A TEMPORARY MODEL TO STORE THE WISH DATA FOR MY PRACTICE


class wishdataAdmin(admin.ModelAdmin):  # change this line according to your company (replace with your own domain model admin)
    list_display = ["id", "username", "name", "astrology_message", "mobilenumber"]  # change this line according to your company (update fields)


admin.site.register(wishdata, wishdataAdmin)  # change this line according to your company (update model and admin class names)


class AuthorAdmin(admin.ModelAdmin):  # change this line according to your company (rename/redesign for your business domain)
    list_display = ["authorname", "age", "location"]  # change this line according to your company (update fields)


admin.site.register(author, AuthorAdmin)  # change this line according to your company


class BookAdmin(admin.ModelAdmin):  # change this line according to your company (rename/redesign for your business domain)
    list_display = ["title", "author", "published_date"]  # change this line according to your company (update fields)
    list_filter = ["author"]      # change this line according to your company (update filter fields)
    search_fields = ("title",)    # change this line according to your company (update search fields)


admin.site.register(book, BookAdmin)  # change this line according to your company
