$(document).ready(function(){
	$(document).on("click",".qrcode", function(e){
		var uuid = $(this).data("uuidbook");
		$("showqrcode").empty();
		
		$.ajax({
			url : "/qrcode/",
			type : "POST",
			data : {"uuid" : ""+uuid+""},
			dataType : "json",
			cache : false,
			success : function(s) {
				$("#showqrcode").html(s.data.html);
				$("#modal-qrcode").modal("show")
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