import flask
import json
import pymongo
import hashlib
import uuid
import datetime
import base64
import bcrypt
import requests
import io
import smtplib
import ssl
import time
import __lib.thai_strftime as datetimethai
from __lib.promptpay import createqr_promptpay
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
from hashlib import sha256
from flask import Flask, render_template, request, jsonify, session, abort, redirect, send_from_directory, Response, send_file

#Set Path
path_config = "bin/config.json"

#Status 
STATUS_DATA = [
	"NOPAYMENT",
	"WAITINGPAYMENT",
	"SUCCESSPAYMENT",
	"FAILEDPAYMENT",
	"TIMEOUTPAYMENT"
]

with open(path_config,"r",encoding="utf8") as conf :
	d_config = json.loads(conf.read())

app = Flask(
	f"{d_config['main']['title']} [ Admin ]",
	static_folder="staticadmin",
	static_url_path="/static"
)

#Path Public
app.config["PATH_ROOM_IMAGES"] = rf"static/images/rooms"

#Type File Support
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG"]

#LIMIT FILE
app.config["MAX_IMAGE_FILESIZE"] = 3 * 1024 * 1024

# !!! DO NOT EDIT !!! #
#Flask Secret Key
app.secret_key = "IvFVxtLTxDCbFrzxxCCHnWkWfXmhxAyhLSgUFKboYNOkfsYpHuEWwsbfXfBlgkvDTiaarwMwCjyMrwFfkwKtFMVzExnlZkUJFmGgJikWjdakfGUCxysuXkrTUjIrhBYz"
#!!!!!!!!!!!!!!!!!!!!!#


@app.route("/", methods=["GET","POST"])
def login() :
	if "__UUID" in session :
		redirect("/",code=302)

	if request.method == "POST" :
		c_user = __checkuser(
			user=request.form["username"],
			passwd=request.form["password"]
		)

		if not c_user is None :
			session["__UUID"] = c_user["uuid"]

			return jsonify({
				"code" : 200,
				"icon" : "success",
				"title" : "เข้าสู่ระบบสำเร็จ",
				"description" : "ระบบกำลังนำพาไปยังหน้าหลัก",
				"redirect" : "/dashboard"
			}), 200

		return jsonify({
			"code" : 401,
			"icon" : "error",
			"title" : "เข้าสู่ระบบไม่สำเร็จ",
			"description" : "ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง โปรดกรุณาลองใหม่อีกครั้ง"
		}), 200


	return render_template(
		"admin/login.html",
		title=d_config["main"]["title"],
		descripion=d_config["main"]["description"],
		navtitle=d_config["main"]["navbartitle"],
		page="เข้าสู่ระบบ"
	)

@app.route("/dashboard")
def dashboard() :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		summerydata = __createsummerydashboard()

		
		return render_template(
			"admin/dashboard.html",
			title=d_config["main"]["title"],
			descripion=d_config["main"]["description"],
			navtitle=d_config["main"]["navbartitle"],
			page="แดชบอร์ด",
			profile=profile,
			summery=summerydata
		)

	return redirect("/",code=302)

@app.route("/listroom")
def listroom() :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		return render_template(
			"admin/listroom.html",
			title=d_config["main"]["title"],
			descripion=d_config["main"]["description"],
			navtitle=d_config["main"]["navbartitle"],
			page="ลิสห้องพัก",
			profile=profile,
			dataroom=__getrooms(),
			datagroup=__datagroup()
		)

	return redirect("/",code=302)

@app.route("/listgroup")
def listgroup() :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		return render_template(
			"admin/listgroup.html",
			title=d_config["main"]["title"],
			descripion=d_config["main"]["description"],
			navtitle=d_config["main"]["navbartitle"],
			page="ลิสกลุ่ม",
			profile=profile,
			datagroup=__datagroup()
		)

	return redirect("/",code=302)


@app.route("/listbook")
def listbook() :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		return render_template(
			"admin/listbook.html",
			title=d_config["main"]["title"],
			descripion=d_config["main"]["description"],
			navtitle=d_config["main"]["navbartitle"],
			page="ลิสการจองห้องพัก",
			profile=profile,
			databook=__getroomsbook()
		)

	return redirect("/",code=302)

@app.route("/checkpayment")
def checkpayment() :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		return render_template(
			"admin/checkpayment.html",
			title=d_config["main"]["title"],
			descripion=d_config["main"]["description"],
			navtitle=d_config["main"]["navbartitle"],
			page="ตรวจสอบการชำระเงิน",
			profile=profile,
			databook=__getroomsbook()
		)

	return redirect("/",code=302)

@app.route("/summerytotal")
def summerytotal() :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		return render_template(
			"admin/summerytotal.html",
			title=d_config["main"]["title"],
			descripion=d_config["main"]["description"],
			navtitle=d_config["main"]["navbartitle"],
			page="สรุปยอดทั้งหมด",
			profile=profile
		)

	return redirect("/",code=302)

@app.route("/manageusers")
def manageusers() :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		return render_template(
			"admin/manageusers.html",
			title=d_config["main"]["title"],
			descripion=d_config["main"]["description"],
			navtitle=d_config["main"]["navbartitle"],
			page="จัดการผู้ใช้งาน",
			profile=profile,
			users=__getusers()
		)

	return redirect("/",code=302)

