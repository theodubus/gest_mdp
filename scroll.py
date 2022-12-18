from tkinter import ttk
import tkinter as tk
from functools import partial as fp
import platform

"""
Cette partie du code qui gère la frame scrollable ne m'appartient pas,
elle a été trouvée en ligne via ce lien :
https://gist.github.com/JackTheEngineer/81df334f3dcff09fd19e4169dd560c59
"""

class VerticalScrolledFrame(ttk.Frame):
    """
    A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    * -- NOTE: You will need to comment / uncomment code the differently for windows or linux
    * -- or write your own 'os' type check.
    * This comes from a different naming of the the scrollwheel 'button', on different systems.
    """


    def __init__(self, parent, *args, **kw):

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        if platform.system() != "Windows":
            """
            This is linux code for scrolling the window,
            It has different buttons for scrolling the windows
            It may or may not also work for macOS, I haven't tested
            """

            def _on_mousewheel(event, scroll):
                canvas.yview_scroll(int(scroll), "units")

            def _bind_to_mousewheel(event):
                canvas.bind_all("<Button-4>", fp(_on_mousewheel, scroll=-1))
                canvas.bind_all("<Button-5>", fp(_on_mousewheel, scroll=1))

            def _unbind_from_mousewheel(event):
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")

        else:
            """
            This is windows code for scrolling the Frame
            """
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            def _bind_to_mousewheel(event):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
            def _unbind_from_mousewheel(event):
                canvas.unbind_all("<MouseWheel>")


        ttk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set, bg="#F8F6F4")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # style used by default for all ttk.Frames
        s = ttk.Style()
        s.configure('TFrame', background="#F8F6F4")

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        interior.bind('<Configure>', _configure_interior)
        canvas.bind('<Configure>', _configure_canvas)
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        self.canvas = canvas

    # méthode qui fait revenir le scroll au début
    def reset(self):
        self.canvas.yview_moveto(0)
