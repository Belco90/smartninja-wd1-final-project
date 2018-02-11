#!/usr/bin/env python
import os
import jinja2
import webapp2
import json
from google.appengine.api import urlfetch, users
from models import Message, User

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


def get_weather_info(location):
    url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=db8b1ce1eaccb7d82980f5c1144e2eec".format(location)
    response = urlfetch.fetch(url)
    data = response.content
    weather_info = json.loads(data)

    if weather_info and str(weather_info["cod"]) == "200":
        return weather_info

    return None


class BaseHandler(webapp2.RequestHandler):

    def get_common_context(self, redirect_to_name=None):
        current_user = users.get_current_user()
        if current_user:
            return {
                "user": current_user,
                "path": self.request.path,
                "logged_in": True,
                "logout_url": users.create_logout_url('/'),
            }

        elif not redirect_to_name:
            return {
                "user": current_user,
                "logged_in": False,
                "login_url": users.create_login_url('/'),
            }

        else:
            self.redirect_to(redirect_to_name)

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        context = self.get_common_context()
        current_user = context["user"]
        if current_user:
            user_db = User.get_by_user(current_user)
            if not user_db:
                new_user_db = User(user_id=current_user.user_id(), nickname=current_user.nickname())
                new_user_db.put()

        return self.render_template("main.html", params=context)


class NewMessageHandler(BaseHandler):
    def get(self):
        context = self.get_common_context("main-url")
        context["receivers"] = User.query().fetch()

        return self.render_template("new-message.html", params=context)

    def post(self):
        context = self.get_common_context("main-url")
        current_user = context["user"]

        subject = unicode(self.request.get("subject"))
        to = self.request.get("to")
        content = unicode(self.request.get("content"))
        important = self.request.get("important")

        if to and content:
            new_message = Message(
                subject=subject,
                body=content,
                sender=current_user.user_id(),
                receiver=to,
                important=bool(important),
            )
            new_message.put()

            context["success_message"] = "Message sent successfully"

        else:
            context["error_message"] = "Please fill all required inputs"
            context["receivers"] = User.query().fetch()
            context["subject"] = subject
            context["to"] = to
            context["content"] = content
            context["important"] = important

        return self.render_template("new-message.html", params=context)


class InboxHandler(BaseHandler):
    def get(self):
        context = self.get_common_context("main-url")

        current_user = context["user"]
        context["messages"] = Message.query(Message.receiver == current_user.user_id()).fetch()

        return self.render_template("inbox.html", params=context)


class SentHandler(BaseHandler):
    def get(self):
        context = self.get_common_context("main-url")

        current_user = context["user"]
        context["messages"] = Message.query(Message.sender == current_user.user_id()).fetch()

        return self.render_template("sent.html", params=context)


class WeatherHandler(BaseHandler):
    def get(self):
        context = self.get_common_context("main-url")

        location = self.request.get("location")

        if not location:
            location = "Malaga,es"

        context["weather"] = get_weather_info(location)

        return self.render_template("weather.html", params=context)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main-url"),
    webapp2.Route('/new-message', NewMessageHandler, name="new-message-url"),
    webapp2.Route('/inbox', InboxHandler, name="inbox-url"),
    webapp2.Route('/sent', SentHandler, name="sent-url"),
    webapp2.Route('/weather', WeatherHandler, name="weather-url"),
], debug=True)
