// Call the dataTables jQuery plugin
$(document).ready(function() {
	$('#dataTable').DataTable();
	
	$(document).on("click","#dataimage, #dataimage",function(e){
		e.preventDefault();
		$("img[id=data]").attr("src",$(this).data("image-path"));
		$("#modal-data").modal("show");
	});

	$(document).on("click","#confrim, #confrim",function(e){
		status = $(this).data("status");
		uuid = $(this).data("uuid-book");
		
		Swal.fire({
			title: "คุณแน่ใจ?",
			text: "คุณจะยืนยันการชำระเงิน?",
			icon: "warning",
			showCancelButton: true,
			confirmButtonColor: "#3085d6",
			cancelButtonColor: "#d33",
			confirmButtonText: "ยืนยัน",
			showLoaderOnConfirm: true,
			preConfirm : () => {
				return new Promise(function(resolve) {
					$.ajax({
						url : "/confrim",
						method : "POST",
						data : {"uuid" : ""+uuid+"","action" : "confrim", "status" : ""+status+""},
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