var start = "";
var end = "";
var price_preday = 0;

$(document).ready(function() {
	$(":file").filestyle({htmlIcon: "<i class=\"fas fa-file-image\"></i> ",text: "เลือกรูปภาพ"});

	$("#startsummery, #endsummery").datetimepicker({
		format: 'YYYY-MM-DD',
		ignoreReadonly: true,
	});
	
	$("form[id=summerydata]").submit(function(e){
		e.preventDefault();

		$.ajax({
			url : "/summerydata",
			type : "POST",
			data : $(this).serialize(),
			dataType : "json",
			success : function(s) {
				if(s.alert != "swalert"){
					$("#showdata").html(s.data.html);
				}else{
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
				}
			},
			error : function(e){
				Swal.fire({
					icon : "error",
					title : "เกิดข้อผิดพลาด",
					text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
				});
			}
		});
	});
});