from tkinter import *
from PIL import ImageTk, Image
import json

MAX_SIZE = (800, 800)
REMOVE = 0
DRAW = 1

MODE = IntVar
PETITE = IntVar
IMG_ID = IntVar
PATH_TO_SAVE = ""
JSON_DATA = {}


def is_within_box(x, y, bbox):
    """Checking if the x,y point is within the box"""
    if (bbox.x_start <= x <= bbox.x_end) and (bbox.y_start <= y <= bbox.y_end):
        return True
    else:
        return False


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

            self.rescaled = False
            self.ratio = None
            self.drawn_obj = None

        elif len(kwargs) == 3:
            rect = kwargs['rect']
            frame = kwargs['frame']
            category_name = kwargs['category_name']

            self.ratio = frame.ratio

            self.x_start, self.y_start, self.x_end, self.y_end = frame.canvas.coords(rect)
            self.x_start_orig = int(self.x_start / self.ratio)
            self.y_start_orig = int(self.y_start / self.ratio)
            self.x_end_orig = int(self.x_end / self.ratio)
            self.y_end_orig = int(self.y_end / self.ratio)
            self.score = 1.0
            self.rescaled = True

            self.img_id = IMG_ID.get()
            self.drawn_obj = rect
            self.category_name = category_name

        else:
            print('BBOX class error!')
            print(**kwargs)

    def rescale(self, ratio):
        self.x_start *= ratio
        self.y_start *= ratio
        self.x_end *= ratio
        self.y_end *= ratio
        self.ratio = ratio
        self.rescaled = True

    def draw(self, frame):
        color = 'orange' if self.category_name == 'p' else 'blue'
        if not self.rescaled:
            self.rescale(frame.ratio)
        self.drawn_obj = frame.canvas.create_rectangle(self.x_start, self.y_start, self.x_end, self.y_end,
                                                       outline=color, width=4)

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


class ButtonsFrame(Frame):
    def __init__(self, master, data, iframe):
        Frame.__init__(self, master=None)
        self.iframe = iframe

        self.leftButton = Button(self, command=self.leftButtonClick, text="<")
        self.rightButton = Button(self, command=self.rightButtonClick, text=">")
        self.saveButton = Button(self, command=self.saveButtonClick, text="Save")
        self.remButton = Button(self, command=self.remButtonClick, text="Remove Mode")
        self.drawButton = Button(self, command=self.drawButtonClick, text="Draw Mode")
        self.delSelButton = Button(self, command=self.delSelButtonClick, text="Delete selected", state='disabled')
        self.petButton = Button(self, command=self.petButtonClick, text="Petite")
        self.grandButton = Button(self, command=self.grandButtonClick, text="Grande")

        self.master.bind("<Key>", self.keyHandler)

        self.mode_text = StringVar()
        self.class_text = StringVar()
        self.update_text()
        self.imgid_text = StringVar(self, str(IMG_ID.get()))

        self.modeLabel = Label(self, textvariable=self.mode_text)
        self.imgidLabel = Label(self, textvariable=self.imgid_text)
        self.classLabel = Label(self, textvariable=self.class_text)

        self.leftButton.pack(fill=Y, side=LEFT)
        self.imgidLabel.pack(fill=Y, side=LEFT)
        self.rightButton.pack(fill=Y, side=LEFT)
        self.saveButton.pack(fill=Y, side=LEFT)
        self.remButton.pack(fill=Y, side=LEFT)
        self.drawButton.pack(fill=Y, side=LEFT)
        self.delSelButton.pack(fill=Y, side=LEFT)
        self.petButton.pack(fill=Y, side=LEFT)
        self.grandButton.pack(fill=Y, side=LEFT)
        self.modeLabel.pack(fill=Y, side=LEFT, padx=(10, 10), pady=(10, 10))
        self.classLabel.pack(fill=Y, side=LEFT, padx=(10, 10), pady=(10, 10))

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
        if IMG_ID.get() > 0:
            IMG_ID.set(IMG_ID.get() - 1)
            self.imgid_text.set('{}'.format(IMG_ID.get()))
            self.iframe.bboxes = None
            self.iframe.chose_data()
            self.iframe.draw_img()
            self.iframe.draw_ann()

    def rightButtonClick(self):
        if IMG_ID.get() < num_img(self.iframe.data) - 1:
            IMG_ID.set(IMG_ID.get() + 1)
            self.imgid_text.set('{}'.format(IMG_ID.get()))
            self.iframe.bboxes = None
            self.iframe.chose_data()
            self.iframe.draw_img()
            self.iframe.draw_ann()

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

        if (MODE.get() == REMOVE) and (event.keysym == 'Delete' or event.keysym == 'BackSpace'):
            for bbox in self.iframe.selected_bboxes:
                self.iframe.canvas.delete(bbox.drawn_obj)
                self.iframe.bboxes.remove(bbox)
            self.iframe.selected_bboxes = []

        self.update_text()


