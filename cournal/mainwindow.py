#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Fabian Henze
# 
# Cournal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cournal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cournal.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk
from gi.repository.GLib import GError

from .viewer import Layout
from .viewer.tools import pen
from .document import Document, xojparser
from . import ConnectionDialog, AboutDialog

pdf_filter = Gtk.FileFilter()
pdf_filter.add_mime_type("application/pdf")
xoj_filter = Gtk.FileFilter()
xoj_filter.add_mime_type("application/x-xoj")

class MainWindow(Gtk.Window):
    def __init__(self, **args):
        Gtk.Window.__init__(self, title="Cournal", **args)
        
        self.document = None
        self.last_filename = None
        
        self.set_default_size(width=500, height=700)
        self.set_icon_name("cournal")
        
        # Bob the builder
        builder = Gtk.Builder()
        builder.add_from_file("mainwindow.glade")
        self.add(builder.get_object("outer_box"))
        
        # Initialize the main journal layout
        self.layout = None
        self.scrolledwindow = builder.get_object("scrolledwindow")
        
        # Menu Bar:
        self.menu_open_xoj = builder.get_object("imagemenuitem_open_xoj")
        self.menu_open_pdf = builder.get_object("imagemenuitem_open_pdf")
        self.menu_connect = builder.get_object("imagemenuitem_connect")
        self.menu_save = builder.get_object("imagemenuitem_save")
        self.menu_save_as = builder.get_object("imagemenuitem_save_as")
        self.menu_export_pdf = builder.get_object("imagemenuitem_export_pdf")
        self.menu_import_xoj = builder.get_object("imagemenuitem_import_xoj")
        self.menu_quit = builder.get_object("imagemenuitem_quit")
        self.menu_about = builder.get_object("imagemenuitem_about")
        # Toolbar:
        self.tool_open_pdf = builder.get_object("tool_open_pdf")
        self.tool_save = builder.get_object("tool_save")
        self.tool_connect = builder.get_object("tool_connect")
        self.tool_zoom_in = builder.get_object("tool_zoom_in")
        self.tool_zoom_out = builder.get_object("tool_zoom_out")
        self.tool_zoom_100 = builder.get_object("tool_zoom_100")
        self.tool_pen_color = builder.get_object("tool_pen_color")

        self.menu_connect.set_sensitive(False)
        self.menu_save.set_sensitive(False)
        self.menu_save_as.set_sensitive(False)
        self.menu_export_pdf.set_sensitive(False)
        self.menu_import_xoj.set_sensitive(False)
        self.tool_save.set_sensitive(False)
        self.tool_connect.set_sensitive(False)
        self.tool_zoom_in.set_sensitive(False)
        self.tool_zoom_out.set_sensitive(False)
        self.tool_zoom_100.set_sensitive(False)
        self.tool_pen_color.set_sensitive(False)
        
        self.menu_open_xoj.connect("activate", self.run_open_xoj_dialog)
        self.menu_open_pdf.connect("activate", self.run_open_pdf_dialog)
        self.menu_connect.connect("activate", self.run_connection_dialog)
        self.menu_save.connect("activate", self.save)
        self.menu_save_as.connect("activate", self.run_save_as_dialog)
        self.menu_export_pdf.connect("activate", self.run_export_pdf_dialog)
        self.menu_import_xoj.connect("activate", self.run_import_xoj_dialog)
        self.menu_quit.connect("activate", lambda _: self.destroy())
        self.menu_about.connect("activate", self.run_about_dialog)
        self.tool_open_pdf.connect("clicked", self.run_open_pdf_dialog)
        self.tool_save.connect("clicked", self.save)
        self.tool_connect.connect("clicked", self.run_connection_dialog)
        self.tool_zoom_in.connect("clicked", self.zoom_in)
        self.tool_zoom_out.connect("clicked", self.zoom_out)
        self.tool_zoom_100.connect("clicked", self.zoom_100)
        self.tool_pen_color.connect("color-set", self.change_pen_color)
    
    def _set_document(self, document):
        self.document = document
        for child in self.scrolledwindow.get_children():
            self.scrolledwindow.remove(child)
        self.layout = Layout(self.document)
        self.scrolledwindow.add(self.layout)
        self.scrolledwindow.show_all()
        self.last_filename = None
        
        self.menu_connect.set_sensitive(True)
        self.menu_save.set_sensitive(True)
        self.menu_save_as.set_sensitive(True)
        self.menu_export_pdf.set_sensitive(True)
        self.menu_import_xoj.set_sensitive(True)
        self.tool_save.set_sensitive(True)
        self.tool_connect.set_sensitive(True)
        self.tool_zoom_in.set_sensitive(True)
        self.tool_zoom_out.set_sensitive(True)
        self.tool_zoom_100.set_sensitive(True)
        self.tool_pen_color.set_sensitive(True)
    
    def run_open_pdf_dialog(self, menuitem):
        dialog = Gtk.FileChooserDialog("Open File", self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(pdf_filter)
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            
            try:
                document = Document(filename)
            except GError as ex:
                self.run_error_dialog("Unable to open PDF", ex)
                dialog.destroy()
                return
            self._set_document(document)
        dialog.destroy()
    
    def run_connection_dialog(self, menuitem):
        def destroyed(widget):
            self._connection_dialog = None
        # Need to hold a reference, so the object does not get garbage collected
        self._connection_dialog = ConnectionDialog(self)
        self._connection_dialog.connect("destroy", destroyed)
        self._connection_dialog.run_nonblocking()
        
    def run_import_xoj_dialog(self, menuitem):
        dialog = Gtk.FileChooserDialog("Open File", self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(xoj_filter)

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            xojparser.import_into_document(self.document, filename, self)
        dialog.destroy()
    
    def run_open_xoj_dialog(self, menuitem):
        dialog = Gtk.FileChooserDialog("Open File", self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(xoj_filter)

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            try:
                document = xojparser.new_document(filename, self)
            except Exception as ex:
                print(ex)
                dialog.destroy()
                return
            self._set_document(document)
            self.last_filename = filename
        dialog.destroy()

    def save(self, menuitem):
        if self.last_filename:
            self.document.save_xoj_file(self.last_filename)
        else:
            self.run_save_as_dialog(menuitem)
    
    def run_save_as_dialog(self, menuitem):
        dialog = Gtk.FileChooserDialog("Save File As", self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(xoj_filter)
        dialog.set_current_name("document.xoj")

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            self.document.save_xoj_file(filename)
            self.last_filename = filename
        dialog.destroy()

    def run_export_pdf_dialog(self, menuitem):
        dialog = Gtk.FileChooserDialog("Export PDF", self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(pdf_filter)
        dialog.set_current_name("annotated_document.pdf")
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            self.document.export_pdf(filename)
        dialog.destroy()
        
    def run_about_dialog(self, menuitem):
        def destroyed(widget):
            self._about_dialog = None
        # Need to hold a reference, so the object does not get garbage collected
        self._about_dialog = AboutDialog(self)
        self._about_dialog.connect("destroy", destroyed)
        self._about_dialog.run_nonblocking()
    
    def run_error_dialog(self, first, second):
        print("Unable to open PDF file:", second)
        message = Gtk.MessageDialog(self, (Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT), Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, first)
        message.format_secondary_text(second)
        message.set_title("Error")
        message.connect("response", lambda _,x: message.destroy())
        message.show()
        
    def change_pen_color(self, menuitem):
        color = menuitem.get_rgba()
        red = int(color.red*255)
        green = int(color.green*255)
        blue = int(color.blue*255)
        opacity = int(color.alpha*255)
        
        pen.color = red, green, blue, opacity        
    
    def zoom_in(self, menuitem):
        self.layout.set_zoomlevel(change=0.2)
    
    def zoom_out(self, menuitem):
        self.layout.set_zoomlevel(change=-0.2)
    
    def zoom_100(self, menuitem):
        self.layout.set_zoomlevel(1)
