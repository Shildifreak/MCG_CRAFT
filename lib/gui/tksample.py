# -*- coding: utf-8 -*-
import Tkinter

window = Tkinter.Tk()

label = Tkinter.Label(window, text="Ich bin ein Label!")
label.grid(row = 0, column = 1)

button = Tkinter.Button(window, text="Drück mich!")
button.configure(command = lambda:button.configure(text="Danke ^^"))
button.grid(row = 1, column = 0)

entrycontent = Tkinter.StringVar()
entrycontent.set("hey")

entry = Tkinter.Entry(window, textvar=entrycontent)
entry.grid(row = 2, column = 0, columnspan = 2, sticky = Tkinter.W+Tkinter.E)

entry2 = Tkinter.Entry(window, textvar=entrycontent)
entry2.grid(row = 3, column = 0, columnspan = 2)

def testfunc(*args):
    print args
entrycontent.trace("w",testfunc)

window.mainloop()
