$(document).ready(function(){
	$("#login").submit(function(e){
		e.preventDefault();
		$.ajax({
			url : "/",
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
});