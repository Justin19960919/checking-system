import logging
import os 
import pandas as pd
from process import Process

class Match:

	def __init__(self, uploads):
		self.uploads = uploads
		self.curTime = Process.getCurTime()

	def setup(self):
		self.cashFlow_USHOP = uploads["cashFlow_USHOP"]		
		self.cashFlow= uploads["cashFlow"]		


	def matchProcess(self, mergedDf, df1_col, df2_col, df1_money, df2_money):
		fullyMatched = mergedDf[mergedDf[df1_col].notna() & mergedDf[df2_col].notna() & mergedDf[df1_money] == mergedDf[df2_money]]
		moneyUnMatched = mergedDf[mergedDf[df1_col].notna() & mergedDf[df2_col].notna() & mergedDf[df1_money] != mergedDf[df2_money]]
		df1UnMatched = mergedDf[mergedDf[df1_col].notna() & mergedDf[df2_col].isna()]
		df2UnMatched = mergedDf[mergedDf[df1_col].isna() & mergedDf[df2_col].notna()]
		return fullyMatched, moneyUnMatched, df1UnMatched, df2UnMatched


	################### Match up files ######################
	def matchCashFlow_cathay(self, filename, cathay):
		# change directory temporarily
		os.chdir(f"{self.cur_time}/{filename}")
 
		logging.info("-------------- 開始 國泰世華 對帳... ----------------")
		
		# filter out cashFlow ushop to 國泰世華visa
		cashFlow_cathay = self.cashFlow_USHOP[self.cashFlow_USHOP["付款方式"] == "國泰世華VISA"]
		logging.info(f"對帳單中 是USHOP 相關交易，且使用國泰轉帳 的有 {cashFlow_cathay.shape[0]} 行")
		
		logging.info(f"Cathay File: getting cash_id row out of 付款資訊 ...")
		cashFlow_cathay['cash_id'] = cashFlow_cathay["付款資訊"].apply(lambda x: str(x)[-14:])

		
		# MERGING cashflow file and cathay file ...
		cashFlow_cathay_merged = cashFlow_cathay.merge(cathay, left_on = "cash_id", right_on = "訂單編號", how = "outer")
                
		### matching ###

		fullyMatched, moneyUnMatched, cathayUnMatched, cashflowUnMatched = self.matchProcess(cashFlow_cathay_merged, "訂單編號", "cash_id", "請/退款金額", "交易金額")
		# number of entries
		logging.info(f"總共{cashFlow_cathay_merged.shape[0]} 筆")			
		
		# logging and export
		logging.info(f"對帳單 - 國泰: 全部對到的有 {fullyMatched.shape[0]} 筆")
		Process.exportExcel(fullyMatched, "全部對到")
		
		logging.info(f"對帳單 - 國泰: 金流沒對到的有 {moneyUnMatched.shape[0]} 筆")
		Process.exportExcel(moneyUnMatched, "金流未對到")
		
		logging.info(f"對帳單 - 國泰: 國泰沒有對到的有 {cathayUnMatched.shape[0]} 筆")
		Process.exportExcel(cathayUnMatched, "國泰沒對到")
		
		logging.info(f"對帳單 - 國泰: 對帳單沒對到的有 {cashflowUnMatched.shape[0]} 筆")
		Process.exportExcel(cashflowUnMatched, "對帳單沒對到")
		

		logging.info("--------- 結束 國泰世華 對帳... ---------")
		# change back to root (go up two levels)
		os.chdir("../../")




	def matchCashFlow_711(self, filename, file711):
		os.chdir(f"{self.cur_time}/{filename}")

		logging.info("-------------- 開始 7-11 對帳... ----------------")
		SOURCE711 = "7-11[代收]"


		cashFlow_711 = self.cashFlow_USHOP[self.cashFlow_USHOP["出貨類型"] == SOURCE711]
		logging.info(f"對帳單中 使用 {SOURCE711} 的總共有 {cashFlow_711.shape[0]} 筆")

		# MERGE (outer merge of 711 file and cashflow)
		cashFlow_711_merged = cashFlow_711.merge(file711, left_on = "出貨單號", right_on = "配送編號", how = "outer")

		### matching ###
		fullyMatched, moneyUnMatched, sevenElevenUnMatched, cashflowUnMatched = self.matchProcess(cashFlow_711_merged, "配送編號", "出貨單號", "交易金額", "配送金額")
		
		# number of entries
		logging.info(f"總共{cashFlow_711_merged.shape[0]} 筆")	
		
		# logging and export
		logging.info(f"對帳單 - 7-11: 全部對到的有 {fullyMatched.shape[0]} 筆")
		Process.exportExcel(fullyMatched, "全部對到")
							
		logging.info(f"對帳單 - 7-11: 金流沒對到的有 {moneyUnMatched.shape[0]} 筆")
		Process.exportExcel(moneyUnMatched, "金流未對到")
							
		logging.info(f"對帳單 - 7-11: 7-11沒有對到的有 {sevenElevenUnMatched.shape[0]} 筆")
		Process.exportExcel(sevenElevenUnMatched, "711沒對到")
							
		logging.info(f"對帳單 - 7-11: 對帳單沒對到的有 {cashflowUnMatched.shape[0]} 筆")
		Process.exportExcel(cashflowUnMatched, "對帳單沒對到")

		logging.info("--------- 結束 711 對帳... ---------")

		# change back
		os.chdir("../../")


	def matchCashFlow_paypal(self, filename,, paypal):
		os.chdir(f"{self.cur_time}/{filename}")

		logging.info("-------------- Starting matching of cashflow and paypal file ----------------")
		cashFlow_paypal = self.cashFlow_USHOP[self.cashFlow_USHOP["付款方式"] == "PayPal"]
		# add logger
		logging.info(f"對帳單中使用 paypal 的總共有 {cashFlow_paypal.shape[0]} 行")


		cashFlow_paypal["交易序號"] = cashFlow_paypal["交易序號"].astype(str)
		
		# merge cashflow with paypal file
		cashFlow_paypal_merged = cashFlow_paypal.merge(paypal, left_on = "交易序號", right_on = "paypal_交易序號", how = "outer")

		cashFlow_paypal_merged["總額"] = cashFlow_paypal_match["總額"].apply(lambda x: float(str(x).replace(",","") if x != None else None))
		
		# number of entries
		logging.info(f"總共{cashFlow_paypal_merged.shape[0]} 筆")	


		fullyMatched, moneyUnMatched, paypalUnMatched, cashflowUnMatched = self.matchProcess(cashFlow_paypal_merged, "交易序號", "paypal_交易序號", '交易金額', '總額')

		# logging and export
		logging.info(f"對帳單 - paypal: 全部對到的有 {fullyMatched.shape[0]} 筆")
		Process.exportExcel(fullyMatched, "全部對到")
							
		logging.info(f"對帳單 - paypal: 金流沒對到的有 {moneyUnMatched.shape[0]} 筆")
		Process.exportExcel(moneyUnMatched, "金流未對到")
							
		logging.info(f"對帳單 - paypal: paypal沒有對到的有 {paypalUnMatched.shape[0]} 筆")
		Process.exportExcel(paypalUnMatched, "711沒對到")
							
		logging.info(f"對帳單 - paypal: 對帳單沒對到的有 {cashflowUnMatched.shape[0]} 筆")
		Process.exportExcel(cashflowUnMatched, "對帳單沒對到")

		logging.info("--------- 結束 paypal 對帳... ---------")	
		os.chdir("../../")


	def matchCashFlow_linepay(self):
		pass



	def match(self):
		self.setup()
		if "國泰世華銀行" in self.uploads:
			self.matchCashFlow_cathay("國泰世華銀行", self.uploads["國泰世華銀行"])

		if "7-11" in uploads:
			self.matchCashFlow_711("7-11", self.uploads["7-11"])

		if "Paypal" in self.uploads:
			self.matchCashFlow_paypal("Paypal", self.uploads["Paypal"])

		if "Line-Pay" in self.uploads:
			self.matchCashFlow_linepay("Line-Pay", self.uploads["Line-Pay"])

