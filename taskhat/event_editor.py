import gtk
import gobject
import pango

from taskgroup import escape
from event import WeeklyRecurringEvent, event_sort_func

def togformatter(column, renderer, model, iter):
   event = model.get_value(iter, 0)
   renderer.set_property('active', event.deleted)

def eventformatter(column, renderer, model, iter):
   event = model.get_value(iter, 0)
   if event.deleted:
      renderer.set_property('markup', '<span strikethrough="true">%s</span>' % escape(event.text))
   else:
      renderer.set_property('text', event.text)

def weekdayformatter(column, renderer, model, iter):
   event = model.get_value(iter, 0)
   renderer.set_property('text', event.get_datestring())

def timeformatter(column, renderer, model, iter):
   event = model.get_value(iter, 0)
   renderer.set_property('text', event.get_timestring())

class EventEditor:
   def __init__(self, window, persist, taskhat):
      self.persist = persist
      self.taskhat = taskhat

      dialog = self.dialog = gtk.Dialog(parent=window)
      dialog.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
      dialog.set_size_request(450, 300)

      model = self.model = gtk.ListStore(gobject.TYPE_PYOBJECT)
      tree_view = self.tree_view = gtk.TreeView(model)
      tree_view.show()

      self.model.set_sort_func(13, event_sort_func)
      self.model.set_sort_column_id(13, gtk.SORT_DESCENDING)

      for event in persist.events:
         if not event.deleted and event.text:
            self.model.set(self.model.append(), 0, event)

      checkbox = gtk.TreeViewColumn('')
      renderer = gtk.CellRendererToggle()
      renderer.connect('toggled', self.destroy_event)
      checkbox.pack_end(renderer, False)
      checkbox.set_cell_data_func(renderer, togformatter)
      self.tree_view.append_column(checkbox)

      column = gtk.TreeViewColumn('Event Description')
      renderer = gtk.CellRendererText()
      renderer.set_property('editable', True)
      renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
      column.pack_start(renderer, True)
      column.set_expand(True)
      column.set_min_width(200)
      column.set_cell_data_func(renderer, eventformatter)
      renderer.connect('edited', self.text_changed)
      self.tree_view.append_column(column)

      column = gtk.TreeViewColumn('MTuWThFSaSu')
      renderer = gtk.CellRendererText()
      renderer.set_property('editable', True)
      renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
      column.pack_start(renderer, True)
      column.set_expand(True)
      column.set_cell_data_func(renderer, weekdayformatter)
      renderer.connect('edited', self.weekday_changed)
      self.tree_view.append_column(column)

      column = gtk.TreeViewColumn('xx:xx[pm]')
      renderer = gtk.CellRendererText()
      renderer.set_property('editable', True)
      renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
      column.pack_start(renderer, True)
      column.set_expand(True)
      column.set_cell_data_func(renderer, timeformatter)
      renderer.connect('edited', self.time_changed)
      self.tree_view.append_column(column)

      button_new = self.button = gtk.Button('New Event')
      button_new.connect('clicked', self.new_event)
      button_new.show()
      bbox = gtk.HBox()
      bbox.show()
      bbox.pack_start(button_new, False, False)
      self.update_button_state()

      dialog.set_modal(True)
      dialog.set_title('Edit Recurring Events')
      scrolled_window = gtk.ScrolledWindow()
      scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
      scrolled_window.add_with_viewport(tree_view)
      scrolled_window.show()
      vbox = gtk.VBox()
      vbox.pack_start(scrolled_window)
      vbox.pack_end(bbox, False, False)
      vbox.show()
      frame = gtk.Frame()
      frame.set_border_width(5)
      frame.set_shadow_type(gtk.SHADOW_NONE)
      frame.show()
      frame.add(vbox)
      dialog.vbox.pack_start(frame)
      button = gtk.Button('Close')
      def dest(*args):
         dialog.destroy()
      button.connect('clicked', dest)
      button.show()
      dialog.action_area.pack_end(button)

   def text_changed(self, renderer, path, text):
      event = self.model.get_value(self.model.iter_nth_child(None, int(path)), 0)
      val = text.strip()
      if val and val != event.text:
         event.text = val
         self.taskhat.update_events()
         self.persist.sync()
         self.update_button_state()
   
   def weekday_changed(self, renderer, path, text):
      event = self.model.get_value(self.model.iter_nth_child(None, int(path)), 0)
      event.days = WeeklyRecurringEvent.parse_datestring(text)
      self.taskhat.update_events()
      self.persist.sync()

   def time_changed(self, renderer, path, text):
      miter = self.model.iter_nth_child(None, int(path))
      event = self.model.get_value(miter, 0)
      event.tdelta = WeeklyRecurringEvent.parse_timestring(text)
      self.model.remove(miter)
      self.model.set(self.model.append(), 0, event)
      self.persist.resort_events()
      self.taskhat.update_events()
      self.persist.sync()

   def update_button_state(self):
      miter = self.model.iter_nth_child(None, len(self.model)-1)
      if not miter or self.model.get_value(miter, 0).text:
         self.button.set_sensitive(True)
      else:
         self.button.set_sensitive(False)

   def new_event(self, widget):
      event = WeeklyRecurringEvent.from_text('', '', '')
      self.model.set(self.model.append(), 0, event)
      self.persist.events.append(event)
      self.persist.resort_events()
      self.update_button_state()
   
   def destroy_event(self, widget, path):
      miter = self.model.iter_nth_child(None, int(path))
      event = self.model.get_value(miter, 0)
      event.deleted = not event.deleted
      self.model.row_changed(path, miter)
      self.taskhat.update_events()
      self.persist.sync()

   def run(self):
      self.dialog.show()

# vim: et sw=3
