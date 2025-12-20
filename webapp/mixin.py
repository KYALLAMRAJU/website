from django.http import HttpResponse,JsonResponse
from django.core.serializers import serialize,deserialize
import json
from webapp.models import wishdata


class HTTPResponseMixin(object):
    def render_to_http_response(self, json_data,status=200, **response_kwargs):
        return HttpResponse(json_data, **response_kwargs, content_type='application/json', status=status)

class JSONResponseMixin(object):
    def render_to_json_response(self, context,status=200, **response_kwargs):
        return JsonResponse(context, **response_kwargs, safe=False,status=status)

# THIS CODE IS TO REMOVE THE EXTRA METADATA FROM THE DJANGO SERIALIZE METHOD OUTPUT
class SerializeMixin(object):
    def serialize(self, qs):
        json_data = serialize('json', qs)
        dict_data = json.loads(json_data)
        finallist = []
        for obj in dict_data:
            finallist.append({
                'id': obj['pk'],
                'fields': {
                    'username':obj['fields']['username'],
                    'name':obj['fields']['name'],
                    'astrology_message':obj['fields']['astrology_message'],
                    'mobilenumber':obj['fields']['mobilenumber'],
                }
            }
            )
        fjsondata = json.dumps(finallist, indent=1)
        return fjsondata

