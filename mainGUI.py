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
from process import Process
from read import Read
from match import Match
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
        self.createUploadField("linepay", 5, "xlsx")


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
        allowedFileTypes = [('.xlsx file', '*.xlsx'), ('.csv file', '*.csv'), ('.xls file', "*.xls")]
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
            "711USHOP2": "統一速網 - ROVOLETA",
            "paypal": "PayPal",
            "linepay": "LINE PAY"
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
        LINEPAY = "linepay"
        
        uploads = {}

        uploadCount = 0
        if CASHFLOW not in self.uploadedFiles.keys():
            logging.exception(f"{CASHFLOW} file not uploaded .. abort")
            print(f"{CASHFLOW} file not uploaded .. abort")
            return 

        # initiate read file class functionality
        readFiles = Read()

        # read in cashflow file
        cashFlow, cashFlow_USHOP = readFiles.readInCashFlow(self.uploadedFiles[CASHFLOW])
        uploads["cashFlow"] = cashFlow
        uploads["cashFlow_USHOP"] = cashFlow_USHOP
        
        # start the whole process
        Process.start()
        Process.setUpDateFolder()

        

        ######### Four different kind of files #########
        # cathay
        if CATHAY in self.uploadedFiles.keys():
            cathay = readFiles.readCathay(self.uploadedFiles[CATHAY])
            # do matching
            uploadCount += 1
            Process.setUpSubfolder("國泰世華銀行")
            uploads["國泰世華銀行"] = cathay


        # 7-11
        if USHOP711_1 in self.uploadedFiles.keys() and USHOP711_2 in self.uploadedFiles.keys():
            file711 = readFiles.read711(self.uploadedFiles[USHOP711_1], self.uploadedFiles[USHOP711_2])
            # do matching
            uploadCount += 1
            Process.setUpSubfolder("7-11")
            uploads["7-11"] = file711

        # paypal
        if PAYPAL in self.uploadedFiles.keys():
            paypal = readFiles.readPayPal(self.uploadedFiles[PAYPAL])
            # do matching
            uploadCount += 1
            Process.setUpSubfolder("Paypal")
            uploads["Paypal"] = paypal


        # linepay
        if LINEPAY in self.uploadedFiles.keys():
            linePay = readFiles.readLinePay(self.uploadedFiles[LINEPAY])
            # do matching
            uploadCount += 1
            Process.setUpSubfolder("Line-Pay")
            uploads["Line-Pay"] = linePay


        # if only cashflow file is uploaded, and submit starts, then there is nothing to match, abort.
        if uploadCount == 0:
            print("There is nothing to match ...")
            return  
        
        #### start matching ####
        # uploads dictionary of uploaded files

        match = Match(uploads)
        match.match()
        # if all goes well
        self.matchingStatus = True


    # Multithreading to run progress bar and matching at the same time
    def process(self):
        print("Starting matching process ...")
        self.match()
        
        print("Starting progress bar ...") 
        self.startProgressBar()
        
        print("Matching status: ", self.matchingStatus)
        self.checkExecution()
        
# Main
app = GUI()
app.mainloop()










