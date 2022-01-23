import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import json

BBOX_INFO = StringVar
REMOVE = 0
DRAW = 1
MAX_SIZE = (800, 800)

MODE = IntVar
PETITE = IntVar
IMG_ID = IntVar
PATH_TO_SAVE = ""


class ImageFrame(Frame):

    def __init__(self, master, data):
        ''' Initialize the main Frame '''

        Frame.__init__(self, master=None, bd=2, relief=SUNKEN)

        self.x = None
        self.create_canvas()

        self.data = data
        self.parse_coco_annotations()
        self.updated_data = None

        self.image_annotations = None
        self.image_fname = None
        self.im = None
        self.tk_im = None
        self.new_size = None
        self.imscale = 1.0
        self.delta = 1.3

        self.bboxes = None
        self.selected_bboxes = []

        self.chose_data()
        self.image = Image.open(self.image_fname)  # open image
        self.width, self.height = self.image.size

        # rectangle from the mouse drag
        self.temp_rect = None
        self.start_x = None
        self.start_y = None

        # Mouse response
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Bind events to the Canvas for zoom
        self.canvas.bind('<Configure>', self.draw_crop_image)  # canvas is resized
        self.canvas.bind('<MouseWheel>', self.wheel)
        self.canvas.bind('<Button-5>', self.wheel)
        self.canvas.bind('<Button-4>', self.wheel)

        # Bind events to Canvas for pan
        self.canvas.bind('<ButtonPress-2>', self.move_from)
        self.canvas.bind('<B2-Motion>', self.move_to)
        self.canvas.bind('<ButtonPress-3>', self.move_from)
        self.canvas.bind('<B3-Motion>', self.move_to)

        self.draw_complete_img()
        self.draw_ann()
        self.container = None
        self.create_container()
        self.shrink_to_fit_screen()

    def create_canvas(self):
        """Crete a required canvas"""
        self.x = self.y = 0
        self.canvas = Canvas(self, cursor="cross")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.yscroll = Scrollbar(self, orient=VERTICAL)
        self.xscroll = Scrollbar(self, orient=HORIZONTAL)

        self.yscroll.config(command=self.scroll_y)
        self.xscroll.config(command=self.scroll_x)

        self.canvas.config(yscrollcommand=self.yscroll.set)
        self.canvas.config(xscrollcommand=self.xscroll.set)

        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        self.canvas.update()
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.yscroll.grid(row=0, column=1, stick=N + S)
        self.xscroll.grid(row=1, column=0, sticky=E + W)

    def create_container(self):
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0, tags='container')
        self.canvas.lower(self.container)

    def save_coco_annotations(self, filename='updated.json'):
        """
        Save a new COCO json file from updated annotations
        """
        coco_annotations = []
        for img_id in range(num_img(self.data)):
            coco_annotations.extend(self.annotations[img_id])

        self.updated_data = {
            "categories": [],
            "info": [],
            "licenses": [],
            "images": self.data['images'],
            "annotations": coco_annotations
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.updated_data, f, ensure_ascii=False, indent=4)

    def bbox_hover_event(self, event):
        """
        Show bbox info when the cursor is hovering over it:
        """
        bbox_id = event.widget.find_withtag('current')[0]
        for bbox in self.bboxes:
            if bbox.drawn_obj == bbox_id:
                text = 'Category: {}\nScore: {}'.format(bbox.category_name, round(bbox.score, 2))
                BBOX_INFO.set(text)

    def on_button_press(self, event):
        """
        Create a rectangle on the left mouse button click [in a draw mode].
        Chose a bbox for deletion [in a remove mode]
        """

        if MODE.get() == DRAW:
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)

            # create rectangle if not yet exist
            if not self.temp_rect:
                self.temp_rect = self.canvas.create_rectangle((self.x, self.y, 1, 1), outline='white', width=4,
                                                              tags='annotation_bbox')

        if MODE.get() == REMOVE:
            for bbox in self.bboxes:
                if self.is_within_box(event.x, event.y, bbox) and bbox not in self.selected_bboxes:
                    self.selected_bboxes.append(bbox)
                    self.canvas.itemconfig(bbox.drawn_obj, outline='red', fill='')

                elif self.is_within_box(event.x, event.y, bbox) and bbox in self.selected_bboxes:
                    self.selected_bboxes.remove(bbox)
                    if bbox.category_name == 'g':
                        self.canvas.itemconfig(bbox.drawn_obj, outline='blue', fill='')
                    else:
                        self.canvas.itemconfig(bbox.drawn_obj, outline='orange', fill='')

    def on_move_press(self, event):
        """Extend the rectangle on the cursor move [only in a draw mode]"""

        if MODE.get() == DRAW:
            curX = self.canvas.canvasx(event.x)
            curY = self.canvas.canvasy(event.y)

            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            if event.x > 0.9 * w:
                self.canvas.xview_scroll(1, 'units')
            elif event.x < 0.1 * w:
                self.canvas.xview_scroll(-1, 'units')
            if event.y > 0.9 * h:
                self.canvas.yview_scroll(1, 'units')
            elif event.y < 0.1 * h:
                self.canvas.yview_scroll(-1, 'units')

            # expand rectangle as you drag the mouse
            self.canvas.coords(self.temp_rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        """Adding a bbox to the list [only in a draw mode]"""
        if MODE.get() == DRAW:
            if PETITE.get():
                category_name = 'p'
                self.canvas.itemconfig(self.temp_rect, outline='orange', fill='')
            else:
                category_name = 'g'
                self.canvas.itemconfig(self.temp_rect, outline='blue', fill='')
            new_bbox = BBox(rect=self.temp_rect, frame=self, category_name=category_name)
            self.bboxes.append(new_bbox)
            self.save_annotation_state()

            self.temp_rect = None

    def draw_complete_img(self):
        """draw full sized image on startup/right or left button click"""
        self.canvas.delete('complete_img')
        self.canvas.delete('cropped_img')
        self.im = Image.open(self.image_fname)

        self.tk_im = ImageTk.PhotoImage(self.im.resize((self.im.size[0], self.im.size[0]), Image.ANTIALIAS))
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_im, tags='complete_img')
        self.canvas.config(scrollregion=(self.canvas.bbox(ALL)))

    def chose_data(self):
        """
        Chose the image and annotations according to the global variable IMG_ID [controlled from the button panel]
        """
        self.image_annotations = self.annotations[IMG_ID.get()]
        self.image_fname = [datum['file_name'] for datum in self.data['images'] if datum['id'] == IMG_ID.get()][0]

    def parse_coco_annotations(self):
        """
        Parse coco dictionary and create an internal memory representation where annotations are grouped by the img_id
        """
        self.annotations = {}
        for img_id in range(num_img(self.data)):
            self.annotations[img_id] = [datum for datum in self.data['annotations'] if datum['image_id'] == img_id]

    def scroll_y(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image """
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.draw_crop_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image """
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.draw_crop_image()  # redraw the image

    def move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        """ Move canvas to the new position with right mouse click"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.draw_crop_image()  # redraw the image

    def wheel(self, event):
        """ Zoom with mouse wheel """
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return
            self.imscale /= self.delta
            scale /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return
            self.imscale *= self.delta
            scale *= self.delta

        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.draw_crop_image()

    def key_zoom_in(self, event):
        """ Zoom with mouse +- keys """

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        scale = 1.0
        scale *= self.delta
        self.imscale *= self.delta
        self.canvas.scale('all', x, y, scale,
                          scale)  # rescale all canvas objects
        self.draw_crop_image()

    def key_zoom_out(self, event):
        """ Zoom with mouse +- keys """

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        scale = 1.0
        scale /= self.delta
        self.imscale /= self.delta
        self.canvas.scale('all', x, y, scale,
                          scale)  # rescale all canvas objects
        self.draw_crop_image()

    def shrink_to_fit_screen(self):
        """ shrink image/canvas to fit screen upon opening/changing images"""

        self.imscale = self.compute_optimal_scaling()
        print(self.canvas.winfo_width() / 2)
        self.canvas.scale('all', self.canvas.winfo_screenwidth() / 2, 0, self.imscale, self.imscale)
        self.draw_crop_image()

    def draw_crop_image(self, event=None):

        """ Draw cropped image on canvas """
        self.image = Image.open(self.image_fname)
        self.canvas.delete('complete_img')

        bbox1 = self.canvas.bbox(self.container)  # get image area

        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))

        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]

        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)  # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not

            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk, tags='cropped_img')
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

    def draw_ann(self):
        if not self.bboxes:
            self.bboxes = [BBox(json_ann=json_ann) for json_ann in self.image_annotations]

        for bbox in self.bboxes:
            bbox.draw(self)

    def save_annotation_state(self):
        self.annotations[IMG_ID.get()] = [bbox.convert_to_ann() for bbox in self.bboxes]

    def delete_canvas_annotations(self):
        self.canvas.delete('annotation_bbox')

    def is_within_box(self, x, y, bbox):
        """Checking if the x,y point is within the box"""
        x = self.canvas.canvasx(x)
        y = self.canvas.canvasy(y)

        canvas_bbox = self.canvas.bbox(self.container)

        img_coords_x = (x - canvas_bbox[0]) / self.imscale
        img_coords_y = (y - canvas_bbox[1]) / self.imscale

        if (bbox.x_start_orig <= img_coords_x <= bbox.x_end_orig) and (bbox.y_start_orig
                                                                       <= img_coords_y <= bbox.y_end_orig):
            return True
        else:
            return False

    def compute_optimal_scaling(self):
        """Compute image scale that fits screen size"""
        scale = 0.9 * min(MAX_SIZE) / min(self.width, self.height)
        return scale


class ButtonsFrame(Frame):
    def __init__(self, master, data, iframe):
        Frame.__init__(self, master=None)
        self.iframe = iframe

        self.navFrame = Frame(self)
        self.leftButton = Button(self.navFrame, command=self.leftButtonClick, text="<")
        self.rightButton = Button(self.navFrame, command=self.rightButtonClick, text=">")

        self.modFrame = Frame(self)
        self.remButton = Button(self.modFrame, command=self.remButtonClick, text="Remove Mode")
        self.drawButton = Button(self.modFrame, command=self.drawButtonClick, text="Draw Mode")

        self.categFrame = Frame(self)
        self.petButton = Button(self.categFrame, command=self.petButtonClick, text="Petite")
        self.grandButton = Button(self.categFrame, command=self.grandButtonClick, text="Grande")

        self.delSelButton = Button(self, command=self.delSelButtonClick, text="Delete selected", state='disabled')
        self.saveButton = Button(self, command=self.saveButtonClick, text="Save")

        self.master.bind("<Key>", self.keyHandler)

        self.mode_text = StringVar()
        self.class_text = StringVar()
        self.update_text()
        self.imgid_text = StringVar(self, str(IMG_ID.get()))

        self.modeLabel = Label(self, textvariable=self.mode_text)
        self.imgidLabel = Label(self.navFrame, textvariable=self.imgid_text)
        self.classLabel = Label(self, textvariable=self.class_text)
        self.bboxLabel = Label(self, textvariable=BBOX_INFO)

        padx = (10, 10)
        pady = (2, 2)

        self.navFrame.grid(rowspan=2, column=0, row=0)
        self.leftButton.pack(fill=Y, side=LEFT, padx=(10, 0))
        self.imgidLabel.pack(fill=Y, side=LEFT, pady=pady)
        self.rightButton.pack(fill=Y, side=LEFT, padx=(0, 10))

        self.modFrame.grid(column=1, row=0, rowspan=2)
        self.drawButton.pack(fill=X, padx=padx, pady=pady)
        self.remButton.pack(fill=X, padx=padx, pady=pady)

        self.categFrame.grid(column=2, row=0, rowspan=2)
        self.petButton.pack(fill=X, padx=padx, pady=pady)
        self.grandButton.pack(fill=X, padx=padx, pady=pady)

        self.modeLabel.grid(column=3, row=0, padx=padx, pady=pady)
        self.classLabel.grid(column=3, row=1, padx=padx, pady=pady)

        self.delSelButton.grid(column=4, row=0, padx=padx, pady=pady, rowspan=2)
        self.saveButton.grid(column=5, row=0, padx=padx, pady=pady, rowspan=2)

        self.bboxLabel.grid(column=6, row=0, padx=padx, pady=pady, rowspan=2)

    def update_text(self):
        self.mode_text.set("Draw mode" if MODE.get() == DRAW else "Remove mode")
        if MODE.get() == DRAW:
            self.class_text.set("Petite" if PETITE.get() else "Grande")
            self.delSelButton.config(state='disabled')
            self.petButton.config(state='normal')
            self.grandButton.config(state='normal')
        elif MODE.get() == REMOVE:
            self.class_text.set("")
            self.delSelButton.config(state='normal')
            self.petButton.config(state='disabled')
            self.grandButton.config(state='disabled')

    def saveButtonClick(self):

        self.iframe.annotations[IMG_ID.get()] = [bbox.convert_to_ann() for bbox in self.iframe.bboxes]
        self.iframe.save_coco_annotations(PATH_TO_SAVE)
        print('Saved to {}'.format(PATH_TO_SAVE))

    def leftButtonClick(self):
        self.iframe.save_annotation_state()
        if IMG_ID.get() > 0:
            IMG_ID.set(IMG_ID.get() - 1)
            self.imgid_text.set('{}'.format(IMG_ID.get()))
            self.iframe.bboxes = None
            self.iframe.chose_data()
            self.iframe.delete_canvas_annotations()
            self.iframe.imscale = 1.0

            self.iframe.draw_complete_img()
            self.iframe.draw_ann()
            self.iframe.canvas.delete('container')
            self.iframe.create_container()

            self.iframe.shrink_to_fit_screen()

    def rightButtonClick(self):
        self.iframe.save_annotation_state()
        if IMG_ID.get() < num_img(self.iframe.data) - 1:
            IMG_ID.set(IMG_ID.get() + 1)
            self.imgid_text.set('{}'.format(IMG_ID.get()))
            self.iframe.bboxes = None
            self.iframe.chose_data()
            self.iframe.delete_canvas_annotations()
            self.iframe.imscale = 1.0

            self.iframe.draw_complete_img()
            self.iframe.draw_ann()
            self.iframe.canvas.delete('container')
            self.iframe.create_container()

            self.iframe.shrink_to_fit_screen()

    def remButtonClick(self):
        MODE.set(REMOVE)
        self.update_text()

    def drawButtonClick(self):
        MODE.set(DRAW)
        self.update_text()

    def petButtonClick(self):
        PETITE.set(1)
        self.update_text()

    def grandButtonClick(self):
        PETITE.set(0)
        self.update_text()

    def delSelButtonClick(self):
        if MODE.get() == REMOVE:
            for bbox in self.iframe.selected_bboxes:
                bbox.remove_from_canvas(self.iframe.canvas)
                self.iframe.bboxes.remove(bbox)
            self.iframe.selected_bboxes = []

    def keyHandler(self, event):
        if event.char.lower() == 'd':
            MODE.set(DRAW)

        if event.char.lower() == 'r':
            MODE.set(REMOVE)

        if event.char.lower() == 'p':
            PETITE.set(1)

        if event.char.lower() == 'g':
            PETITE.set(0)

        if event.char.lower() == 'i':
            self.iframe.key_zoom_in(event)

        if event.char.lower() == 'o':
            self.iframe.key_zoom_out(event)

        if (MODE.get() == REMOVE) and (event.keysym == 'Delete' or event.keysym == 'BackSpace'):
            for bbox in self.iframe.selected_bboxes:
                self.iframe.canvas.delete(bbox.drawn_obj)
                self.iframe.bboxes.remove(bbox)
            self.iframe.selected_bboxes = []

        self.update_text()


class BBox:
    def __init__(self, **kwargs):

        if len(kwargs) == 1:
            json_ann = kwargs['json_ann']

            self.x_start, self.y_start, self.x_end, self.y_end = (
                json_ann['bbox'][0],
                json_ann['bbox'][1],
                json_ann['bbox'][0] + json_ann['bbox'][2],
                json_ann['bbox'][1] + json_ann['bbox'][3]
            )
            self.x_start_orig, self.y_start_orig, self.x_end_orig, self.y_end_orig = (
                json_ann['bbox'][0],
                json_ann['bbox'][1],
                json_ann['bbox'][0] + json_ann['bbox'][2],
                json_ann['bbox'][1] + json_ann['bbox'][3]
            )
            self.category_name = json_ann['category_name']
            self.img_id = json_ann['image_id']
            self.score = json_ann['score']

            self.imscale = None
            self.drawn_obj = None

        elif len(kwargs) == 3:
            rect = kwargs['rect']
            frame = kwargs['frame']
            category_name = kwargs['category_name']

            self.imscale = frame.imscale
            self.x_start, self.y_start, self.x_end, self.y_end = frame.canvas.coords(rect)

            bbox = frame.canvas.bbox(frame.container)

            self.x_start_orig = (self.x_start - bbox[0]) / self.imscale
            self.y_start_orig = (self.y_start - bbox[1]) / self.imscale
            self.x_end_orig = (self.x_end - bbox[0]) / self.imscale
            self.y_end_orig = (self.y_end - bbox[1]) / self.imscale

            self.score = 1.0
            self.rescaled = True

            self.img_id = IMG_ID.get()
            self.drawn_obj = rect
            self.category_name = category_name

        else:
            print('BBOX class error!')
            print(**kwargs)

    def draw(self, frame):
        color = 'orange' if self.category_name == 'p' else 'blue'

        self.drawn_obj = frame.canvas.create_rectangle(self.x_start, self.y_start, self.x_end, self.y_end,
                                                       outline=color, width=4, tags='annotation_bbox')
        frame.canvas.lift(self.drawn_obj)
        frame.canvas.tag_bind(self.drawn_obj, '<Enter>', frame.bbox_hover_event)

    def remove_from_canvas(self, canvas):
        canvas.delete(self.drawn_obj)
        self.drawn_obj = None

    def convert_to_ann(self):
        json_ann = {"iscrowd": 0, "segmentation": [], "category_name": self.category_name,
                    "category_id": 1 if self.category_name == 'p' else 0, "score": self.score, "image_id": self.img_id,
                    'bbox': [
                        self.x_start_orig,
                        self.y_start_orig,
                        self.x_end_orig - self.x_start_orig,
                        self.y_end_orig - self.y_start_orig
                    ]}
        json_ann['area'] = json_ann['bbox'][2] * json_ann['bbox'][3]
        return json_ann


def num_img(data):
    return len(data['images']) if len(data['images']) > 0 else 1


def build_amend_GUI(input_path, output_path):
    global MODE
    global PETITE
    global IMG_ID
    global REMOVE
    global PATH_TO_SAVE
    global BBOX_INFO
    global MAX_SIZE
    global DRAW

    root = tk.Tk()
    root.title('petiteFinder')

    # handle UNIX/WINDOWS/OSX window handling differences
    try:
        root.state('zoomed')
    except tk.TclError:
        root.attributes('-zoomed', 1)

    PATH_TO_SAVE = output_path
    REMOVE = 0
    DRAW = 1
    MODE = IntVar(root, DRAW)  # Mode by default: DRAW or REMOVE
    PETITE = IntVar(root, 1)  # Petite or Grande in Draw Mode by default
    IMG_ID = IntVar(root, 0)  # IMG_ID by default
    BBOX_INFO = StringVar(root, '')  # bbox to show by default in info
    MAX_SIZE = (root.winfo_screenwidth(), root.winfo_screenheight())

    json_data = json.load(open(input_path))
    iframe = ImageFrame(root, json_data)
    bframe = ButtonsFrame(root, json_data, iframe)

    bframe.pack()
    iframe.pack(fill=BOTH, expand=1)
    root.mainloop()


if __name__ == "__main__":
    build_amend_GUI()
