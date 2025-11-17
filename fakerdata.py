import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','webProject.settings' ) #SETTINGS ENVIRONMENT SHOULD BE AVAILABLE TO THIS SCRIPT
import django
django.setup() #PLEASE SETUP DJANGO

from webapp.models import *
from faker import Faker
import random as r
fk=Faker()
def mobilenumber():
    fd = r.randint(6, 9)
    fn = str(fd)
    tn = ""
    for i in range(9):
        tn = tn + str(r.randint(0, 9))
    return int(fn + tn)
def populate(n):
    for i in range(n):
        fusername = fk.license_plate
        fname=fk.name()
        fmessage=fk.text()
        fmobile=mobilenumber()
        wdata=wishdata.objects.get_or_create(username=fusername,name=fname,astrology_message=fmessage,mobilenumber=fmobile)
#main
n=int(input("Enter the number of records to be populated:"))
populate(n)
print("{} records populated".format(n))