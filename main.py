#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, jinja2, cgi, os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPosts(db.Model):
    title = db.StringProperty(required = True)
    post_content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Index(Handler):
    def get (self):
        page = """<center> <a href="/blog"> Build-a-blog by Mary </a></center>"""
        self.response.write(page)

class PostIndex(Handler):

    def render_index(self, title="", post_content=""):
        posts = db.GqlQuery("SELECT * FROM BlogPosts ORDER BY created DESC LIMIT 5")
        self.render("index.html", title=title, post_content=post_content, posts=posts)
    def get(self):
        self.render_index()

class NewPost(Handler):
    def write_form(self, title="", post_content="", error=""):
        self.render("newpost.html", title=title, post_content=post_content, error=error)

    def get(self):
        self.write_form()

    def post(self):
        title = self.request.get("title")
        post_content = self.request.get("post_content")

        if title and post_content:
            post = BlogPosts(title=title, post_content=post_content)
            post.put()
            d=int(post.key().id())
            ###self.redirect("/blog/"+ str(post.key().id()))
            self.redirect("/blog/%s" % d)
        else:
            error = "Please make sure to title and create your new entry!"
            self.write_form(title, post_content, error)

class PublishedPost(Handler):
    def get(self, id):
        int_id=int(id)
        post = BlogPosts.get_by_id(int_id)
        ###self.response.out.write(id)
        self.render('post.html', post=post)

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', PostIndex),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', PublishedPost)

###    ("/published", PublishedPost)

], debug=True)
