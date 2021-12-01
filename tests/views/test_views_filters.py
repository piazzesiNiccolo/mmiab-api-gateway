import pytest
from datetime import datetime
from mib.views.filters import delivery_datetime_format,datetime_format
class TestVIewsFilters:

    @pytest.mark.parametrize("date, fmt",[ 
        (datetime.strptime("01/02/2000","%d/%m/%Y"),"00:00 01/02/2000"),
        (None,"")
    ])
    def test_delivery_datetime_filter(self, date,fmt):
        assert delivery_datetime_format(date) == fmt

    def test_datetime_filter(self):
        assert datetime_format("01/02/2000") == "2000-02-01"