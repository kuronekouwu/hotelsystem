$(document).ready(function(e){
	var data = getUrlVars();

	if(data.select_room) {
		var id = data.select_room;

		$.ajax({
			url : "/selectroomd/"+id,
			type : "POST",
			dataType : "json",
			cache : false,
			success : function(d) {
				if(d.alert == "swalert") {
					Swal.fire({
						icon : d.data.icon,
						title : d.data.title,
						text : d.data.description,
						timer : 4000
					}).then((result) => {
						if(result.value){
							location.href=d.data.redirect;
						}
					});
				}else{
					$("#showroom").html(d.data.html);
					$("#bookrooms").modal("show");
					$("#selectroomjs").attr("src","/static/vendor/app.selectroom.js");
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
	}
});

function getUrlVars()
{
	var vars = [], hash;
	var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
	for(var i = 0; i < hashes.length; i++)
	{
		hash = hashes[i].split('=');
		vars.push(hash[0]);
		vars[hash[0]] = hash[1];
	}
	return vars;
}