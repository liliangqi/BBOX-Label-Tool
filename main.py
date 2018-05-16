
#--------------------------------------------------------------------------
# Name:        Person bounding box label and attribute tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Created:     06/06/2014
# Rectified:   05/11/2018  by Liangqi Li
#
#--------------------------------------------------------------------------
from __future__ import division
from tkinter import *
from tkinter import ttk
from PIL import Image as pilimg 
from PIL import ImageTk
import os
import glob
import random
from tkinter.filedialog import *

# colors for the bboxes
COLORS = ['red', 'blue', 'orange', 'yellow', 'pink', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256
# 指定缩放后的图像大小
DEST_SIZE = 1200, 900

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = False, height = False)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # all things that need to be writen to txt
        self.current_id = '1'
        self.current_class = 'person'
        self.current_difficult = 'easy'
        self.current_age = 0  # 3 choices
        self.current_gender = 0  # 2 choices
        self.current_direction = 0  # 3 choices
        self.current_sleeve = 0  # 2 choices
        self.current_coat = 0  # 5 choices
        self.current_pants_style = 0  # 3 choices
        self.current_pants = 0  # 3 choices
        self.current_shoes = 0  # 4 choices
        self.current_haircut = 0  # 3 choices
        self.current_hat = 0  # bool
        self.current_glasses = 0  # bool
        self.current_handbag = 0  # bool
        self.current_shoulderbag = 0  # bool
        self.current_backpack = 0  # bool
        self.current_front_res = 0  # bool
        self.current_longcoat = 0  # bool
        self.current_phone = 0  # bool

        self.attributes_dict = {
        '行人': 'person', '人脸': 'face', '简单': 'easy', '困难': 'hard',
        '小于18岁': 0, '18~60岁': 1, '大于60岁': 2, '男': 0, '女': 1, '正面': 0,
        '侧面': 1, '背面': 2, '长袖': 0, '短袖': 1, '都不是': 0, '条纹': 1,
        '图案': 2, '格子': 3, '披肩或马甲': 4, '长裤': 1, '短裤': 2, '裙子': 3,
        '靴子': 1, '皮鞋': 2, '运动鞋': 3, '短发': 0, '长发': 1, '光头': 2,
        '戴帽子': 3}


        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        self.entry = Listbox(self.frame, width=4, height=1)
        self.entry.grid(row=0, column=1, sticky=W+E)
        self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        self.ldBtn.grid(row = 0, column = 2, sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 30, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)
        self.btnDel = Button(self.frame, text = 'Delete',
            command = self.delBBox)
        self.btnDel.grid(row = 3, column = 2, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'ClearAll',
            command = self.clearBBox)
        self.btnClear.grid(row=4, column=2, sticky=W+E+N) 
        
        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 8, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, 
            command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, 
            command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go',
            command = self.gotoImage)
        self.goBtn.pack(side = LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 10)
        self.egPanel.grid(row = 1, column = 0, rowspan = 5, sticky = N)
        self.tmpLabel2 = Label(self.egPanel, text = "Examples:")
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(10, weight = 1)

        # for debugging
