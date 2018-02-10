from google.appengine.ext import ndb


class Message(ndb.Model):
    subject = ndb.StringProperty()
    body = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)
    sender = ndb.StringProperty(required=True)
    receiver = ndb.StringProperty(required=True)
    important = ndb.BooleanProperty(default=False)

    def get_sender_nickname(self):
        return User.get_nickname_from_user_id(self.sender)

    def get_receiver_nickname(self):
        return User.get_nickname_from_user_id(self.receiver)


class User(ndb.Model):
    user_id = ndb.StringProperty()
    nickname = ndb.StringProperty()

    @classmethod
    def get_by_user(cls, user):
        return cls.query().filter(cls.user_id == user.user_id()).get()

    @classmethod
    def get_nickname_from_user_id(cls, user_id):
        user = cls.query().filter(cls.user_id == user_id).get()

        if user:
            return user.nickname

        return None
