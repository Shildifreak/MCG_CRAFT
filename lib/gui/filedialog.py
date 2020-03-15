import sys

defined = False

# open_dialog(path): False or path
# save_dialog(path): False or path

# GTK
if not defined:
	try:
		import gi
		gi.require_version('Gtk', '3.0')
		from gi.repository import Gtk
	except:
		pass
	else:

		print("using Gtk >3.0 from gi")
		defined = True
		def _dialog(path,mode,button_text,title):
			dialog = Gtk.FileChooserDialog(title, None,
				mode,
				(button_text, Gtk.ResponseType.OK))

			filter_shl = Gtk.FileFilter()
			filter_shl.set_name("MCGCraft Savegames")
			filter_shl.add_pattern("*.mc.*")
			dialog.add_filter(filter_shl)

			filter_any = Gtk.FileFilter()
			filter_any.set_name("Any files")
			filter_any.add_pattern("*")
			dialog.add_filter(filter_any)

			dialog.set_current_folder(path)

			response = dialog.run()
			if response == Gtk.ResponseType.OK:
				filename = dialog.get_filename()
			else:
				filename = False

			dialog.destroy()
			while Gtk.events_pending(): # to make sure window is really deleted from screen
				Gtk.main_iteration()
			return filename

		def open_dialog(path):
			return _dialog(path, Gtk.FileChooserAction.OPEN,Gtk.STOCK_OPEN,"choose savegame to open")

		def save_dialog(path):
			return _dialog(path, Gtk.FileChooserAction.SAVE,Gtk.STOCK_SAVE,"create file for savegame")

# TK
if not defined:
	try:
		if sys.version < "3":
			import Tkinter
			import tkFileDialog as FileDialog
		else:
			import tkinter as Tkinter
			import tkinter.filedialog as FileDialog
	except:
		pass
	else:
		print("using Tkinter/tkinter")
		defined = True

		def _dialog(path,dialog_function,title):
			root = Tkinter.Tk()
			root.withdraw()
			filename = dialog_function(filetypes = [("MCGCraft Savegames","*.mc.*"),("Any files","*")],
									   initialdir = path,
									   defaultextension=".mc.txt",
									   title=title)
			root.destroy()
			return filename if filename else False

		def open_dialog(path):
			return _dialog(path, FileDialog.askopenfilename,"choose savegame to open")

		def save_dialog(path):
			return _dialog(path, FileDialog.asksaveasfilename,"create file for savegame")

if not defined:
	raise ImportError("no filedialog implementation found. Please install one of the following:\n"
					  "- Tkinter/tkinter\n"
					  "- gi with Gtk >3.0")

if __name__ == "__main__":
	print("open",open_dialog(".."))
	print("save",save_dialog(".."))