@app.route("/logout")
def logout() :
	session.clear()
	return redirect("/",code=302)

#API private
@app.route("/insert", methods=["POST"])
def addgroup() :
	if "__UUID" in session :
		c_pro = __getprofile(
			uuid=session["__UUID"]
		)

		if not c_pro is None :
			if request.form["action"] == "addgroup" :
				#Check if Group same!
				if __datagroup(name=request.form["groupname"]) is None :
					#Insert data
					ins =  __insertgroup(
						title=request.form["groupname"],
						password=request.form["grouppassword"]
					)
					
					if ins != "" :
						try :
							if request.form["page"] == "true" :
								return __swalert(
									title="สำเร็จ",
									text="ระบบได้เพิ่มข้อมูลแล้ว",
									icon="success",
									redirect="/listgroup"
								) 
						except :
							return jsonify({
								"alert" : "html",
								"data" : {
									"html" : "%s" % render_template("admin/option_select.html",data_group=__datagroup())
								}
							})
				
				
				return __swalert(
					title="กลุ่มนี้ได้ถูกสร้างแล้ว",
					text="กรุณาใช้ชื่ออื่น",
					icon="info",
					redirect=""
				)

			if request.form["action"] == "addroom" : 		
				try :
					s = int(request.form["roomprice"])
					if s < 0 :
						
						return __swalert(
							title="ราคาห้องต้องเป็นจำนวนเต็มเท่านั้น",
							text="กรุณาลองใหม่อีกครั้ง",
							icon="warning",
							redirect=""
						)
				except :
					return abort(400)

				if not __datagroup(uuid=request.form["groupid"]) is None :
					try :
						room_images = request.files["roomimage"]
						data_room = room_images.read()

						if __allowimg(room_images.filename) :
							if len(data_room) <= app.config["MAX_IMAGE_FILESIZE"] :
								uid_room = uuid.uuid4()
								with open(f"{app.config['PATH_ROOM_IMAGES']}/{uid_room}.jpg","wb") as w :
									w.write(data_room)

									ins = __insertroom(
										uuidroom=uid_room,
										room=request.form["roomname"],
										password=request.form["roompassword"],
										price=int(request.form["roomprice"]),
										groupid=request.form["groupid"]
									)
									
									return __swalert(
										title="สำเร็จ",
										text="ระบบได้เพิ่มข้อมูลแล้ว",
										icon="success",
										redirect="/listroom"
									)

							return __swalert(
								title="ไฟล์มีขนาดใหญ่เกิน",
								text="ขนาดไฟล์ไม่เกิน 3 MB. กรุณาลองใหม่อีกครั้ง",
								icon="warning",
								redirect=""
							)

						return __swalert(
							title="ไฟล์นี้ไม่รองรับ",
							text="ภาพรองรับเป็น JPG เท่านั้น กรุณาลองใหม่อีกครั้ง",
							icon="error",
							redirect=""
						)
								
					except Exception as e :
						return abort(400)
				
			if request.form["action"] == "addbook" :
				room = __datarooms(
					uuid=session["__UUID"],
					roomuuid=request.form["roomuuid"]
				)
					
				if room == "LOGIN_REQUIRED" :
					return __swalert(
						title="โปรดกรุณาเข้าสู่ระบบ",
						text="",
						icon="error",
						redirect="/"
				)

				if room == "ROOM_NOTFOUND" : 
					return __swalert(
						title="ไม่พบข้อมูลห้อง",
						text="โปรดกรุณาเลือกใหม่",
						icon="warning",
						redirect="/listbook"
					)
					
				if room["status"] == True :
					start = __checkdatevaild(request.form["startbook"])
					end = __checkdatevaild(request.form["endbook"])

					if start != False and end != False :
						diff = __datediff(request.form["startbook"],request.form["endbook"])

					while (True) :
						if int(datetime.datetime.strptime(request.form["startbook"], "%Y-%m-%d").timestamp()) <= int(datetime.datetime.now().timestamp()) :
							if str(datetime.datetime.now().strftime("%Y-%m-%d")) == str(request.form["startbook"]) :
								break

							return __swalert(
								title="กรุณาเลือกวันถัดไปเท่านั้น",
								text="กรุณาลองใหม่อีกครั้ง",
								icon="warning",
								redirect=""
							)

						break 
							
					if diff > 0 :
						i_data = __insertbook(
							uuiduser=session["__UUID"],
							uuidroom=request.form["roomuuid"],
							start=request.form["startbook"],
							end=request.form["endbook"],
							ammout=room["price"]*diff,
							status=request.form["status"]
						)

						if not i_data is None :
							return __swalert(
								title="สำเร็จ",
								text="ระบบได้เพิ่มข้อมูลแล้ว",
								icon="success",
								redirect="/listbook"
							)
							
					return __swalert(
						title="กรุณาเลือกวันถัดไปเท่านั้น",
						text="กรุณาลองใหม่อีกครั้ง",
						icon="warning",
						redirect=""
					)

				return __swalert(
					title="ห้องนี้มีคนถูกจองแล้ว",
					text="โปรดกรุณาเลือกใหม่",
					icon="warning",
					redirect=""
				)

	return __swalert(
		title="โปรดกรุณาเข้าสู่ระบบ",
		text="",
		icon="error",
		redirect="/"
	)
	

