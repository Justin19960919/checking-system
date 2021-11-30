from datetime import datetime
import pandas as pd 
import numpy as np 
import logging
import os

'''
A Matching class that matches checking file 
with other files based on different criterias
'''

class Match:
	cur_time = str(datetime.now().date())

	def __init__(self, checkingFile):
		# set up logging
		logging.basicConfig(level = logging.DEBUG, filename = 'app.log', format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')
		logging.info("開始對帳..")
		
		
		self.setUpDateFolder()
		
		# read in checking file
		self.readInChecking(checkingFile)


	# gets called when we init an object
	def setUpDateFolder(self):
		root = os.getcwd()
		if not os.path.exists(root + f"/{self.cur_time}"):
			logging.info(f"Setting up folder with today's date {self.cur_time}")
			os.mkdir(self.cur_time)
		else:
			logging.info(f"Folder named {self.cur_time} already exists, proceeding...")


	def setUpSubfolder(self, folderName):
		# needs to check if subfolder exists already
		os.chdir(self.cur_time)
		if folderName not in os.listdir():
			logging.info(f"Creating subfolder: {folderName} under {self.cur_time}")			
			os.mkdir(folderName)
		else:
			logging.info(f"{folderName} already exists in {self.cur_time} folder ...")

		# move back to root
		os.chdir("../")


	def fileTypeCheck(self, fileRoute, fileType):
		currentFileType = str(fileRoute).split(".")[-1].strip()
		return currentFileType == fileType


	def exportExcel(self, file, fileName):
		file.to_excel(f"{fileName}.xlsx")  


	def checkColumns(self, reservedColumns, df, dfName):
		for c in reservedColumns:
			if c not in df.columns:
				logging.exception(f"{c} not in {dfName}'s columns ")
				raise Exception(f"{c} not in {dfName}'s columns ")
				return
	

	################### read in files ######################

	# read in checking file
	def readInChecking(self,checkingFile):
		logging.info("讀入對帳單 檔案...")
		print("讀入對帳單 檔案...")
		if not self.fileTypeCheck(checkingFile, "xlsx"):
			logging.error(f"{checkingFile} 不是 .xlsx 檔，請更換")
			raise Exception(f"{checkingFile} 不是.xlsx 檔, 請使用 excel 檔")

		TARGET_STORES = ["USHOP_0號店", "USHOP_1號店"]
		# read in and initiate the checking file	
		cashFlow = pd.read_excel(checkingFile, engine='openpyxl') 

		# check if columns are in it
		cashflow_reserve_columns = ['交易平台', '交易序號', '出貨類型', '取消日期', '付款方式', '出貨單號', '交易金額', '配送狀態時間','平台訂單編號', '付款資訊', '建立時間']
		self.checkColumns(cashflow_reserve_columns, cashFlow, "cashflow")
		
		# modifications
		cashFlow = cashFlow[cashFlow["取消日期"].isna()]	
		cashFlow['createTime'] = cashFlow['建立時間'].apply(lambda x:x.date())
		self.cashFlow = cashFlow
		# filter by TARGET_STORES
		self.cashFlow_USHOP = cashFlow[cashFlow['交易平台'].isin(TARGET_STORES)]  
		
		# log 
		logging.info(f"對帳單中 只有 USHOP的 有{self.cashFlow_USHOP.shape[0]} 行")
		print("Done..")

	# read in cathay file
	def readCathay(self, fileCathay):
		print(f"讀入 國泰檔案... ")
		logging.info(f"讀入 國泰檔案... ")
		
		if not self.fileTypeCheck(fileCathay, "xlsx"):
			logging.error(f"{fileCathay} 不是 .xlsx 檔，請更換")
			raise Exception(f"{fileCathay} is not an excel file, use .xlsx file")

		cathay = pd.read_excel(fileCathay, engine='openpyxl')
		

		# check if the required columns are in it
		cathay_reserve_columns = ['訂單編號', '訂單時間', '請/退款金額']
		self.checkColumns(cathay_reserve_columns, cathay, "cathay")
		

		# transform dates
		cathay['date'] = cathay['訂單時間'].apply(lambda x: pd.to_datetime(str(x)[:10], format = "%Y-%m-%d").date())
		# log
		logging.info(f"國泰檔案總共有 {cathay.shape[0]} 行")
		print("Done..")
		
		self.cathay = cathay

	# read in both 711 files and conacatenate
	def read711(self, file711_1, file711_2):
		print(f"讀入7 - 11 檔案... ")
		logging.info(f"讀入 7 - 11 檔案...")	
		if not self.fileTypeCheck(file711_1, "xlsx") and self.fileTypeCheck(file711_2, "xlsx"):
			logging.error(f"{file711_1} or {file711_2} 不是 .xlsx 檔，請更換")
			raise Exception(f"{file711_1} or {file711_2} 不是 .xlsx 檔 , 請更換")

		# read in 711 first file
		file711_1 = pd.read_excel(file711_1, engine='openpyxl') 
		
		# read in 711 second file
		file711_2 = pd.read_excel(file711_2, engine='openpyxl') 	
		
		file711 = pd.concat([file711_1, file711_2], axis = 0)

		# check if required columns are inside
		seven_reserved_columns = ["代收日期","配送金額","配送編號"]
		self.checkColumns(seven_reserved_columns, file711, "file711")

		
		# log
		logging.info(f"7-11 代收對帳單 總共有{file711.shape[0]} 行")
		print("Done..")
		self.file711 = file711

	
	# read in pay pal file
	def readPayPal(self, filePayPal):
		print("讀入 paypal 檔")
		logging.info("讀入paypal 檔")
		# check
		if not self.fileTypeCheck(filePayPal, "csv"):
			logging.error(f"{filePayPal} 不是 .csv 檔")
			raise Exception(f"{filePayPal} 不是 .csv 檔, use .csv 檔")
		
		paypal = pd.read_csv(filePayPal)
		
		# check if required columns are inside
		paypal_reserved_columns = ["類型","主旨","總額"]
		self.checkColumns(paypal_reserved_columns, paypal, "paypal")

		
		paypal = paypal[paypal['類型'] == "快速結帳付款"]
		paypal['paypal_交易序號'] = paypal['主旨'].apply(lambda x: x.split("-")[1].strip())

		# log
		logging.info(f"pay pal檔 總共有 {paypal.shape[0]} 行")
		print("Done..")

		self.paypal = paypal

	def readLinePay(self):
	        pass

	def matchProcess(self, mergedDf, df1_col, df2_col, df1_money, df2_money):
		fullyMatched = mergedDf[mergedDf[df1_col].notna() & mergedDf[df2_col].notna() & mergedDf[df1_money] == mergedDf[df2_money]]
		moneyUnMatched = mergedDf[mergedDf[df1_col].notna() & mergedDf[df2_col].notna() & mergedDf[df1_money] != mergedDf[df2_money]]
		df1UnMatched = mergedDf[mergedDf[df1_col].notna() & mergedDf[df2_col].isna()]
		df2UnMatched = mergedDf[mergedDf[df1_col].isna() & mergedDf[df2_col].notna()]
		return fullyMatched, moneyUnMatched, df1UnMatched, df2UnMatched

	################### Match up files ######################

	def matchCashFlow_cathay(self):
		
		# set up cathay folder under the current date
		self.setUpSubfolder("cathay")
		
		# change directory temporarily
		os.chdir(f"{self.cur_time}/cathay")

		logging.info("-------------- Starting matching of cashflow and cathay file ----------------")
		
		# filter out cashFlow ushop to 國泰世華visa
		cashFlow_cathay = self.cashFlow_USHOP[self.cashFlow_USHOP["付款方式"] == "國泰世華VISA"]
		logging.info(f"對帳單中 是USHOP 相關交易，且使用國泰轉帳 的有 {cashFlow_cathay.shape[0]} 行")
		
		logging.info(f"Cathay File: getting cash_id row out of 付款資訊 ...")
		cashFlow_cathay['cash_id'] = cashFlow_cathay["付款資訊"].apply(lambda x: str(x)[-14:])

		
		# MERGING cashflow file and cathay file ...
		cashFlow_cathay_merged = cashFlow_cathay.merge(self.cathay, left_on = "cash_id", right_on = "訂單編號", how = "outer")
                
		### matching ###

		fullyMatched, moneyUnMatched, cathayUnMatched, cashflowUnMatched = self.matchProcess(cashFlow_cathay_merged, "訂單編號", "cash_id", "請/退款金額", "交易金額")
		# number of entries
		logging.info(f"總共{cashFlow_cathay_merged.shape[0]} 筆")			
		
		# logging and export
		logging.info(f"對帳單 - 國泰: 全部對到的有 {fullyMatched.shape[0]} 筆")
		self.exportExcel(fullyMatched, "fullyMatched")
		
		logging.info(f"對帳單 - 國泰: 金流沒對到的有 {moneyUnMatched.shape[0]} 筆")
		self.exportExcel(moneyUnMatched, "moneyUnMatched")
		
		logging.info(f"對帳單 - 國泰: 國泰沒有對到的有 {cathayUnMatched.shape[0]} 筆")
		self.exportExcel(cathayUnMatched, "cathayUnMatched")
		
		logging.info(f"對帳單 - 國泰: 對帳單沒對到的有 {cashflowUnMatched.shape[0]} 筆")
		self.exportExcel(cashflowUnMatched, "cashflowUnMatched")
		

		logging.info("--------- Finished cashflow / cathay matching ---------")
		# change back to root (go up two levels)
		os.chdir("../../")




	def matchCashFlow_711(self):
		# set up 711 sub folder
		self.setUpSubfolder("711")
		os.chdir(f"{self.cur_time}/711")

		logging.info("-------------- Starting matching of cashflow and 711 file ----------------")
		SOURCE711 = "7-11[代收]"


		cashFlow_711 = self.cashFlow_USHOP[self.cashFlow_USHOP["出貨類型"] == SOURCE711]
		logging.info(f"對帳單中 使用 {SOURCE711} 的總共有 {cashFlow_711.shape[0]} 筆")

		# MERGE (outer merge of 711 file and cashflow)
		cashFlow_711_merged = cashFlow_711.merge(self.file711, left_on = "出貨單號", right_on = "配送編號", how = "outer")

	
		### matching ###
		fullyMatched, moneyUnMatched, sevenElevenUnMatched, cashflowUnMatched = self.matchProcess(cashFlow_711_merged, "配送編號", "出貨單號", "交易金額", "配送金額")
		
		# number of entries
		logging.info(f"總共{cashFlow_711_merged.shape[0]} 筆")	
		
		# logging and export
		logging.info(f"對帳單 - 7-11: 全部對到的有 {fullyMatched.shape[0]} 筆")
		self.exportExcel(fullyMatched, "fullyMatched")
							
		logging.info(f"對帳單 - 7-11: 金流沒對到的有 {moneyUnMatched.shape[0]} 筆")
		self.exportExcel(moneyUnMatched, "moneyUnMatched")
							
		logging.info(f"對帳單 - 7-11: 7-11沒有對到的有 {sevenElevenUnMatched.shape[0]} 筆")
		self.exportExcel(sevenElevenUnMatched, "seven_eleven_UnMatched")
							
		logging.info(f"對帳單 - 7-11: 對帳單沒對到的有 {cashflowUnMatched.shape[0]} 筆")
		self.exportExcel(cashflowUnMatched, "cashflowUnMatched")

		logging.info("--------- Finished cashflow / 711 matching ---------")

		# change back
		os.chdir("../../")


	def matchCashFlow_paypal(self):
		self.setUpSubfolder("paypal")
		os.chdir(f"{self.cur_time}/paypal")
		
		logging.info("-------------- Starting matching of cashflow and paypal file ----------------")
		cashFlow_paypal = self.cashFlow_USHOP[self.cashFlow_USHOP["付款方式"] == "PayPal"]
		# add logger
		logging.info(f"對帳單中使用 paypal 的總共有 {cashFlow_paypal.shape[0]} 行")


		cashFlow_paypal["交易序號"] = cashFlow_paypal["交易序號"].astype(str)
		
		# merge cashflow with paypal file
		cashFlow_paypal_merged = cashFlow_paypal.merge(self.paypal, left_on = "交易序號", right_on = "paypal_交易序號", how = "outer")


		# number of entries
		logging.info(f"總共{cashFlow_paypal_merged.shape[0]} 筆")	

		# cashflow not matched
		cashFlow_paypal_cashFlow_unmatch = cashFlow_paypal_merged[cashFlow_paypal_merged['交易序號'].isna()]
		logging.info(f"對帳單 - paypal: 對帳單 這邊沒對到的有  {cashFlow_paypal_cashFlow_unmatch.shape[0]} 筆")
		self.exportExcel(cashFlow_paypal_cashFlow_unmatch, "cashFlow_unmatch")

		# paypal not matched
		cashFlow_paypal_paypal_unmatch = cashFlow_paypal_merged[cashFlow_paypal_merged['paypal_交易序號'].isna(
			)]
		logging.info(f"對帳單 - paypal: paypal 這邊沒對到的有  {cashFlow_paypal_paypal_unmatch.shape[0]} 筆")
		self.exportExcel(cashFlow_paypal_paypal_unmatch, "paypal_unmatch")


		# both match
		cashFlow_paypal_match = cashFlow_paypal_merged[cashFlow_paypal_merged['交易序號'].notna() & cashFlow_paypal_merged['paypal_交易序號'].notna()]
		cashFlow_paypal_match["總額"] = cashFlow_paypal_match["總額"].apply(lambda x: float(str(x).replace(",","")))
		
		# get money unmatched in matched records
		cashFlow_paypal_match_moneyUnmatch = cashFlow_paypal_match[cashFlow_paypal_match['交易金額'] != cashFlow_paypal_match['總額']]
		logging.info(f"對帳單 - paypal: 金流 沒對到的有  {cashFlow_paypal_match_moneyUnmatch.shape[0]} 筆")
		self.exportExcel(cashFlow_paypal_match_moneyUnmatch, "moneyUnmatch")

		# money matched
		cashFlow_paypal_moneyMatch = cashFlow_paypal_match[cashFlow_paypal_match['交易金額'] == cashFlow_paypal_match['總額']]
		logging.info(f"對帳單 - paypal: 金流 對到的有  {cashFlow_paypal_moneyMatch.shape[0]} 筆")
		self.exportExcel(cashFlow_paypal_moneyMatch, "moneyMatch")

		logging.info("--------- Finished cashflow / paypal matching ---------")
	
		os.chdir("../../")


	def matchCashFlow_linepay(self):
		pass



