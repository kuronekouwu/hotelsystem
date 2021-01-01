# Coded By wannaphong
# https://github.com/wannaphong/pypromptpay

import libscrc
import qrcode
import io
import base64

def createqr_promptpay(account,one_time=True,country="TH",money="",currency="THB"):
	Version = "0002"+"01" # เวชั่นของ  PromptPay
	if one_time == True: # one_time คือ ต้องการให้โค้ดนี้ครั้งเดียวหรือไม่
		one_time = "010212" # 12 ใช้ครั้งเดียว
	else:
		one_time ="010211" # 11 ใช้ได้้หลายครั้ง
	
	if len(account) == 10 or len(account) == 13 : 
		merchant_account_information = "2937" # ข้อมูลผู้ขาย
	else :
		merchant_account_information = "2939" # ข้อมูลผู้ขาย

	merchant_account_information += "0016"+"A000000677010111" # หมายเลขแอปพลิเคชั่น PromptPay
	if len(account) == 10: #ถ้าบัญชีนี้เป็นเบอร์โทร
		account = list(account)
		merchant_account_information += "011300" # 01 หมายเลขโทรศัพท์ ความยาว 13 ขึ้นต้น 00
		if country == "TH":
			merchant_account_information += "66" # รหัสประเทศ 66 คือประเทศไทย
		del account[0] # ตัดเลข 0 หน้าเบอร์ออก
		merchant_account_information += ''.join(account)

	elif len(account) == 13 : #ถ้าบัญชีนี้เป็นบัตรประชาชน
		merchant_account_information += "0213" + account.replace('-','')
	else : #ไม่ใช่เบอร์โทร และ บัตรประชาชน เป็นเลขอ้างอิง
		merchant_account_information += "0315" + account + "5303764"

	country = "5802" + country # ประเทศ
	if currency == "THB":
		currency = "5303" + "764" # "764"  คือเงินบาทไทย ตาม https://en.wikipedia.org/wiki/ISO_4217
	if money != "": # กรณีกำหนดเงิน
		check_money = money.split('.') # แยกจาก .
		if len(check_money) == 1 or len(check_money[1]) == 1: # กรณีที่ไม่มี . หรือ มีทศนิยมแค่หลักเดียว
			money = "54" + "0" + str(len(str(float(money))) + 1) + str(float(money)) + "0"
		else:
			money = "54" + "0" + str(len(str(float(money)))) + str(float(money)) # กรณีที่มีทศนิยมครบ
			
	check_sum = Version+one_time+merchant_account_information+country+currency+money+"6304" # เช็คค่า check sum

	check_sum1 = hex(libscrc.xmodem(check_sum.encode('ascii'), 0xffff)).replace('0x','')
	if len(check_sum1) < 4: # # แก้ไขข้อมูล check_sum ไม่ครบ 4 หลัก
		check_sum1 = ("0"*(4-len(check_sum1))) + check_sum1
	check_sum += check_sum1

	img = qrcode.make(check_sum.upper())
	buffered = io.BytesIO()
	img.save(buffered, format="PNG")
	buffered.seek(0)
	img_byte = buffered.getvalue()
	
	return "data:image/png;base64," + base64.b64encode(img_byte).decode()