@app.route("/edit", methods=["POST"])
def editroom() :
	if "__UUID" in session :
		c_pro = __getprofile(
			uuid=session["__UUID"]
		)

		if not c_pro is None :
			if request.form["action"] == "editroom" :
				try :
					s = float(request.form["roomprice"])
					if s < 0 :
						return __swalert(
							title="ราคาห้องต้องเป็นจำนวนเต็มเท่านั้น",
							text="กรุณาลองใหม่อีกครั้ง",
							icon="warning",
							redirect=""
						)
				except :
					abort(400)

				if not __datagroup(uuid=request.form["uuidgroup"]) is None :
					#Insert data
					ins =  __updateroom(
						room=request.form["roomname"],
						password=request.form["roompassword"],
						price=request.form["roomprice"],
						uuidroom=request.form["uuidroom"]
					)

						
					if not ins is None :
						return __swalert(
							title="สำเร็จ",
							text="ระบบได้ทำการแก้ไขข้อมูลแล้ว",
							icon="success",
							redirect="/listroom"
						)
			
			if request.form["action"] == "editgroup" :
				if not __datagroup(uuid=request.form["uuidgroup"]) is None :
					#Insert data
					ins =  __updategroup(
						title=request.form["groupname"],
						password=request.form["grouppassword"],
						uuidgroup=request.form["uuidgroup"]
					)

						
					if not ins is None :
						return __swalert(
							title="สำเร็จ",
							text="ระบบได้ทำการแก้ไขข้อมูลแล้ว",
							icon="success",
							redirect="/listgroup"
						)

			if request.form["action"] == "edituser" :
				upd = __updateuser(
					uuid=request.form["uuiduser"],
					firstname=request.form["firstname"],
					lastname=request.form["lastname"],
					email=request.form["emailuser"]
				)

				if not upd is None :
					return __swalert(
						title="สำเร็จ",
						text="ระบบได้ทำการแก้ไขข้อมูลแล้ว",
						icon="success",
						redirect="/manageusers"
					)

	return  __swalert(
		title="โปรดกรุณาเข้าสู่ระบบ",
		text="",
		icon="error",
		redirect="/"
	)

@app.route("/info", methods=["POST"])
def inforoom() :
	if "__UUID" in session :
		c_pro = __getprofile(
			uuid=session["__UUID"]
		)

		if not c_pro is None :
			if request.form["action"] == "inforoom" :
				return jsonify({
					"html" : "%s" % render_template("admin/inforoom.html",dataroom=__getinforoom(uuid=request.form["uuid"]))
				})
			
			if request.form["action"] == "infogroup" :
				return jsonify({
					"html" : "%s" % render_template("admin/infogroup.html",datagroup=__getinfogroup(uuid=request.form["uuid"]))
				})

			if request.form["action"] == "infobook" :
				return jsonify({
					"html" : "%s" % render_template("admin/infobook.html",databook=__getinfobook(uuid=request.form["uuid"]))
				})

			if request.form["action"] == "infousers" :
				return jsonify({
					"html" : "%s" % render_template("admin/infousers.html",datauser=__getuserinfo(uuid=request.form["uuid"]))
				})

	return __swalert(
		title="โปรดกรุณาเข้าสู่ระบบ",
		text="",
		icon="error",
		redirect="/"
	)


@app.route("/delete", methods=["POST"])
def deleteroom() :
	if "__UUID" in session :
		c_pro = __getprofile(
			uuid=session["__UUID"]
		)

		if not c_pro is None :
			c = __connectdb()

			if request.form["action"] == "deleteroom" :
				delete = c[__getconfigmongodb()["db"]]["rooms"].delete_one({
					"uuidroom" : "%s" % request.form["uuid"]
				}) 

				if not delete is None :
					return __swalert(
						title="สำเร็จ",
						text="ระบบได้ทำการลบข้อมูลแล้ว",
						icon="success",
						redirect="/listroom"
					)

			if request.form["action"] == "deletegroup" :
				delete = c[__getconfigmongodb()["db"]]["groupdata"].delete_one({
					"uuid" : "%s" % request.form["uuid"]
				}) 
				delete_m = c[__getconfigmongodb()["db"]]["rooms"].delete_many({
					"uuidroom" : "%s" % request.form["uuid"]
				}) 

				if not delete is None :
					return __swalert(
						title="สำเร็จ",
						text="ระบบได้ทำการลบข้อมูลแล้ว",
						icon="success",
						redirect="/listgroup"
					)
			if request.form["action"] == "deletebook" :
				delete = c[__getconfigmongodb()["db"]]["bookroom"].delete_one({
					"bookid" : "%s" % request.form["uuid"]
				}) 

				if not delete is None :
					return __swalert(
						title="สำเร็จ",
						text="ระบบได้ทำการลบข้อมูลแล้ว",
						icon="success",
						redirect="/listbook"
					)
			
			if request.form["action"] == "deleteuser" :
				delete = c[__getconfigmongodb()["db"]]["user_members"].delete_one({
					"uuid" : "%s" % request.form["uuid"]
				}) 

				if not delete is None :
					return __swalert(
						title="สำเร็จ",
						text="ระบบได้ทำการลบข้อมูลแล้ว",
						icon="success",
						redirect="/manageusers"
					)

	return __swalert(
		title="โปรดกรุณาเข้าสู่ระบบ",
		text="",
		icon="error",
		redirect="/"
	)

