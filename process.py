from datetime import datetime
import pandas as pd 
import logging
import os


'''
A Matching class that matches checking file 
with other files based on different criterias
'''

class Process:

	@staticmethod
	def getCurTime():
		return str(datetime.now().date())


	@staticmethod
	def start():
		# set up logging
		logging.basicConfig(level = logging.DEBUG, filename = 'app.log', format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')
		logging.info("開始對帳..")
			

	# gets called when we init an object
	@staticmethod
	def setUpDateFolder():
		root = os.getcwd()
		if not os.path.exists(root + f"/{Process.getCurTime()}"):
			logging.info(f"使用 {Process.getCurTime()}來建立當前資料夾..")
			os.mkdir(Process.getCurTime())
		else:
			logging.info(f"{Process.getCurTime()}已經存在，繼續...")

	@staticmethod
	def setUpSubfolder(folderName):
		# needs to check if exists already
		os.chdir(Process.getCurTime())
		if folderName not in os.listdir():
			logging.info(f"在{Process.getCurTime()}裡面建立 {folderName} 的資料夾")			
			os.mkdir(folderName)
		else:
			logging.info(f"{folderName}已經存在 在{Process.getCurTime()}裡頭...")

		# move back to root
		os.chdir("../")

	@staticmethod
	def exportExcel(file, fileName):
		file.to_excel(f"{fileName}.xlsx")  















