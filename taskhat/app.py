#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import sys
import traceback
import gtk
import pango

from task import Task
from persist import Persist
from taskgroup import TaskGroup, escape
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
         self.app.window.show()
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
      self.window.connect('delete_event', self.close)
      self.window.set_title('Taskhat')
      self.window.set_icon_name('stock_notes')
      self.window.realize()

      box1 = gtk.VBox()
      box2 = gtk.HBox()
      box2.set_border_width(4)

      abox = gtk.HBox()
      image = gtk.Image()
      image.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
      label = gtk.Label('Add')
      abox.pack_start(image, False, False, 0)
      abox.pack_start(label, False, False, 0)
      abox.show()
      image.show()
      label.show()

      abutton = self.abutton = gtk.ToolButton(abox, 'Add')
      abutton.set_sensitive(False)
      abutton.connect('clicked', self.entry_done)
      abutton.show()

      abox = gtk.HBox()
      image = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_IN)
      abox.pack_start(image, False, False, 0)
      abox.show()
      image.show()
      tool = gtk.ToolButton(abox, 'Tools')

      def NOTIMPLEMENTED(*args):
         dialog = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL)
         dialog.set_markup("NOTIMPLEMENTED")
         button = gtk.Button("Ok")
         def dest(*args):
            dialog.destroy()
         button.connect('clicked', dest)
         button.show()
         dialog.action_area.pack_end(button)
         dialog.show()

      popup_menu = gtk.Menu()

      s = 'Edit Recurring Events'
      x = gtk.MenuItem(s)
      x.connect('activate', self.rev_handler)
      x.show()
      popup_menu.append(x)

      s = 'Revert Changes'
      x = gtk.MenuItem(s)
      x.connect('activate', NOTIMPLEMENTED)
      x.show()
      popup_menu.append(x)

      x = gtk.SeparatorMenuItem()
      x.show()
      popup_menu.append(x)

      s = 'Help'
      x = gtk.MenuItem(s)
      x.connect('activate', NOTIMPLEMENTED)
      x.show()
      popup_menu.append(x)

      s = 'About'
      x = gtk.MenuItem(s)
      x.connect('activate', self.about_menu)
      x.show()
      popup_menu.append(x)

      popup_menu.attach_to_widget(tool, None)
      popup_menu.show()

      def tool_menu(widget):
         popup_menu.popup(None, None, None, 1, 0)

      tool.connect('clicked', tool_menu)

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

      TaskGroup('Today', self.window, self.persist, (None, 0), events=True)
      TaskGroup('Tomorrow', self.window, self.persist, (1, 1))
      TaskGroup('In Two Days', self.window, self.persist, (2, 2))
      TaskGroup('Next 7 Days', self.window, self.persist, (3, 7))
      TaskGroup('Future', self.window, self.persist, (8, None))
      for group in TaskGroup.groups:
         box3.pack_start(group, False, False)

      ebox3.modify_bg(gtk.STATE_NORMAL, self.window.get_style().base[gtk.STATE_NORMAL])

      status = self.status = gtk.Label(Taskhat.HELP_STRING)
      status.set_alignment(0,.5)
      status.set_ellipsize(pango.ELLIPSIZE_END)
      status.show()
      status.set_sensitive(False)
      box2.pack_start(status, True, True)
      sep = gtk.Label(' ')
      sep.show()
      box2.pack_start(sep, False, False)
      sep = gtk.VSeparator()
      sep.show()
      box2.pack_end(tool, False, False)
      box2.pack_end(sep, False, False)
      box2.pack_end(abutton, False, False)
      tool.show()
      box2.pack_end(entry, False, False)
      box1.pack_start(box2, False, False)
      box1.pack_start(scrolled_window)

      self.window.add(box1)
      self.window.set_size_request(530, 565)

      box2.show()
      box1.show()

      accelgroup = gtk.AccelGroup()
      self.window.add_accel_group(accelgroup)
      action = gtk.Action('Quit', '_Quit me!', 'Quit the Program', gtk.STOCK_QUIT)
      action.connect('activate', self.close)
      actiongroup = gtk.ActionGroup('BasicAction')
      actiongroup.add_action_with_accel(action, None)
      action.set_accel_group(accelgroup)
      menubar = gtk.MenuBar()
      menuitem = action.create_menu_item()
      menubar.append(menuitem)
      box1.pack_start(menubar, False)

      TaskGroup.origin = scrolled_window

      self.persist.restore(self.insert_task, self.update_events)
      self.persist.restore_geometry(self.window)
      self.window.show()
      entry.grab_focus()
      self.window.connect('notify::style', self.update_group_styles)
      self.window.connect('notify::is-active', self.save_geom)

   def save_geom(self, *args):
      self.persist.save_geometry(self.window.get_position(), self.window.get_size())

   def update_events(self):
      for g in TaskGroup.groups:
         g.update()

   def rev_handler(self, *args):
      dialog = gtk.Dialog(parent=self.window)
      dialog.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
      s = gtk.Label()
      s.set_padding(20,20)
      s.set_text('\n'.join(map(str, self.persist.events)))
      s.show()
      dialog.set_modal(True)
      dialog.vbox.pack_start(s)
      button = gtk.Button("Ok")
      def dest(*args):
         dialog.destroy()
      button.connect('clicked', dest)
      button.show()
      dialog.action_area.pack_end(button)
      dialog.show()

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

   def close(self, widget, data=None):
      gtk.main_quit()

   def about_menu(self, *args):
      dialog = gtk.AboutDialog()
      dialog.set_name('Taskhat')
      dialog.set_version('0.2')
      dialog.set_comments('Taskhat is optimized for the workflow of the typical university student.')
      dialog.set_copyright('Copyright Eric Liang (2010)')
      dialog.run()
      dialog.hide()

   def main(self):
      try:
         from ctypes import cdll
         cdll.LoadLibrary('libc.so.6').prctl(15, 'taskhat', 0, 0, 0)
      except:
         pass
      def handler(e_type, e_value, e_trace):
         sys.excepthook = sys.__excepthook__
         msg = str(e_value) + '\n'
         msg += '\n'.join(traceback.format_tb(e_trace))
         msg += '\n' + 'Further exceptions will not be shown.'
         dialog = gtk.MessageDialog(parent=self.window, buttons=gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR)
         dialog.set_title(str(e_type))
         dialog.set_markup(escape(msg))
         dialog.run()
         dialog.hide()
      sys.excepthook = handler
      gtk.main()

# vim: et sw=3
