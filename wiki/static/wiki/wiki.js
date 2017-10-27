$(function() {
	$('#show-source').click(function() {
		$('.article_content, .article_edit').slideUp();
		$('.article_source').slideDown();
	});
	$('#hide-source').click(function() {
		$('.article_source, .article_edit').slideUp();
		$('.article_content').slideDown();
	});
	$('#edit-page').click(function() {
		$('.article_content, .article_source').slideUp();
		$('.article_edit').slideDown();
	});

	$('#go-back').click(function() {
		window.history.back();
	});
});