@app.route("/addbook")
def addbook() :
	if "__UUID" in session :
		c_pro = __getprofile(
			uuid=session["__UUID"]
		)
		res = []
		room = []

		if not c_pro is None :
			for x in __datagroup() :
				for y in __getrooms() :
					if x["uuid"] == y["uuidgroup"] and y["status"] == True :
						room.append({
							"uuid" : "%s" % y["uuidroom"],
							"name" : "%s" % y["room"],
							"price" : y["price"]
						})	
				res.append({
					"title" : "%s" % x["title"],
					"rooms" :  room
				})
			return jsonify({
				"alert" : "json",
				"data" : res
			})

	return __swalert(
		title="โปรดกรุณาเข้าสู่ระบบ",
		text="",
		icon="error",
		redirect="/"
	)

@app.route("/confrim",methods=["POST"]) 
def confrim() :
	if "__UUID" in session :
		c_pro = __getprofile(
			uuid=session["__UUID"]
		)

		if not c_pro is None :
			if request.form["action"] == "confrim" :
				s = False

				for x in STATUS_DATA :
					if x == request.form["status"] :
						s = True 
						break
				
				if s == False :
					abort(400)

				u = __updatebook(
					uuid=request.form["uuid"],
					status=request.form["status"],
				)

				if not u is None :
					return __swalert(
						title="สำเร็จ",
						text="ระบบได้ทำการบันทึกข้อมูลแล้ว",
						icon="success",
						redirect="/checkpayment"
					)

	return __swalert(
		title="โปรดกรุณาเข้าสู่ระบบ",
		text="",
		icon="error",
		redirect="/"
	)
@app.route("/summerydata", methods=["POST"])
def summerydata() :
	if "__UUID" in session :
		c_pro = __getprofile(
			uuid=session["__UUID"]
		)

		if not c_pro is None :
			if request.form["startsummery"] == "" or request.form["endsummery"] == "" :
				return __swalert(
					title="กรุณากรอกข้อมูลให้ครบ",
					text="",
					icon="warning",
					redirect=""
				)
			start = __checkdatevaild(request.form["startsummery"])
			end = __checkdatevaild(request.form["endsummery"])

			if start != False and end != False :
				#Set Array
				total = []
				res = []
				
				#Chart.js Array
				chartjs_lable = []
				chartjs_data = []

				diff = __datediff(request.form["startsummery"],request.form["endsummery"])

				c = __connectdb()

				if diff >= 0 :
					pipe = [
						{
							"$match" : { 
								"date" : { 
									"$gte" : datetime.datetime.strptime(request.form["startsummery"],"%Y-%m-%d"), 
									"$lt" : datetime.datetime.strptime(request.form["endsummery"],"%Y-%m-%d") 
								},
								"status" : "SUCCESSPAYMENT"
							},
						},
						{
							"$group" : {
								"_id" : {
									"date" : "$date"
								},
								"total" : {
									"$sum" : "$payment.payment_ammout"
								}
							}
						}
					]

					for x in c[__getconfigmongodb()["db"]]["bookroom"].aggregate(pipeline=pipe) :
						#Total All
						total.append(x["total"])

						#Summery Date
						res.append({
							"date" : x["_id"]["date"],
							"total" : x["total"]
						})

						#Chart.js Data
						chartjs_lable.append(datetimethai.thai_strftime(x["_id"]["date"],"%d %B %Y"))
						chartjs_data.append(x["total"])

					return jsonify({
						"alert" : "html",
						"data" : {
							"html" : "%s" % render_template(
								"admin/summerydata.html",
								datetime_all=res,
								total_all=sum(total),
								date_summery=[
									datetime.datetime.strptime(request.form["startsummery"],"%Y-%m-%d"),
									datetime.datetime.strptime(request.form["endsummery"],"%Y-%m-%d")
								],
								chartjs_lable=chartjs_lable,
								chartjs_data=chartjs_data
							)
						}
					})

				return jsonify({
					"alert" : "swalert",
					"data" : {
						"title" : "กรุณาเลือกวันถัดไปเท่านั้น",
						"description" : "กรุณาลองใหม่อีกครั้ง",
						"icon" : "warning",
						"redirect" : ""
					}
				}), 200

	return __swalert(
		title="โปรดกรุณาเข้าสู่ระบบ",
		text="",
		icon="error",
		redirect="/"
	)

@app.route("/js/<path:path>")
def jsfile(path):
	if "__UUID" in session :
		c_pro = __getprofile(
			uuid=session["__UUID"]
		) 

		if not c_pro is None :
			return send_from_directory("bin/js", path)
	
	abort(403)

@app.route("/idcard/<uuid>")
def idcardimage(uuid) :
	if "__UUID" in session :
		c = __getprofile(
			uuid=session["__UUID"]
		)

		if not c is None :
			#Request 
			r = requests.post("http://127.0.0.1:8085/idcardimage",json={"uuid" : "%s" % uuid}, stream=True)
			if r.status_code == 200 :
				return Response(io.BytesIO(r.content),mimetype="image/jpg")
			
	return jsonify({"code" : "ERR_AUTHFAIL"})

