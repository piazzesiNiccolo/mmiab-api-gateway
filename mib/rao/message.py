from datetime import datetime

class Message:

    def __init__(self, id_message=None, id_sender=None, message_body='',
        delivery_date=None, recipients=[], img_path=None, to_filter=False,
        reply_to=None, is_sent=False, is_arrived=False, **kwargs
    ):
        self.id_message = id_message
        self.id_sender = id_sender
        self.message_body = message_body
        try:
            dt = datetime.strptime(delivery_date, '%H:%M %d/%m/%Y')
            self.delivery_date = dt
        except (ValueError, TypeError):
            self.delivery_date = None
        self.recipients = recipients
        self.img_path = img_path
        self.to_filter = to_filter
        self.reply_to = reply_to
        self.is_sent = is_sent
        self.is_arrived = is_arrived
        self.extra_data = kwargs.copy()

    @staticmethod
    def build_from_json(json: dict):
        return Message(**json)

    def __getattr__(self, attrname):
        if attrname in self.__dict__:
            return self.__dict__[attrname]
        elif attrname in self.extra_data:
            return self.extra_data[attrname]
        else:
            raise AttributeError(f"Attribute {attrname} does not exist")





