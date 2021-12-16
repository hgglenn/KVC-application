import tkinter
from tkinter import filedialog
from tkinter import ttk
from PIL import ImageTk, Image
import qrcode
from pyzbar.pyzbar import decode
import time
import threading

##
# @author Henry Glenn
# The purpose of this program is to create and read QR code package labels.

class KVCApp:
    def __init__(self):
        self.MAX_QR_LENGTH = 1000
        self._root = tkinter.Tk()
        self._root.configure(bg='blue')
        self._root.title("KVC Application")
        self._rootSize = (500, 600)
        self._root.geometry(f"{self._rootSize[0]}x{self._rootSize[1]}")

        s = ttk.Style()
        s.theme_use('default')
        s.configure('TNotebook.Tab', background="#ababab")
        s.map("TNotebook", background=[("selected", "#a3a3a3")])

        self._style = ttk.Style()
        self._style.configure('TNotebook.Tab', width=50, font=("URW Gothic L", "11", "normal"))

        self._tabControl = ttk.Notebook(self._root)

        self._finalLabelData = {}
        self._canUpdateLabel = True
        self._queueUpdateLabel = False

        # Initialize read label tab
        self._readTab = ttk.Frame(self._tabControl)

        self._nullImage = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xc8\x00\x00\x00\xc8\x08\x06\x00\x00\x00\xadX\xae\x9e\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x02\x14IDATx^\xed\xd31\x01\xc0 \x10\xc0\xc0o\xfd{\x86\x0e\x1d!\n\xee\x96(\xc8\xb3>\x03\x1c\xbd\x7f\x81\x03\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\x04\x83@0\x08\\\xcdlS\xd9\x05\x8c\x82\xcdR\xb7\x00\x00\x00\x00IEND\xaeB`\x82'
        self._userInputtedPhotoResized = None

        self._userInputtedPhoto = ImageTk.PhotoImage(data=self._nullImage)
        self._userInputtedPhotoButton = tkinter.Button(self._readTab,
                                                       text="Select image",
                                                       image=self._userInputtedPhoto,
                                                       height=200,
                                                       width=200,
                                                       compound=tkinter.CENTER,
                                                       command=self.userInputPhotoButtonPressed)
        self._labelTranslation = tkinter.Text(self._readTab,
                                              borderwidth=2,
                                              relief="sunken",
                                              height=3,
                                              width=25)
        self._labelTranslation.tag_configure("tag_name", justify='center')
        self._labelTranslation.insert(1.0, "No image selected")
        self._labelTranslation.tag_add("tag_name", "1.0", "end")
        self._labelTranslation.config(state="disabled")
        self._translatedText = ""

        self._labelSubOutput1 = tkinter.Text(self._readTab,
                                            state="disabled",
                                            borderwidth=2,
                                            height=1,
                                            width=25)

        self._labelSubOutput2 = tkinter.Text(self._readTab,
                                            state="disabled",
                                            borderwidth=2,
                                            height=1,
                                            width=25)

        self._labelSubOutput3 = tkinter.Text(self._readTab,
                                            state="disabled",
                                            borderwidth=2,
                                            height=1,
                                            width=25)

        self._labelSubOutput4 = tkinter.Text(self._readTab,
                                            state="disabled",
                                            borderwidth=2,
                                            height=1,
                                            width=25)

        self._labelSubOutput5 = tkinter.Text(self._readTab,
                                            state="disabled",
                                            borderwidth=2,
                                            height=1,
                                            width=25)

        self._labelSubOutputLabel1 = tkinter.Label(self._readTab,
                                                  text="Donor Full Name",
                                                  relief=tkinter.GROOVE)

        self._labelSubOutputLabel2 = tkinter.Label(self._readTab,
                                                  text="Recipient Full Name",
                                                  relief=tkinter.GROOVE)

        self._labelSubOutputLabel3 = tkinter.Label(self._readTab,
                                                  text="Sent from",
                                                  relief=tkinter.GROOVE)
        self._labelSubOutputLabel4 = tkinter.Label(self._readTab,
                                                  text="Sent to",
                                                  relief=tkinter.GROOVE)

        self._labelSubOutputLabel5 = tkinter.Label(self._readTab,
                                                  text="Gift Description",
                                                  relief=tkinter.GROOVE)

        self._labelSubOutput1.place(x=150, y=320)
        self._labelSubOutput2.place(x=150, y=360)
        self._labelSubOutput3.place(x=150, y=400)
        self._labelSubOutput4.place(x=150, y=440)
        self._labelSubOutput5.place(x=150, y=480)

        self._labelSubOutputLabel1.place(x=50, y=320)
        self._labelSubOutputLabel2.place(x=34, y=360)
        self._labelSubOutputLabel3.place(x=86, y=400)
        self._labelSubOutputLabel4.place(x=103, y=440)
        self._labelSubOutputLabel5.place(x=58, y=480)
        self._userInputtedPhotoButton.place(x=150, y=25)
        self._labelTranslation.place(x=150, y=235)
        self._tabControl.add(self._readTab, text="Read Label")

        # Initialize write label tab
        self._writeTab = ttk.Frame(self._tabControl)
        self._newLabelHolder = tkinter.Label(self._writeTab,
                                             borderwidth=2,
                                             relief="raised",
                                             height=200,
                                             width=200,
                                             compound=tkinter.CENTER)

        self._labelDataViewer = tkinter.Text(self._writeTab,
                                             borderwidth=2,
                                             relief="sunken",
                                             height=3,
                                             width=25)
        self._labelDataViewer.config(state="disabled")

        self._lengthLabel = tkinter.Label(self._writeTab,
                                          text="")

        self._labelDataSubInput1 = tkinter.Text(self._writeTab,
                                                borderwidth=2,
                                                relief="sunken",
                                                height=1,
                                                width=25)

        self._labelDataSubInput2 = tkinter.Text(self._writeTab,
                                                borderwidth=2,
                                                relief="sunken",
                                                height=1,
                                                width=25)

        self._labelDataSubInput3 = tkinter.Text(self._writeTab,
                                                borderwidth=2,
                                                relief="sunken",
                                                height=1,
                                                width=25)

        self._labelDataSubInput4 = tkinter.Text(self._writeTab,
                                                borderwidth=2,
                                                relief="sunken",
                                                height=1,
                                                width=25)

        self._labelDataSubInput5 = tkinter.Text(self._writeTab,
                                                borderwidth=2,
                                                relief="sunken",
                                                height=1,
                                                width=25)

        self._labelDataSubInput1.bind('<KeyPress>', self.updateLabels)
        self._labelDataSubInput1.bind('<KeyRelease>', self.updateLabels)
        self._labelDataSubInput2.bind('<KeyPress>', self.updateLabels)
        self._labelDataSubInput2.bind('<KeyRelease>', self.updateLabels)
        self._labelDataSubInput3.bind('<KeyPress>', self.updateLabels)
        self._labelDataSubInput3.bind('<KeyRelease>', self.updateLabels)
        self._labelDataSubInput4.bind('<KeyPress>', self.updateLabels)
        self._labelDataSubInput4.bind('<KeyRelease>', self.updateLabels)
        self._labelDataSubInput5.bind('<KeyPress>', self.updateLabels)
        self._labelDataSubInput5.bind('<KeyRelease>', self.updateLabels)

        self._labelSubInputLabel1 = tkinter.Label(self._writeTab,
                                                  text="Donor Full Name",
                                                  relief=tkinter.GROOVE)

        self._labelSubInputLabel2 = tkinter.Label(self._writeTab,
                                                  text="Recipient Full Name",
                                                  relief=tkinter.GROOVE)

        self._labelSubInputLabel3 = tkinter.Label(self._writeTab,
                                                  text="Sent from",
                                                  relief=tkinter.GROOVE)
        self._labelSubInputLabel4 = tkinter.Label(self._writeTab,
                                                  text="Sent to",
                                                  relief=tkinter.GROOVE)

        self._labelSubInputLabel5 = tkinter.Label(self._writeTab,
                                                  text="Gift Description",
                                                  relief=tkinter.GROOVE)

        self._lengthLabel = tkinter.Label(self._writeTab,
                                          text="",
                                          relief=tkinter.RIDGE)

        self._createLabelButton = tkinter.Button(self._writeTab,
                                                 text="Create Label",
                                                 height=2,
                                                 width=28,
                                                 command=self.createLabel)

        text = self._labelDataViewer.get("1.0", "end").strip()
        code = qrcode.make(text)
        label = code.get_image()
        label = label.resize((200, 200))
        self._newLabel = ImageTk.PhotoImage(label)
        self._newLabelHolder.config(image=self._newLabel)
        self._newLabelHolder.place(x=150, y=25)
        self._labelDataViewer.place(x=150, y=235)
        self._lengthLabel.place(x=150, y=290)

        self._labelDataSubInput1.place(x=150, y=320)
        self._labelDataSubInput2.place(x=150, y=360)
        self._labelDataSubInput3.place(x=150, y=400)
        self._labelDataSubInput4.place(x=150, y=440)
        self._labelDataSubInput5.place(x=150, y=480)

        self._labelSubInputLabel1.place(x=50, y=320)
        self._labelSubInputLabel2.place(x=34, y=360)
        self._labelSubInputLabel3.place(x=86, y=400)
        self._labelSubInputLabel4.place(x=103, y=440)
        self._labelSubInputLabel5.place(x=58, y=480)

        self._createLabelButton.place(x=150, y=520)
        self._tabControl.add(self._writeTab, text="Create Label")
        self._tabControl.pack(expand=1, fill="both")

        self.updateLabels(None, True)

        self._root.mainloop()

    def userInputPhotoButtonPressed(self):
        filename = filedialog.askopenfilename(filetypes=(("png files", "*.png"), ("All files", "*.*")))
        if filename != "":
            self._userInputtedPhotoResized = ImageTk.PhotoImage(image=Image.open(filename).resize((200, 200)))
            self._userInputtedPhotoButton.config(text="", image=self._userInputtedPhotoResized)

            data = decode(Image.open(filename))
            text = data[0][0].decode("utf-8")
            print(text)

            self._translatedText = text
            self._labelTranslation.config(state="normal")
            if self._translatedText == "":
                self._labelTranslation.delete(1.0, tkinter.END)
                self._labelTranslation.insert(1.0, "No data detected")
                self._labelTranslation.tag_add("tag_name", "1.0", "end")
            elif self._translatedText != "":
                self._labelTranslation.delete(1.0, tkinter.END)
                self._labelTranslation.insert(1.0, text)
            self._labelTranslation.config(state="disabled")


            outputLableData = self.convertToList(text)
            self._labelSubOutput1.config(state="normal")
            self._labelSubOutput1.delete(1.0, tkinter.END)
            self._labelSubOutput1.insert(1.0, str(outputLableData[0]))
            self._labelSubOutput1.config(state="disabled")

            self._labelSubOutput2.config(state="normal")
            self._labelSubOutput2.delete(1.0, tkinter.END)
            self._labelSubOutput2.insert(1.0, str(outputLableData[1]))
            self._labelSubOutput2.config(state="disabled")

            self._labelSubOutput3.config(state="normal")
            self._labelSubOutput3.delete(1.0, tkinter.END)
            self._labelSubOutput3.insert(1.0, str(outputLableData[2]))
            self._labelSubOutput3.config(state="disabled")

            self._labelSubOutput4.config(state="normal")
            self._labelSubOutput4.delete(1.0, tkinter.END)
            self._labelSubOutput4.insert(1.0, str(outputLableData[3]))
            self._labelSubOutput4.config(state="disabled")

            self._labelSubOutput5.config(state="normal")
            self._labelSubOutput5.delete(1.0, tkinter.END)
            self._labelSubOutput5.insert(1.0, str(outputLableData[4]))
            self._labelSubOutput5.config(state="disabled")

            print("Pass")


            pass

    def updateLabels(self, event, first=False):
        if self._canUpdateLabel is True:
            self.startQueue()
        if first is True:
            data1 = self._labelDataSubInput1.get("1.0", "end").strip()
            data2 = self._labelDataSubInput2.get("1.0", "end").strip()
            data3 = self._labelDataSubInput3.get("1.0", "end").strip()
            data4 = self._labelDataSubInput4.get("1.0", "end").strip()
            data5 = self._labelDataSubInput5.get("1.0", "end").strip()

            data1 = data1.replace("\n", ". ")
            data2 = data2.replace("\n", ". ")
            data3 = data3.replace("\n", ". ")
            data4 = data4.replace("\n", ". ")
            data5 = data5.replace("\n", ". ")

            self._finalLabelData = str(data1 + "\n" +
                                       data2 + "\n" +
                                       data3 + "\n" +
                                       data4 + "\n" +
                                       data5)
            text = str(self._finalLabelData)

            if str(self._finalLabelData) != self._labelDataViewer.get(1.0, tkinter.END).strip():
                length = len(text)
                if length > self.MAX_QR_LENGTH:
                    self._labelDataViewer.config(state="normal")
                    self._labelDataViewer.delete(1.0, tkinter.END)
                    self._labelDataViewer.insert(1.0, "Too much Data")
                    self._labelDataViewer.config(state="disabled")
                    self._lengthLabel.config(text=f"{length} / {self.MAX_QR_LENGTH} characters")

                    code = qrcode.make("")
                    label = code.get_image()
                    label = label.resize((200, 200))
                    self._newLabel = ImageTk.PhotoImage(label)
                    self._newLabelHolder.config(image=self._newLabel)

                elif length <= self.MAX_QR_LENGTH:
                    self._lengthLabel.config(text=f"{length} / {self.MAX_QR_LENGTH} characters")

                    self._labelDataViewer.config(state="normal")
                    self._labelDataViewer.delete(1.0, tkinter.END)
                    self._labelDataViewer.insert(1.0, text)
                    self._labelDataViewer.config(state="disabled")

                    code = qrcode.make(text)
                    label = code.get_image()
                    label = label.resize((200, 200))
                    self._newLabel = ImageTk.PhotoImage(label)
                    self._newLabelHolder.config(image=self._newLabel)

    def startQueue(self):
        self._canUpdateLabel = False
        queue = threading.Thread(target=self.queue)
        queue.start()

    def queue(self):
        time.sleep(1)

        data1 = self._labelDataSubInput1.get("1.0", "end").strip()
        data2 = self._labelDataSubInput2.get("1.0", "end").strip()
        data3 = self._labelDataSubInput3.get("1.0", "end").strip()
        data4 = self._labelDataSubInput4.get("1.0", "end").strip()
        data5 = self._labelDataSubInput5.get("1.0", "end").strip()

        data1 = data1.replace("\n", ". ")
        data2 = data2.replace("\n", ". ")
        data3 = data3.replace("\n", ". ")
        data4 = data4.replace("\n", ". ")
        data5 = data5.replace("\n", ". ")

        self._finalLabelData = str(data1 + "\n" +
                   data2 + "\n" +
                   data3 + "\n" +
                   data4 + "\n" +
                   data5)
        text = str(self._finalLabelData)

        if str(self._finalLabelData) != self._labelDataViewer.get(1.0, tkinter.END).strip():
            length = len(text) - 4
            if length > self.MAX_QR_LENGTH:
                self._labelDataViewer.config(state="normal")
                self._labelDataViewer.delete(1.0, tkinter.END)
                self._labelDataViewer.insert(1.0, "Too much Data")
                self._labelDataViewer.config(state="disabled")
                self._lengthLabel.config(text=f"{length} / {self.MAX_QR_LENGTH} characters")

                code = qrcode.make("")
                label = code.get_image()
                label = label.resize((200, 200))
                self._newLabel = ImageTk.PhotoImage(label)
                self._newLabelHolder.config(image=self._newLabel)

            elif length <= self.MAX_QR_LENGTH:
                self._lengthLabel.config(text=f"{length} / {self.MAX_QR_LENGTH} characters")

                self._labelDataViewer.config(state="normal")
                self._labelDataViewer.delete(1.0, tkinter.END)
                self._labelDataViewer.insert(1.0, text)
                self._labelDataViewer.config(state="disabled")

                code = qrcode.make(text)
                label = code.get_image()
                label = label.resize((200, 200))
                self._newLabel = ImageTk.PhotoImage(label)
                self._newLabelHolder.config(image=self._newLabel)

        self._canUpdateLabel = True

    def createLabel(self):
        data1 = self._labelDataSubInput1.get("1.0", "end").strip()
        data2 = self._labelDataSubInput2.get("1.0", "end").strip()
        data3 = self._labelDataSubInput3.get("1.0", "end").strip()
        data4 = self._labelDataSubInput4.get("1.0", "end").strip()
        data5 = self._labelDataSubInput5.get("1.0", "end").strip()

        data1 = data1.replace("\n", ". ")
        data2 = data2.replace("\n", ". ")
        data3 = data3.replace("\n", ". ")
        data4 = data4.replace("\n", ". ")
        data5 = data5.replace("\n", ". ")

        data = str(data1 + "\n" +
                   data2 + "\n" +
                   data3 + "\n" +
                   data4 + "\n" +
                   data5)
        code = qrcode.make(data)
        print(data, "pass")
        filename = tkinter.filedialog.asksaveasfile(mode="w", filetypes=(("png file", "*.png"), ("jpeg file", "*.jpg")),
                                                    defaultextension=".png")
        if filename is not None:
            code.save(filename.name)

    def convertToList(self, data):
        data = data.split("\n")
        return data


app = KVCApp()
