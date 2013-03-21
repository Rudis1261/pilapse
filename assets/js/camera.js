// Lets make it easy to change the filename
var myScript = "index.html";

// When the key is pressed, set it in the DB by running the AJAX
$(".action").click(function(event) {
        event.preventDefault();        
        var getAction = $(this).attr('data');
	
	
	if (getAction == 'take_photo') {
		var getTv = $('#tv').val();
		var getFt = $('#ft').val();
		$.get(myScript, { action: getAction, ft: getFt, tv: getTv }, function(data){
			console.log(data);
		});
	}
	
	
	if (getAction == 'focus') {
		var getFt = $('#ft').val();
		$.get(myScript, { action: getAction, ft: getFt }, function(data){
			console.log(data);
		});
	}
	
});
