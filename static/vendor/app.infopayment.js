$(":file").filestyle({htmlIcon: "<i class=\"fas fa-file-image\"></i> ",text: "เลือกรูปภาพ"});


$("#uploaddata").submit(function(e){
	e.preventDefault();

	$.ajax({
		url : "/uploaddata/",
		data : new FormData($(this)[0]),
		dataType : "json",
		type : "POST",
		cache : false,
		contentType: false,
		processData: false,
		ontentType: false,
		success : function(s) {
			if(s.alert == "swalert") {
				Swal.fire({
					icon : s.data.icon,
					title : s.data.title,
					text : s.data.description,
					timer : 4000
				}).then((result) => {
					if(result.value) {
						if(s.data.redirect != "") {
							location.href=s.data.redirect;
						}
					}
				});
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