
$(document).ready(function() {
    de_lad1337_books_init();
    $(document).keydown(function(e){
        var curActiveBooks = $('.de-lad1337-books .book.active')
        if(curActiveBooks.length){
            var curActiveBook = $(curActiveBooks[0])
            if (e.keyCode == 37) {
                prevBookOfActive();
                return false;
             }
            if (e.keyCode == 39) {
                nextBookOfActive();
                return false;
             }
        }
    });
    
});

function getActiveBook(){
    var aBs = $('.de-lad1337-books .book.active')
    if(aBs.length)
        return aBs[0]
    else
        return aBs
}

function prevBookOfActive(){
    prevBookOf(getActiveBook())
}

function nextBookOfActive(){
    nextBookOf(getActiveBook())
}


function prevBookOf(activeBook){
    var prev = $(activeBook).prev('.book');
    if(prev.length){
        setBookActive(prev[0])
    }
}

function nextBookOf(activeBook){
    var next = $(activeBook).next('.book');
    if(next.length){
        setBookActive(next[0])
    }
}


function de_lad1337_books_init(){
    $('.de-lad1337-books .book .inner>img, .de-lad1337-books .book .spine').click(function(){
        var b = $(this).parents('.book')
        setBookActive(b);
    });
    $('.de-lad1337-books .book .inner>img').swipe( {
        //Generic swipe handler for all directions
        swipe:function(event, direction, distance, duration, fingerCount) {
            if(direction == 'left'){
                prevBookOfActive();
            }else if(direction == 'right'){
                nextBookOfActive();
            }
        },
        //Default is 75px, set to 0 for demo so any distance triggers swipe
         threshold: 50
      });

    $('.de-lad1337-books .book').not('.active').tooltip({container: 'body'})

}

function setBookActive(book){
    var t = $(book);
    var books = $('.de-lad1337-books .book');
    
    $('body').removeClass('no-tooltip');
    if(t.hasClass('active')){
        books.removeClass('active in-active');
        books.attr('style', '');
    }else{
        books.removeClass('active').addClass('in-active');
        
        books.attr('style', '');
        
        t.addClass('active').removeClass('in-active');
        //console.log(t.position());
        
        var parentWidth = t.parent().width();
        var width = 500;
        var leftOffset = t.position()['left']
        var offset = (parentWidth - (width + leftOffset + 70));
        if(offset < 0){
            t.css('left', offset+"px");
        }

        $('body').addClass('no-tooltip');
        //console.log($('.paper', t).width());
        
    }
}