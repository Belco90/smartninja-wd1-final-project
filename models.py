from google.appengine.ext import ndb


class Message(ndb.Model):
    subject = ndb.StringProperty()
    body = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)
    sender = ndb.StringProperty(required=True)
    receiver = ndb.StringProperty(required=True)
    important = ndb.BooleanProperty(default=False)
