#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gtk

from task import Task, TaskDate
from persist import Persist
from taskgroup import TaskGroup

from datetime import datetime

HELP_STRING = ' Enter a new task:'

def calc_offset(weekday):
   return weekday - datetime.today().weekday()

def parse_date(text):
   x = None
   out = '<?>'
   off = None
   try:
      x = text.split()[-1]
   except:
      return '<?>', text, off
   x = x.lower()
   found = True
   if x.startswith('mon'):
      out = 'Monday'
      off = calc_offset(0)
   elif x.startswith('tue'):
      out = 'Tuesday'
      off = calc_offset(1)
   elif x.startswith('wed'):
      out = 'Wednesday'
      off = calc_offset(2)
   elif x.startswith('thu'):
      out = 'Thursday'
      off = calc_offset(3)
   elif x.startswith('fri'):
      out = 'Friday'
      off = calc_offset(4)
   elif x.startswith('sat'):
      out = 'Saturday'
      off = calc_offset(5)
   elif x.startswith('sun'):
      out = 'Sunday'
      off = calc_offset(6)
   elif x.startswith('tod') or x == 'now':
      out = 'today'
      off = 0
   elif x.startswith('tom'):
      out = 'tomorrow'
      off = 1
   elif x.startswith('nex'):
      out = 'next week'
      off = 7
   else:
      found = False
   if found:
      text = ' '.join(text.split()[:-1])
   return out, text, off

def derive_label(text):
   ttype = '<?>'
   parse = False
   verb = 'due'
   prio = Task.PRIORITY_LOW
   if text.endswith('!'):
      ttype = 'Important task'
      prio = Task.PRIORITY_HIGH
   elif text.endswith('='):
      ttype = 'Regular task'
      prio = Task.PRIORITY_MEDIUM
   elif text.endswith('-'):
      ttype = 'Idle task'
      prio = Task.PRIORITY_LOW
   elif text.endswith('*'):
      ttype = 'Administrivia'
      prio = Task.PRIORITY_ADMIN
   else:
      parse = True
   if parse:
      text = ' ' + text + ' '
      if ' hw ' in text or ' homework ' in text:
         ttype = 'Homework'
         prio = Task.PRIORITY_MEDIUM
      if ' proj' in text:
         ttype = 'Project'
         prio = Task.PRIORITY_HIGH
      if ' read ' in text:
         ttype = 'Reading'
         prio = Task.PRIORITY_LOW
      if ' final ' in text or ' midterm ' in text or ' study ' in text or ' exam ' in text:
         ttype = 'Exam'
         verb = 'on'
         prio = Task.PRIORITY_HIGH
      if ' quiz ' in text:
         ttype = 'Quiz'
         verb = 'on'
         prio = Task.PRIORITY_MEDIUM
      if ' turn in ' in text:
         ttype = 'Administrivia'
         prio = Task.PRIORITY_ADMIN
   else:
      text = text[:-1]
   date, text, off = parse_date(text)
   return (" %s %s %s" % (ttype, verb, date)), text.strip(), TaskDate(off), prio

class Taskhat:
   def __init__(self):
      self.persist = Persist('Default')
      self.window = gtk.Window()
      self.window.connect('destroy', self.destroy)
      self.window.set_title('Taskhat')
      self.window.set_icon_name('stock_task')
      self.window.realize()

      box1 = gtk.VBox()
      box2 = gtk.HBox()
      box2.set_border_width(4)

      abox = gtk.HBox()
      image = gtk.Image()
      image.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
      label = gtk.Label("Add")
      abox.pack_start(image, False, False, 0)
      abox.pack_start(label, False, False, 0)
      abox.show()
      image.show()
      label.show()

      abutton = self.abutton = gtk.ToolButton(abox, "Add")
      abutton.set_sensitive(False)
      abutton.connect('clicked', self.entry_done)
      abutton.show()

      entry = self.entry = gtk.Entry()
      entry.connect('changed', self.entry_changed)
      entry.connect('activate', self.entry_done)
      entry.set_width_chars(25)
      entry.show()

      scrolled_window = gtk.ScrolledWindow()
      scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
      scrolled_window.show()
      box3 = gtk.VBox()
      box3.show()
      ebox3 = self.ebox3 = gtk.EventBox()
      ebox3.add(box3)
      ebox3.show()
      scrolled_window.add_with_viewport(ebox3)

      today = TaskGroup("Today", self.window, self.persist)
      tomorrow = TaskGroup("Tomorrow", self.window, self.persist)
      future = TaskGroup("Future", self.window, self.persist)
      self.groups = [today, tomorrow, future]
      for group in self.groups:
         box3.pack_start(group, False, False)

      ebox3.modify_bg(gtk.STATE_NORMAL, self.window.get_style().base[gtk.STATE_NORMAL])

      status = self.status = gtk.Label(HELP_STRING)
      status.show()
      status.set_sensitive(False)
      box2.pack_start(status, False, False)
      box2.pack_end(abutton, False, False)
      box2.pack_end(entry, False, False)
      box1.pack_start(box2, False, False)
      box1.pack_start(scrolled_window)

      self.window.add(box1)
      self.window.set_size_request(530, 565)

      box2.show()
      box1.show()

      self.persist.restore(self.insert_task)
      self.window.show()
      entry.grab_focus()
      self.window.connect('notify::style', self.update_group_styles)

   def update_group_styles(self, args, x):
      self.ebox3.modify_bg(gtk.STATE_NORMAL, self.window.get_style().base[gtk.STATE_NORMAL])

   def validate_entry_text(self, contents):
      return contents.strip()

   def group_of_entry(self, entry):
      return self.groups[2]

   def get_active_text(self, combobox):
      model = combobox.get_model()
      active = combobox.get_active()
      if active < 0:
         return None
      return model[active][0]

   def entry_changed(self, widget, data=None):
      text = self.validate_entry_text(widget.get_text())
      if text:
         self.abutton.set_sensitive(True)
         self.status.set_label(derive_label(text)[0])
      else:
         self.abutton.set_sensitive(False)
         self.status.set_label(HELP_STRING)

   def insert_task(self, task):
      self.group_of_entry(task.text).add(task)

   def entry_done(self, widget, data=None):
      res = derive_label(self.validate_entry_text(self.entry.get_text()))
      text = res[1]
      if text:
         task = Task(text, res[2], res[3])
         self.insert_task(task)
         self.persist.save(task)
         self.entry.set_text('')

   def main(self):
      gtk.main()
  
   def destroy(self, widget):
      gtk.main_quit()

# vim: et sw=3
