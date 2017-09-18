$(function() {
	$('#show-source').click(function() {
		$('.article_content').slideUp();
		$('.article_source').slideDown();
	});
	$('#hide-source').click(function() {
		$('.article_source').slideUp();
		$('.article_content').slideDown();
	});
});
