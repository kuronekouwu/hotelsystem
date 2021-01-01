var start = "";
var end = "";
var price_preday = 0;

$(document).ready(function() {
	$('#dataTable').DataTable();
	$(":file").filestyle({htmlIcon: "<i class=\"fas fa-file-image\"></i> ",text: "เลือกรูปภาพ"});

	$("#startbook, #endbook").datetimepicker({
		format: 'YYYY-MM-DD',
		ignoreReadonly: true,
	});

	$("#startbook").on("hide.datetimepicker", function(e) {
		start = moment(e.date.format("YYYY-MM-DD"))
	
		if(start != "" && end != "") {
			diff = datediff(start,end);
			res = diff * price_preday;
			if(diff > 0){
				$("#price_all").val(res + " บาท");
			}
		}
	});
	
	$("#endbook").on("hide.datetimepicker", function(e) {
		end =  moment(e.date.format("YYYY-MM-DD"));
	
		if(start != "" && end != "") {
			diff = datediff(start,end);
			res = diff * price_preday;
			if(diff > 0){
				$("#price_all").val(res + " บาท");
			}
		}
	});
	
	$(document).on("click","#addbook",function(e){
		e.preventDefault();
		$.ajax({
			url : "/addbook",
			type : "GET",
			dataType : "json",
			cache : false,
			success : function(s) {
				if(s.alert != "swalert") {
					$("#roomlist").empty();
					$("#roomlist").html("<option value=\"\" data-price=\"0\" selected></option>")
					for (let datagroup = 0; datagroup < s.data.length; datagroup++) {
						$("#roomlist").append("<optgroup label=\""+s.data[datagroup].title+"\" id=\""+datagroup+"\">");
						for (let dataroom = 0; dataroom < s.data[datagroup].rooms.length; dataroom++) {
							$("optgroup[id=\""+datagroup+"\"]").append("<option value=\""+s.data[datagroup].rooms[dataroom].uuid+"\" data-price=\""+s.data[datagroup].rooms[dataroom].price+"\">"+s.data[datagroup].rooms[dataroom].name+"</option>");
						}
					}
					$("#modal-data").modal("show");
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

	/*$("select[id=roomlist]").change(function(){
		$("#roomprice").val($(this).find(':selected').attr("data-price"))
		 price_preday= $(this).find(':selected').attr("data-price");
	});*/

	$("input[id=roomprice").on("change paste keyup", function() {
		price_preday = $(this).val();
		if(start != "" && end != "") {
			diff = datediff(start,end);
			res = diff * price_preday;
			if(diff > 0){
				$("#price_all").val(res + " บาท");
			}
		}
	 });

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

	$(document).on("click","#info, #info",function(e){
		e.preventDefault();

		$.ajax({
			url : "/info",
			type : "POST",
			data : {"uuid" : ""+$(this).data("uuid-book")+"","action" : "infobook"},
			dataType : "json",
			cache : false,
			success : function(s){
				$("#infobookdata").html(s.html);
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
		id = $(this).data("id");
		uuid = $(this).data("uuid-book");

		Swal.fire({
			title: "คุณแน่ใจ?",
			text: "คุณต้องการที่จะลบการจองห้องพัก ID  "+id+" ?",
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
						data : {"uuid" : ""+uuid+"","action" : "deletebook"},
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