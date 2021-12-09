import pytest
import os
import mock
import io
import base64
from werkzeug.datastructures import FileStorage
from mib.rao.utils import Utils
from uuid import uuid4
from tempfile import mkstemp


class TestUtils:
    def test_save_profile_picture(self):
        Utils.save_profile_picture({})
        filename = "test.png"
        with mock.patch("os.path.join") as m:
            fake_path = "mib/static/assets/" + filename
            m.return_value = fake_path
            Utils.save_profile_picture(
                {
                    "data": base64.b64encode(b"many data").decode("utf-8"),
                    "name": filename,
                }
            )
            with open(fake_path, "rb") as file:
                assert file.read() == b"many data"
            os.remove(fake_path)
