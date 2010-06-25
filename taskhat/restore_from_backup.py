import gtk

class RestoreFromBackup:
   def __init__(self, window, persist, taskhat):
      self.persist = persist
      self.window = window
      self.taskhat = taskhat

      dialog = self.dialog = gtk.Dialog(parent=window)
      dialog.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
      dialog.set_title("Revert Changes")
      dialog.set_modal(True)

      label = gtk.Label("Restore task data from ")
      spin = gtk.combo_box_new_text()
      spin.append_text("last sync")
      spin.append_text("1 day ago")
      spin.append_text("2 days ago")
      spin.append_text("3 days ago")
      spin.append_text("4 days ago")
      spin.append_text("5 days ago")
      spin.append_text("6 days ago")
      spin.connect('changed', self.change_select)
      label.show()
      spin.show()

      hbox = gtk.HBox()
      img = gtk.Image()
      img.set_from_stock(gtk.STOCK_REVERT_TO_SAVED, gtk.ICON_SIZE_DIALOG)
      img.show()
      img.set_padding(5, 5)
      frame = gtk.Frame()
      frame.set_shadow_type(gtk.SHADOW_NONE)
      frame.set_border_width(5)
      frame.show()
      frame.add(hbox)
      hbox.pack_start(img)
      hbox.pack_start(label)
      hbox.pack_start(spin, False, False)
      hbox.show()
      dialog.vbox.pack_start(frame)

      cbutton = gtk.Button(stock=gtk.STOCK_CANCEL)
      cbutton.grab_focus()
      def cancel(*args):
         self.persist.restore(self.taskhat.insert_task, self.taskhat.update_events,
            f_clear=self.taskhat.clear_all)
         dialog.destroy()
      cbutton.connect('clicked', cancel)
      cbutton.show()
      dialog.action_area.pack_end(cbutton)

      button = self.sbutton = gtk.Button('Sync')
      def sync_changes(*args):
         self.persist.sync()
         dialog.destroy()
      button.connect('clicked', sync_changes)
      button.set_sensitive(False)
      button.show()
      cbutton.grab_focus()
      dialog.action_area.pack_end(button)

   def change_select(self, widget):
      days_ago = widget.get_active()
      self.persist.restore(self.taskhat.insert_task, self.taskhat.update_events,
         days_ago, self.taskhat.clear_all)
      self.sbutton.set_sensitive(True)

   def run(self):
      self.dialog.show()

# vim: et sw=3
