#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gtk, gobject, pango

class TaskGroup(gtk.VBox):
   def __init__(self, name, style):
      super(gtk.VBox, self).__init__()
      self.model = gtk.ListStore(gobject.TYPE_STRING)
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

      cell = gtk.CellRendererText()
      column = gtk.TreeViewColumn("Tasks", cell, text=0)
      self.tree_view.append_column(column)

      self.tree_view.show()
      self.ebox.show()
      self.show()

   def add(self, text):
      self.label.show()
      self.model.set(self.model.append(), 0, text)

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

      entry = self.entry = gtk.Entry()
      entry.connect('changed', self.entry_changed)
      entry.connect('activate', self.entry_done)
      entry.set_width_chars(25)
      entry.show()

      combo = self.combo = gtk.combo_box_new_text()
      self.add_category('All')
      self.add_category('Work')
      self.add_category('Home')
      combo.set_active(0)
      combo.show()

      item_new = self.item_new = gtk.MenuItem('New Category...')
      item_new.connect('activate', self.new_category_add)
      item_new.show()
      menu.add(item_new)

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

      box2.pack_start(combo, False, False)
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

   def new_category_add(self, widget):
      name = 'UNIMPLEMENTED'
      if name:
         self.menu.remove(self.item_new)
         self.add_category(name)
         self.menu.add(self.item_new)
         self.entry_done(widget, name)

   def add_category(self, name):
      self.combo.append_text(name)
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
      else:
         self.abutton.set_sensitive(False)

   def entry_done(self, widget, data=None):
      if not data:
         data = self.get_active_text(self.combo)
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
