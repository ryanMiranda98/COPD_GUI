from tkinter import *
from tkinter.filedialog import askopenfilename

root = Tk()
root.title("COPD DETECTION SYSTEM")


def myClick():
    filename = askopenfilename(filetypes=[(".wav", ".mp3")])
    print(filename)

myButton = Button(root, text="Upload File", padx=50, command=myClick)
myButton.pack()

root.mainloop()