class ImageFrame(Frame):
    def __init__(self, master, data):
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
        self.ratio = None
        self.new_size = None

        self.bboxes = None
        self.selected_bboxes = []

        # chose an image -> annotations -> draw both
        self.chose_data()
        self.draw_img()
        self.draw_ann()

        # rectangle from the mouse drag
        self.temp_rect = None
        self.start_x = None
        self.start_y = None

        # Mouse response
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def create_canvas(self):
        """Crete a required canvas"""
        self.x = self.y = 0
        self.canvas = Canvas(self, cursor="cross")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.yscroll = Scrollbar(self, orient=VERTICAL)
        self.xscroll = Scrollbar(self, orient=HORIZONTAL)
        self.yscroll.config(command=self.canvas.yview)
        self.xscroll.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.yscroll.set)
        self.canvas.config(xscrollcommand=self.xscroll.set)

        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        self.yscroll.grid(row=0, column=1, stick=N + S)
        self.xscroll.grid(row=1, column=0, sticky=E + W)

    def chose_data(self):
        """
        Chose the image and annotations according to the global variable IMG_ID [controlled from the button panel]
        """
        self.image_annotations = self.annotations[IMG_ID.get()]
        self.image_fname = [datum['file_name'] for datum in self.data['images'] if datum['id'] == IMG_ID.get()][0]

    def draw_img(self):
        self.im = Image.open(self.image_fname)

        self.ratio = min(
            MAX_SIZE[0] / self.im.size[0],
            MAX_SIZE[1] / self.im.size[1]
        )

        self.new_size = [
            int(self.im.size[0] * self.ratio),
            int(self.im.size[1] * self.ratio)
        ]

        self.tk_im = ImageTk.PhotoImage(self.im.resize((self.new_size[0], self.new_size[1]), Image.ANTIALIAS))
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_im)
        self.canvas.config(scrollregion=(self.canvas.bbox(ALL)))

    def draw_ann(self):
        if not self.bboxes:
            self.bboxes = [BBox(json_ann=json_ann) for json_ann in self.image_annotations]

        for bbox in self.bboxes:
            bbox.draw(self)

    def parse_coco_annotations(self):
        """
        Parse coco dictionary and create an internal memory representation where annotations are grouped by the img_id
        """
        self.annotations = {}
        for img_id in range(num_img(self.data)):
            self.annotations[img_id] = [datum for datum in JSON_DATA['annotations'] if datum['image_id'] == img_id]

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

    def on_button_press(self, event):
        '''
        Create a rectangle on the left mouse button click [in a draw mode].
        Chose a bbox for deletion [in a remove mode]
        '''

        if MODE.get() == DRAW:
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)

            # create rectangle if not yet exist
            if not self.temp_rect:
                self.temp_rect = self.canvas.create_rectangle((self.x, self.y, 1, 1), outline='white')

        if MODE.get() == REMOVE:
            for bbox in self.bboxes:
                if is_within_box(event.x, event.y, bbox) and bbox not in self.selected_bboxes:
                    self.selected_bboxes.append(bbox)
                    self.canvas.itemconfig(bbox.drawn_obj, outline='red', fill='')

                elif is_within_box(event.x, event.y, bbox) and bbox in self.selected_bboxes:
                    self.selected_bboxes.remove(bbox)
                    if bbox.category_name == 'g':
                        self.canvas.itemconfig(bbox.drawn_obj, outline='blue', fill='')
                    else:
                        self.canvas.itemconfig(bbox.drawn_obj, outline='orange', fill='')

    def on_move_press(self, event):
        '''Extend the rectangle on the cursor move [only in a draw mode]'''

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
        '''Adding a bbox to the list [only in a draw mode]'''
        if MODE.get() == DRAW:
            if PETITE.get():
                category_name = 'p'
                self.canvas.itemconfig(self.temp_rect, outline='green', fill='')
            else:
                category_name = 'g'
                self.canvas.itemconfig(self.temp_rect, outline='blue', fill='')

            self.bboxes.append(BBox(rect=self.temp_rect, frame=self, category_name=category_name))
            self.temp_rect = None


def num_img(data):
    return len(data['images']) if len(data['images']) > 0 else 1


def build_amend_GUI(input_path, output_path):
    global MODE
    global PETITE
    global IMG_ID
    global JSON_DATA
    global MAX_SIZE
    global PATH_TO_SAVE

    window = Tk()
    window.title('petiteFinder')
    window.attributes('-zoomed', 1)

    MAX_SIZE = (window.winfo_screenwidth(), window.winfo_screenheight())

    JSON_DATA = json.load(open(input_path))

    PATH_TO_SAVE = output_path

    MODE = IntVar(window, DRAW)  # Mode by default: DRAW or REMOVE
    PETITE = IntVar(window, 1)  # Petite or Grande in Draw Mode by default
    IMG_ID = IntVar(window, 0)  # IMG_ID by default

    iframe = ImageFrame(window, JSON_DATA)
    bframe = ButtonsFrame(window, JSON_DATA, iframe)

    bframe.pack()
    iframe.pack(fill=BOTH, expand=1)

    window.mainloop()


if __name__ == "__main__":
    build_amend_GUI()
