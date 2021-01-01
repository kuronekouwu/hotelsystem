var start = "";
var end = "";
var price = $("input[id=price_preview]").val();

$("#startbook, #endbook").datetimepicker({
	format: 'YYYY-MM-DD',
	ignoreReadonly: true,
});

$("#startbook").on("hide.datetimepicker", function(e) {
	start = moment(e.date.format("YYYY-MM-DD"))

	if(start != "" && end != "") {
		diff = datediff(start,end);
		res = diff * price;
		if(diff > 0){
			$("#priceall").text(res+" บาท");
		}
	}
});

$("#endbook").on("hide.datetimepicker", function(e) {
	end =  moment(e.date.format("YYYY-MM-DD"));

	if(start != "" && end != "") {
		diff = datediff(start,end);
		res = diff * price;
		if(diff > 0){
			$("#priceall").text(res+" บาท");
		}
	}
});


$("form[id=bookroom]").submit(function(e){
	e.preventDefault();
	$(".bookroomd").attr("disabled",true);
	
	$.ajax({
		url : "/selectroomb",
		method : "POST",
		data : $(this).serialize(),
		dataType : "json",
		cache : false,
		success : function(s) {
			$(".bookroomd").attr("disabled",false);
			if(s.alert != "swalert") {
				$("#showroom").html(s.data.html);
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
		error : function(e) { 
			$(".bookroomd").attr("disabled",false);
			Swal.fire({
				icon : "error",
				title : "เกิดข้อผิดพลาด",
				text : "ระบบเกิดปัญหาขัดข้อง โปรดติดต่อที่ฝ่ายผู้ดูแลระบบ"
			});
		}
	});
});

function datediff(start,end) {
	diff =  new Date(end-start);
	return Math.round(diff/1000/60/60/24);
}