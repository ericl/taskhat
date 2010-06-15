#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gtk

from task import Task, TaskDate
from persist import Persist
from taskgroup import TaskGroup
from parse import derive_label

DBUS_OK = True

try:
   import dbus
   import dbus.service
   import dbus.mainloop.glib

   dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
   sessionbus = dbus.SessionBus()

   class TaskhatDBusPresence(dbus.service.Object):
      def __init__(self, app):
         dbus.service.Object.__init__(self, sessionbus, '/Taskhat')
         self.dbus_name = dbus.service.BusName('org.riclian.Taskhat', sessionbus)
         self.app = app

      @dbus.service.method('org.riclian.TaskhatInterface',
         in_signature = '', out_signature = '')
      def Present(self):
         print 'handled dbus "Present" call'
         self.app.window.present()

except ImportError:
   DBUS_OK = False
   print 'Warning: No dbus support'

def run_app():
   if DBUS_OK:
      try:
         sessionbus.get_object('org.riclian.Taskhat', '/Taskhat').Present()
      except Exception, e:
         if 'ServiceUnknown' in str(e):
            Taskhat().main()
         else:
            print e
   else:
      Taskhat().main()

class Taskhat:

   HELP_STRING = ' Enter a new task:'

   def __init__(self):
      if DBUS_OK:
         self.dbus_presence = TaskhatDBusPresence(self)

      self.persist = Persist('Default')
      self.window = gtk.Window()
      self.window.connect('destroy', self.destroy)
      self.window.set_title('Taskhat')
      self.window.set_icon_name('stock_notes')
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

      TaskGroup("Undated", self.window, self.persist, (None, -TaskDate.FUTURE), True)
      TaskGroup("Overdue", self.window, self.persist, (-TaskDate.FUTURE, -1))
      TaskGroup("Today", self.window, self.persist, (0, 0))
      TaskGroup("Tomorrow", self.window, self.persist, (1, 1))
      TaskGroup("Next 7 Days", self.window, self.persist, (2, 7))
      TaskGroup("Future", self.window, self.persist, (8, None))
      for group in TaskGroup.groups:
         box3.pack_start(group, False, False)

      ebox3.modify_bg(gtk.STATE_NORMAL, self.window.get_style().base[gtk.STATE_NORMAL])

      status = self.status = gtk.Label(Taskhat.HELP_STRING)
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

      TaskGroup.origin = scrolled_window

      self.persist.restore(self.insert_task)
      self.persist.restore_geometry(self.window)
      self.window.show()
      entry.grab_focus()
      self.window.connect('notify::style', self.update_group_styles)

      def save_geom(*args):
         self.persist.save_geometry(self.window.get_position(), self.window.get_size())

      self.window.connect('notify::is-active', save_geom)

   def update_group_styles(self, args, x):
      self.ebox3.modify_bg(gtk.STATE_NORMAL, self.window.get_style().base[gtk.STATE_NORMAL])

   def validate_entry_text(self, contents):
      return contents.strip()

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
         self.status.set_label(Taskhat.HELP_STRING)

   def insert_task(self, task):
      TaskGroup.groups[0].smart_assign(task)

   def entry_done(self, widget, data=None):
      res = derive_label(self.validate_entry_text(self.entry.get_text()))
      text = res[1]
      if not text:
         text = '<?>'
      task = Task(text, res[2], res[3])
      self.insert_task(task)
      self.persist.save(task)
      self.entry.set_text('')

   def main(self):
      try:
         from ctypes import cdll
         cdll.LoadLibrary('libc.so.6').prctl(15, 'taskhat', 0, 0, 0)
      except:
         pass
      gtk.main()
  
   def destroy(self, widget):
      gtk.main_quit()

# vim: et sw=3
