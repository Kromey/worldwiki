$(function() {
	$('#show-source').click(function() {
		$('.article_content').slideUp();
		$('.article_source').slideDown();
	});
	$('#hide-source').click(function() {
		$('.article_source').slideUp();
		$('.article_content').slideDown();
	});

	$('#go-back').click(function() {
		window.history.back();
	});

	$('textarea[data-provide=markdown]').markdown({
		onPreview: function(e, previewContainer) {
			$.post("/w/special:preview", $('#article-form').serialize())
			.done(function(result) {
				previewContainer.html(result);
			})
			.fail(function() {
				previewContainer.text('Oops! Something went wrong; preview is not available at the moment. Sorry. :-(');
			});

			return "Formatting...";
		}
	});
});
