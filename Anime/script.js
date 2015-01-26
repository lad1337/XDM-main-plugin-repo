
$(document).ready(function() {
    
    $('.de-lad1337-anime').on('click', '.Show>.info .poster', function(){
        var p = $(this).closest('.Show');
        p.toggleClass('active')
        if(!p.hasClass("active"))
            return;
        data = {}
        data['id'] = $(p).data('id')
        if($('.episodes-container tbody', p).html())
            return;

        var table = $('.episodes-container table', p);
        table.addClass("striped animate loading");
        jQuery.get( webRoot+'/getChildrensPaint', data, function(res){
            table.removeClass("striped animate loading").addClass("done");
            $('.episodes-container tbody', p).html(res);
            table.dataTable( {
                "bPaginate": true,
                "sPaginationType": "bootstrap",
                "bDestroy": true,
                "sDom": "<'row'<'span8'l><'span8'f>r>t<'pull-right'p>",
                "bLengthChange": false,
                "iDisplayLength": uranime_page_size,
                "bFilter": false,
                "bSort": false,
                "bInfo": false,
                "bAutoWidth": false,
                "fnDrawCallback": function () {
                    if(this.fnPagingInfo().iTotalPages == 1){
                        $('.episodes-container .dataTables_paginate', p).hide();
                    }
                }
            });
        });
    });

    $('.de-lad1337-anime').on('click', 'th .simple-status-select a', function(){
        var table = $(this).closest('table')
        var status_id = $(this).data('id')
        $('input[type="checkbox"]', table).each(function(k, v){
            var t = $(this)
            if(!t.prop("checked"))
                return
            var row = $(this).closest('tr')
            var element_id = row.data('id')
            var status_link = $('.status-select a',row).first()
            console.log(status_link)
            ajaxSetElementStatus(status_link, status_id, element_id, true)
        });
    });


    $('.de-lad1337-anime').on('click', '.switch', function(){
        var show = $(this).closest('.Show');
        var container = $(".episodes-container", show).toggleClass("flipped");
        console.log($(this));
        if(container.hasClass("flipped")){
            $(this).text("Episodes");
        }else{
            $(this).text("Info");
        }
    });
    
    $('.de-lad1337-anime').on('click', 'th .icon-check', function(){
        table = $(this).closest('table')
        $('input[type="checkbox"]', table).each(function(k, v){
            var t = $(this)
            t.prop("checked", !t.prop("checked"))
        });
    });

    $('.de-lad1337-anime').on('dblclick', 'th .icon-check', function(){
        table = $(this).closest('table');
        var all = 0;
        var checked = 0;
        
        var cbs = $('input[type="checkbox"]', table);
        
        cbs.each(function(k, v){
            all++;
            if($(this).prop("checked"))
                checked++;
        });
        cbs.prop("checked", checked/all > 0.5)
    });

    $('.de-lad1337-anime').on('mouseenter', '.Episode td.title img', function(){
        var t = $(this).parent();
        $(this).qtip('destroy', true);
        $(this).qtip({ // Grab some elements to apply the tooltip to
            content: {
                text: function(){
                    img = $('img', t)
                    overview = $('.overview', t).clone()
                    overview.prepend(img.clone().addClass('pull-left'))
                    return overview;
                },
                title: function(){
                    return $('span', t).text()
                }
            },
            style:{
                classes: 'qtip-bootstrap de-lad1337-anime episode-tooltip'
            },
            show: {
                solo: true,
                ready: true,
                event: 'click'
            },
            position: {
                viewport: $(window),
                my: 'bottom left',  // Position my top left...
                at: 'top center', // at the bottom right of...
            }
        })
    });
});

function de_uranime_anime_init(){
    init_progress_bar_resize($('.de-lad1337-anime'));
}

/* API method to get paging information */
$.fn.dataTableExt.oApi.fnPagingInfo = function ( oSettings )
{
    return {
        "iStart":         oSettings._iDisplayStart,
        "iEnd":           oSettings.fnDisplayEnd(),
        "iLength":        oSettings._iDisplayLength,
        "iTotal":         oSettings.fnRecordsTotal(),
        "iFilteredTotal": oSettings.fnRecordsDisplay(),
        "iPage":          oSettings._iDisplayLength === -1 ?
            0 : Math.ceil( oSettings._iDisplayStart / oSettings._iDisplayLength ),
        "iTotalPages":    oSettings._iDisplayLength === -1 ?
            0 : Math.ceil( oSettings.fnRecordsDisplay() / oSettings._iDisplayLength )
    };
}
 
