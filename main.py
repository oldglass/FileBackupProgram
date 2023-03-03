import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtGui import *
import psutil
import time
import shutil
import tkinter
from tkinter import filedialog
# import pystray
# from pystray import MenuItem
# from pystray import Menu
# from PIL import Image

taskList = {}
whatStr = ["저장 하려는 폴더 선택", "백업 할 위치 선택"]
form_class = uic.loadUiType("FileBackupProgram.ui")[0]
dialog_class = uic.loadUiType("Setting.ui")[0]
dialog_class2 = uic.loadUiType("Add.ui")[0]
isCopying = False
copyValue = 0

def checkList():
    try:
        list = open("FBPList.txt", "r", encoding="UTF-8")
    except:
        list = open("FBPList.txt", "x")
        # print("check failed!")
        list.close()
        list = open("FBPList.txt", "r", encoding="UTF-8")

    while True:
        listdata = list.readline()
        if not listdata:
            break
        listdata = listdata[:-1]
        # print(listdata)
        listdata = listdata.split("/*/")
        # print(listdata[0])
        taskList[listdata[0]] = eval(listdata[1])
        # print(taskList.keys())
    list.close()


def writeList():
    list = open("FBPList.txt", "w", encoding="UTF-8")

    for i in taskList.keys():
        list.write(i + "/*/")
        list.writelines(str(taskList[i]))
        list.write("\n")
    list.close()


def addToList(name, folder, backup, isbackup):  # 0번째는 해당 프로그램 실행 여부, 1번째는 백업 여부,
    # 2번째는 백업 할 폴더경로, 3번째는 저장 할 경로, 4번째는 마지막으로 백업한 시간
    taskList[name] = [False, isbackup, folder, backup, 0]


def fileLocation(what):
    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", True)
    location = filedialog.askdirectory(initialdir="C:/", title=whatStr[what])
    # print(location)
    return location


def backupFolder(name, copylo, backuplo):
    value = taskList.get(name)
    timeformat = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    value[4] = timeformat
    programname = name[:len(name) - 4]
    finallo = backuplo + "/" + programname + "/FBP_" + timeformat
    count = 0
    print("before stop")
    # myWindow.worker.stop()
    print("before try")
    # pgWorker = progressWorker()
    # pgWorker.start()
    # print("backupLocation:", finallo)
    try:
        # shutil.copytree(copylo, finallo, copy_function=copytreeFunction)
        shutil.copytree(copylo, finallo)
        print("after copy1")
    except:
        count = count + 1
        # shutil.copytree(copylo, finallo + " (" + str(count) + ")", copy_function=copytreeFunction)
        shutil.copytree(copylo, finallo + " (" + str(count) + ")")
        print("after copy2")
    print("backup end")
    # myWindow.worker.start()
    #myWindow.viewDetail()
    print("endend")


def folderWalk(copylo):
    file_count = 0

    for (root, directories, files) in os.walk(copylo):
        '''
        for d in directories:
            dir = os.path.join(root, d)
            print(dir)
        '''
        for i in files:
            file_count += 1
    return file_count


def copytreeFunction(src, dst):
    global copyValue
    global isCopying

    if not isCopying:
        isCopying = True
    print("Copying {0}".format(src))
    shutil.copy2(src, dst)
    copyValue += 1


class Worker(QThread):
    power = True
    stopbool = False

    def __init__(self):
        super().__init__()

    def run(self):
        while self.power:
            # print("power")
            if self.stopbool or len(taskList) == 0:
                continue
            start = time.time()
            processlist = []
            # tasklist_copy = copy.copy(taskList)
            # print(tasklist_copy)
            for i in psutil.process_iter():
                processlist.append(i.name())
            # print("@", len(set(processlist)))
            # print("$", set(taskList))
            comparelist = set(taskList) & set(processlist)
            # print("#", comparelist)
            for i in taskList:
                isrunning = False
                for j in comparelist:
                    if i in j:
                        isrunning = True
                if taskList[i][0] == isrunning:
                    continue
                taskList[i][0] = isrunning
                if taskList[i][1]:
                    backupFolder(i, taskList[i][2], taskList[i][3])
            end = time.time()
            print(f"{end - start:.5f} sec")

    def pause(self, real):
        if real == 0:
            self.stopbool = True
        else:
            self.power = False

    def restart(self, real):
        if real == 0:
            self.stopbool = False
        else:
            self.power = True
            worker = Worker()
            worker.start()

    def getstopbool(self):
        return self.stopbool

    def getpower(self):
        return self.power

    def stop(self):
        # self.stopcheck = True
        self.pause()
        self.power = False
        self.quit()


