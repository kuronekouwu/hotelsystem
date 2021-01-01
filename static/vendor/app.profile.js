$(document).ready(function(){
	$(document).on("click",".changeprofile", function(e){
		$("#editprofile").modal("show");
	});

	$(document).on("click",".password", function(e){
		$("#mchangepassowrd").modal("show");
	});

	$("#profile-change").submit(function(e){
		e.preventDefault();
		$(".profilechange").attr("disabled",true);
		$.ajax({
			url : "/profile",
			type : "POST",
			data : $(this).serialize(),
			dataType : "json",
			cache : false,
			success : function(s) {
				$(".profilechange").attr("disabled",false);
				Swal.fire({
					icon : s.data.icon,
					title : s.data.title,
					text : s.data.description,
					timer : 4000
				}).then((result) =>{
					if(result.value){
						if(s.data.redirect != "") {
							location.href=s.data.redirect;
						}
					}
				});
			},
			error : function(e) { 
				$(".profilechange").attr("disabled",false);
				Swal.fire({
					icon : "error",
					title : "เกิดข้อผิดพลาด",
					text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
				});
			}
		});
	});

	$("#passwordchange").submit(function(e){
		e.preventDefault();
		$(".passwd").attr("disabled",true);
		$.ajax({
			url : "/profile",
			type : "POST",
			data : $(this).serialize(),
			dataType : "json",
			cache : false,
			success : function(s) {
				$(".passwd").attr("disabled",false);
				Swal.fire({
					icon : s.data.icon,
					title : s.data.title,
					text : s.data.description,
					timer : 4000
				}).then((result) =>{
					if(result.value){
						if(s.data.redirect != "") {
							location.href=s.data.redirect;
						}
					}
				});
				
			},
			error : function(e) { 
				$(".passwd").attr("disabled",false);
				Swal.fire({
					icon : "error",
					title : "เกิดข้อผิดพลาด",
					text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
				});
			}
		});
	});
});