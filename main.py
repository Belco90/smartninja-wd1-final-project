#!/usr/bin/env python
import os
import jinja2
import webapp2
from google.appengine.api import users
from models import Message

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


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

        return self.render_template("main.html", params=context)


class NewMessageHandler(BaseHandler):
    def get(self):
        context = self.get_common_context("main-url")

        return self.render_template("new-message.html", params=context)

    def post(self):
        context = self.get_common_context("main-url")

        subject = self.request.get("subject")
        to = self.request.get("to")
        content = self.request.get("content")
        important = self.request.get("important")

        if to and content:
            new_message = Message(
                subject=subject,
                body=content,
                sender=context["user"].user_id(),
                receiver=to,
                important=bool(important),
            )
            new_message.put()

            context["success_message"] = "Message sent successfully"

        else:
            context["error_message"] = "Please fill all required inputs"
            context["subject"] = subject
            context["to"] = to
            context["content"] = content
            context["important"] = important

        return self.render_template("new-message.html", params=context)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main-url"),
    webapp2.Route('/new-message', NewMessageHandler, name="new-message-url"),
], debug=True)
