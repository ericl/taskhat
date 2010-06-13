#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gtk
import gobject

class GTasks:
   def __init__(self):
      self.window = gtk.Window()
      self.window.connect('destroy', self.destroy)
      self.window.set_title('GTasks')
      self.window.set_icon_name('stock_task')

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
      abutton.set_sensitive(False)
      abutton.connect('clicked', self.entry_done)
      abutton.show()

      entry = self.entry = gtk.Entry()
      entry.connect('changed', self.entry_changed)
      entry.connect('activate', self.entry_done)
      entry.set_width_chars(25)
      entry.show()

      combo = gtk.ComboBox()
      renderer = gtk.CellRendererText()
      combo.pack_start(renderer, True)
      combo.show()

      scrolled_window = gtk.ScrolledWindow()
      scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
      model = self.model = gtk.ListStore(gobject.TYPE_STRING)
      tree_view = gtk.TreeView(model)
      scrolled_window.add_with_viewport(tree_view)
      tree_view.set_headers_visible(False)
      tree_view.show()
      scrolled_window.show()
      cell = gtk.CellRendererText()

      column = gtk.TreeViewColumn("Tasks", cell, text=0)
      tree_view.append_column(column)

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

   def entry_changed(self, widget, data=None):
      if widget.get_text():
         self.abutton.set_sensitive(True)
      else:
         self.abutton.set_sensitive(False)

   def entry_done(self, widget, data=None):
      iter = self.model.append()
      self.model.set(iter, 0, self.entry.get_text())
      self.entry.set_text('')

   def main(self):
      gtk.main()
  
   def destroy(self, widget):
      gtk.main_quit()

if __name__ == '__main__':
   gtasks = GTasks()
   gtasks.main()

# vim: sw=3
