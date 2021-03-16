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
		def _dialog(path,dialog_type,title,filetypes,defaultextension):
			global dialog
			if dialog_type == "open_file":
				action,button_text = Gtk.FileChooserAction.OPEN,Gtk.STOCK_OPEN
			elif dialog_type == "save_file":
				action,button_text = Gtk.FileChooserAction.SAVE,Gtk.STOCK_SAVE
			else:
				raise NotImplementedError("dialog type %s is not supported" % dialog_type)
			
			dialog = Gtk.FileChooserDialog(title=title,action=action)
			dialog.add_button(button_text, Gtk.ResponseType.OK)

			for filetype_name, filetype_extension in filetypes:
				file_filter = Gtk.FileFilter()
				file_filter.set_name(filetype_name)
				file_filter.add_pattern(filetype_extension)
				dialog.add_filter(file_filter)

			#filter_any = Gtk.FileFilter()
			#filter_any.set_name("Any files")
			#filter_any.add_pattern("*")
			#dialog.add_filter(filter_any)

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

		def _dialog(path,dialog_type,title,filetypes,defaultextension):
			if dialog_type == "open_file":
				dialog_function = FileDialog.askopenfilename
			elif dialog_type == "save_file":
				FileDialog.asksaveasfilename
			else:
				raise NotImplementedError("dialog type %s is not supported" % dialog_type)

			root = Tkinter.Tk()
			root.withdraw()
			filename = dialog_function(filetypes = filetypes,
									   initialdir = path,
									   defaultextension=defaultextension,
									   title=title)
			root.destroy()
			return filename if filename else False

DEFAULT_FILETYPES = [("MCGCraft Savegames","*.mc.*"),("Any files","*")]
DEFAULT_DEFAULTEXTENSION = ".mc.txt"

def open_dialog(path,title="choose savegame to open",filetypes=DEFAULT_FILETYPES,defaultextension=DEFAULT_DEFAULTEXTENSION):
	return _dialog(path, "open_file",title,filetypes,defaultextension)

def save_dialog(path,title="create file for savegame",filetypes=DEFAULT_FILETYPES,defaultextension=DEFAULT_DEFAULTEXTENSION):
	return _dialog(path, "save_file",title,filetypes,defaultextension)

if not defined:
	raise ImportError("no filedialog implementation found. Please install one of the following:\n"
					  "- Tkinter/tkinter\n"
					  "- gi with Gtk >3.0")

if __name__ == "__main__":
	print("open",open_dialog(".."))
	print("save",save_dialog(".."))