@app.route("/slipbank/<uuiduser>/<uuidbook>")
def slipbankimage(uuiduser,uuidbook) :
	if "__UUID" in session :
		c = __getprofile(
			uuid=session["__UUID"]
		)

		if not c is None :
			#Request 
			r = requests.post("http://127.0.0.1:8085/slipbankimage",json={"uuid" : "%s" % uuiduser, "uuid_book" : "%s" % uuidbook}, stream=True)
			if r.status_code == 200 :
				return Response(io.BytesIO(r.content),mimetype="image/jpg")
			
	return jsonify({"code" : "ERR_AUTHFAIL"})

def __connectdb() :
	try :
		conn = pymongo.MongoClient(__getconnectmongodb(),serverSelectionTimeoutMS=5000)
		conn.server_info()

		return conn
	except Exception as e :
		abort(500)

def __getconfigmongodb() :
	global path_config

	with open(path_config,"r",encoding="utf8") as conf :
		d = json.loads(conf.read())

		res = {
			"db" : d["mongodb"]["database"]
		}

		return res

def __getconnectmongodb() :
	global path_config

	with open(path_config,"r",encoding="utf8") as conf :
		d = json.loads(conf.read())
		if d["mongodb"]["srv"] is True :
			res = "mongodb+srv://%s:%s@%s/%s" % (
				d["mongodb"]["username"],
				d["mongodb"]["password"],
				d["mongodb"]["host"],
				d["mongodb"]["database_auth"]
			)
		else :
			res = "mongodb://%s:%s@%s:%s/%s" % (
				d["mongodb"]["username"],
				d["mongodb"]["password"],
				d["mongodb"]["host"],
				d["mongodb"]["port"],
				d["mongodb"]["database_auth"]
			)

		return res

def __updateuser(do,uuid,data) :
	conn = __connectdb()

	if do == "secretkey" :
		json = {
			"$set" : {
				"secretkey" : "%s" % data
			}
		}

	return conn[__getconfigmongodb()["db"]]["user_admin"].update_one({"uuid" : "%s" % uuid},json) 

def __updateroom(room,password,price,uuidroom) :
	c = __connectdb()

	if not c is None :
		return c[__getconfigmongodb()["db"]]["rooms"].update_one({
			"uuidroom" : "%s" % uuidroom  
		},
		{
			"$set" : {
				"room" : "%s" % room, 
				"price" : price, 
				"password_room" : "%s" % base64.b64encode(password.encode("utf-8")).decode("utf-8")
			}
		})

def __updateuser(uuid,firstname,lastname,email) : 
	c = __connectdb()

	if not c is None :
		return c[__getconfigmongodb()["db"]]["user_members"].update_one({
			"uuid" : "%s" % uuid  
		},
		{
			"$set" : {
				"details.firstname" : "%s" % firstname, 
				"details.lastname" : "%s" % lastname, 
				"email" : "%s" % email
			}
		})

def __updategroup(title,password,uuidgroup) :
	c = __connectdb()

	if not c is None :
		return c[__getconfigmongodb()["db"]]["groupdata"].update_one({
			"uuid" : "%s" % uuidgroup
		},
		{
			"$set" : {
				"title" : "%s" % title,
				"password" : "%s" % base64.b64encode(password.encode("utf-8")).decode("utf-8").decode("utf-8")
			}
		})

def __updatebook(uuid,status) :
	conn = __connectdb() 

	s_payment = False
	s_timeout = datetime.datetime.now() + datetime.timedelta(hours=1)

	if status == "SUCCESSPAYMENT" :
		s_payment = True
		s_timeout = None

	if not conn is None :
		return conn[__getconfigmongodb()["db"]]["bookroom"].update_one({
			"bookid" : "%s" % uuid
		},
		{
			"$set" : {
				"status" : "%s" % status,
				"payment.payment_status" : s_payment ,
				"payment.payment_timeout" : s_timeout,
				"details.statusroom" : "STARTEDBOOK",
				"email_checkpayment" : True
			}
		}) 

def __getprofile(uuid) :
	conn = __connectdb()

	return conn[__getconfigmongodb()["db"]]["user_admin"].find_one({
		"uuid" : "%s" % uuid
	})

def __getrooms() :
	res = []
	roomsdata = []
	conn = __connectdb()

	for rooms in conn[__getconfigmongodb()["db"]]["groupdata"].find({}) :
		for roomsdetails in conn[__getconfigmongodb()["db"]]["rooms"].find({"uuidgroup" : "%s" % rooms["uuid"]}) :
			del roomsdetails["_id"]
			roomsdetails.update({"group" : "%s" % rooms["title"]})
			roomsdata.append(roomsdetails)

	return roomsdata

def __getuserinfo(uuid) :
	conn = __connectdb()
	data = conn[__getconfigmongodb()["db"]]["user_members"].find_one({"uuid" : "%s" % uuid})

	return {
		"firstname" : "%s" % data["details"]["firstname"],
		"lastname" : "%s" % data["details"]["lastname"],
		"email" : "%s" % data["email"],
		"uuid" : "%s" % data["uuid"]
	}