class ProgressWorker(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        name = myWindow.listBox.currentText()
        value = taskList.get(name)
        max_value = folderWalk(value[2])
        myWindow.pgCopy.setHidden(False)
        myWindow.pgCopy.setMaximum(max_value)
        myWindow.pgCopy.setValue(0)
        while myWindow.pgCopy.value() != max_value:
            myWindow.pgCopy.setValue(copyValue)
        myWindow.pgCopy.setHidden(True)

    def stop(self):
        self.quit()


''' 트레이 아이콘 띄우고 싶다
class TrayWorker(QThread):
    def __init__(self):
        super().__init__()
        self.image = Image.open("file_backup.png")
        self.menu = (MenuItem("FileBackupProgram", self.action), MenuItem("Exit", self.action))
        self.icon = pystray.Icon("FileBackupProgram", self.image, "Title", self.menu)

    def action(self):
        pass

    def run(self):
        self.icon.run()
        print("icon run")

    def stop(self):
        self.icon.stop()
'''



class AddWindow(QtWidgets.QDialog, dialog_class2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        processlist = []
        for i in psutil.process_iter():
            processlist.append(i.name())
        processlist = sorted(list(set(processlist)))
        # print(len(processlist))
        for i in processlist:
            self.taskListBox.addItem(i)
        self.folderTool.clicked.connect(self.folderLo)
        self.backupTool.clicked.connect(self.backupLo)
        self.cancelButton.clicked.connect(self.cancelbtn)
        self.saveButton.clicked.connect(self.savebtn)

    def folderLo(self):
        location = fileLocation(0)
        self.folderRouteLine.setText(location)

    def backupLo(self):
        location = fileLocation(1)
        self.backupRouteLine.setText(location)

    def cancelbtn(self):
        self.close()

    def savebtn(self):
        name = self.taskListBox.currentText()
        folder = self.folderRouteLine.text()
        backup = self.backupRouteLine.text()
        radio = self.yesRadio.isChecked()
        addToList(name, folder, backup, radio)
        self.close()
        writeList()
        myWindow.refresh()


class SettingWindow(QtWidgets.QDialog, dialog_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        name = myWindow.listBox.currentText()
        value = taskList.get(name)
        self.nameLabel.setText(name)
        self.folderRouteLine.setText(value[2])
        self.backupRouteLine.setText(value[3])
        self.yesRadio.setChecked(value[1])
        self.noRadio.setChecked(not value[1])
        self.folderTool.clicked.connect(self.folderLo)
        self.backupTool.clicked.connect(self.backupLo)
        self.cancelButton.clicked.connect(self.cancelbtn)
        self.saveButton.clicked.connect(self.savebtn)

    def folderLo(self):
        location = fileLocation(0)
        self.folderRouteLine.setText(location)

    def backupLo(self):
        location = fileLocation(1)
        self.backupRouteLine.setText(location)

    def cancelbtn(self):
        self.close()

    def savebtn(self):
        name = myWindow.listBox.currentText()
        folder = self.folderRouteLine.text()
        backup = self.backupRouteLine.text()
        radio = self.yesRadio.isChecked()
        # print(name)
        taskList[name] = [False, radio, folder, backup]
        # print(radio)
        self.close()
        writeList()
        myWindow.refresh()


class MyWindow(QtWidgets.QMainWindow, form_class):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.refresh()
        self.viewDetail()
        self.addButton.clicked.connect(self.addbtn)
        self.removeButton.clicked.connect(self.removebtn)
        self.settingButton.clicked.connect(self.settingbtn)
        self.backupButton.clicked.connect(self.manualBackup)
        self.stopButton.clicked.connect(self.toggleBackup)
        self.listBox.currentIndexChanged.connect(self.viewDetail)
        self.pgCopy.setHidden(True)


        # self.trayworker = TrayWorker()
        # self.trayworker.start()

    def addbtn(self):
        AddWindow().exec_()

    def removebtn(self):
        if not self.listBox.currentText() == "":
            myWindow.worker.pause()
            print("worker.pause")
            del(taskList[self.listBox.currentText()])
            print("list.delete")
            writeList()
            print("list.write")
            self.refresh()
            print("list.refresh")
            myWindow.worker.restart()
            print("worker.restart")

    def settingbtn(self):
        SettingWindow().exec_()

    def refresh(self):
        self.listBox.clear()
        print("클리어")
        for i in taskList.keys():
            self.listBox.addItem(i)

    def viewDetail(self):
        name = self.listBox.currentText()
        if name != "":
            value = taskList.get(name)
            self.textBox.setText("프로그램 이름: " + str(name) + "\n프로그램 실행 여부:" + str(value[0])
                                 + "\n저장할 폴더 경로: " + str(value[2]) + "\n백업시킬 경로: " + str(value[3])
                                 + "\n마지막 백업 시간: " + str(value[4]))
        else:
            self.textBox.setText("")

    def manualBackup(self):
        name = self.listBox.currentText()
        value = taskList.get(name)
        backupFolder(name, value[2], value[3])
        # print("backup complete!")
        self.refresh()
        self.listBox.setCurrentText(name)

    def toggleBackup(self):
        if not self.worker.getstopbool():
            # print("getstopbool = false")
            self.worker.pause()
            self.stopButton.setText("백업 재개")
            self.isBackupLabel.setText("실시간 백업 작동여부: 아니오")
        else:
            # print("getstopbool = true")
            self.worker.restart()
            self.stopButton.setText("백업 정지")
            self.isBackupLabel.setText("실시간 백업 작동여부: 예")

    # def progress(self):


    def closeEvent(self, event):
        # print("종료이벤트")
        self.worker.stop()
        # print("워커 멈춤")
        for i in taskList.keys():
            taskList[i][0] = False
        # print("태스크리스트 초기화")
        writeList()
        # print("라이트리스트")
        # self.trayworker.stop()
        event.accept()


if __name__ == "__main__":
    checkList()
    app = QtWidgets.QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    worker = Worker()
    worker.start()
    app.exec_()