##        self.setImage()
##        self.loadDir()

    def loadDir(self):
        '''
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
        '''
        self.parent.focus()
        self.imageDir = askdirectory()
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        self.entry.insert(0, self.imageDir)
        if len(self.imageList) == 0:
            print('No .jpg images found in the specified dir!')
            return   

        # set up output dir
        self.outDir = self.imageDir
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        
        labeledPicList = glob.glob(os.path.join(self.outDir, '*.txt'))
        
        for label in labeledPicList:
            data = open(label, 'r')
            if '0\n' == data.read():
                data.close()
                continue
            data.close()
            picture = label.replace('Labels', 'Images').replace('.txt', '.jpg')
            if picture in self.imageList:
                self.imageList.remove(picture)

        # load example bboxes
        self.egDir = os.path.join(self.outDir, '..')
        filelist = glob.glob(os.path.join(self.egDir, '*.jpg'))
        filelist.extend(glob.glob(os.path.join(self.egDir, '*.png')))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = pilimg.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, pilimg.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image=self.egList[-1], width=SIZE[0],
                height=SIZE[1])


        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)
        self.loadImage()
        print('%d images loaded from %s' %(self.total, self.imageDir))

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        pil_image = pilimg.open(imagepath)

        # 缩放到指定大小
        resize_image = pil_image.resize((DEST_SIZE[0], DEST_SIZE[1]),
            pilimg.ANTIALIAS)

        self.img = resize_image
        self.imgSize = self.img.size
        self.truesize = pil_image.size
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), 
            height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # 载入图片以后的键盘响应
        # press <Espace> to cancel current bbox
        self.parent.bind("<Escape>", self.cancelBBox)
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage)  # press 'a' to go backforward
        self.parent.bind("d", self.nextImage)  # press 'd' to go forward

        # 每次load进新的图片时初始化person和hard
        self.current_id = '1'
        self.current_difficult = 'easy'
        self.current_class = 'person'

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0

        # 再次标记某张图片时从对应的txt文件里读入已有的bbox
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    # 添加两种bbox，tbbox用于添加入txt文件，tmp用于画框
                    tbbox = [t.strip() for t in line.split()]
                    tmp = tbbox[:] # 取一个切片防止tbbox被更改

                    rate0 = DEST_SIZE[0]/self.truesize[0]
                    rate1 = DEST_SIZE[1]/self.truesize[1]
                    tmp[-4] = int(int(tmp[-4]) * rate0)
                    tmp[-3] = int(int(tmp[-3]) * rate1)
                    tmp[-2] = int(int(tmp[-2]) * rate0)
                    tmp[-1] = int(int(tmp[-1]) * rate1)

                    self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(
                        tmp[-4], tmp[-3], tmp[-2], tmp[-1], width = 2,
                        outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])

                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, 'p%s %s (%s, %s) -> (%s, %s)' % \
                        (tbbox[0], tbbox[1], tbbox[-4], tbbox[-3], tbbox[-2],
                            tbbox[-1]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1,
                        fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' %len(self.bboxList))
            for bbox in self.bboxList:
                tx0 = int(bbox[-4] * self.truesize[0]/DEST_SIZE[0])
                ty0 = int(bbox[-3] * self.truesize[1]/DEST_SIZE[1])
                tx1 = int(bbox[-2] * self.truesize[0]/DEST_SIZE[0])
                ty1 = int(bbox[-1] * self.truesize[1]/DEST_SIZE[1])
                tbbox = bbox[:-4] + (tx0, ty0, tx1, ty1)
                f.write(' '.join(map(str, tbbox)) + '\n')
        print('Image No. %d saved' %(self.cur))


    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'],
                event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'],
                event.y)
            if x2 > self.imgSize[0]:
                x2 = self.imgSize[0]
            if y2 > self.imgSize[1]:
                y2 = self.imgSize[1]    

            tx0 = int(x1 * self.truesize[0]/DEST_SIZE[0])
            ty0 = int(y1 * self.truesize[1]/DEST_SIZE[1])
            tx1 = int(x2 * self.truesize[0]/DEST_SIZE[0])
            ty1 = int(y2 * self.truesize[1]/DEST_SIZE[1])

            tbbox = (tx0, ty0, tx1, ty1)
            bbox = (x1, y1, x2, y2)

            self.pop_new_window(tbbox, bbox)

        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y,
                self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x,
                self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'],
                self.STATE['y'], event.x, event.y, width = 2, 
                outline = COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def prevImage(self, event=None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event=None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()

    def pop_new_window(self, tbbox, bbox):

        def complete_choose():
            # set value for each box
            self.current_id = id_chosen.get()
            self.current_class = self.attributes_dict[clas_chosen.get()]
            self.current_difficult = self.attributes_dict[
                difficulty_chosen.get()]
            self.current_age = self.attributes_dict[age_chosen.get()]
            self.current_gender = self.attributes_dict[gender_chosen.get()]
            self.current_direction = self.attributes_dict[
                direnction_chosen.get()]
            self.current_sleeve = self.attributes_dict[sleeve_chosen.get()]
            self.current_coat = self.attributes_dict[coat_chosen.get()]
            self.current_pants_style = self.attributes_dict[
                pants_style_chosen.get()]
            self.current_pants = self.attributes_dict[pants_chosen.get()]
            self.current_shoes = self.attributes_dict[shoes_chosen.get()]
            self.current_haircut = self.attributes_dict[haircut_chosen.get()]
            # Add to bboxList
            all_attributes = (
                self.current_id, self.current_class, self.current_difficult,
                self.current_age, self.current_gender, self.current_direction,
                self.current_sleeve, self.current_coat,
                self.current_pants_style, self.current_pants,
                self.current_shoes, self.current_haircut, self.current_glasses,
                self.current_handbag, self.current_shoulderbag,
                self.current_backpack, self.current_front_res,
                self.current_longcoat, self.current_phone, x1, y1, x2, y2)
            self.bboxList.append(all_attributes)
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, 'p%s %s (%d, %d) -> (%d, %d)' %\
                (self.current_id, self.current_class, tx0, ty0, tx1, ty1))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, 
                fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
            info_window.destroy()

        tx0, ty0, tx1, ty1 = tbbox
        x1, y1, x2, y2 = bbox

        info_window = Toplevel(self.parent)
        info_window.geometry('450x300')
        info_window.title('选择属性')

        ttk.Label(info_window, text="ID").grid(column=0, row=0)
        id_num = StringVar()
        id_chosen = ttk.Combobox(info_window, width=12, textvariable=id_num,
            state='readonly')
        id_chosen['values'] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        id_chosen.grid(column=1, row=0)
        id_chosen.current(0)

        ttk.Label(info_window, text="种类").grid(column=2, row=0)
        clas = StringVar()
        clas_chosen = ttk.Combobox(info_window, width=12, textvariable=clas,
            state='readonly')
        clas_chosen['values'] = ('行人', '人脸')
        clas_chosen.grid(column=3, row=0)
        clas_chosen.current(0)

        ttk.Label(info_window, text="难度").grid(column=0, row=1)
        difficulty = StringVar()
        difficulty_chosen = ttk.Combobox(info_window, width=12,
            textvariable=difficulty, state='readonly')
        difficulty_chosen['values'] = ('简单', '困难')
        difficulty_chosen.grid(column=1, row=1)
        difficulty_chosen.current(0)

        ttk.Label(info_window, text="年龄").grid(column=2, row=1)
        age = StringVar()
        age_chosen = ttk.Combobox(info_window, width=12, textvariable=age,
            state='readonly')
        age_chosen['values'] = ('小于18岁', '18~60岁', '大于60岁')
        age_chosen.grid(column=3, row=1)
        age_chosen.current(0)

        ttk.Label(info_window, text="性别").grid(column=0, row=2)
        gender = StringVar()
        gender_chosen = ttk.Combobox(info_window, width=12,
            textvariable=gender, state='readonly')
        gender_chosen['values'] = ('男', '女')
        gender_chosen.grid(column=1, row=2)
        gender_chosen.current(0)

        ttk.Label(info_window, text="朝向").grid(column=2, row=2)
        direnction = StringVar()
        direnction_chosen = ttk.Combobox(info_window, width=12,
            textvariable=direnction, state='readonly')
        direnction_chosen['values'] = ('正面', '侧面', '背面')
        direnction_chosen.grid(column=3, row=2)
        direnction_chosen.current(0)

        ttk.Label(info_window, text="袖子").grid(column=0, row=3)
        sleeve = StringVar()
        sleeve_chosen = ttk.Combobox(info_window, width=12,
            textvariable=sleeve, state='readonly')
        sleeve_chosen['values'] = ('长袖', '短袖')
        sleeve_chosen.grid(column=1, row=3)
        sleeve_chosen.current(0)

        ttk.Label(info_window, text="上衣装饰").grid(column=2, row=3)
        coat = StringVar()
        coat_chosen = ttk.Combobox(info_window, width=12, textvariable=coat,
            state='readonly')
        coat_chosen['values'] = ('都不是', '条纹', '图案', '格子', '披肩或马甲')
        coat_chosen.grid(column=3, row=3)
        coat_chosen.current(0)

        ttk.Label(info_window, text="下身装饰").grid(column=0, row=4)
        pants_style = StringVar()
        pants_style_chosen = ttk.Combobox(info_window, width=12,
            textvariable=pants_style, state='readonly')
        pants_style_chosen['values'] = ('都不是', '条纹', '图案')
        pants_style_chosen.grid(column=1, row=4)
        pants_style_chosen.current(0)

        ttk.Label(info_window, text="裤子类型").grid(column=2, row=4)
        pants = StringVar()
        pants_chosen = ttk.Combobox(info_window, width=12, textvariable=pants,
            state='readonly')
        pants_chosen['values'] = ('都不是', '长裤', '短裤', '裙子')
        pants_chosen.grid(column=3, row=4)
        pants_chosen.current(0)

        ttk.Label(info_window, text="鞋子类型").grid(column=0, row=5)
        shoes = StringVar()
        shoes_chosen = ttk.Combobox(info_window, width=12, textvariable=shoes,
            state='readonly')
        shoes_chosen['values'] = ('都不是', '靴子', '皮鞋', '运动鞋')
        shoes_chosen.grid(column=1, row=5)
        shoes_chosen.current(0)

        ttk.Label(info_window, text="发型").grid(column=2, row=5)
        haircut = StringVar()
        haircut_chosen = ttk.Combobox(info_window, width=12, textvariable=haircut,
            state='readonly')
        haircut_chosen['values'] = ('短发', '长发', '光头', '戴帽子')
        haircut_chosen.grid(column=3, row=5)
        haircut_chosen.current(0)

        ttk.Label(info_window, text="其他属性").grid(column=0, row=6)

        self.glasses = IntVar()
        check_glasses = Checkbutton(info_window, text="眼镜",
            variable=self.glasses, command=self.check_glasses_button)
        check_glasses.grid(column=0, row=7, sticky=W)

        self.handbag = IntVar()
        check_handbag = Checkbutton(info_window, text="手提包",
            variable=self.handbag, command=self.check_handbag_button)
        check_handbag.grid(column=1, row=7, sticky=W)

        self.shoulderbag = IntVar()
        check_shoulderbag = Checkbutton(info_window, text="单肩包",
            variable=self.shoulderbag, command=self.check_shoulderbag_button)
        check_shoulderbag.grid(column=2, row=7, sticky=W)

        self.backpack = IntVar()
        check_backpack = Checkbutton(info_window, text="背包",
            variable=self.backpack, command=self.check_backpack_button)
        check_backpack.grid(column=3, row=7, sticky=W)

        self.front_res = IntVar()
        check_front_res = Checkbutton(info_window, text="身前拿物品",
            variable=self.front_res, command=self.check_front_res_button)
        check_front_res.grid(column=0, row=8, sticky=W)

        self.longcoat = IntVar()
        check_longcoat = Checkbutton(info_window, text="长大衣",
            variable=self.longcoat, command=self.check_longcoat_button)
        check_longcoat.grid(column=1, row=8, sticky=W)

        self.phone = IntVar()
        check_phone = Checkbutton(info_window, text="打电话",
            variable=self.phone, command=self.check_phone_button)
        check_phone.grid(column=2, row=8, sticky=W)

        # ==================================================
        confirm_button = Button(info_window, text='确定', height=3, width=6,
            command=complete_choose)
        # confirm_button.grid(column=0, row=9, sticky=W)
        confirm_button.place(x=150, y=250)

    def check_glasses_button(self):
        self.current_glasses = self.glasses.get()

    def check_handbag_button(self):
        self.current_handbag = self.handbag.get()

    def check_shoulderbag_button(self):
        self.current_shoulderbag = self.shoulderbag.get()

    def check_backpack_button(self):
        self.current_backpack = self.backpack.get()

    def check_front_res_button(self):
        self.current_front_res = self.front_res.get()

    def check_longcoat_button(self):
        self.current_longcoat = self.longcoat.get()

    def check_phone_button(self):
        self.current_phone = self.phone.get()


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()