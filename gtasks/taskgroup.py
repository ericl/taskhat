import gtk
import gobject
import pango

from task import Task

def togformatter(column, renderer, model, iter):
   task = model.get_value(iter, 0)
   renderer.set_property('active', task.removed)

def dateformatter(column, renderer, model, iter):
   task = model.get_value(iter, 0)
   renderer.set_property('markup', task.pretty_date())
   renderer.set_property('xalign', 0.5)
   renderer.set_property('alignment', pango.ALIGN_CENTER)

def prioformatter(column, renderer, model, iter):
   task = model.get_value(iter, 0)
   renderer.set_property('text', task.prio.symbol())
   renderer.set_property('xalign', 0.5)
   renderer.set_property('alignment', pango.ALIGN_CENTER)

def taskformatter(column, renderer, model, iter):
   task = model.get_value(iter, 0)
   if task.removed:
      renderer.set_property('markup', '<span strikethrough="true">%s</span>' % task.text)
   else:
      renderer.set_property('text', task.text)


class TaskGroup(gtk.VBox):
   def __init__(self, name, realizedparent, persist):
      super(gtk.VBox, self).__init__()
      self.persist = persist
      self.model = gtk.ListStore(gobject.TYPE_PYOBJECT)
      self.tree_view = gtk.TreeView(self.model)
      self.ebox = gtk.EventBox()
      self.label = gtk.Label(name)
      self.realizedparent = realizedparent

      self.ebox.add(self.label)

      self.label.modify_font(pango.FontDescription('Sans Bold 15'))
      self.label.set_alignment(0,0)
      self.label.set_padding(3,3)
      self.pack_start(self.ebox, False, False)
      self.pack_start(self.tree_view, False, False)
      self.tree_view.set_headers_visible(False)

      cells = gtk.CellRendererText()
      cell0 = gtk.CellRendererToggle()
      cell0.connect('toggled', self.destroy_task)
      cell4 = gtk.CellRendererPixbuf()
      checkbox = gtk.TreeViewColumn('Done')
      checkbox.pack_start(cells, True)
      checkbox.pack_end(cell0, False)
      checkbox.set_min_width(45)
      checkbox.set_cell_data_func(cell0, togformatter)

      column = gtk.TreeViewColumn('Tasks')
      renderer = gtk.CellRendererText()
      renderer.set_property('editable', True)
      column.pack_start(renderer, True)
      column.set_expand(True)
      column.set_cell_data_func(renderer, taskformatter)

      renderer = gtk.CellRendererCombo()
      renderer.set_property('editable', True)
      renderer.set_property('has_entry', False)
      prio_store = gtk.ListStore(gobject.TYPE_STRING)
      prio_store.set(prio_store.append(), 0, str(Task.PRIORITY_ADMIN))
      prio_store.set(prio_store.append(), 0, str(Task.PRIORITY_HIGH))
      prio_store.set(prio_store.append(), 0, str(Task.PRIORITY_MEDIUM))
      prio_store.set(prio_store.append(), 0, str(Task.PRIORITY_LOW))
      renderer.set_property('model', prio_store)
      prio = gtk.TreeViewColumn("Type")
      prio.pack_start(renderer, True)
      prio.set_cell_data_func(renderer, prioformatter)

      renderer = gtk.CellRendererCombo()
      renderer.set_property('editable', True)
      renderer.set_property('has_entry', False)
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
      dates = gtk.TreeViewColumn("Dates")
      dates.pack_start(renderer, True)
      dates.set_cell_data_func(renderer, dateformatter)

      notes = gtk.TreeViewColumn("Notes", cell4)
      notes.pack_end(cells, True)
      notes.set_min_width(40)

      self.tree_view.append_column(checkbox)
      self.tree_view.append_column(prio)
      self.tree_view.append_column(column)
      self.tree_view.append_column(dates)
      self.tree_view.append_column(notes)
      self.tree_view.set_hover_selection(True)

      self.tree_view.show()
      self.ebox.show()
      self.pull_styles_from_window()
      self.show()

   def pull_styles_from_window(self):
      style = self.realizedparent.get_style()
      self.ebox.modify_bg(gtk.STATE_NORMAL, style.base[gtk.STATE_NORMAL])
      self.label.modify_fg(gtk.STATE_NORMAL, style.bg[gtk.STATE_SELECTED])

   def add(self, task):
      self.label.show()
      self.model.set(self.model.append(), 0, task)

   def destroy_task(self, widget, index):
      task = self.model.get_value(self.model.iter_nth_child(None, int(index)), 0)
      task.removed = not task.removed
      if task.removed:
         self.persist.destroy(task)
      else:
         self.persist.save(task)

