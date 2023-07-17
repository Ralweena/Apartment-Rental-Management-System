jQuery(document).ready(function($){
  
    $('.live-search-list').each(function(){
    $(this).attr('data-search-term', $(this).text().toLowerCase());
    });
      
    $('.live-search-box').on('keyup', function(){
      
    var searchTerm = $(this).val().toLowerCase();
      
        $('.live-search-list').each(function(){
      
            if ($(this).filter('[data-search-term *= ' + searchTerm + ']').length > 0 || searchTerm.length < 1) {
                $(this).show();
            } else {
                $(this).hide();
            }
      
        });
      
    });
      
    });