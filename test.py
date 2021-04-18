import tkinter as Tk

def clic(s1, s2, s3):
    print('Clic gauche sur le bouton ' + s1 + s2 + s3)


def main(a, b):
    button = Tk.Button(root, text = 'toto', command = lambda : c=a+b; print(c))
    button.pack()

root = Tk.Tk()
main(quit, [])
root.mainloop()
