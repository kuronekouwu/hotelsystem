# Hotel System

ระบบจองห้องพักโรงแรง [ Flask Python ]

## FUNCTION :
- จองห้องพัก
- มีหลังบ้าน ( Admin )
- สแกนจ่ายด้วยพร้อมเพย์หลังจ้องห้องพัก
- มีระบบยกเลิกอัตโนมัติหลังไม่จ่ายภายใน 1 ชั่วโมง
- จัดการห้องพัก, Users, ประตูใหญ่
- มี API เพื่อป้องกันการดึงข้อมูล
- มี  File Config สามารถตั้งค่าในนั้นได้โลด!
- อื่น ๆ 

## สิ่งที่ต้องเตรียม  
- Python 3.7 +
- MongoDB [ BSON ]

## วิธีติดตั้ง
- ติดตั้ง Library ดังนี้  pip install flask, pymongo, fastapi, uvicorn, aiofiles, gevent, libscrc, qrcode, requests, bcrypt
- ตั้งค่า config.json ใน Folder "Bin" 
- อัพ File JSON ขึ้น MongoDB โดย File DB จะอยู่ใน db.rar
- รัน File servermain.py, serverapi.py และ serveradmin.py

พร้อมใช้งาน!

## URL
- URL User : http://127.0.0.1:8082
- URL Admin : http://127.0.0.1:9000

## หน้าบ้าน 
- User : members1
- Pass : members1

## หลังบ้าน 
- User : admin
- Pass : admin

## สุดท้ายนี้
Happy New Year 2021 ครับ!
