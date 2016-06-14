#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Opravilo

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("index.html")


class RezultatHandler(BaseHandler):
    def post(self):
        rezultat = self.request.get("vnos")
        opravilo = Opravilo(vnos=rezultat)
        opravilo.put()
        self.render("rezultat.html")
        return self.write(rezultat)
#        return self.write(rezultat)
#        return self.render("rezultat.html")


class SeznamOpravilHandler(BaseHandler):
    def get(self):
        seznam = Opravilo.query(Opravilo.izbrisan == False).order(Opravilo.vnos).fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam_opravil.html", params=params)


class PosameznoOpraviloHandler(BaseHandler):
    def get(self, opravilo_id):
        opravilo = Opravilo.get_by_id(int(opravilo_id))
        params = {"opravilo": opravilo}
        return self.render_template("posamezno_opravilo.html", params=params)


class UrediOpraviloHandler(BaseHandler):
    def get(self, opravilo_id):
        opravilo = Opravilo.get_by_id(int(opravilo_id))
        params = {"opravilo": opravilo}
        return self.render_template("uredi_opravilo.html", params=params)

    def post(self, opravilo_id):
        vnos = self.request.get("vnos")
        opravilo = Opravilo.get_by_id(int(opravilo_id))
        opravilo.vnos = vnos
        opravilo.put()
        return self.redirect_to("seznam-opravil")


class IzbrisiOpraviloHandler(BaseHandler):
    def get(self, opravilo_id):
        opravilo = Opravilo.get_by_id(int(opravilo_id))
        params = {"opravilo": opravilo}
        return self.render_template("izbrisi_opravilo.html", params=params)

    def post(self, opravilo_id):
        opravilo = Opravilo.get_by_id(int(opravilo_id))
        opravilo.izbrisan = True
        opravilo.put()
        return self.redirect_to("seznam-opravil")


class SeznamIzbrisanihOpravilHandler(BaseHandler):
    def get(self):
        seznam = Opravilo.query(Opravilo.izbrisan == True).order(Opravilo.vnos).fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam_izbrisanih_opravil.html", params=params)


class PonovnoIzpisiOpraviloHandler(BaseHandler):
    def get(self, opravilo_id):
        opravilo = Opravilo.get_by_id(int(opravilo_id))
        params = {"opravilo": opravilo}
        return self.render_template("restore.html", params=params)

    def post(self, opravilo_id):
        opravilo = Opravilo.get_by_id(int(opravilo_id))
        opravilo.izbrisan = False
        opravilo.put()
        return self.redirect_to("seznam-opravil")



app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam-opravil', SeznamOpravilHandler, name="seznam-opravil"),
    webapp2.Route('/opravilo/<opravilo_id:\d+>', PosameznoOpraviloHandler),
    webapp2.Route('/opravilo/<opravilo_id:\d+>/uredi', UrediOpraviloHandler),
    webapp2.Route('/opravilo/<opravilo_id:\d+>/izbrisi', IzbrisiOpraviloHandler),
    webapp2.Route('/opravilo/<opravilo_id:\d+>/restore', PonovnoIzpisiOpraviloHandler),
    webapp2.Route('/seznam-izbrisanih-opravil', SeznamIzbrisanihOpravilHandler),
], debug=True)