def __datarooms(uuid,roomid=None,roomuuid=None) :
	find = __getprofile(uuid)
	if not find is None :
		conn = __connectdb()

		if not roomid is None :
			return conn[__getconfigmongodb()["db"]]["rooms"].find_one(
				{"room" : "%s" % roomid}
			)
		elif not roomuuid is None :
			return conn[__getconfigmongodb()["db"]]["rooms"].find_one(
				{"uuidroom" : "%s" % roomuuid}
			)

	return "LOGIN_REQUIRED"

def __datagroup(name=None,uuid=None) :
	c = __connectdb()

	if not c is None :
		if not name is None :
			return c[__getconfigmongodb()["db"]]["groupdata"].find_one({
				"title" : "%s" % name
			})

		if not name is None :
			return c[__getconfigmongodb()["db"]]["groupdata"].find_one({
				"uuid" : "%s" % uuid
			})

		return c[__getconfigmongodb()["db"]]["groupdata"].find({}) 

def __getroomsbook() :
	res = []
	conn = __connectdb()

	for rooms in conn[__getconfigmongodb()["db"]]["bookroom"].find({}) :
		del rooms["_id"]

		for roomdetail in conn[__getconfigmongodb()["db"]]["rooms"].find({ "uuidroom" : "%s" % rooms["details"]["roomuuid"] }) :
			rooms["details"].update({"roomname" : "%s" % roomdetail["room"]})

		for username in conn[__getconfigmongodb()["db"]]["user_members"].find({"uuid" : "%s" % rooms["user"]["uuid"]}) :
			rooms["user"].update({"name" : "%s" % username["details"]["firstname"] + " " + username["details"]["lastname"]})

		res.append(rooms)

	return res

def __getusers() :
	res = []
	conn = __connectdb()
	
	for users in conn[__getconfigmongodb()["db"]]["user_members"].find({}) :
		res.append({
			"uuid" : "%s" % users["uuid"],
			"user" : "%s" % users["username"],
			"name" : "%s %s" % (users["details"]["firstname"],users["details"]["lastname"]),
			"email" : "%s" % users["email"]
		})
	
	return res

def __insertgroup(title,password) :
	c = __connectdb()

	if not c is None :
		uuid_room = uuid.uuid4()

		ins = c[__getconfigmongodb()["db"]]["groupdata"].insert_one({
			"uuid" : "%s" % uuid_room,
			"title" : "%s" % title,
			"details" : "",
			"password" : "%s" % base64.b64encode(password.encode("utf-8")).decode("utf-8")
		})

		if not ins is None :
			return uuid_room

		return None 

	abort(500)
	
def __insertroom(uuidroom,room,password,price,groupid) :
	c = __connectdb()

	if not c is None :
		#uuid_room = uuid.uuid4()

		ins =  c[__getconfigmongodb()["db"]]["rooms"].insert_one({ 
			"room" : "%s" % room, 
			"status" : True, 
			"price" : int(price), 
			"admin" : {
				"create_at" : datetime.datetime.now(), 
				"create_by" : "%s" % __getprofile(uuid=session["__UUID"])["details"]["name"]
			}, 
			"uuidroom" : "%s" % uuidroom, 
			"uuidgroup" : "%s" % groupid, 
			"password_room" : "%s" % base64.b64encode(password.encode("utf-8")).decode("utf-8")
		})

		if not ins is None :
			return True

def __insertbook(uuiduser,uuidroom,start,end,ammout,status) :
	conn = __connectdb()

	if not __getprofile(uuiduser) is None :
		s = False

		for x in STATUS_DATA :
			if x == status :
				s = True 
				break
		
		if s == False :
			abort(400)

		#Create QRCode
		qr = createqr_promptpay(
			account=d_config["promptpay"]["account"],
			one_time=True,
			country="TH",
			money="%s" % ammout,
			currency="THB"
		)
		
		b_uuid = uuid.uuid4()

		#Check if SUCCESS
		if status == "SUCCESSPAYMENT" :
			payment_status = True
			payment_timeout = None 
		else :
			payment_status = False
			payment_timeout = datetime.datetime.now() + datetime.timedelta(hours=1)

		conn[__getconfigmongodb()["db"]]["bookroom"].insert_one({ 
			"date" : datetime.datetime.now(), 
			"bookid" : "%s" % b_uuid, 
			"status" : "%s" % status, 
			"details" : {
				"roomuuid" : "%s" % uuidroom, 
				"start" : datetime.datetime.strptime(start, "%Y-%m-%d"), 
				"end" : datetime.datetime.strptime(end, "%Y-%m-%d")
			},
			"payment" : {
				"payment_status" : payment_status, 
				"payment_ammout" : ammout,
				"payment_images" : "%s" % qr,
				"payment_timeout" : payment_timeout
			},
			"user" : {
				"uuid" : "%s" % uuiduser,
 			},
			"email_checkpayment" : False,
			"email_admin" : False
		})

		return [qr,b_uuid]

def __getinforoom(uuid) :
	c = __connectdb() 

	if not c is None :
		return c[__getconfigmongodb()["db"]]["rooms"].find_one({
			"uuidroom" : "%s" % uuid
		})

