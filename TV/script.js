
$(document).ready(function() {
    var $tv = $('.de-lad1337-tv');
    
    $tv.on('click', '.Show>.info img.poster, .Show>.info img.banner', function(){
        var p = $(this).closest('.Show');
        p.toggleClass('active');
    });
    $tv.on('click', '.Season .progress', function(e){
        var multi = e.shiftKey;
        var s = $(this).closest('.Season');
        var p = $(this).closest('.Show');
        $(s).addClass('active');
        if(!multi){
            $('.label', p).removeClass('label-success');
            $('.Season', p).removeClass('active');
        }
        $('.label', s).addClass('label-success');
        $(s).addClass('active');
        var data = {};
        data['id'] = $(s).data('id');
        jQuery.get(webRoot+'/getChildrensPaint', data, function(res){
            if(!multi){
                $('.cur-season-container tbody', p).html(res);
            }else
                $('.cur-season-container tbody', p).append(res);
            initDownloadbars();
        });
    });

    $tv.on('click', 'th .simple-status-select a', function(){
        var table = $(this).closest('table');
        var status_id = $(this).data('id');
        $('input[type="checkbox"]', table).each(function(k, v){
            var t = $(this);
            if(!t.prop("checked"))
                return;
            var row = $(this).closest('tr');
            var element_id = row.data('id');
            var status_link = $('.status-select a',row).first();
            console.log(status_link);
            ajaxSetElementStatus(status_link, status_id, element_id, true)
        });
    });

    $tv.on('click', 'th .icon-check', function(){
        table = $(this).closest('table');
        $('input[type="checkbox"]', table).each(function(k, v){
            var t = $(this);
            t.prop("checked", !t.prop("checked"))
        });
    });

    $tv.on('dblclick', 'th .icon-check', function(){
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

    $tv.on('mouseenter', '.Episode td.title img', function(){
    	var t = $(this).parent();
    	//$(this).qtip('destroy', true);
    	$(this).qtip({ // Grab some elements to apply the tooltip to
    		content: {
    	        text: function(){
    	        	var img = $('img', t);
    	        	var overview = $('.overview', t).clone();
    	        	overview.prepend(img.clone().addClass('pull-left'));
    	        	return overview;
    	        },
    			title: function(){
    	        	return $('span', t).text()
    			}
    	    },
    	    style:{
    	    	classes: 'qtip-bootstrap de-lad1337-tv episode-tooltip'
    	    },
    	    show: {
    	        solo: true,
    	        ready: true
    	    },
    	    position: {
    	        my: 'bottom left',  // Position my top left...
    	        at: 'top center' // at the bottom right of...
    	    }
    	});
    });
    
});

function de_lad1337_tv_init(){
    init_progress_bar_resize($tv);
}

