from flask import current_app, Blueprint, render_template, abort, request, redirect, url_for, flash, Response 
from flask.ext.login import login_user, logout_user, current_user, login_required
import simplejson as json
import os 
from time import time, localtime, strftime
from uuid import uuid4 


from spike.views import role_required
from spike import seeds 
from spike.model import *

settings = Blueprint('settings', __name__, url_prefix = '/settings')

@settings.route("/")
def index():
  settings = Settings.query.order_by(Settings.name).all()
  if not settings:
    return(redirect("/rules"))
  return(render_template("settings/index.html", settings = settings))

@settings.route("/mz")
def mz_index():
  mz = ValueTemplates.query.filter(ValueTemplates.name == "naxsi_mz").order_by(ValueTemplates.value).all()
  if not mz:
    return(redirect("/settings"))
  return(render_template("settings/mz.html", mz = mz))

@settings.route("/mz/del", methods = ["POST"])
def mz_del():
  nd = request.form
  mzid = nd["mzid"]


  dmz = ValueTemplates.query.filter(ValueTemplates.id == mzid).first()
  if not dmz:
    flash("Nothing found in %s " % (mzid), "error")
    return(redirect("/settings/mz"))
  
  db.session.delete(dmz)
  try:
    db.session.commit()
    flash("OK: deleted %s " % (dmz.value), "success")
  except:
    flash("ERROR while trying to delete : %s" % (dmz.value ), "error")
  return(redirect("/settings/mz"))

@settings.route("/mz/new", methods = ["POST"])
def mz_new():
  nd = request.form
  nmz = nd["nmz"]
  mz = ValueTemplates("naxsi_mz", nmz)
  db.session.add(mz)
  db.session.commit()
  flash("Updated MZ: %s" % nmz, "success")  
  return(redirect("/settings/mz"))

@settings.route("/scores")
def score_index():
  sc = ValueTemplates.query.filter(ValueTemplates.name == "naxsi_score").order_by(ValueTemplates.value).all()
  if not sc:
    return(redirect("/settings"))
  return(render_template("settings/scores.html", scores = sc))

@settings.route("/scores/new", methods = ["POST"])
def score_new():
  nd = request.form
  nsc = nd["nscore"]
  if nsc[0] != "$":
    nsc = "$%s" % nsc
  sc = ValueTemplates("naxsi_score", nsc.upper())
  db.session.add(sc)
  db.session.commit()
  flash("Updated Score: %s" % nsc, "success")  
  return(redirect("/settings/scores"))

@settings.route("/scores/del", methods = ["POST"])
def scores_del():
  nd = request.form
  scid = nd["scid"]
  dsc = ValueTemplates.query.filter(ValueTemplates.id == scid).first()
  if not dsc:
    flash("Nothing found in %s " % (scid), "error")
    return(redirect("/settings/scores"))  
  db.session.delete(dsc)
  try:
    db.session.commit()
    flash("OK: deleted %s " % (dsc.value), "success")
  except:
    flash("ERROR while trying to delete : %s" % (dsc.value ), "error")
  return(redirect("/settings/scores"))

@settings.route("/update")
def mz_update():
  out = "".join(os.popen("./server update"))
  flash("OK: update " , "success")
  
  return(render_template("layouts/pre.html", text = out, title="Spike-Update"))
  

@settings.route("/save", methods = ["POST"])
def save_settings():
  
  sform = request.form
  for s in sform:
    sfind = Settings.query.filter(Settings.name == s).first()
    if not sfind:
      print "> no value for %s" % sfind
      continue
    if sfind.value != sform[s]:
      sfind.value = sform[s]
      db.session.add(sfind)
      flash("Updated setting: %s" % s, "success")
  db.session.commit()
  os.system("touch spike/__init__.py")
  return(redirect("/settings"))
  

@settings.route("/<path:szone>")
def szone(szone=0):
  return(render_template("notyet.html", text = ""))
