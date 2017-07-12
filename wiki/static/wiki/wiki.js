$(function() {
	$('#show-source').click(function() {
		$('.page_content').slideUp();
		$('.page_source').slideDown();
	});
	$('#hide-source').click(function() {
		$('.page_source').slideUp();
		$('.page_content').slideDown();
	});
});
