$(document).ready(function(){
	$("#login").submit(function(e){
		e.preventDefault();
		$.ajax({
			url : "/login",
			type : "POST",
			data : $(this).serialize(),
			dataType : "json",
			cache : false,
			success : function(d) {
				Swal.fire({
					icon : d.icon,
					title : d.title,
					text : d.description
				}).then((result) => {
					if(d.redirect != ""){
						window.location = d.redirect
					}
				});
			},
			error : function(e) {
				Swal.fire({
					icon : "error",
					title : "เกิดข้อผิดพลาด",
					text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
				});
			}
		});
	});
	
	$("#register").submit(function(e){
		e.preventDefault();
		$.ajax({
			url : "/register",
			type : "POST",
			data : $(this).serialize(),
			dataType : "json",
			cache : false,
			success : function(d) {
				Swal.fire({
					icon : d.icon,
					title : d.title,
					text : d.description
				}).then((result) => {
					if(d.code == 200){
						window.location = "/"
					}
				});
			},
			error : function(e) {
				Swal.fire({
					icon : "error",
					title : "เกิดข้อผิดพลาด",
					text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
				});
			}
		});
	});

	$(document).on("click",".maproom",function(e){
		$("#maproommodal").modal("show");
	});
	
	$(document).on("click",".book",function(e){
		var id = $(this).data("roomuuid");

		$.ajax({
			url : "/selectroomd/"+id,
			type : "POST",
			dataType : "json",
			cache : false,
			success : function(d) {
				if(d.alert == "swalert") {
					Swal.fire({
						icon : d.data.icon,
						title : d.data.title,
						text : d.data.description,
						timer : 4000
					}).then((result) => {
						if(result.value){
							location.href=d.data.redirect;
						}
					});
				}else{
					$("#showroom").html(d.data.html);
					$("#bookrooms").modal("show");
					$("#selectroomjs").attr("src","/static/vendor/app.selectroom.js");
				}
			},
			error : function(e) {
				Swal.fire({
					icon : "error",
					title : "เกิดข้อผิดพลาด",
					text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
				});
			}
		});
	});

	$(document).on("click",".bookinfo",function(e){
		var id = $(this).data("roomuuid");

		$.ajax({
			url : "/selectroomi/"+id,
			type : "POST",
			dataType : "json",
			cache : false,
			success : function(d) {
				$("#showinfo").html(d.data.html);
				$("#bookinfo").modal("show");
			},
			error : function(e) {
				Swal.fire({
					icon : "error",
					title : "เกิดข้อผิดพลาด",
					text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
				});
			}
		});
	});
});