import gtk
import gobject
import pango

from time import make_time, now

from task import Task, TaskDate

SPACER = '<span size="900">\n\n</span>'
SPACER_NO_NEWLINE = '<span size="000">\n </span>'

def escape(s):
   return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# no blending when A=1, B=0
def blend(a, b, A=0.90, B=0.10):
   return gtk.gdk.Color(int(A*a.red + B*b.red), int(A*a.green + B*b.green), int(A*a.blue + B*b.blue))

def togformatter(column, renderer, model, iter):
   task = model.get_value(iter, 0)
   renderer.set_property('active', task.removed)

def dateformatter(column, renderer, model, iter):
   task = model.get_value(iter, 0)
   renderer.set_property('markup', task.date.markup())

def prefixformatter(column, renderer, model, iter):
   task = model.get_value(iter, 0)
   renderer.set_property('text', task.prefix)

def prioformatter(column, renderer, model, iter):
   task = model.get_value(iter, 0)
   renderer.set_property('markup', str(task.prio))
   renderer.set_property('xalign', 0.5)
   renderer.set_property('alignment', pango.ALIGN_CENTER)

def taskformatter(column, renderer, model, iter):
   task = model.get_value(iter, 0)
   if task.removed:
      renderer.set_property('markup', '<span strikethrough="true">%s</span>' % escape(task.text))
   else:
      renderer.set_property('text', task.text)

