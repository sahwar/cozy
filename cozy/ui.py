import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk

class CozyUI:
  def __init__(self, pkgdatadir, app):
    self.pkgdir = pkgdatadir
    self.app = app

  def activate(self):
    self.init_window()

  def startup(self):
    self.init_resources()
    self.init_css()
    self.init_actions()

  def init_resources(self):
    resource = Gio.resource_load(os.path.join(self.pkgdir, 'cozy.ui.gresource'))
    Gio.Resource._register(resource)

    resource = Gio.resource_load(os.path.join(self.pkgdir, 'cozy.img.gresource'))
    Gio.Resource._register(resource)

    self.window_builder = Gtk.Builder.new_from_resource("/de/geigi/cozy/main_window.ui")
    self.search_builder = Gtk.Builder.new_from_resource("/de/geigi/cozy/search_popover.ui")
    self.timer_builder = Gtk.Builder.new_from_resource("/de/geigi/cozy/timer_popover.ui")
    self.settings_builder = Gtk.Builder.new_from_resource("/de/geigi/cozy/settings.ui")
    self.menu_builder = Gtk.Builder.new_from_resource("/de/geigi/cozy/app_menu.ui")
    self.about_builder = Gtk.Builder.new_from_resource("/de/geigi/cozy/about.ui")

  def init_css(self):
    if Gtk.get_minor_version() > 18:
      print("Fanciest design possible")
      cssProviderFile = Gio.File.new_for_uri("resource:///de/geigi/cozy/application.css")
    else :
      print("Using legacy css file")
      cssProviderFile = Gio.File.new_for_uri("resource:///de/geigi/cozy/application_legacy.css")
    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_file(cssProviderFile)

    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

  def init_window(self):
    self.window = self.window_builder.get_object("app_window")
    self.window.set_application(self.app)
    self.window.show_all()
    self.window.present()

    author_box = self.window_builder.get_object("author_box")
    reader_box = self.window_builder.get_object("reader_box")
    search_button = self.window_builder.get_object("search_button")
    search_popover = self.search_builder.get_object("search_popover")
    timer_button = self.window_builder.get_object("timer_button")
    timer_popover = self.timer_builder.get_object("timer_popover")

    self.timer_switch = self.timer_builder.get_object("timer_switch")
    self.timer_scale = self.timer_builder.get_object("timer_scale")
    self.timer_spinner = self.timer_builder.get_object("timer_spinner")
    self.timer_buffer = self.timer_builder.get_object("timer_buffer")

    # get settings window
    self.settings_window = self.settings_builder.get_object("settings_window")
    self.settings_window.set_transient_for(self.window)
    self.settings_window.connect("destroy", self.hide_window)

    # get about dialog
    self.about_dialog = self.about_builder.get_object("about_dialog")
    self.about_dialog.set_transient_for(self.window)

    # init popovers
    search_button.set_popover(search_popover)
    timer_button.set_popover(timer_popover)

    # add marks to timer scale
    for i in range(0, 181, 15):
      self.timer_scale.add_mark(i, Gtk.PositionType.RIGHT, None)

    # timer SpinButton text format
    self.timer_spinner.connect("value-changed", self.on_timer_changed)
    self.init_timer_buffer()

    # shortcuts
    self.accel = Gtk.AccelGroup()

    # DEMO #
    scale = self.window_builder.get_object("progress_scale")
    scale.set_range(0, 4)

    for i in range(1,100):
      row_a = ListBoxRowWithData(i)
      row_b = ListBoxRowWithData(i)

      author_box.add(row_a)
      reader_box.add(row_b)
      pass

    author_box.show_all()
    reader_box.show_all()

  def init_actions(self):
    self.accel = Gtk.AccelGroup()

    menu = self.menu_builder.get_object("app_menu")
    self.app.set_app_menu(menu)

    help_action = Gio.SimpleAction.new("help", None)
    help_action.connect("activate", self.help)
    self.app.add_action(help_action)

    about_action = Gio.SimpleAction.new("about", None)
    about_action.connect("activate", self.about)
    self.app.add_action(about_action)

    quit_action = Gio.SimpleAction.new("quit", None)
    quit_action.connect("activate", self.quit)
    self.app.add_action(quit_action)
    self.app.set_accels_for_action("app.quit", ["<Control>q", "<Control>w"])


    pref_action = Gio.SimpleAction.new("prefs", None)
    pref_action.connect("activate", self.show_prefs)
    self.app.add_action(pref_action)
    self.app.set_accels_for_action("app.prefs", ["<Control>comma"])

  def help(self, action, parameter):
    pass

  def quit(self, action, parameter):
      self.app.quit()

  def about(self, action, parameter):
    self.about_dialog.show()
    pass

  def show_prefs(self, action, parameter):
    self.settings_window.show()
    pass

  def hide_window(self, widget, data=None):
    widget.hide()

  def init_timer_buffer(self):
    adjustment = self.timer_spinner.get_adjustment()
    value = adjustment.get_value()

    text = str(int(value)) + " min"
    self.timer_buffer.set_text(text, len(text))

    return True

  def on_timer_changed(self, spinner):
    if not self.timer_switch.get_active():
      self.timer_switch.set_active(True)

    adjustment = self.timer_spinner.get_adjustment()
    value = adjustment.get_value()

    text = str(int(value)) + " min"
    self.timer_buffer.set_text(text, len(text))

class ListBoxRowWithData(Gtk.ListBoxRow):
  def __init__(self, data):
    super(Gtk.ListBoxRow, self).__init__()
    self.data = data
    label = Gtk.Label(data)
    label.set_xalign(0.0)
    self.add(label)