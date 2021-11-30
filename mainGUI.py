# TKinter
# https://www.datacamp.com/community/tutorials/gui-tkinter-python
# https://www.tutorialspoint.com/python/tk_label.htm
# TK docs
#https://tkdocs.com/tutorial/firstexample.html


import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo


# Matching class
from match import Match



#import threading
import logging


# Inherit from the Tk module in tkinter
class GUI(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        logging.basicConfig(level = logging.DEBUG, filename = 'app.log', format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')
        self.initStorage()
        
        ##################
        self.initWindow()       
        self.constructLayOut()


    def initStorage(self):
        self.uploadedFiles = {}

        
    def initWindow(self):
        self.title("金流比對系統")
        # width * height
        self.geometry('800x300')
        # set minimum window size value
        self.minsize(800, 300)
        # set maximum window size value
        self.maxsize(800, 300)


    def constructLayOut(self):
        self.constructUploadFields()
        self.constructProgressBar()
        self.constructProcessButton()


    def constructUploadFields(self):
        self.createUploadField("cashflow", 0, "xlsx")
        self.createUploadField("cathay", 1, "xlsx")
        self.createUploadField("711USHOP1", 2, "xlsx")
        self.createUploadField("711USHOP2", 3, "xlsx")
        self.createUploadField("paypal", 4, "csv")


    def constructProgressBar(self):
        self.pb = ttk.Progressbar(orient="horizontal", length=200, mode="determinate")
        # padx, pady can take a 2-tuple that represent the left/right and top/bottom padding.
        self.pb.grid(row= 9,column=1, pady=(30,0))


        self.processStatus = tk.StringVar()
        processStatusLabel = tk.Label(textvariable=self.processStatus, fg="red").grid(row=10, column=1, padx=2) 



    def constructProcessButton(self):
        processBtn = tk.Button(text = "對帳開始！",highlightcolor="blue", height=2, command = self.process)
        # need to move button to middle
        processBtn.grid(row=11, column=1, pady=(5,0))



    ### UTILITY FUNCTIONS ###
    def select_file(self, fileCategory, uploadStatus):
        # only allow uploads of excel files and csv files
        allowedFileTypes = [('excel file', '*.xlsx'), ('csv file', '*.csv')]
        fileName = askopenfilename(title="select a file", filetypes= allowedFileTypes)

        if fileName:
            showinfo(title = "Selected file is: ", message=fileName)
            self.uploadedFiles[fileCategory] = fileName
            uploadStatus.set("Upload Successful!")
        else:
            showinfo(title = "You haven't selected a file")
            uploadStatus.set("Upload Failed!")

        print(f"Current uploaded files include: {self.uploadedFiles}")



    def createUploadField(self, category, row_num, ft):

        nameTransform = {
            "cashflow": "銷貨明細表",
            "cathay": "國泰世華對帳單",
            "711USHOP1": "統一速網 - AROO",
            "711USHOP2": "統一宿網 - ROVOLETA",
            "paypal": "PayPal"
            # Linepay
        }

        uploadStatus = tk.StringVar()
        
        uploadLabel = tk.Label(text=f"上傳 {nameTransform[category]} ({ft}):")
        uploadLabel.grid(row=row_num, column=0, sticky = "W")

        uploadBtn = tk.Button(text = "選擇檔案", command = lambda: self.select_file(category, uploadStatus))
        uploadBtn.grid(row=row_num, column=1, padx = 100)
        # upload feedback: 
        uploadFeedBack = tk.Label(textvariable=uploadStatus).grid(row=row_num, column=2, padx=10) # sticky = (W, E)



    def startProgressBar(self):
        # progress bar information
        PROGRESSBAR_MIN = 0
        PROGRESSBAR_MAX = 5000
        self.bytes = PROGRESSBAR_MIN
        self.maxbytes = PROGRESSBAR_MAX
        self.pb["value"] = PROGRESSBAR_MIN
        self.pb["maximum"] = PROGRESSBAR_MAX
        self.updateProgressBar()


    def updateProgressBar(self):
        '''simulate reading 500 bytes; update progress bar'''
        self.bytes += 500
        self.pb["value"] = self.bytes
        if self.bytes < self.maxbytes:
            self.after(200, self.updateProgressBar) # call itself after 100 ms


    def checkExecution(self):
        if self.matchingStatus:
            self.processStatus.set("Matching Completed!")            
        else:
            self.processStatus.set("Matching Failed!")


    def match(self):
        # FLAG to check if we successfully run through this function
        self.matchingStatus = False
        print("-----------------")
        print(f"Current uploaded files include: {self.uploadedFiles}")
        print("-----------------")
        
        # Constants
        CASHFLOW = "cashflow"
        CATHAY = "cathay"
        USHOP711_1 = "711USHOP1"
        USHOP711_2 = "711USHOP2"
        PAYPAL = "paypal"
        uploadCount = 0

        if CASHFLOW not in self.uploadedFiles.keys():
            logging.exception(f"{CASHFLOW} file not uploaded .. abort")
            print(f"{CASHFLOW} file not uploaded .. abort")
            return 

        # Once we are sure the user uploads a cashflow file, we init the Match object
        m = Match(self.uploadedFiles[CASHFLOW])
        
        if CATHAY in self.uploadedFiles.keys():
            m.readCathay(self.uploadedFiles[CATHAY])
            m.matchCashFlow_cathay()        
            uploadCount += 1

        if USHOP711_1 in self.uploadedFiles.keys() and USHOP711_2 in self.uploadedFiles.keys():
            m.read711(self.uploadedFiles[USHOP711_1], self.uploadedFiles[USHOP711_2])
            m.matchCashFlow_711()
            uploadCount += 2

        if PAYPAL in self.uploadedFiles.keys():
            m.readPayPal(self.uploadedFiles[PAYPAL])
            m.matchCashFlow_paypal()
            uploadCount += 1

        # if only cashflow file is uploaded, and submit starts, then there is nothing to match, abort.
        if uploadCount == 0:
            print("There is nothing to match ...")
            return  
        
        # if all goes well
        self.matchingStatus = True


    # Multithreading to run progress bar and matching at the same time
    def process(self):
        print("Starting progress bar ...") 
        self.startProgressBar()
        print("Starting matching process ...")
        self.match()
        print("Matching status: ", self.matchingStatus)
        self.checkExecution()

# Main
app = GUI()
app.mainloop()









