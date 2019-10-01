$(document).ready(function() {
	$('#about-btn').click(
		function() {
			alert('You clicked the button using jQuery!');
			$(this).removeClass('btn-primary').addClass('btn-success');
		});

	$("#about-btn").click(function() {
		msgStr = $("#msg").html()
		msgStr = msgStr + " ooo, fancy!"
		$("#msg").html(msgStr)
	})
});
