标注工具源码及部分解析

　　该工具由Python语言编写（Python3），主要使用了tkinter库来进行GUI界面设计。

    #-------------------------------------------------------------------------------
    # Name:        Object bounding box label tool
    # Purpose:     Label object bboxes for ImageNet Detection data
    # Created:     06/06/2014
    # Rectified:   09/29/2017
    #
    #-------------------------------------------------------------------------------
    from __future__ import division
    from tkinter import *
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
    
    classLabels = ['1', '2', '3', '4', '5', '6', '7', '8']
    hardLabels = ['easy', 'hard', 'very']
    
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
            self.currentClass = '1'
            self.currentHard = 'easy'
    
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
            
            #select class type
            self.classPanel = Frame(self.frame)
            self.classPanel.grid(row=5, column=0, columnspan=10, sticky=W+E)
            label = Label(self.classPanel, text='person:')
            label.grid(row=5, column=1, sticky = W+N)
           
            self.classbox = Listbox(self.classPanel, width=4, height=2)
            self.classbox.grid(row=5,column=2)
            self.classbox.insert(0, '1')
            self.classbox.itemconfig(0, fg=COLORS[0])
            for each in range(len(classLabels)):
                function = 'select' + classLabels[each]
                print(classLabels[each])
                btnMat = Button(self.classPanel, text=classLabels[each],
                    command=getattr(self, function))
                btnMat.grid(row = 5, column = each + 3)
            
            #select hard type
            self.hardPanel = Frame(self.frame)
            self.hardPanel.grid(row=5, column=2, columnspan=4, sticky=W+E)
            hard = Label(self.hardPanel, text='hard:')
            hard.grid(row=5, column=3, sticky = W+N)
           
            self.hard = Listbox(self.hardPanel, width=4, height=2)
            self.hard.grid(row=5,column=4)
            self.hard.insert(0, 'easy')
            self.hard.itemconfig(0, fg=COLORS[1])
            for each in range(len(hardLabels)):
                function = 'choose_' + hardLabels[each]
                print(classLabels[each])
                btnMat = Button(self.hardPanel, text=hardLabels[each],
                    command=getattr(self, function))
                btnMat.grid(row = 5, column = each + 5)
            
            
            # control panel for image navigation
            self.ctrPanel = Frame(self.frame)
            self.ctrPanel.grid(row = 6, column = 1, columnspan = 2, sticky = W+E)
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
            #self.category = askdirectory()
    ##        if not os.path.isdir(s):
    ##            tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
    ##            return
            # get image list
            # self.imageDir = os.path.join(r'./Images', '%d' %(self.category))
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
                self.egLabels[i].config(image=self.egList[-1], width=SIZE[0], height=SIZE[1])
    
    
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
            self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
            self.parent.bind("s", self.cancelBBox)
            self.parent.bind("a", self.prevImage) # press 'a' to go backforward
            self.parent.bind("d", self.nextImage) # press 'd' to go forward
            self.parent.bind("1", self.select1)
            self.parent.bind("2", self.select2)
            self.parent.bind("3", self.select3)
            self.parent.bind("4", self.select4)
            self.parent.bind("5", self.select5)
            self.parent.bind("6", self.select6)
            self.parent.bind("7", self.select7)
            self.parent.bind("8", self.select8)
            self.parent.bind("e", self.choose_easy)
            self.parent.bind("h", self.choose_hard)
            self.parent.bind("v", self.choose_very)
    
            # 每次load进新的图片时初始化person和hard
            self.currentClass = '1'
            self.currentHard = 'easy'
            self.classbox.delete(0,END)
            self.classbox.insert(0, '1')
            self.classbox.itemconfig(0, fg=COLORS[0])
            self.hard.delete(0,END)
            self.hard.insert(0, 'easy')
            self.hard.itemconfig(0, fg=COLORS[1])
    
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
                    tbbox = [bbox[0], bbox[1], tx0, ty0, tx1, ty1]
                    f.write(' '.join(map(str, tbbox)) + '\n')
            print('Image No. %d saved' %(self.cur))
    
    
        def mouseClick(self, event):
            if self.STATE['click'] == 0:
                self.STATE['x'], self.STATE['y'] = event.x, event.y
                #self.STATE['x'], self.STATE['y'] = self.imgSize[0], self.imgSize[1]
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
    
                self.bboxList.append((self.currentClass, self.currentHard, 
                    x1, y1, x2, y2))
                self.bboxIdList.append(self.bboxId)
                self.bboxId = None
                self.listbox.insert(END, 'p%s %s (%d, %d) -> (%d, %d)' %\
                    (self.currentClass, self.currentHard, tx0, ty0, tx1, ty1))
                self.listbox.itemconfig(len(self.bboxIdList) - 1, 
                    fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
    
                # 每画一个框personID自动加1
                if self.currentClass == '8':
                    self.currentClass = '2'
                else:
                    self.currentClass = str(int(self.currentClass) + 1)
                self.classbox.delete(0,END)
                self.classbox.insert(0, self.currentClass)
                self.classbox.itemconfig(0, fg=COLORS[0])
    
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
            
        def select1(self, event=None):
            self.currentClass = '1'
            self.classbox.delete(0,END)
            self.classbox.insert(0, '1')
            self.classbox.itemconfig(0,fg = COLORS[0])
        
        def select2(self, event=None):
            self.currentClass = '2'    
            self.classbox.delete(0,END)    
            self.classbox.insert(0, '2')
            self.classbox.itemconfig(0,fg = COLORS[0])
        
        def select3(self, event=None):
            self.currentClass = '3'    
            self.classbox.delete(0,END)    
            self.classbox.insert(0, '3')
            self.classbox.itemconfig(0,fg = COLORS[0])
            
        def select4(self, event=None):
            self.currentClass = '4'    
            self.classbox.delete(0,END)    
            self.classbox.insert(0, '4')
            self.classbox.itemconfig(0,fg = COLORS[0])
            
        def select5(self, event=None):
            self.currentClass = '5'
            self.classbox.delete(0,END)
            self.classbox.insert(0, '5')
            self.classbox.itemconfig(0,fg = COLORS[0])
            
        def select6(self, event=None):
            self.currentClass = '6'
            self.classbox.delete(0,END)    
            self.classbox.insert(0, '6')
            self.classbox.itemconfig(0,fg = COLORS[0])
            
        def select7(self, event=None):
            self.currentClass = '7'    
            self.classbox.delete(0,END)    
            self.classbox.insert(0, '7')
            self.classbox.itemconfig(0,fg = COLORS[0])
            
        def select8(self, event=None):
            self.currentClass = '8'    
            self.classbox.delete(0,END)    
            self.classbox.insert(0, '8')
            self.classbox.itemconfig(0,fg = COLORS[0])
    
        def choose_easy(self, event=None):
            self.currentHard = 'easy'
            self.hard.delete(0,END)
            self.hard.insert(0, 'easy')
            self.hard.itemconfig(0,fg = COLORS[1])
    
        def choose_hard(self, event=None):
            self.currentHard = 'hard'
            self.hard.delete(0,END)
            self.hard.insert(0, 'hard')
            self.hard.itemconfig(0,fg = COLORS[1])
    
        def choose_very(self, event=None):
            self.currentHard = 'very'
            self.hard.delete(0,END)
            self.hard.insert(0, 'very')
            self.hard.itemconfig(0,fg = COLORS[1])
    
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
    
    ##    def setImage(self, imagepath = r'test2.png'):
    ##        self.img = Image.open(imagepath)
    ##        self.tkimg = ImageTk.PhotoImage(self.img)
    ##        self.mainPanel.config(width = self.tkimg.width())
    ##        self.mainPanel.config(height = self.tkimg.height())
    ##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
    
    if __name__ == '__main__':
        root = Tk()
        tool = LabelTool(root)
        root.mainloop()

　　

　　由于某些图片分辨率过高，载入后会使得GUI界面显示不完全，故代码第23行设置了缩放后图片的大小，这里的分辨率需要按照个人显示屏的大小进行调整，例如24英寸左右的屏幕设置为1200, 900，而13英寸的屏幕则设置为720, 540较为适宜，这里的比例4:3是根据笔者数据集的原图1600:1200的分辨率来设置的。此处参考了Qiushi的想法。

　　而要进行行人重识别工作，就要将行人区分开来，所以代码第91行至第106行设置了行人的ID编号，考虑到笔者的数据集中，同一张图像里出现的行人数大多在8个以内，故将ID设置为从1到8。可以用鼠标在GUI界面进行点击选择，也可以使用键盘数字1~8来进行选择。此处参考了达文喜的想法。

　　同时，因为存在遮挡、背光、行人像素过少等原因，行人的识别难度也有区别，我们在进行实验的时候必须要考虑到这些因素，因此代码第108行至第123行设置了bounding box里行人识别的难易程度，分为easy、hard和very，分别表示容易识别、难以识别和极难识别。可以用鼠标在GUI界面进行选择，也可以使用键盘E、H或V来进行选择。

　　考虑到一张图像中某个行人不可能出现多次，所以代码第353行至第360行进行了设置。每当我们框出一个person，ID就会自动加一；如果前一个框的ID是8，则当前框的ID为1。

---

使用方法

1. 修改源代码第23行，改为适合自己屏幕大小的分辨率
2. 代码第183行设置了目标图像格式为jpg，如需标注png图片可自行更改
3. 将该源码保存为py文件，比如labelbbox.py，保存到工程目录下（其实任意位置都可以）
4. 在终端中cd到该py文件的目录下，然后运行该脚本
       cd XXX # 你存放的目录
       python labelbbox.py
   弹出的界面如下所示
   
5. 点击右上角的Load按钮载入需要标注的图片的文件夹，然后所有该文件夹下的图片都会被载入
   
6. 载入后GUI界面上会自动显示目标行人的example和第一张图片，我们即可开始使用鼠标画框
   - 画框时默认第一个框的ID为1，难易程度为easy，如需更改务必在画框前进行更改
   - 画第二个框及后续框的时候，每画一个，ID会自动加一，但难易程度保持不变；亦即上一个框选择了hard，那么当前框的难易程度也默认为hard，如需更改务必在画框前进行更改
7. GUI界面的右侧有一个显示标注结果的list，每当框出一个人，就会显示该person的ID以及识别的难易程度，如下图所示
   
8. 若标记起始点选择错误，可使用Esc键取消；若画成的框有问题，可以在右侧的list中点击有问题的框，按下面的Delete按钮删除，或按Clear All按钮清空所有的框
9. 标注完该文件夹的一张图片后，可使用左下角的Next >>按钮或键盘上的D键载入下一张图片开始标注；同理可使用左下角的<< Prev按钮或键盘上的A键重新载入之前标记过的图片进行更改。注意每次新载入一张图片时，ID会自动变为1，难易程度会自动变为easy
10. 每当新载入图片（上一张或下一张）时，当前标注的结果都会在该图片所属的文件夹下被保存为一个txt文件
    
    文件名是由所标注的图片1.jpg得到，第一行的7表示一共有7个框，下面的7行是详细情况，各列分别表示的是(ID, difficulty, xmin, ymin, xmax, ymax)
11. 处理完该文件夹下所有的图片后可以按GUI界面右上角的Load重新载入另一个文件夹
