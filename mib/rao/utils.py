import os
import base64
from flask import current_app

class Utils:

    def save_profile_picture(json: dict):

        if 'data' in json and 'name' in json:
            b64_file = json['data']
            bytes_file = base64.b64decode(b64_file.encode('utf-8'))
            file_name = json['name']
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
            with open(file_path, 'wb') as file:
                file.write(bytes_file)
