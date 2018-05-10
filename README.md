# 配置所需软件

## MacOS环境

1. 进入[Anaconda下载官网](https://www.anaconda.com/download/)，选择**macOS**，然后选择**Python 3.6**版本

2. 这里有两种安装方式，一种是图形界面安装，另一种是命令行安装，这里我们选择图形界面安装，点击绿色的图标**Download**

   ![](http://oxg3si0yz.bkt.clouddn.com/1.png)

   ​

3. 下载完成后打开**Anaconda3-5.0.0-MacOSX-x86_64.pkg**

   ![](http://oxg3si0yz.bkt.clouddn.com/2.png)

4. 按照安装提示完成安装，无需更改**目的卷宗**，它会自动安装到你的主文件夹下

5. 安装完成后我们能够发现在**~/.bash_profile**文件中增加了两行

   ```shell
   # added by Anaconda3 4.4.0 installer
   export PATH="Users/yourname/anaconda/bin:$PATH"
   ```

   这里是完成了环境变量的配置，要使其生效，则在终端输入`source ~/.bash_profile`即可。

6. 在终端中输入`python`，弹出如下信息则说明安装成功。

![](http://oxg3si0yz.bkt.clouddn.com/3.png)

## Windows环境

1. 进入[Anaconda下载官网](https://www.anaconda.com/download/)，选择**Windows**，然后选择**Python 3.6**版本

2. Windows对应的安装方式只有图形界面安装，根据自己计算机和系统的位数选择32位或64位安装包下载即可

3. 打开刚才下载的**Anaconda3-5.0.0-Windows-x86_64.exe**

   <img src="http://oxg3si0yz.bkt.clouddn.com/4.png" width="600px"/>

4. **Destination Folder**无需设置，默认为C盘，如有需要可进行更改，但要记住安装目录

5. 勾选以下两项，将Anaconda3加入环境变量并将Anaconda3作为默认的Python3.6

   <img src="http://oxg3si0yz.bkt.clouddn.com/5.png" width="600px"/>

6. 使用`cmd`命令呼出终端界面，输入`python`，弹出如下信息则说明安装成功。

   ![](http://oxg3si0yz.bkt.clouddn.com/6.png)

# 标记工具使用方法

1. 解压`BBOX-Label-Tool.zip`

2. 修改源代码第23行，改为适合自己屏幕大小的分辨率（例如24英寸左右的屏幕设置为`1200, 900`，而13英寸的屏幕则设置为`720, 540`较为适宜）

3. 在终端中cd到该py文件的目录下，然后运行该脚本

   ```shell
   cd xxx/BBOX-Label-Tool # 你存放的目录
   python main.py
   ```

   弹出的界面如下所示

   ![](http://oxg3si0yz.bkt.clouddn.com/bbox1.png)

4. 点击右上角的**Load**按钮载入需要标注的图片的**文件夹**，然后所有该文件夹下的图片都会被载入

   ![](http://oxg3si0yz.bkt.clouddn.com/ltchooseDir.png)

5. 载入后GUI界面上会自动显示目标行人的example和第一张图片，我们即可开始使用鼠标画框

   - 鼠标点击第一下是开始画框，点击第二下是确定框
   - 点击第二下之后会弹出一个属性选择框，下拉菜单的内容**必须**手动选择，复选的选项根据情况判断是否选中

   ![](http://oxg3si0yz.bkt.clouddn.com/bbox2.png)

6. 关于属性的说明：

   1. ID：行人的编号，选择范围从1到10，需注意只有当前所选行人或人脸的样本与左边小图所示的样本是**同一个人**才能选择1，否则选择2到10；但在同一个文件夹下的所有图片中出现的所有行人应保持序号一致（例如这里将红色羽绒服大叔标记为2号，那么如果下一张图片中又出现了该大叔，仍需标记为2号）
   2. 种类：行人或人脸，容易理解，需注意同一个行人与其人脸的一致性，若行人是背对镜头则不标记其人脸；除此之外，出现的正脸和侧脸都要标出来
   3. 难度：可选简单或困难，表示识别出这个行人或人脸的难易程度，主观判断即可
   4. 其他的属性较简单，不再一一说明
   5. 全部属性选择完成以后点击*确定*按钮，完成当前行人/人脸的标注

7. 若标记起始点选择错误，可使用**Esc**键取消；若画成的框有问题，可以在右侧的list中点击有问题的框，按下面的**Delete**按钮删除，或按**Clear All**按钮清空所有的框

8. 标注完该文件夹的一张图片后，可使用左下角的**Next >>**按钮或键盘上的**D**键载入下一张图片开始标注；同理可使用左下角的**<< Prev**按钮或键盘上的**A**键重新载入之前标记过的图片进行更改

   **注意**：标记完当前文件夹下的所有图片后仍需按**D**键或**A**键对标记结果进行保存（保存为txt文件）

9. 处理完该文件夹下所有的图片后可以按GUI界面右上角的**Load**重新载入另一个文件夹

10. 若要重新标记某个已经标注过的文件夹下的图片，需先将该文件夹下的txt文件删除，否则不会读取该文件夹下的任何图片

---

# 数据集结构

　　原始数据集为mp4视频数据，目前已经全部转为jpg图片格式，结构如下图所示

![](http://oxg3si0yz.bkt.clouddn.com/ltdatasetStrcut.png)

　　数据集分为五个**dataset1**、**dataset2**、**dataset3**、**dataset4**和**dataset5**，每个dataset中又包含若干子文件夹，这些子文件夹每个都对应一个主要的person，比如当前选中的**./dataset1/13/**文件夹，有三个视频文件转化而来的图片文件夹和一张单独的图片（最下方的**P0020160...000432.jpg**），这张图片将用作example。
