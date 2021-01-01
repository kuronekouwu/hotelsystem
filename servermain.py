import flask
import pymongo
import json
import datetime
import uuid
import hashlib
import os
import requests
import bcrypt
import base64
import time
import re
from __lib.promptpay import createqr_promptpay
from threading import Thread
from hashlib import sha256
from flask import Flask, render_template, request, abort, session, jsonify, redirect, send_from_directory, url_for
from gevent.pywsgi import WSGIServer
from werkzeug.utils import secure_filename

#Status 
STATUS_DATA = [
	"NOPAYMENT",
	"WAITINGPAYMENT",
	"SUCCESSPAYMENT",
	"FAILEDPAYMENT",
	"TIMEOUTPAYMENT"
]

path_config = "bin/config.json"

with open(path_config,"r",encoding="utf8") as conf :
	d_config = json.loads(conf.read())

app = Flask(f"{d_config['main']['title']} [ Admin ]")

# !!! DO NOT EDIT !!! #
#Flask Secret Key
app.secret_key = "nEq2k5HZci5KPdoOQJMhYETh7T_mFV-pXNIL0KPlOD4I_ySQyles7AefXGQB5B-VI1vgwNd30ltthuIsyxVwDA"
#!!!!!!!!!!!!!!!!!!!!!#

#Path API
app.config["IDCARD_PATH"] = rf"bin/api/idcard"
app.config["SLIPBANK_PATH"] = rf"bin/api/slipbank"
app.config["PATH_ROOM_IMAGES"] = rf"static/images/rooms"

#Type File Support
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG"]

#LIMIT FILE
app.config["MAX_IMAGE_FILESIZE"] = 3 * 1024 * 1024


@app.route("/")
def home() :
	profile = None
	
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

	return render_template(
		"home.html",
		title=d_config["main"]["title"],
		descripion=d_config["main"]["description"],
		navtitle=d_config["main"]["navbartitle"],
		page="หน้าหลัก",
		profile=profile,
		fb=d_config["contact"]["facebook"],
		fb_url=d_config["contact"]["facebook_url"],
		ig=d_config["contact"]["instragram"],
		ig_url=d_config["contact"]["instragram_url"],
		phone=d_config["contact"]["phone"],
		phone_format=re.sub("[0-9]","",d_config["contact"]["phone"])
	)