/* Bootstrap style pagination control */
$.extend( $.fn.dataTableExt.oPagination, {
    "bootstrap": {
        "fnInit": function( oSettings, nPaging, fnDraw ) {
            var oLang = oSettings.oLanguage.oPaginate;
            var fnClickHandler = function ( e ) {
                e.preventDefault();
                if ( oSettings.oApi._fnPageChange(oSettings, e.data.action) ) {
                    fnDraw( oSettings );
                }
            };
 
            $(nPaging).addClass('pagination').append(
                '<ul>'+
                    '<li class="prev disabled"><a href="#">&larr;</a></li>'+
                    '<li class="next disabled"><a href="#"> &rarr; </a></li>'+
                '</ul>'
            );
            var els = $('a', nPaging);
            $(els[0]).bind( 'click.DT', { action: "previous" }, fnClickHandler );
            $(els[1]).bind( 'click.DT', { action: "next" }, fnClickHandler );
        },
 
        "fnUpdate": function ( oSettings, fnDraw ) {
            var iListLength = 5;
            var oPaging = oSettings.oInstance.fnPagingInfo();
            var an = oSettings.aanFeatures.p;
            var i, j, sClass, iStart, iEnd, iHalf=Math.floor(iListLength/2);
 
            if ( oPaging.iTotalPages < iListLength) {
                iStart = 1;
                iEnd = oPaging.iTotalPages;
            }
            else if ( oPaging.iPage <= iHalf ) {
                iStart = 1;
                iEnd = iListLength;
            } else if ( oPaging.iPage >= (oPaging.iTotalPages-iHalf) ) {
                iStart = oPaging.iTotalPages - iListLength + 1;
                iEnd = oPaging.iTotalPages;
            } else {
                iStart = oPaging.iPage - iHalf + 1;
                iEnd = iStart + iListLength - 1;
            }
 
            for ( i=0, iLen=an.length ; i<iLen ; i++ ) {
                // Remove the middle elements
                $('li:gt(0)', an[i]).filter(':not(:last)').remove();
 
                // Add the new list items and their event handlers
                for ( j=iStart ; j<=iEnd ; j++ ) {
                    sClass = (j==oPaging.iPage+1) ? 'class="active"' : '';
                    $('<li '+sClass+'><a href="#">'+j+'</a></li>')
                        .insertBefore( $('li:last', an[i])[0] )
                        .bind('click', function (e) {
                            e.preventDefault();
                            oSettings._iDisplayStart = (parseInt($('a', this).text(),10)-1) * oPaging.iLength;
                            fnDraw( oSettings );
                        } );
                }
 
                // Add / remove disabled classes from the static elements
                if ( oPaging.iPage === 0 ) {
                    $('li:first', an[i]).addClass('disabled');
                } else {
                    $('li:first', an[i]).removeClass('disabled');
                }
 
                if ( oPaging.iPage === oPaging.iTotalPages-1 || oPaging.iTotalPages === 0 ) {
                    $('li:last', an[i]).addClass('disabled');
                } else {
                    $('li:last', an[i]).removeClass('disabled');
                }
            }
        }
    }
} );


$.fn.dataTableExt.oApi.fnPagingInfo = function ( oSettings )
{
  return {
    "iStart":         oSettings._iDisplayStart,
    "iEnd":           oSettings.fnDisplayEnd(),
    "iLength":        oSettings._iDisplayLength,
    "iTotal":         oSettings.fnRecordsTotal(),
    "iFilteredTotal": oSettings.fnRecordsDisplay(),
    "iPage":          Math.ceil( oSettings._iDisplayStart / oSettings._iDisplayLength ),
    "iTotalPages":    Math.ceil( oSettings.fnRecordsDisplay() / oSettings._iDisplayLength )
  };
}
