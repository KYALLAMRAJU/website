import json
from webapp.models import wishdata

class reusable:
    def get_object_by_id(self, id):
        print(type(id))
        try:
            if not str(id).isdigit():
                print("inside id is not in")
                return None
            id=int(id)
            obj = wishdata.objects.get(id=id)
        except wishdata.DoesNotExist:
            obj = None
        return obj

    def is_json(self,incomingdata):
        try:
            p_data=json.loads(incomingdata)
            valid=True
        except ValueError:
            valid=False
        return  valid


