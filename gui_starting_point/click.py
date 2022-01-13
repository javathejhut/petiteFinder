from Tkinter import *
#import tkinter#, tkconstants, tkFileDialog
from tkFileDialog import askopenfilename
from PIL import ImageTk, Image

if __name__ == "__main__":
    root = Tk()
    root.minsize(500,500)
    
    petites = []
    grandes = []

    #setting up a tkinter canvas with scrollbars
    frame = Frame(root, bd=2, relief=SUNKEN)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    xscroll = Scrollbar(frame, orient=HORIZONTAL)
    xscroll.grid(row=1, column=0, sticky=E+W)
    yscroll = Scrollbar(frame)
    yscroll.grid(row=0, column=1, sticky=N+S)
    canvas = Canvas(frame, bd=0, xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    xscroll.config(command=canvas.xview)
    yscroll.config(command=canvas.yview)
    frame.pack(fill=BOTH,expand=1)

    #adding the image
    File = askopenfilename(parent=root, initialdir="M:/",title='Choose an image.')
    print("opening %s" % File)
    img1 = Image.open(File)
    maxsize = [2000.0, 1200.0]
    ratio = min(maxsize[0]/img1.size[0], maxsize[1]/img1.size[1])
    newsize = [int(img1.size[0]*ratio),int(img1.size[1]*ratio)]
    #print newsize
    img = ImageTk.PhotoImage(img1.resize((newsize[0],newsize[1]), Image.ANTIALIAS))
    canvas.config(width=newsize[0], height=newsize[1])
    canvas.create_image(0,0,image=img,anchor="nw")
    canvas.config(scrollregion=canvas.bbox(ALL))
        
    fp = open("1_petite.txt", "w+")
    fg = open("1_grande.txt", "w+")
    '''
    #functions to be called when mouse is clicked
    def petitemark(event):
        petites.append([event.x/ratio,event.y/ratio])
       #marks petite colonies green
        canvas.create_oval(event.x-1,event.y+1,event.x+1,event.y-1,outline='green')
    def grandemark(event):
        grandes.append([event.x/ratio,event.y/ratio])
        #marks grande colonies red
        canvas.create_oval(event.x-1,event.y+1,event.x+1,event.y-1,outline='red')
    def close(event):
        root.destroy()
        f.close()
        print("The petites are located at", petites, "\n The grandes are located at", grandes)
    '''
    
    #for i in range(0,5):
        #f.write(i,i+1)
    
    #functions to be called when mouse is clicked
    def petitemark(event):
        fp.write(str(event.x) + "," + str(event.y) +"\n")
        #marks petite colonies green
        canvas.create_oval(event.x-1,event.y+1,event.x+1,event.y-1,outline='green')
    def grandemark(event):
        fg.write(str(event.x) + "," + str(event.y) +"\n")
        #marks grande colonies red
        canvas.create_oval(event.x-1,event.y+1,event.x+1,event.y-1,outline='red')
    def close(event):
        root.destroy()
        f.close()
    
    
    #mouseclick event
    root.bind("<Button-1>",petitemark)
    root.bind("<Button-2>",grandemark)
    root.bind("<Key>", close)

root.mainloop()
