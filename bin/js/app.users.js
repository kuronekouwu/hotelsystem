var start = "";
var end = "";
var price_preday = 0;

$(document).ready(function() {
	$('#dataTable').DataTable();

	$("form[id=addbookdata]").submit(function(e){
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
					if(s.data.redirect != "") {
						$("#addbookdata").trigger("reset");
						location.href=s.data.redirect;
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
		data : {"uuid" : ""+$(this).data("uuid-user")+"","action" : "infousers"},
		dataType : "json",
		cache : false,
		success : function(s){
			$("#infouserdata").html(s.html);
			$("#modal-data").modal("show");
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
	name = $(this).data("name-user");
	uuid = $(this).data("uuid-user");

	Swal.fire({
		title: "คุณแน่ใจ?",
		text: "คุณจะต้องการลบผู้ใช้งาน "+name+" ?",
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
					data : {"uuid" : ""+uuid+"","action" : "deleteuser"},
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

function datediff(start,end) {
	diff =  new Date(end-start);
	return Math.round(diff/1000/60/60/24);
}