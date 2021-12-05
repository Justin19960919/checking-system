import logging
import os 
import pandas as pd
from process import Process


class Match:

	def __init__(self, uploads):
		self.uploads = uploads
		self.cur_time = Process.getCurTime()

	def setup(self):
		self.cashFlow_USHOP = self.uploads["cashFlow_USHOP"]		
		self.cashFlow= self.uploads["cashFlow"]		


	def matchProcess(self, mergedDf, cashFlow_col, df_col, cashFlow_money_col, df_money_col):
	    idExists = mergedDf[mergedDf[cashFlow_col].notna() & mergedDf[df_col].notna()] 
	    # turn to float
	    mergedDf[cashFlow_money_col] = mergedDf[cashFlow_money_col].astype(float)
	    mergedDf[df_money_col] = mergedDf[df_money_col].astype(float)
	    
	    moneyMatch = idExists[idExists[cashFlow_money_col] == idExists[df_money_col]]
	    moneyUnMatch = idExists[idExists[cashFlow_money_col] != idExists[df_money_col]]
	    cashFlowNotExist = mergedDf[mergedDf[cashFlow_col].isna() & mergedDf[df_col].notna()]
	    otherNotExist = mergedDf[mergedDf[cashFlow_col].notna() & mergedDf[df_col].isna()]
	    return moneyMatch, moneyUnMatch, cashFlowNotExist, otherNotExist

	def matchAndExport(self, mergedDf, name, cashFlowCol, otherCol, cashFlowMoney, otherMoney):
		moneyMatch, moneyUnMatch, cashFlowNotExist, otherNotExist = self.matchProcess(mergedDf, cashFlowCol, otherCol, cashFlowMoney, otherMoney)		
		# number of entries
		logging.info(f"總共{mergedDf.shape[0]} 筆")			
		
		# logging and export
		logging.info(f"對帳單 - {name}: 全部對到的有 {moneyMatch.shape[0]} 筆")
		Process.exportExcel(moneyMatch, "全部對到")
		
		logging.info(f"對帳單 - {name}: 金流沒對到的有 {moneyUnMatch.shape[0]} 筆")
		Process.exportExcel(moneyUnMatch, "金流未對到")
		
		logging.info(f"對帳單 - {name}: 對帳單沒對到的有 {cashFlowNotExist.shape[0]} 筆")
		Process.exportExcel(cashFlowNotExist, "對帳單沒對到")
		
		logging.info(f"對帳單 - {name}: {name}沒有對到的有 {otherNotExist.shape[0]} 筆")
		Process.exportExcel(otherNotExist, f"{name}沒對到")
		
		logging.info(f"--------- 結束 {name} 對帳... ---------")


	################### Match up files ######################
	def matchCashFlow_cathay(self, filename, cathay):
		# change directory temporarily
		os.chdir(f"{self.cur_time}/{filename}")
 
		logging.info("-------------- 開始 國泰世華 對帳... ----------------")
		
		# filter out cashFlow ushop to 國泰世華visa
		cashFlow_cathay = self.cashFlow_USHOP[self.cashFlow_USHOP["付款方式"] == "國泰世華VISA"]
		logging.info(f"對帳單是USHOP 相關交易，且使用國泰轉帳 的有 {cashFlow_cathay.shape[0]} 行")
		cashFlow_cathay['cash_id'] = cashFlow_cathay["付款資訊"].apply(lambda x: str(x)[-14:])

		logging.info(f"國泰 總共有 {cathay.shape[0]} 行")
		# MERGING cashflow file and cathay file ...
		cashFlow_cathay_merged = cashFlow_cathay.merge(cathay, left_on = "cash_id", right_on = "訂單編號", how = "outer")
        
		self.matchAndExport(cashFlow_cathay_merged, "國泰", "cash_id", "訂單編號", "請/退款金額", "交易金額" )

		# change back to root (go up two levels)
		os.chdir("../../")




	def matchCashFlow_711(self, filename, file711):
		os.chdir(f"{self.cur_time}/{filename}")

		logging.info("-------------- 開始 7-11 對帳... ----------------")
		SOURCE711 = "7-11[代收]"

		cashFlow_711 = self.cashFlow_USHOP[self.cashFlow_USHOP["出貨類型"] == SOURCE711]
		logging.info(f"對帳單中使用 {SOURCE711} 的總共有 {cashFlow_711.shape[0]} 筆")
		logging.info(f"7-11 總共有 {file711.shape[0]} 筆")

		# MERGE (outer merge of 711 file and cashflow)
		cashFlow_711_merged = cashFlow_711.merge(file711, left_on = "出貨單號", right_on = "配送編號", how = "outer")

		### matching ###	
		self.matchAndExport(cashFlow_711_merged, "7-11","出貨單號", "配送編號", "交易金額", "配送金額" )

		# change back
		os.chdir("../../")


	def matchCashFlow_paypal(self, filename, paypal):
		os.chdir(f"{self.cur_time}/{filename}")

		logging.info("-------------- Starting matching of cashflow and paypal file ----------------")
		cashFlow_paypal = self.cashFlow_USHOP[self.cashFlow_USHOP["付款方式"] == "PayPal"]
		# add logger
		logging.info(f"對帳單中使用 paypal 的總共有 {cashFlow_paypal.shape[0]} 行")
		logging.info(f"paypal 檔總共有 {paypal.shape[0]} 行")

		cashFlow_paypal["交易序號"] = cashFlow_paypal["交易序號"].astype(str)
		
		# merge cashflow with paypal file
		cashFlow_paypal_merged = cashFlow_paypal.merge(paypal, left_on = "交易序號", right_on = "paypal_交易序號", how = "outer")

		cashFlow_paypal_merged["總額"] = cashFlow_paypal_merged["總額"].apply(lambda x: float(str(x).replace(",","") if x != None else None))
		

		self.matchAndExport(cashFlow_paypal_merged, "paypal", "交易序號", "paypal_交易序號", "交易金額", "總額")
		os.chdir("../../")



	def matchCashFlow_linepay(self, filename, linepay):
		os.chdir(f"{self.cur_time}/{filename}")

		logging.info("-------------- Starting matching of cashflow and linepay file ----------------")
		
		cashFlow_linepay = self.cashFlow_USHOP[self.cashFlow_USHOP["付款方式"] == "LINE Pay"]
		cashFlow_linepay["line_id"] = cashFlow_linepay["付款資訊"].apply(lambda x: x.split(":")[1].strip())
		
		# merge cashflow with paypal file
		cashFlow_linepay_merged = cashFlow_linepay.merge(linepay, left_on = "line_id", right_on = "訂單號碼", how = "outer")
		self.matchAndExport(cashFlow_linepay_merged, "linepay", "line_id", "訂單號碼", "交易金額", "付款金額")
		os.chdir("../../")


	def match(self):
		self.setup()
		if "國泰世華銀行" in self.uploads:
			self.matchCashFlow_cathay("國泰世華銀行", self.uploads["國泰世華銀行"])

		if "7-11" in self.uploads:
			self.matchCashFlow_711("7-11", self.uploads["7-11"])

		if "Paypal" in self.uploads:
			self.matchCashFlow_paypal("Paypal", self.uploads["Paypal"])

		if "Line-Pay" in self.uploads:
			self.matchCashFlow_linepay("Line-Pay", self.uploads["Line-Pay"])