@app.route("/profile", methods=["GET","POST"])
def profile() :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		if request.method == "POST" :
			conn = __connectdb()
			
			if request.form["action"] == "editprofile" :
				if request.form["gender"] == "male" or request.form["gender"] == "female" :
					#Update User
					conn[__getconfigmongodb()["db"]]["user_members"].update_one({
						"uuid" : "%s" % session["__UUID"]
					},
					{
						"$set" : {
							"details.firstname" : "%s" % request.form["firstname"],
							"details.lastname" : "%s" % request.form["lastname"],
							"details.gender" : "%s" % request.form["gender"]
						}
					})

					return jsonify({
						"alert" : "swalert",
						"data" : {
							"title" : "สำเร็จ",
							"description" : "ระบบได้ทำการแก้ไขข้อมูลแล้ว",
							"icon" : "success",
							"redirect" : "/"
						}
					})

			if request.form["action"] == "changepassowrd" :
				if request.form["password"] == request.form["conpassword"] :
					#Update User
					conn[__getconfigmongodb()["db"]]["user_members"].update_one({
						"uuid" : "%s" % session["__UUID"]
					},
					{
						"$set" : {
							"password" : "%s" % bcrypt.hashpw(request.form["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
						}
					})

					return jsonify({
						"alert" : "swalert",
						"data" : {
							"title" : "สำเร็จ",
							"description" : "ระบบได้ทำการแก้ไขข้อมูลแล้ว",
							"icon" : "success",
							"redirect" : "/"
						}
					})

				return jsonify({
					"alert" : "swalert",
					"data" : {
						"title" : "รหัสผ่านไม่ตรงกัน",
						"description" : "กรุณาลองใหม่อีกครั้ง",
						"icon" : "warning",
						"redirect" : ""
					}
				})
			return abort(400)
			

		return render_template(
			"profile.html",
			title=d_config["main"]["title"],
			descripion=d_config["main"]["description"],
			navtitle=d_config["main"]["navbartitle"],
			page="โปรไฟล์",
			profile=profile
		)

	return redirect(url_for("home"))

@app.route("/rooms")
def roomslist() :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)
		
		return render_template(
			"roomlist.html",
			title=d_config["main"]["title"],
			descripion=d_config["main"]["description"],
			navtitle=d_config["main"]["navbartitle"],
			page="ลิสจองห้องพัก",
			profile=profile,
			rooms=__getroomsbook(session["__UUID"])
		)

	return redirect(url_for("home"))

@app.route("/rooms/<uuid>")
def roomsinfo(uuid) :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		f = __getroominfobook(
			uuid=session["__UUID"],
			uuidroom=uuid
		)


		if not f is None : 
			return render_template(
				"roominfo.html",
				title=d_config["main"]["title"],
				descripion=d_config["main"]["description"],
				navtitle=d_config["main"]["navbartitle"],
				page="ข้อมูลห้องพัก",
				profile=profile,
				inforoom=f
			)

		return redirect("/rooms",code=302)
		

	return redirect(url_for("home"))

@app.route("/rooms/<uuid>/infopayment",methods=["GET","POST"])
def infopayment(uuid) :
	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

		f = __getroominfobook(
			uuid=session["__UUID"],
			uuidroom=uuid
		)

		if f["status"] == "SUCCESSPAYMENT" or f["status"] == "WAITINGPAYMENT" :
			return redirect("/rooms",code=302)

		if not f is None : 
			if f["status"] == STATUS_DATA[4] :
				return render_template(
					"errors/roomtimeout.html",
					title=d_config["main"]["title"],
					descripion=d_config["main"]["description"],
					navtitle=d_config["main"]["navbartitle"],
					page="หมดเวลาชำระเงิน",
					profile=profile
				)

			if f["status"] == STATUS_DATA[3] :
				return render_template(
					"errors/roomfail.html",
					title=d_config["main"]["title"],
					descripion=d_config["main"]["description"],
					navtitle=d_config["main"]["navbartitle"],
					page="หมดเวลาชำระเงิน",
					profile=profile
				)

			try :
				r = requests.post("http://127.0.0.1:8085/checkidcard",json={"uuid" : "%s" % session["__UUID"]}, timeout=3)
			except Exception as e :
				print(f"[ Error ] : REQUEST << {e} >>")
				abort(500)

			return render_template(
				"infopayment.html",
				title=d_config["main"]["title"],
				descripion=d_config["main"]["description"],
				navtitle=d_config["main"]["navbartitle"],
				page="แจ้งชำระเงิน",
				profile=profile,
				inforoom=f,
				hideidcard=str(r.json()["code"])
			)
			
		return redirect("/rooms",code=302)
		

	return redirect("/login",code=302)


@app.route("/selectroom")
def selectroom() :
	profile = None

	if "__UUID" in session :
		profile = __getprofile(
			uuid=session["__UUID"]
		)

	rooms = __getrooms()
		
	return render_template(
		"selectroom.html",
		title=d_config["main"]["title"],
		descripion=d_config["main"]["description"],
		navtitle=d_config["main"]["navbartitle"],
		page="เลือกห้อง",
		profile=profile,
		rooms=rooms
	)

	#return redirect("/login",code=302)

@app.route("/login",methods=["GET","POST"])
def login() :
	if "__UUID" in session :
		return redirect(url_for("home"))

	if request.method == "POST" :
		c_user = __checkuser(
			user=request.form["username"],
			passwd=request.form["password"]
		)

		if not c_user is None :
			redirect_location = "/"
			session["__UUID"] = c_user["uuid"]

			if request.form["selectroom"] != "" and request.form["selectroom"] != "None" :
				redirect_location = "/selectroom?select_room=%s" % request.form["selectroom"]

			return jsonify({
				"code" : 200,
				"icon" : "success",
				"title" : "เข้าสู่ระบบสำเร็จ",
				"description" : "ระบบกำลังนำพาไปยังหน้าหลัก",
				"redirect" : "%s" % redirect_location
			}), 200

		return jsonify({
			"code" : 401,
			"icon" : "error",
			"title" : "เข้าสู่ระบบไม่สำเร็จ",
			"description" : "ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง โปรดกรุณาลองใหม่อีกครั้ง",
			"redirect" : ""
		}), 200

	
	return render_template(
		"login.html",
		title=d_config["main"]["title"],
		descripion=d_config["main"]["description"],
		navtitle=d_config["main"]["navbartitle"],
		page="เข้าสู่ระบบ",
		selroom=request.args.get("room_select")
	)

@app.route("/register",methods=["GET","POST"])
def register() :
	if "__UUID" in session :
		redirect(url_for("home"))

	if request.method == "POST" :
		if request.form["username"] != "" and request.form["password"] != "" and request.form["conpassword"] != "" and request.form["firstname"] != "" and request.form["lastname"] != "" and request.form["gender"] != "" and request.form["email"] != "" :
			if request.form["password"] == request.form["conpassword"] :
				c_user = __registeruser(
					user=request.form["username"],
					passwd=request.form["password"],
					firstname=request.form["firstname"],
					lastname=request.form["lastname"],
					gender=request.form["gender"],
					email=request.form["email"]
				)

				if c_user == "USERNAME_TAKEN" :
					return jsonify({
						"code" : 401,
						"icon" : "info",
						"title" : "ชื่อผู้ใช่นี้มีในระบบแล้ว",
						"description" : "กรุณาลองใหม่อีกครั้ง"
					}), 200
				
				if c_user == "SUCCESS" : 
					return jsonify({
						"code" : 200,
						"icon" : "success",
						"title" : "สมัครสมาชิกสำเร็จ",
						"description" : ""
					}), 200

			return jsonify({
				"code" : 401,
				"icon" : "info",
				"title" : "รหัสผ่านไม่ตรงกัน",
				"description" : "กรุณาลองใหม่อีกครั้ง"
			}), 200

		return jsonify({
			"code" : 401,
			"icon" : "warning",
			"title" : "ข้อมูลการสมัครไม่ครบ",
			"description" : "กรุณาลองใหม่อีกครั้ง"
		}), 200

	return render_template(
		"register.html",
		title=d_config["main"]["title"],
		descripion=d_config["main"]["description"],
		navtitle=d_config["main"]["navbartitle"],
		page="สมัครสมาชิก"
	)


@app.route("/logout")
def logout() :
	session.clear()
	return redirect(url_for("home"))

#API private
@app.route("/selectroomd/<rooms>", methods=["POST"])
def selectroomd(rooms) :
	if "__UUID" in session :
		room = __datarooms(
			uuid=session["__UUID"],
			roomid=rooms
		)

		if room != False :
			return jsonify({
				"alert" : "html",
				"data" : {
					"html" : "%s" % render_template(
						"roombook.html",
						data=room,
						status=str(room["status"]),
						images=f"{app.config['PATH_ROOM_IMAGES']}/{room['uuidroom']}.jpg"
					)
				}
			})

	return jsonify({
			"alert" : "swalert",
			"data" : {
				"title" : "โปรดกรุณาเข้าสู่ระบบ",
				"description" : "",
				"icon" : "error",
				"redirect" : "/login?room_select=%s" % rooms
			}
		})

#API private
@app.route("/selectroomi/<rooms>", methods=["POST"])
def selectroomi(rooms) :
	room = __datarooms_nouuid(
		roomid=rooms
	)

	if room != False :
		return jsonify({
			"alert" : "html",
			"data" : {
				"html" : "%s" % render_template(
					"roominfo_modal.html",
					data=room,
					status=str(room["status"]),
					images=f"{app.config['PATH_ROOM_IMAGES']}/{room['uuidroom']}.jpg"
				)
			}
		})

@app.route("/selectroomb", methods=["POST"])
def bookroom() :
	room = __datarooms(
		uuid=session["__UUID"],
		roomuuid=request.form["uuid"]
	)

	#print(room)

	if room == "LOGIN_REQUIRED" :
		return jsonify({
			"alert" : "swalert",
			"data" : {
				"title" : "โปรดกรุณาเข้าสู่ระบบ",
				"description" : "",
				"icon" : "error",
				"redirect" : "/login"
			}
		})

	if room == "ROOM_NOTFOUND" : 
		return jsonify({
			"alert" : "swalert",
			"data" : {
				"title" : "ไม่พบข้อมูลห้อง",
				"description" : "โปรดกรุณาเลือกใหม่",
				"icon" : "warning",
				"redirect" : "/selectroom"
			}
		}), 200

	if room["status"] == True :
		#Check Date is Vaild
		if request.form["startbook"] == "" or request.form["endbook"] == "" :
			return jsonify({
				"alert" : "swalert",
				"data" : {
					"title" : "กรุณากรอกวันที่พัก",
					"description" : "",
					"icon" : "info",
					"redirect" : ""
				}
			}), 200

		start = __checkdatevaild(request.form["startbook"])
		end = __checkdatevaild(request.form["endbook"])
		
		if start != False and end != False :
			diff = __datediff(request.form["startbook"],request.form["endbook"])

		while (True) :
			if int(datetime.datetime.strptime(request.form["startbook"], "%Y-%m-%d").timestamp()) <= int(datetime.datetime.now().timestamp()) :
				if str(datetime.datetime.now().strftime("%Y-%m-%d")) == str(request.form["startbook"]) :
					break

				return jsonify({
					"alert" : "swalert",
					"data" : {
						"title" : "กรุณาเลือกวันถัดไปเท่านั้น",
						"description" : "กรุณาลองใหม่อีกครั้ง",
						"icon" : "warning",
						"redirect" : ""
					}
				}), 200
			
			break 

		if diff > 0 :
			i_qr = __insertbook(
				uuiduser=session["__UUID"],
				uuidroom=request.form["uuid"],
				start=request.form["startbook"],
				end=request.form["endbook"],
				ammout=room["price"]*diff
			)
				
			if not i_qr[0] is None :
				return jsonify({
					"alert" : "payment",
					"data" : {
						"html" : "%s" % render_template(
							"payment.html",
							qrcodepay=i_qr[0],
							nameow=d_config["promptpay"]["name"],
							ammout=room["price"]*diff,
							uuidbook=i_qr[1]
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
		

	return jsonify({
		"alert" : "swalert",
		"data" : {
			"title" : "ห้องนี้มีคนถูกจองแล้ว",
			"description" : "โปรดกรุณาเลือกใหม่",
			"icon" : "warning",
			"redirect" : "/selectroom"
		}
	}), 200

@app.route("/uploaddata/", methods=["POST"])
def uploadimage() :
	data_idcard = ""

	#Check User if not Fake
	if "__UUID" in session :
		c = __getprofile(
			uuid=session["__UUID"]
		)

		#Get Data
		c_room = __checkbook(request.form["uuidroom"])

		if not c is None :
			if not c_room is None :
				if c_room["status"] == STATUS_DATA[1] or c_room["status"] == STATUS_DATA[2] or c_room["status"] == STATUS_DATA[3] or c_room["status"] == STATUS_DATA[4] :
					return jsonify({
						"code" : "ERR_HACKED"
					}),400
					
				#Get MD5 Key
				try :
					r_c = requests.post("http://127.0.0.1:8085/checkidcard",json={"uuid" : "%s" % session["__UUID"]})
					r = requests.post("http://127.0.0.1:8085/getuuid",json={"uuid" : "%s" % session["__UUID"]})
				except Exception as e :
					print(f"[ Error ] : REQUEST << {e} >>")
					abort(500)

				#Get File
				if r_c.json()["code"] == False :
					idcard = request.files["idcard"]
					data_idcard = idcard.read()

				slipbank  = request.files["paymentslip"]
				data_slipbank = slipbank.read()
			
				if __allowimg(slipbank.filename) :
					if len(data_idcard) >= app.config["MAX_IMAGE_FILESIZE"] and len(data_slipbank) >= app.config["MAX_IMAGE_FILESIZE"] :
						return jsonify({
							"code" : "ERR_FILE_OVER_SIZE",
							"alert" : "swalert",
							"data" : {
								"title" : "ไฟล์มีขนาดใหญ่เกิน",
								"description" : "ขนาดไฟล์ไม่เกิน 3 MB. กรุณาลองใหม่อีกครั้ง",
								"icon" : "warning",
								"redirect" : "%s" % request.url
							}
						}),200
					
					try :
						if __allowimg(idcard.filename)  :
							with open(f"{app.config['IDCARD_PATH']}/{r.json()['code']}.jpg","wb") as w :
								w.write(data_idcard)
						else :
							return jsonify({
								"code" : "ERR_FILE_NOTSUPPORT",
								"alert" : "swalert",
								"data" : {
									"title" : "ไฟล์นี้ไม่รองรับ",
									"description" : "รูปบัตรประชาชน ภาพรองรับเป็น JPG เท่านั้น กรุณาลองใหม่อีกครั้ง",
									"icon" : "error",
									"redirect" : ""
								}
							}),200
					except :
						pass

					with open(f"{app.config['SLIPBANK_PATH']}/{request.form['uuidroom']}.jpg","wb") as w :
						w.write(data_slipbank)

					#Updata Book
					__updatebook(request.form["uuidroom"],{"$set" : { "status" : "WAITINGPAYMENT", "email_admin" : True }})

					return jsonify({
						"code" : "OK",
						"alert" : "swalert",
						"data" : {
							"title" : "อัพโหลดสำเร็จ",
							"description" : "ระบบได้ทำการอัพโหลดข้อมูลแล้ว โปรดรอเจ้าหน้าที่ยืนยันภายใน 24 ชม.",
							"icon" : "success",
							"redirect" : "/rooms"
						}
					}), 200

				return jsonify({
					"code" : "ERR_FILE_NOTSUPPORT",
					"alert" : "swalert",
					"data" : {
						"title" : "ไฟล์นี้ไม่รองรับ",
						"description" : "รูปสลิป รองรับเป็น JPG เท่านั้น กรุณาลองใหม่อีกครั้ง",
						"icon" : "error",
						"redirect" : ""
					}
				}),200
					

		return jsonify({
			"code" : "ERR_NOTFOUND"
		}),404

@app.route("/qrcode/", methods=["POST"])
def qrcodedata() :
	conn = __connectdb()
	find = conn[__getconfigmongodb()["db"]]["bookroom"].find_one({"bookid" : "%s" % request.form["uuid"]})

	if not find is None :
		return jsonify({
			"alert" : "payment",
			"data" : {
				"html" : "%s" % render_template(
					"payment.html",
					qrcodepay=find["payment"]["payment_images"],
					nameow=d_config["promptpay"]["name"],
					ammout=find["payment"]["payment_ammout"],
					uuidbook=find["bookid"]
				)
			}
		})

	return jsonify(
		{
			"code" : "ERR_BADREQUEST"
		}
	),400
		

@app.route("/download/<path:path>")
def jsfile(path):
	if "__UUID" in session :
		c_pro = __getprofile(
			uuid=session["__UUID"]
		) 

		if not c_pro is None :
			return send_from_directory("bin/downloads", path)
	
	abort(403)

#Function
def __connectdb() :
	e = None 

	try :
		conn = pymongo.MongoClient(__getconnectmongodb(),serverSelectionTimeoutMS=5000)
		conn.server_info()

		return conn
	except Exception as e :
		print("Failed connect to MongoDB retrying connect....")

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

def __datarooms_nouuid(roomid=None,roomuuid=None) :
	conn = __connectdb()

	if not roomid is None :
		return conn[__getconfigmongodb()["db"]]["rooms"].find_one(
			{"room" : "%s" % roomid}
		)
	elif not roomuuid is None :
		return conn[__getconfigmongodb()["db"]]["rooms"].find_one(
			{"uuidroom" : "%s" % roomuuid}
		)

def __getprofile(uuid) :
	conn = __connectdb()

	return conn[__getconfigmongodb()["db"]]["user_members"].find_one({
		"uuid" : "%s" % uuid
	})

def __getrooms() :
	res = []
	roomsdata = []
	conn = __connectdb()

	for rooms in conn[__getconfigmongodb()["db"]]["groupdata"].find({}) :
		for roomsdetails in conn[__getconfigmongodb()["db"]]["rooms"].find({ "uuidgroup" : "%s" % rooms["uuid"]}) :
			del roomsdetails["_id"]
			roomsdata.append(roomsdetails)

		res.append({
			"title" : "%s" % rooms["title"],
			"details" : "%s" % rooms["details"],
			"roomdetail" :  roomsdata
		})

	return res

def __getroomsbook(uuid) :
	res = []
	conn = __connectdb()

	for rooms in conn[__getconfigmongodb()["db"]]["bookroom"].find({ "user.uuid" : "%s" % uuid }) :
		del rooms["_id"]

		for roomdetail in conn[__getconfigmongodb()["db"]]["rooms"].find({ "uuidroom" : "%s" % rooms["details"]["roomuuid"] }) :
			rooms["details"]["roomuuid"] = roomdetail["room"]

		res.append(rooms)

	return res

def __getroominfobook(uuid,uuidroom) :
	conn = __connectdb() 

	if not __getprofile(uuid) is None :
		find =  conn[__getconfigmongodb()["db"]]["bookroom"].find_one({"bookid" : "%s" % uuidroom})

		if not find is None :
			findroom  = conn[__getconfigmongodb()["db"]]["rooms"].find_one({"uuidroom" : "%s" % find["details"]["roomuuid"]})
			find["details"].update({
				"roomname" : findroom["room"]
			})

			#print(findroom)
			if find["status"] == STATUS_DATA[2] :
				findgroup  = conn[__getconfigmongodb()["db"]]["groupdata"].find_one({"uuid" : "%s" % findroom["uuidgroup"]})
				find.update({
					"password_group" : "%s" % base64.b64decode(findgroup["password"].encode("utf-8")).decode("utf-8"), 
					"password_room" : "%s" % base64.b64decode(findroom["password_room"].encode("utf-8")).decode("utf-8")
				})

			return find

	return None 


def __insertbook(uuiduser,uuidroom,start,end,ammout) :
	conn = __connectdb()

	if not __getprofile(uuiduser) is None :
		#Create QRCode
		qr = createqr_promptpay(
			account=re.sub("[0-9","",d_config["promptpay"]["account"]),
			one_time=True,
			country="TH",
			money="%s" % ammout,
			currency="THB"
		)
		
		b_uuid = uuid.uuid4()

		#Insert Data
		conn[__getconfigmongodb()["db"]]["bookroom"].insert_one({ 
			"date" : datetime.datetime.now(), 
			"bookid" : "%s" % b_uuid, 
			"status" : "NOPAYMENT", 
			"details" : {
				"roomuuid" : "%s" % uuidroom, 
				"start" : datetime.datetime.strptime(start, "%Y-%m-%d"), 
				"end" : datetime.datetime.strptime(end, "%Y-%m-%d"),
				"statusroom" : None
			},
			"payment" : {
				"payment_status" : False, 
				"payment_ammout" : int(ammout),
				"payment_images" : "%s" % qr,
				"payment_timeout" : datetime.datetime.now() + datetime.timedelta(hours=1)
			},
			"user" : {
				"uuid" : "%s" % uuiduser,
 			},
			"email_checkpayment" : False,
			"email_admin" : False
		}) 

		#Update Room Status
		conn[__getconfigmongodb()["db"]]["rooms"].update_one({
			"uuidroom" : "%s" % uuidroom
		},
		{
			"$set" : {
				"status" : False
			}
		})
		return [qr,b_uuid]

def __datediff(start,end) :
	d1 = datetime.datetime.strptime(start, "%Y-%m-%d")
	d2 = datetime.datetime.strptime(end, "%Y-%m-%d")
	diff = d2 - d1
	
	return diff.days

def __checkbook(uuid) :
	conn = __connectdb()

	return conn[__getconfigmongodb()["db"]]["bookroom"].find_one({
		"bookid" : "%s" % uuid
	})
def __updatebook(uuid,json=None) :
	conn = __connectdb()

	return conn[__getconfigmongodb()["db"]]["bookroom"].update_one({"bookid" : "%s" % uuid},json) 

def __updateuser(do,uuid,data) :
	conn = __connectdb()

	if do == "secretkey" :
		json = {
			"$set" : {
				"secretkey" : "%s" % data
			}
		}

	return conn[__getconfigmongodb()["db"]]["user_members"].update_one({"uuid" : "%s" % uuid},json) 

def __checkdatevaild(string) : 
	try:
		datetime.datetime.strptime(string,"%Y-%m-%d")
		return True
	except ValueError:
		return False

def __allowimg(filename) :
	if not "." in filename:
		return False

	ext = filename.rsplit(".", 1)[1]

	if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
		return True
	else:
		return False

def __checkuser(user,passwd) :
	conn = __connectdb()

	#Get Username
	g = conn[__getconfigmongodb()["db"]]["user_members"].find_one({
		"username" : "%s" % user,
	}) 

	if not g is None :
		if bcrypt.checkpw(password=passwd.encode("utf-8"),hashed_password=g["password"].encode("utf-8")) :
			return g
	
	return None

def __registeruser(user,passwd,firstname,lastname,gender,email) :
	conn = __connectdb()
	find = conn[__getconfigmongodb()["db"]]["user_members"].find_one({"username" : "%s" % user})
	u_uuid = uuid.uuid4()

	if find is None :
		#Insert Data
		regis = conn[__getconfigmongodb()["db"]]["user_members"].insert_one({ 
			"username" : "%s" % user, 
			"password" : "%s" % bcrypt.hashpw(passwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"), 
			"details" : {
				"firstname" : "%s" % firstname, 
				"lastname" : "%s" % lastname, 
				"gender" : "%s" % gender
			}, 
			"uuid" : "%s" % u_uuid, 
			"email" : "%s" % email
		})

		if not regis is None :
			return "SUCCESS"
	
	return "USERNAME_TAKEN"

#Thread [ Check if user not payment ]
def __thread_checkpayment() :
	conn = __connectdb()

	while True :
		try :
			for data in conn[__getconfigmongodb()["db"]]["bookroom"].find({}) :
				if not data["payment"]["payment_timeout"] is None :
					if datetime.datetime.now().timestamp() >= data["payment"]["payment_timeout"].timestamp() :
						#Update Bookroom
						conn[__getconfigmongodb()["db"]]["bookroom"].update_one({
							"bookid" : "%s" % data["bookid"]
						},
						{
							"$set" : {
								"status" : "%s" %  STATUS_DATA[4],
								"payment.payment_images" : None,
								"payment.payment_timeout" : None,
							}
						})

						#Update Room
						conn[__getconfigmongodb()["db"]]["rooms"].update_one({
							"uuidroom" : "%s" % data["details"]["roomuuid"]
						},
						{
							"$set" : {
								"status" : True
							}
						})
		except :
			pass

		time.sleep(1)

#Thread [ Check end Booked ]
def __thread_endbooked() :
	conn = __connectdb()

	while True :
		try :
			for data in conn[__getconfigmongodb()["db"]]["bookroom"].find({}) :
				if data["details"]["statusroom"] != "ENDBOOKED" :
					if datetime.datetime.now().timestamp() >= data["details"]["end"].timestamp() :
						#Update Bookroom
						conn[__getconfigmongodb()["db"]]["bookroom"].update_one({
							"bookid" : "%s" % data["bookid"]
						},
						{
							"$set" : {
								"details.statusroom" : "ENDBOOKED"
							}
						})

						#Update Room
						conn[__getconfigmongodb()["db"]]["rooms"].update_one({
							"uuidroom" : "%s" % data["details"]["roomuuid"]
						},
						{
							"$set" : {
								"status" : True
							}
						})
		except :
			pass

		time.sleep(1)

if __name__ == "__main__" : 
	#Start Thread
	thread = Thread(target=__thread_checkpayment)
	thread.daemon = True
	thread2 = Thread(target=__thread_endbooked)
	thread2.daemon = True

	thread.start()
	thread2.start()

	app.run(port=8082,debug=True)