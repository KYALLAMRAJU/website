import os
import django
from webapp.models import *
from faker import Faker
import random as r
os.environ.setdefault('DJANGO_SETTINGS_MODULE','webProject.settings' ) #SETTINGS ENVIRONMENT SHOULD BE AVAILABLE TO THIS SCRIPT

fk=Faker()
class wishdatafaker():
    def mobilenumber(self):
        fd = r.randint(6, 9)
        fn = str(fd)
        tn = ""
        for i in range(9):
            tn = tn + str(r.randint(0, 9))
        return int(fn + tn)
    def populate(self,n):
        for i in range(n):
            fusername = fk.license_plate
            fname=fk.name()
            fmessage=fk.text()
            fmobile=self.mobilenumber()
            wdata=wishdata.objects.get_or_create(username=fusername,name=fname,astrology_message=fmessage,mobilenumber=fmobile)
#main
w=wishdatafaker()
n=int(input("Enter the number of records to be populated:"))
w.populate(n)
print("{} records populated".format(n))

from webapp.models import *
from faker import Faker
fk=Faker()
class authorsfaker():
    def populate2(self,n):
        for i in range(n):
            fauthor=fk.name()
            fage=fk.random_int(min=25, max=80)
            flocation=fk.street_name()
            auth=author.objects.get_or_create(authorname=fauthor,age=fage,location=flocation)
#main
b=authorsfaker()
n=int(input("Enter the number of records to be populated:"))
b.populate2(n)
print("{} records populated".format(n))


from webapp.models import *
from faker import Faker
fk=Faker()
class booksfaker():
    def populate3(self, n):
        for i in range(n):
            ftitle = fk.street_name()
            fdate = fk.date()
            # The following line randomly selects a single author from the database:
            #   fauthor = author.objects.order_by('?').first()
            #
            # Explanation:
            # - order_by('?') tells Django to randomly order the queryset of authors. The '?' is a special argument for random ordering in SQL.
            # - first() returns the first object from this randomly ordered queryset, so you get one random author.
            # - If there are no authors in the database, first() returns None.
            #
            # This is useful for assigning a random author to each new book record being created.
            fauthor = author.objects.order_by('?').first()
            if fauthor is not None:
                new_book, created = book.objects.get_or_create(title=ftitle, author=fauthor, published_date=fdate)
                print(f"Book created: title={ftitle}, author={fauthor.authorname}, published_date={fdate}, created={created}")
            else:
                print("No authors found in the database. Please populate authors first.")
#main
b=booksfaker()
n=int(input("Enter the number of records to be populated:"))
b.populate3(n)
print("{} records populated".format(n))