class TaskGroup(gtk.VBox):
   groups = []
   popup = None

   def __init__(self, name, realizedparent, persist, daterange, top=False, events=False):
      super(gtk.VBox, self).__init__()
      TaskGroup.groups.append(self)
      self.top = top
      self.title = name
      self.events = events
      self.eventbuf = ''
      self.nextbuf = ''
      self.persist = persist
      self.daterange = daterange
      self.model = gtk.ListStore(gobject.TYPE_PYOBJECT)
      self.tree_view = gtk.TreeView(self.model)
      self.ebox = gtk.EventBox()
      self.label = gtk.Label()
      self.realizedparent = realizedparent

      self.model.set_sort_func(42, self.sort_func)
      self.model.set_sort_column_id(42, gtk.SORT_DESCENDING)

      self.ebox.add(self.label)

      self.label.set_alignment(0,0)
      self.label.set_padding(3,3)
      self.pack_start(self.ebox, False, False)
      self.sep = gtk.HSeparator()
      if self.events:
         self.pack_start(self.sep, False, False)
         l2 = gtk.Label()
         l2.set_markup(SPACER_NO_NEWLINE)
         l2.show()
         self.pack_start(l2, False, False)
      self.pack_start(self.tree_view, False, False)
      self.tree_view.set_headers_visible(False)

      checkbox = gtk.TreeViewColumn('Done')
      renderer = gtk.CellRendererText()
      checkbox.pack_start(renderer, True)
      checkbox.set_cell_data_func(renderer, prefixformatter)

      renderer = gtk.CellRendererToggle()
      renderer.connect('toggled', self.destroy_cal)
      renderer.connect('toggled', self.destroy_task)
      checkbox.pack_end(renderer, False)
      checkbox.set_cell_data_func(renderer, togformatter)
      checkbox.set_min_width(45)

      column = gtk.TreeViewColumn('Tasks')
      renderer = gtk.CellRendererText()
      renderer.set_property('editable', True)
      renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
      column.pack_start(renderer, True)
      column.set_expand(True)
      column.set_cell_data_func(renderer, taskformatter)
      renderer.connect('edited', self.text_changed)

      renderer = gtk.CellRendererCombo()
      renderer.set_property('editable', True)
      renderer.set_property('has_entry', False)
      prio_store = self.prio_store = gtk.ListStore(gobject.TYPE_STRING)
      prio_store.set(prio_store.append(), 0, str(Task.PRIORITY_ADMIN))
      prio_store.set(prio_store.append(), 0, str(Task.PRIORITY_HIGH))
      prio_store.set(prio_store.append(), 0, str(Task.PRIORITY_MEDIUM))
      prio_store.set(prio_store.append(), 0, str(Task.PRIORITY_LOW))
      renderer.set_property('model', prio_store)
      renderer.set_property('text_column', 0)
      prio = gtk.TreeViewColumn("Type")
      prio.pack_start(renderer, True)
      prio.set_cell_data_func(renderer, prioformatter)
      prio.set_min_width(30)
      renderer.connect('changed', self.prio_changed)

      # XXX need this to get rid of conflict with row_changed()?
      renderer.connect('editing-started', lambda *x: None)

      renderer = gtk.CellRendererCombo()
      renderer.set_property('editable', True)
      renderer.set_property('has_entry', False)
      renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
      date_store = self.date_store = gtk.ListStore(gobject.TYPE_STRING)
      date_store.set(date_store.append(), 0, "Choose Date...")
      date_store.set(date_store.append(), 0, str(TaskDate(None)))
      date_store.set(date_store.append(), 0, str(TaskDate(0)))
      date_store.set(date_store.append(), 0, str(TaskDate(1)))
      date_store.set(date_store.append(), 0, str(TaskDate(2)))
      date_store.set(date_store.append(), 0, str(TaskDate(3)))
      date_store.set(date_store.append(), 0, str(TaskDate(4)))
      date_store.set(date_store.append(), 0, str(TaskDate(5)))
      date_store.set(date_store.append(), 0, str(TaskDate(6)))
      date_store.set(date_store.append(), 0, str(TaskDate(7)))
      date_store.set(date_store.append(), 0, str(TaskDate(TaskDate.SOON)))
      date_store.set(date_store.append(), 0, str(TaskDate(TaskDate.FUTURE)))
      renderer.set_property('model', date_store)
      renderer.set_property('text_column', 0)
      dates = gtk.TreeViewColumn("Dates")
      dates.set_min_width(90)
      dates.pack_start(renderer, True)
      dates.set_cell_data_func(renderer, dateformatter)
      renderer.connect('changed', self.date_changed)

      # XXX need this to get rid of conflict with row_changed()?
      renderer.connect('editing-started', lambda *x: None)

      renderer = gtk.CellRendererPixbuf()
      notes = gtk.TreeViewColumn("Notes", renderer)
      self.tree_view.connect('button-press-event', self.destroy_cal)

      def activate_row(treeview, path, column):
         pass # TODO hook up to pixbuf for NOTE TAKING
      self.tree_view.connect('row-activated', activate_row)

      renderer = gtk.CellRendererText()
      notes.pack_end(renderer, True)
      notes.set_min_width(25)

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
      self.realizedparent.connect('notify::style', self.pull_styles_from_window)
      self.last_date_sweep = now()
      
      # incremented when removed bit is set
      # decremented when removed from model OR removed bit is unset
      self.garbage_num = 0

      gobject.timeout_add(60*1000, self.date_sweep)

   def clear(self):
      self.model.clear()
      # all being-deleted rows are gone
      self.garbage_num = 0

   def date_sweep(self):
      if self.events:
         self.update_title()
      if self.last_date_sweep.day == now().day:
         return True
      self.last_date_sweep = now()
      iter = self.model.get_iter_first()
      while iter:
         task = self.model.get_value(iter, 0)
         dest = self.where_it_should_go(task)
         if dest != self:
            self.remove(iter)
            dest.add(task)
            iter = self.model.get_iter_first()
         else:
            iter = self.model.iter_next(iter)
      self.update_title()
      return True

   def where_it_should_go(self, task):
      assigned = TaskGroup.groups[0]
      offset = task.date.offset()
      for group in TaskGroup.groups:
         if ((group.daterange[0] is None) or group.daterange[0] <= offset) and \
            ((group.daterange[1] is None) or group.daterange[1] >= offset):
            assigned = group
            break
      return assigned

   def smart_assign(self, task):
      self.where_it_should_go(task).add(task)

   def sort_func(self, model, iter1, iter2):
      task1 = model.get_value(iter1, 0)
      task2 = model.get_value(iter2, 0)
      if task1.date.date is None and task2.date.date is not None:
         return -1
      elif task2.date.date is None and task1.date.date is not None:
         return 1
      if task1.date.date == TaskDate.FUTURE and task2.date.date != TaskDate.FUTURE:
         return -1
      elif task2.date.date == TaskDate.FUTURE and task1.date.date != TaskDate.FUTURE:
         return 1
      if task1.date.date == TaskDate.SOON and task2.date.date != TaskDate.SOON:
         return -1
      elif task2.date.date == TaskDate.SOON and task1.date.date != TaskDate.SOON:
         return 1
      x = [0 if task1.date.special() else (task2.date.date - task1.date.date).days, task2.prio.num - task1.prio.num]
      for comp in x:
         if comp != 0:
            return comp
      return 0

   def garbage_sweep_init(self):
      if self.garbage_num:
         self.garbage_num += 1
         return
      self.garbage_num += 1
      def garbage_sweep():
         for i, x in enumerate(self.model):
            task = x[0]
            if task.removed:
               num = int(5 - task.removed/10.0)
               task.prefix = (' ' * (4-num)) + ('|' * num)
               self.model.row_changed(i, x.iter)
               if task.removed > 50:
                  self.remove(x.iter)
               else:
                  task.removed += 1
         return self.garbage_num > 0
      gobject.timeout_add(100, garbage_sweep)

   def destroy_cal(self, *args):
      if TaskGroup.popup:
         TaskGroup.popup.destroy()
         TaskGroup.popup = None
         return True
      return False

   def pull_styles_from_window(self, *args):
      self.update_title()

   def prio_changed(self, renderer, path, iter):
      miter = self.model.iter_nth_child(None, int(path))
      task = self.model.get_value(miter, 0)
      task.prio = task.prio_match(self.prio_store.get_value(iter, 0))
      self.remove(miter)
      self.add(task)
      self.persist.sync()

   def date_popup(self, task, finish):
      if TaskGroup.popup:
         TaskGroup.popup.destroy()

      self.eventcount = 0
      cal = self.cal = gtk.Calendar()
      cal.set_display_options(gtk.CALENDAR_SHOW_HEADING | gtk.CALENDAR_SHOW_WEEK_NUMBERS | gtk.CALENDAR_SHOW_DAY_NAMES)
      if not task.date.special():
         cal.select_month(task.date.date.month - 1, task.date.date.year)
         cal.select_day(task.date.date.day)
      cal.show()

      popup = TaskGroup.popup = gtk.Window(gtk.WINDOW_POPUP)
      frame = gtk.Frame()
      frame.set_property('border_width', 5)
      frame.add(cal)
      frame.show()
      popup.add(frame)
      pos = TaskGroup.origin.get_property('window').get_origin()
      popup.move(pos[0], pos[1])
      popup.show()
      popup.grab_focus()

      def cal_key_press(widget, args):
         if args.keyval in (65307, 32, 65293): # XXX should find keyvals
            self.destroy_cal()

      def cal_selected(cal):
         self.eventcount += 1
         if self.eventcount == 1:
            cd = cal.get_date()
            d = make_time(cd[0], cd[1]+1, cd[2])
            task.date = TaskDate(date=d)
            finish()
            self.destroy_cal()
         else:
            self.eventcount = 0

      def cal_month_changed(*args):
         self.eventcount += 1

      gtk.gdk.pointer_grab(popup.get_property('window'), True)
      gtk.gdk.keyboard_grab(popup.get_property('window'), True)

      self.realizedparent.connect('button-press-event', self.destroy_cal)
      frame.connect('key-press-event', cal_key_press)
      cal.connect('month-changed', cal_month_changed)
      cal.connect('day-selected', cal_selected)

   def date_changed(self, renderer, path, iter):
      miter = self.model.iter_nth_child(None, int(path))
      task = self.model.get_value(miter, 0)
      value = self.date_store.get_value(iter, 0)
      match = task.match_date(value)

      def finish():
         where = self.where_it_should_go(task)
         if where != self:
            where.add(task)
            self.remove(miter)
         else:
            self.remove(miter)
            self.add(task)
         self.persist.sync()

      if not match:
         self.date_popup(task, finish)
         return
      else:
         task.date = match
         finish()

   def text_changed(self, renderer, path, text):
      task = self.model.get_value(self.model.iter_nth_child(None, int(path)), 0)
      val = text.strip()
      if val:
         task.text = val
         self.persist.sync()

   def any_in_daterange(self, offsets):
      for x in offsets:
         if x >= self.daterange[0] and x <= self.daterange[1]:
            return True
      return False

   def format_event_for_today(self, event):
      if event.occurs_later_today():
         return str(event)
      else:
         return '<span strikethrough="true">%s</span>' % str(event)

   def get_next_group(self):
      i = TaskGroup.groups.index(self) + 1
      if i >= len(TaskGroup.groups):
         return None
      else:
         return TaskGroup.groups[i]

   def update_nextbuf(self):
      buf = ''
      next_group = self.get_next_group()
      if not next_group:
         self.nextbuf = ''
         return
      for event in self.persist.events:
         if event.occurs_in(next_group.daterange):
            if buf:
               buf += SPACER
            buf += '\xc2\xbb  ' + str(event)
      if buf:
         buf += SPACER_NO_NEWLINE
      if not buf:
         self.nextbuf = 'no events %s' % next_group.title.lower()
      else:
         self.nextbuf = '%s:\n' % next_group.title
         self.nextbuf += buf

   def update_eventbuf(self):
      buf = ''
      for event in self.persist.events:
         if event.occurs_in(self.daterange):
            if buf:
               buf += SPACER
            if self.events:
               buf += '  \xc2\xbb  ' + self.format_event_for_today(event)
            else:
               buf += '\xc2\xbb  ' + str(event)
      if buf:
         buf += SPACER_NO_NEWLINE
      if not self.events and not buf:
         self.eventbuf = 'no events'
      else:
         self.eventbuf = buf

   def add(self, task):
      self.model.set(self.model.append(), 0, task)
      self.update(events_changed=False)
      if task.removed:
         self.garbage_sweep_init()

   def update(self, events_changed=True):
      if events_changed:
         self.update_eventbuf()
      have_tasks = len(self.model)
      have_events = self.events and self.eventbuf
      visible = have_tasks or have_events
      if visible:
         self.label.show()
         self.update_title()
         if have_events:
            self.sep.show()
         else:
            self.sep.hide()
      else:
         self.label.hide()
         self.sep.hide()

   def update_title(self):
      desc = 'Sans 15' if self.top else 'Sans Bold 15'
      title = self.title
      style = self.realizedparent.get_style()
      self.update_eventbuf()
      if self.events:
         self.update_nextbuf()
         self.label.set_tooltip_markup(self.nextbuf)
      else:
         self.label.set_tooltip_markup(self.eventbuf)
      self.label.modify_fg(gtk.STATE_NORMAL, style.bg[gtk.STATE_SELECTED])
      if self.events and self.eventbuf:
         self.label.set_markup('<span font_desc="%s">%s</span>%s<span font_desc="%s" foreground="%s">%s</span>'
            % (desc, title, SPACER, 'Sans 10', style.fg[gtk.STATE_NORMAL], self.eventbuf))
         self.ebox.modify_bg(gtk.STATE_NORMAL,
            blend(style.base[gtk.STATE_NORMAL], style.bg[gtk.STATE_SELECTED]))
      else:
         self.label.set_markup('<span font_desc="%s">%s</span>' % (desc, title))
         self.ebox.modify_bg(gtk.STATE_NORMAL, style.base[gtk.STATE_NORMAL])

   def remove(self, miter):
      task = self.model.get_value(miter, 0)
      self.model.remove(miter)
      self.update(events_changed=False)
      if task.removed:
         self.garbage_num -= 1
         assert self.garbage_num >= 0

   def destroy_task(self, widget, path):
      miter = self.model.iter_nth_child(None, int(path))
      task = self.model.get_value(miter, 0)
      task.removed = not task.removed
      if task.removed:
         self.garbage_sweep_init()
      else:
         task.prefix = ''
         self.garbage_num -= 1
         assert self.garbage_num >= 0
      self.persist.sync()

# vim: et sw=3
