// Call the dataTables jQuery plugin
$(document).ready(function() {
	$('#dataTable').DataTable();
	
	$(document).on("click","#addgroup",function(e){
		e.preventDefault();
		$("#modal-data").modal("show");
	});
	
	$("#addgroupdata").submit(function(e){
		e.preventDefault();
		
		$.ajax({
			url : "/insert",
			type : "POST",
			data : $(this).serialize(),
			dataType : "json",
			cache : false,
			success : function(s){
				Swal.fire({
					icon : s.data.icon,
					title : s.data.title,
					text : s.data.description,
					timer : 4000
				}).then((result) =>{
					if(result.value){
						if(s.data.redirect != "") {
							$("#addgroupdata").trigger("reset");
							location.href=s.data.redirect;
						}
					}
				});
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
	
	$(document).on("click","#edit, #edit",function(e){
		e.preventDefault();
		
		$.ajax({
			url : "/info",
			type : "POST",
			data : {"uuid" : ""+$(this).data("uuid-group")+"","action" : "infogroup"},
			dataType : "json",
			cache : false,
			success : function(s){
				$("#dataeditroom").html(s.html);
				$("#modal-data-2").modal("show");
			},
			error : function(e){
				Swal.fire({
					icon : "error",
					title : "เกิดข้อผิดพลาด",
					text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
				});
			}
		})
	});
	
	$(document).on("click","#delete, #delete",function(e){
		name = $(this).data("name-group");
		uuid = $(this).data("uuid-group");
		
		Swal.fire({
			title: "คุณแน่ใจ?",
			text: "คุณจะลบกลุ่ม "+name+" ?",
			icon: "warning",
			showCancelButton: true,
			confirmButtonColor: "#3085d6",
			cancelButtonColor: "#d33",
			confirmButtonText: "ลบ",
			showLoaderOnConfirm: true,
			preConfirm : () => {
				return new Promise(function(resolve) {
					$.ajax({
						url : "/delete",
						method : "POST",
						data : {"uuid" : ""+uuid+"","action" : "deletegroup"},
						dataType : "json",
						cache : false,
						success : function(s){
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
						error : function(e){
							Swal.fire({
								icon : "error",
								title : "เกิดข้อผิดพลาด",
								text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
							});
						}
					});
				});
			},
			allowOutsideClick: false
		});
	});
});