def __getinfogroup(uuid) :
	c = __connectdb() 

	if not c is None :
		return c[__getconfigmongodb()["db"]]["groupdata"].find_one({
			"uuid" : "%s" % uuid
		})

def __createsummerydashboard() :
	#Chart.js Array
	chartjs_lable = []
	chartjs_data = []

	#Connect DB
	c = __connectdb()

	#Get total today 
	pipe_today = [
		{
			"$match" : { 
				"date" : { 
					"$gte" : datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"),"%Y-%m-%d"), 
					"$lt" : datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),"%Y-%m-%d") 
				},
				"status" : "SUCCESSPAYMENT"
			},
		},
		{
			"$group" : {
				"_id" : {
					"date" : "$date"
				},
				"total" : {
					"$sum" : "$payment.payment_ammout"
				}
			}
		}
	]

	pipe_month = [
		{
			"$match" : { 
				"date" : { 
					"$gte" : datetime.datetime.strptime(datetime.datetime.now().replace(day=1).strftime("%Y-%m-%d"),"%Y-%m-%d"), 
					"$lt" :datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),"%Y-%m-%d") 
				},
				"status" : "SUCCESSPAYMENT"
			},
		},
		{
			"$group" : {
				"_id" : {
					"date" : "$date"
				},
				"total" : {
					"$sum" : "$payment.payment_ammout"
				}
			}
		}
	]

	pipe_weeken = [
		{
			"$match" : { 
				"date" : { 
					"$gte" : datetime.datetime.strptime((datetime.datetime.now() - datetime.timedelta(weeks=1)).strftime("%Y-%m-%d"),"%Y-%m-%d"), 
					"$lt" :datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),"%Y-%m-%d") 
				},
				"status" : "SUCCESSPAYMENT"
			},
		},
		{
			"$group" : {
				"_id" : {
					"date" : "$date"
				},
				"total" : {
					"$sum" : "$payment.payment_ammout"
				}
			}
		}
	]

	today_data = list(c[__getconfigmongodb()["db"]]["bookroom"].aggregate(pipeline=pipe_today))
	month_data = list(c[__getconfigmongodb()["db"]]["bookroom"].aggregate(pipeline=pipe_month))
	request_book =  c[__getconfigmongodb()["db"]]["bookroom"].find({"status" : "%s" % STATUS_DATA[1]}).count()


	if len(today_data) > 0 :
		total_today_res = today_data[0]["total"]
	else :
		total_today_res = 0
	
	if len(month_data) > 0 :
		total_month_res = month_data[0]["total"]
	else :
		total_month_res = 0

	for x in c[__getconfigmongodb()["db"]]["bookroom"].aggregate(pipeline=pipe_weeken) :
		#Chart.js Data
		chartjs_lable.append(datetimethai.thai_strftime(x["_id"]["date"],"%d %B %Y"))
		chartjs_data.append(x["total"])

	return {
		"total_today" : total_today_res,
		"total_month" : total_month_res,
		"requests_book" : request_book,
		"data_chart": {
			"chartjs_lable" : chartjs_lable,
			"chartjs_data" : chartjs_data
		}
	}

def __getinfobook(uuid) :
	conn = __connectdb()

	find_book = conn[__getconfigmongodb()["db"]]["bookroom"].find_one({"bookid" : "%s" % uuid}) 

	if not find_book is None :
		find_room = conn[__getconfigmongodb()["db"]]["rooms"].find_one({ "uuidroom" : "%s" % find_book["details"]["roomuuid"] })
		if not find_room is None :
			find_book["details"].update({"roomname" : "%s" % find_room["room"]})
			find_book["details"].update({"price" : find_room["price"]})
		if find_book["status"] == STATUS_DATA[2] :
			findgroup  = conn[__getconfigmongodb()["db"]]["groupdata"].find_one({"uuid" : "%s" % find_room["uuidgroup"]})
			find_book.update({
				"password_group" : "%s" % base64.b64decode(findgroup["password"].encode("utf-8")).decode("utf-8"), 
				"password_room" : "%s" % base64.b64decode(find_room["password_room"].encode("utf-8")).decode("utf-8")
			})

		find_user = conn[__getconfigmongodb()["db"]]["user_members"].find_one({"uuid" : "%s" % find_book["user"]["uuid"]})
		if not find_user is None :
			find_book["user"].update({"name" : "%s" % find_user["details"]["firstname"] + " " + find_user["details"]["lastname"], "email" : "%s" % find_user["email"]})
		else :
			c_pro = __getprofile(
				uuid=session["__UUID"]
			)

			if not c_pro is None :
				find_book["user"].update({"name" : "%s" % c_pro["details"]["name"]})
 
	return find_book

def __allowimg(filename) :
	if not "." in filename:
		return False

	ext = filename.rsplit(".", 1)[1]

	if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
		return True
	else:
		return False

