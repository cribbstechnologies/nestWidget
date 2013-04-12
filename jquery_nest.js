(function($) {
    $.nest = function(container) {
        $.get('/python/nest.py', function(data) {
            container.html('<img src="nestEmpty.png"/>').append('<div id="currentStatus"></div>').append('<div id="currentSettings"></div>').append('<div id="awayStatus"></div>');
            var status = $.parseJSON(data);
            if (status.away) {
                $('#awayStatus').html("Away");
            } else {
                $('#awayStatus').html("Home");
            }
            var current = "" + status.current_temperature;
            current = current.substring(0, current.indexOf("."));
            $('#currentStatus').html(current).append("&#176;F");
            
            container.removeClass();
            if (status.mode == "HEAT") {
                container.addClass("heat");
            } else {
                container.addClass("cool");
            }
            $('#currentSettings').html(status.set_temp).append("&#176;F");
        });
    }
})(jQuery);