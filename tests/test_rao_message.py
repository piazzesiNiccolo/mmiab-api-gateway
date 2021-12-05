from mib.rao.message import Message
import pytest 

class TestRaoMessage:
    @pytest.mark.parametrize("date_val",[ 
        2,
        "02/12/07"
    ])
    def test_build_message_invalid_dates(self,date_val):
        m = Message(
            id_message=1,
            id_sender=1,
            message_body="foo",
            delivery_date=date_val,
            recipients=[]
        )
        assert m.delivery_date is None
    
    def test_get_attr_val_exists(self):
        m = Message(
            id_message=1,
            id_sender=1,
            message_body="foo",
            extra_val="val")
        assert m.__getattr__("message_body") == "foo"
        assert m.__getattr__("extra_val") == "val"
    
    def test_get_attr_val_not_exists(self):
        m = Message(
            id_message=1,
            id_sender=1,
            message_body="foo",
            extra_val="val")
        with pytest.raises(AttributeError) as e:
            m.__getattr__("noattr")
            assert str(e) == "Attribute noattr does not exists"