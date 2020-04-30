import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename

root = Tk()
root.title("COPD Analyzer")
root.geometry("600x400")
# root.minsize(600, 400)

def myClick():
    filename = askopenfilename(filetypes=[(".wav", ".mp3")])
    print(filename)

text=Label(root, text="Select files to upload", width=15, height=10, anchor=SW)
# text.config(anchor=CENTER)
text.pack()

myButton = Button(root, text="Upload File", padx=50, command=myClick)
myButton.pack()

filename = "101_Meditron.wav"
fileNameText=Label(root, text="File Name: "+ filename, width=75, height=10, anchor=SW)
fileNameText.pack()

result = "Positive"
resultText=Label(root, text="Result: " + result, width=75, height=2, anchor=SW)
resultText.pack()

root.mainloop()