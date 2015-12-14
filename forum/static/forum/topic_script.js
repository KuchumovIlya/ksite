function get_url() {
    topic_id = $(".modification_div").attr("topic_id");
    url = "http://127.0.0.1:8000/forum/modification_date/" + topic_id;
    return url
}

last_modification_date = null;

$(document).ready(function() {
    $(".modification_div").hide();

    setInterval(function () {
        $.ajax({
            method: 'GET',
            url: get_url(),
            data: {  }
        })
        .done(function(data) {
            if (last_modification_date == null)
                last_modification_date = data;
            else if (last_modification_date != data)
               $(".modification_div").show();
        });
    }, 3000);
})

