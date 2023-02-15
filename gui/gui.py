from tkinter import *
from tkinter import ttk
import sys
import math

class GUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("GUI")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.root.configure(bg="white")

        # canvas
        self.canvas = Canvas(self.root, width=400, height=400, bg="white")
        self.canvas.pack()

    

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = GUI()
    sys.exit(gui.run())