from rest_framework import renderers
import json

class UserRenderer(renderers.JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Initialize an empty response string
        response = ''

        if 'ErrorDetail' in str(data):
            # If the response data contains an 'ErrorDetail' (indicating an error),
            # create a JSON object with the 'errors' key and the error data
            response = json.dumps({'errors': data})
        else:
            # If the response data does not contain an 'ErrorDetail',
            # convert the data to a JSON string
            response = json.dumps(data)

        return response
