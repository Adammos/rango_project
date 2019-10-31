$(document).ready(function() {
	$('#like_btn').click(function() {
		var category_id_var;
		category_id_var = $(this).attr('data_category');

		$.get('/rango/like_category/', {'category_id': category_id_var},
			function(data) {
				$('#like_count').html(data);
				$('#like_btn').hide();
			})
	});

	// Category search suggestions 
	$("#search-input").keyup(function() {
		var query;
		query = $(this).val();

		$.get('/rango/suggest/', {'suggestion': query},
			function(data) {
				$('#categories-listing').html(data);
			})
	});

	// Adding a new Page model object to the Category
	$('.rango-page-add').click(function() {
		var page_id = $(this).attr('data-page-id');
		var page_url = $(this).attr('data-page-url');
		var category_id = $(this).attr('data-category-id');
		var clickedButton = $(this);

		$.get('/rango/search_add_page/', 
			{'category_id': category_id,
			'page_id': page_id,
			'page_url': page_url},
			function(data) {
				$('#category-pages-list').html(data);
				clickedButton.hide();
			})
	});

});