#Send E-mail
def __send_email(name,roomname,password_group,password_room,uuid,emailreciever) :
	global d_config

	msg = f"""สวัสดีครับคุณ, {name}

ตอนนี้ห้องพักของคุณได้ทำการจองห้องสำเร็จแล้ว และ ชำระเงินสำเร็จแล้วนะครับ โดยข้อมูลรายละเอียดดังนี้

ห้องพัก : {roomname}
รหัสผ่านประตูใหญ่ : {password_group}
รหัสผ่านห้องพัก : {password_room}

รายละเอียดเพิ่มเติม
{d_config['main']['url']}/rooms/{uuid}


- {d_config['main']['title']}
	"""

	try :
		#Setup Mail TEXT
		context = ssl.create_default_context()
		session_email = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
		session_email.login(d_config["emailsetting"]["email"], d_config["emailsetting"]["password"])
		
		message = MIMEMultipart()
		message['From'] = d_config["main"]["email"]
		message['To'] = emailreciever
		message['Subject'] = f"ข้อมูลห้องพัก {roomname}" 
		message.attach(MIMEText(msg, 'plain'))

		#Setting And Send Mail
		text = message.as_string()
		session_email.sendmail(d_config["emailsetting"]["email"], emailreciever, text)
		session_email.quit()

		return True 
	except Exception as e :
		print(e)
		return False

def __send_email_admin(name,roomname,uuid) :
	global d_config

	msg = f"""ข้อมูลคำร้องขอการจองห้องพัก

ID การจองห้อง : {uuid}
ห้องพัก : {roomname}
ชื่อ : {name}
สถานะ : รอชำระเงิน

รายละเอียด : {d_config['main']['url_admin']}/checkpayment

- {d_config['main']['title']}"""
	try :
		#Setup Mail TEXT
		context = ssl.create_default_context()
		session_email = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
		session_email.login(d_config["emailsetting"]["email"], d_config["emailsetting"]["password"])

		message = MIMEMultipart()
		message['From'] = d_config["main"]["email"]
		message['To'] = d_config["emailsetting"]["email_admin"]
		message['Subject'] = f"คำร้องขอการจองห้องพัก" 
		message.attach(MIMEText(msg, 'plain'))

		#Setting And Send Mail
		text = message.as_string()
		session_email.sendmail(d_config["emailsetting"]["email"], d_config["emailsetting"]["email_admin"], text)
		session_email.quit()

		return True 
	except Exception as e :
		print(e)
		return False

#Respone JSON
def __swalert(title,text,icon,redirect) :
	return jsonify(
		{
			"alert" : "swalert",
			"data" : {
				"title" : "%s" % title,
				"description" : "%s" % text,
				"icon" : "%s" % icon,
				"redirect" : "%s" % redirect
			}
		})

#Anthor Function
def __formatgender(gender) : 
	res = {
		"male" : "ชาย",
		"female" : "หญิง"
	} 
	return res[gender]
	
def __checkdatevaild(string) : 
	try:
		datetime.datetime.strptime(string,"%Y-%m-%d")
		return True
	except ValueError:
		return False

def __datediff(start,end) :
	d1 = datetime.datetime.strptime(start, "%Y-%m-%d")
	d2 = datetime.datetime.strptime(end, "%Y-%m-%d")
	diff = d2 - d1
	
	return diff.days

def __checkuser(user,passwd) :
	conn = __connectdb()

	#Get Username
	g = conn[__getconfigmongodb()["db"]]["user_admin"].find_one({
		"username" : "%s" % user,
	}) 

	if not g is None :
		if bcrypt.checkpw(password=passwd.encode("utf-8"),hashed_password=g["password"].encode("utf-8")) :
			return g
	
	return None

def __thread_checksendmail() :

	conn = __connectdb()

	while True :
		try :
			for data in conn[__getconfigmongodb()["db"]]["bookroom"].find({}) :
				if not data["email_checkpayment"] is None :
					if data["email_checkpayment"] == True :
						find = __getinfobook(
							uuid=data["bookid"]
						)

						if not find is None :
							email = __send_email(
								name=find["user"]["name"],
								roomname=find["details"]["roomname"],
								password_group=find["password_group"],
								password_room=find["password_room"],
								uuid=find["bookid"],
								emailreciever=find["user"]["email"]
							)

							if not email is None :
								#Update Bookroom
								conn[__getconfigmongodb()["db"]]["bookroom"].update_one({
									"bookid" : "%s" % data["bookid"]
								},
								{
									"$set" : {
										"email_checkpayment" : None
									}
								})
		except :
			pass
		
		time.sleep(3)

def __thread_checksendmail_checkpayment() :
	conn = __connectdb()

	while True :
		try :
			for data in conn[__getconfigmongodb()["db"]]["bookroom"].find({}) :
				if not data["email_admin"] is None :
					if data["email_admin"] == True :
						find = __getinfobook(uuid=data["bookid"])

						if not find is None :
							email = __send_email_admin(
								name=find["user"]["name"],
								roomname=find["details"]["roomname"],
								uuid=find["bookid"]
							)

							if not email is None :
								#Update Bookroom
								conn[__getconfigmongodb()["db"]]["bookroom"].update_one({
									"bookid" : "%s" % data["bookid"]
								},
								{
									"$set" : {
										"email_admin" : None
									}
								})
		except :
			pass
		
		time.sleep(3)

if __name__ == "__main__" :
	thread = Thread(target=__thread_checksendmail)
	thread.daemon = True
	thread2 = Thread(target=__thread_checksendmail_checkpayment)
	thread2.daemon = True

	thread.start()
	thread2.start()

	app.run(port=9000,debug=True)