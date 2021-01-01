// Call the dataTables jQuery plugin
$(document).ready(function() {
		$('#dataTable').DataTable();
		$(":file").filestyle({htmlIcon: "<i class=\"fas fa-file-image\"></i> ",text: "เลือกรูปภาพ"});

		$(document).on("click","#addroom",function(e){
			e.preventDefault();
			$("#modal-data").modal("show");
		});

		$(document).on("click","#addgroup",function(e){
			e.preventDefault();
			$("#modal-data-2").modal("show");
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
						if(s.alert != "swalert") {
							$("#modal-data-2").modal("hide");
							$("#groupid").html(s.data.html);
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
				})
		});

		$("#addgroomdata").submit(function(e){
			e.preventDefault();

			console.log($(this)[0]);
			$.ajax({
				url : "/insert",
				type : "POST",
				data : new FormData($(this)[0]),
				dataType : "json",
				cache : false,
				contentType: false,
				processData: false,
				ontentType: false,
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
			})
	});

	$(document).on("click","#edit, #edit",function(e){
		e.preventDefault();

		$.ajax({
			url : "/info",
			type : "POST",
			data : {"uuid" : ""+$(this).data("uuid-room")+"","action" : "inforoom"},
			dataType : "json",
			cache : false,
			success : function(s){
				$("#dataeditroom").html(s.html);
				$("#modal-data-3").modal("show");
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
		name = $(this).data("name-room");
		uuid = $(this).data("uuid-room");

		Swal.fire({
			title: "คุณแน่ใจ?",
			text: "คุณจะลบห้องพัก "+name+" ?",
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
						data : {"uuid" : ""+uuid+"","action" : "deleteroom"},
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