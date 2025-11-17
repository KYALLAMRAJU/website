from django.contrib import admin
from webapp.models import *

# Register your models here.

class contacusAdmin(admin.ModelAdmin):
    list_display = ['name','email','subject','message','created_date']
    #prepopulated_fields = {'slug':('name','email')}
    list_filter = ['name']
    search_fields = ('name', 'email')
    date_hierarchy = 'created_date'
admin.site.register(contacus,contacusAdmin)


class aboutDetailsAdmin(admin.ModelAdmin):
    list_display = ['id','title','phase','body']
    prepopulated_fields = {'slug':('title',)}
    list_filter = ['phase']
    search_fields = ('title',)
admin.site.register(aboutdetails,aboutDetailsAdmin)






"""------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

#THE BELOW MODEL IS A TEMPORARY MODEL TO STORE THE WISH DATA FOR MY PRACTICE


class wishdataAdmin(admin.ModelAdmin):
    list_display = ['id','username','name','astrology_message','mobilenumber']
admin.site.register(wishdata,wishdataAdmin)