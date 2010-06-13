#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gtk
import gobject
import pango

from datetime import datetime

def dateformatter(column, renderer, model, iter):
   pyobj = model.get_value(iter, 4)
   renderer.set_property('text', str(pyobj).split()[0])

class TaskGroup(gtk.VBox):
   def __init__(self, name, style):
      super(gtk.VBox, self).__init__()
      self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
      self.tree_view = gtk.TreeView(self.model)
      self.ebox = gtk.EventBox()
      self.label = gtk.Label(name)

      self.ebox.add(self.label)
      # TODO proper styling that changes with gconf changes
      self.ebox.modify_bg(gtk.STATE_NORMAL, style.base[gtk.STATE_NORMAL])
      self.label.modify_fg(gtk.STATE_NORMAL, style.bg[gtk.STATE_SELECTED])
      self.label.modify_font(pango.FontDescription('Sans Bold 15'))
      self.label.set_alignment(0,0)
      self.label.set_padding(3,3)
      self.pack_start(self.ebox, False, False)
      self.pack_start(self.tree_view, False, False)
      self.tree_view.set_headers_visible(False)

      cells = gtk.CellRendererText()
      cell0 = gtk.CellRendererToggle()
      cell1 = gtk.CellRendererText()
      cell2 = gtk.CellRendererText()
      cell4 = gtk.CellRendererPixbuf()
      checkbox = gtk.TreeViewColumn("Done")
      checkbox.pack_start(cells, True)
      checkbox.pack_end(cell0, False)
      checkbox.set_min_width(45)
      checkbox.add_attribute(cell0, 'active', 2)
      prio = gtk.TreeViewColumn("Type", cell1, text=1)
      column = gtk.TreeViewColumn("Tasks", cell2, text=0)
      column.set_expand(True)

      renderer = gtk.CellRendererCombo()
      renderer.set_property('editable', True)
      renderer.set_property('has_entry', True)
      due_date_store = gtk.ListStore(gobject.TYPE_STRING)
      due_date_store.set(due_date_store.append(), 0, "6/13 - Today")
      due_date_store.set(due_date_store.append(), 0, "6/14 - Tomorrow")
      due_date_store.set(due_date_store.append(), 0, "6/15 - Tue")
      due_date_store.set(due_date_store.append(), 0, "6/16 - Wed")
      due_date_store.set(due_date_store.append(), 0, "6/17 - Thu")
      due_date_store.set(due_date_store.append(), 0, "6/18 - Fri")
      due_date_store.set(due_date_store.append(), 0, "6/19 - Tue")
      due_date_store.set(due_date_store.append(), 0, "6/20 - Next Week")
      due_date_store.set(due_date_store.append(), 0, "No Date")
      due_date_store.set(due_date_store.append(), 0, "Choose Date...")
      renderer.set_property('model', due_date_store)
      renderer.set_property('text_column', 0)
      dates = gtk.TreeViewColumn("Dates")
      dates.pack_start(renderer, True)
      dates.set_cell_data_func(renderer, dateformatter)

      notes = gtk.TreeViewColumn("Notes", cell4)
      self.tree_view.append_column(checkbox)
      self.tree_view.append_column(prio)
      self.tree_view.append_column(column)
      self.tree_view.append_column(dates)
      self.tree_view.append_column(notes)

      self.tree_view.show()
      self.ebox.show()
      self.show()

   def add(self, text):
      self.label.show()
      self.model.set(self.model.append(), 0, text, 1, '  -  ', 3, '    ', 4, datetime.today())

class GTasks:
   def __init__(self):
      self.window = gtk.Window()
      self.window.connect('destroy', self.destroy)
      self.window.set_title('GTasks')
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

      abutton = self.abutton = gtk.MenuToolButton(abox, "Add")
      menu = self.menu = gtk.Menu()
      abutton.set_menu(menu)
      abutton.set_sensitive(False)
      abutton.connect('clicked', self.entry_done)
      abutton.show()

      self.add_category('Work')
      self.add_category('Home')

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
      ebox3 = gtk.EventBox()
      ebox3.add(box3)
      ebox3.show()
      scrolled_window.add_with_viewport(ebox3)

      today = TaskGroup("Today", self.window.get_style())
      tomorrow = TaskGroup("Tomorrow", self.window.get_style())
      future = TaskGroup("Future", self.window.get_style())
      self.groups = [today, tomorrow, future]
      for group in self.groups:
         box3.pack_start(group, False, False)

      ebox3.modify_bg(gtk.STATE_NORMAL, self.window.get_style().base[gtk.STATE_NORMAL])

      status = self.status = gtk.Label(' --')
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
      self.window.show()
      entry.grab_focus()

   def add_category(self, name):
      item = gtk.MenuItem(name)
      item.show()
      item.connect('activate', self.entry_done, name)
      self.menu.add(item)

   def validate_entry_text(self, contents):
      return contents.strip()

   i = 0
   def group_of_entry(self, entry):
      self.i += 1
      return self.groups[self.i % len(self.groups)]

   def get_active_text(self, combobox):
      model = combobox.get_model()
      active = combobox.get_active()
      if active < 0:
         return None
      return model[active][0]

   def entry_changed(self, widget, data=None):
      if self.validate_entry_text(widget.get_text()):
         self.abutton.set_sensitive(True)
         self.status.set_label(" New <type>[ due <date>]")
      else:
         self.abutton.set_sensitive(False)
         self.status.set_label(" --")

   def entry_done(self, widget, data=None):
      if not data:
         data = 'All'
      text = self.validate_entry_text(self.entry.get_text())
      if text:
         self.group_of_entry(text).add('%s: %s' % (data, text))
         self.entry.set_text('')

   def main(self):
      gtk.main()
  
   def destroy(self, widget):
      gtk.main_quit()

if __name__ == '__main__':
   gtasks = GTasks()
   gtasks.main()

# vim: sw=3
