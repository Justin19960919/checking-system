import pandas as pd 
import logging

class Read:
	def __init__(self):
		pass
	'''	
	Checks if filetype is correct in fileRoute

	Args:
        fileRoute (str): fileRoute
        fileType (set): set of acceptable file typeds
    
    Returns:
		Boolean        
	'''	
	def fileTypeCheck(self, fileRoute, fileType):
		currentFileType = str(fileRoute).split(".")[-1].strip()
		return currentFileType in fileType

	'''	
	Checks if the correct columns are in the dataframe
	Args:
        reservedColumns (list): list of reserved columns
    	df (pandas dataframe): pandas dataframe
    Returns:
		Boolean        
	'''	
	def checkColumns(self, reservedColumns, df):
		return set(reservedColumns).issubset(set(df.columns))

	'''	
	Read in checking file, and output tuple of cleaned file, and only USHOP files
	Args:
        checkingFile (str): checking file route
    Returns:
        (cashflow pandas dataframe, cashflow with only ushop dataframes)
	'''	
	def readInCashFlow(self, checkingFile):
		########## CONSTANTS ############
		TARGET_STORES = ["USHOP_0號店", "USHOP_1號店"]
		cashflow_reserve_columns = ['交易平台', '交易序號', '出貨類型', '取消日期', '付款方式', '出貨單號', '交易金額', '配送狀態時間','平台訂單編號', '付款資訊', '建立時間']
		##################################
		
		logging.info("讀入 對帳單 檔案...")
		acceptedFileTypes = {"xlsx"}

		if not self.fileTypeCheck(checkingFile, acceptedFileTypes):
			logging.error(f"{checkingFile} 不是 {acceptedFileTypes} 檔，請更換!")
			raise Exception(f"{checkingFile} 不是 {acceptedFileTypes} 檔, 請使用 {acceptedFileTypes}檔")

		# Read in and initiate the checking file
		cashFlow = pd.read_excel(checkingFile, engine="openpyxl")
		# Check columns
		if not self.checkColumns(cashflow_reserve_columns, cashFlow):
			raise Exception("對帳單檔案裡面沒有相對應欄位來進行對帳..")
		
		# Clean data
		cashFlow = cashFlow[cashFlow["取消日期"].isna()]	
		cashFlow['createTime'] = cashFlow['建立時間'].apply(lambda x:x.date())
		
		# Filter by TARGET_STORES
		cashFlow_USHOP = cashFlow[cashFlow['交易平台'].isin(TARGET_STORES)]   
		logging.info(f"對帳單中 只有 USHOP的 有{cashFlow_USHOP.shape[0]} 行")
		
		return cashFlow, cashFlow_USHOP


	'''	
	Read in cathay file
	Args:
        cathayFile (str): cathay file route
    Returns:
        cleaned cathay file
	'''	
	def readCathay(self, cathayFileRoute):
		########## CONSTANTS ############
		cathay_reserve_columns = ['訂單編號', '訂單時間', '請/退款金額']
		##################################
		acceptedFileTypes = {"xlsx"}

		logging.info(f"讀入 國泰檔案... ")
		
		if not self.fileTypeCheck(cathayFileRoute, acceptedFileTypes):
			logging.error(f"{cathayFileRoute} 不是 {acceptedFileTypes} 檔，請更換!")
			raise Exception(f"{cathayFileRoute} 不是{acceptedFileTypes} 檔, 請使用 excel 檔")
		
		# read in file
		cathay = pd.read_excel(cathayFileRoute, engine="openpyxl")
		# Check columns
		if not self.checkColumns(cathay_reserve_columns, cathay):
			raise Exception("國泰 檔案裡面沒有相對應欄位來進行對帳..")
		
		# transform dates
		cathay['date'] = cathay['訂單時間'].apply(lambda x: pd.to_datetime(str(x)[:10], format = "%Y-%m-%d").date())
		# log
		logging.info(f"國泰檔案總共有 {cathay.shape[0]} 行")
		print("Done..")
		
		return cathay



	'''	
	Read in 7-11 file
	Args:
        file711_1 (str): first 7-11 file
        file711_2 (str): second 7-11 file
    Returns:
        cleaned 7-11 file concatenated from two files and converted to pandas df
	'''	
	def read711(self, file711_1, file711_2):
		########## CONSTANTS ############
		seven_reserved_columns = ["代收日期","配送金額","配送編號"]
		##################################
		acceptedFileTypes = {"xlsx"}

		logging.info(f"讀入 7 - 11 檔案...")	
		if not self.fileTypeCheck(file711_1, acceptedFileTypes) or not self.fileTypeCheck(file711_2, acceptedFileTypes):
			logging.error(f"{file711_1} or {file711_2} 不是 {acceptedFileTypes} 檔，請更換")
			raise Exception(f"{file711_1} or {file711_2} 不是 {acceptedFileTypes} 檔 , 請更換")

		# read in 711 first file
		file711_1 = pd.read_excel(file711_1, engine = "openpyxl") 
		# read in 711 second file
		file711_2 = pd.read_excel(file711_2, engine = "openpyxl") 	
		file711 = pd.concat([file711_1, file711_2], axis = 0)

		# check if required columns are inside
		
		if not self.checkColumns(seven_reserved_columns, file711):
			raise Exception("˙7-11 檔案裡面沒有相對應欄位來進行對帳..")

		logging.info(f"7-11 代收對帳單 總共有{file711.shape[0]} 行")

		return file711

	
	'''	
	Read in paypal file
	Args:
        filePayPal (str): paypal file route
    Returns:
        cleaned paypal pandas df
	'''	
	def readPayPal(self, filePayPal):
		########## CONSTANTS ############
		paypal_reserved_columns = ["類型","主旨","總額"]
		##################################
		acceptedFileTypes = {"csv"}
		
		logging.info("讀入paypal 檔")
		# check
		if not self.fileTypeCheck(filePayPal, acceptedFileTypes):
			logging.error(f"{filePayPal} 不是 {acceptedFileTypes} 檔")
			raise Exception(f"{filePayPal} 不是 {acceptedFileTypes} 檔, use {acceptedFileTypes} 檔")
		
		paypal = pd.read_csv(filePayPal)
		
		# check if required columns are inside		
		if not self.checkColumns(paypal_reserved_columns, paypal):
			raise Exception("˙Paypal 檔案裡面沒有相對應欄位來進行對帳..")

		paypal = paypal[paypal['類型'] == "快速結帳付款"]
		paypal['paypal_交易序號'] = paypal['主旨'].apply(lambda x: x.split("-")[1].strip())

		logging.info(f"pay pal檔 總共有 {paypal.shape[0]} 行")

		return paypal

	'''	
	Read in line pay file
	Args:
        filePayPal (str): linepay file route
    Returns:
        cleaned line pay pandas df
	'''	
	def readLinePay(self, linePayRoute):
		acceptedFileTypes = {"xlsx"}
		linepay_reserved_columns = ['訂單號碼', "付款金額"]
		logging.info("讀入linepay 檔")
		# check
		if not self.fileTypeCheck(linePayRoute, acceptedFileTypes):
			logging.error(f"{linePayRoute} 不是 {acceptedFileTypes} 檔")
			raise Exception(f"{linePayRoute} 不是 {acceptedFileTypes} 檔, use {acceptedFileTypes} 檔")
		
		linePay = pd.read_excel(linePayRoute, engine="openpyxl")                
		if not self.checkColumns(linepay_reserved_columns, linePay):
			raise Exception("LinePay 檔案裡面沒有相對應欄位來進行對帳..")
		
		logging.info(f"linePay檔 總共有 {linePay.shape[0]} 行")

		return linePay
























