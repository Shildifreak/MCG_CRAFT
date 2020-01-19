import tkinter as tk

# apparently the code below has first been posted to the no longer available site
# http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
# However you can still find it at a lot of different places on the web including
# https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
# where I first found it.

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Scrollable Frame Demo")
	root.configure(background="gray99")

	scframe = VerticalScrolledFrame(root)
	scframe.pack()

	lis = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
	for i, x in enumerate(lis):
		btn = tk.Button(scframe.interior, height=1, width=80, relief=tk.FLAT, 
			bg="gray99", fg="purple3",
			font="Dosis", text='Button ' + lis[i],
			command=lambda i=i,x=x: openlink(i))
		btn.pack(padx=10, pady=5, side=tk.TOP)

	def openlink(i):
		print(lis[i])

	root.mainloop()
