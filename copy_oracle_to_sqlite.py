import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webProject.settings")  # <- change project name if needed

django.setup()

from webapp.models import contacus, aboutdetails, loginFormdata, wishdata


def copy_table(model):
    oracle_qs = model.objects.using('oracle').all()
    print(f"Copying {model.__name__}: {oracle_qs.count()} rows")

    for obj in oracle_qs:
        data = {}

        for field in model._meta.fields:
            if field.name == 'id':  # Let SQLite auto-increment ID
                continue
            data[field.name] = getattr(obj, field.name)

        model.objects.using('default').create(**data)

    print(f"Done: {model.__name__}")


def main():
    copy_table(contacus)
    copy_table(aboutdetails)
    copy_table(loginFormdata)
    copy_table(wishdata)

    print("\n✔✔✔ ALL DATA MIGRATED FROM ORACLE → SQLITE ✔✔✔\n")


if __name__ == "__main__":
    main()
