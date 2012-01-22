var delay_get = (function(){
    var timer = 0;
    return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
    };
})();

var content_ready = false;
var post_url = "";

function desc_length(string) {
    desc_limit = $("#id_post_txt").val().length;
    $("#desc_limit").html(255 - desc_limit);
    
    if ((255 - desc_limit) < 0) {
        $("#label_post_txt").css({ 'color' : "#ff2222" });
    } else {
        $("#label_post_txt").css({ 'color' : "#ffffff" });
    }
}
    
function link_validator() {
    $("#id_post_url").val($.trim($("#id_post_url").val()));
    var content = $("#id_post_url").val();
    
    var urlRegex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    // Filtering URL from the content using regular expressions
    var url = content.match(urlRegex);

    if((url && url.length > 0) && (content != post_url)) {
        post_url = url;
        $("#post_preview_form").slideDown('slow');
        $("#post_preview_loading").html("<img src='/static/link5/img/load-blue.gif' width='48' height='48'>");
        
        embed_url = "/extracting/?url="+url;
        
        $.getJSON(embed_url, {format: "json"},function(data) {
            
            $("#post_preview").fadeIn('slow'); $("#post_preview_loading").html("");
            
            content_ready = true;
        
            $("#id_post_ttl").val(data.title);
            $("#id_post_txt").val(data.description);
            
            $("#preview_ttl").html(data.title);
            
            // types: video, photo, rich, link
            if (data.type == "photo") {
                $("#preview_med").html("<img src='"+data.url+"' style='max-width:185px;' />");
            } else if (data.type == "video") {
                $("#preview_med").html("<img src='"+data.thumbnail_url+"' width='185' /><img src='/static/link5/img/play.png' border='0' width='20' height='18' class='link_play' />");
            } else if (data.type == "error") {
                $("#preview_med").html("<span style='color: red; font-weight: bold; font-size: 13px;'>Error to get the link content</span>");
            }
            
            $("#preview_txt").html(data.description);
            
            desc_length();
        });
    }
}

function close_link(){
    $("#link_overlay").fadeOut("slow");
    $("#full_view").fadeOut("slow");
    $("#full_view").css({"overflow": "hidden"});
    $("body").css({"overflow": "auto"});
}

function manual_submit() {
    if (content_ready) { 
        document.link_form.submit();    
    } 
}

var instance = null;
var gbks = gbks || {};

gbks.jQueryPlugin = function() { 
  
  this.init = function() {
    $(window).resize($.proxy(this.resize, this));
    this.resize();
  };
  
  this.resize = function() {
    $('.link').wookmark({
      offset: 10,
      itemWidth: 210,
      container: $('#jquerywall_height')
    });
  };
}

$(document).ready(function() {
    
    $("#id_post_url").keyup(function() {
        delay_get(function(){ link_validator() }, 500 );
    });
    
    $("#id_post_txt").keyup(function() { desc_length(); $("#preview_txt").html($("#id_post_txt").val()); });
    
    $("#id_post_ttl").keyup(function() { desc_length(); $("#preview_ttl").html($("#id_post_ttl").val()); });   
        
    $(".link_load").click(function(){
       
        $("#link_overlay").fadeIn("slow");
        $("#full_view").fadeIn("slow");
        $("#full_view_content").focus();
        $("body").css({"overflow": "hidden"});
        $("#full_view").css({"overflow": "auto"});
        
        var url = $(this).attr('href')
        
        $.ajax({
          url: url,
          success: function(data) {
            $('#full_view_content').html(data);
          }
        });
        return false;
    });
    
    $(".likeornot a").click(function(){
        var url = $(this).attr('href');
        var link_id = $(this).attr('id');
        link_id = link_id.split('_');
        $("#likeornot_"+link_id[1]).html("<span class='vote_loading'>Loading...</span>");
        
        setTimeout(function() {$.ajax({
          url: url,
          success: function(data) {
            $("#likeornot_"+link_id[1]).fadeIn("slow");
            $("#likeornot_"+link_id[1]).html(data);
          }
        });}, 300);
        return false;
    });
    
    $("#full_view").click(function(e){
        if (e.target.id == "full_view") {close_link();}
    });
    
    setTimeout(function() { $('#flash_messages').slideUp('slow'); }, 3000);
    
    // Init the layout presentation tool
    instance = new gbks.jQueryPlugin();
    instance.init();
    // If the link is not empty at page loading we have to display the preview
    if ($("#id_post_url").val() && $("#id_post_url").val() !="") link_validator();
});

$(document).keyup(function(e) {
    if (e.keyCode == 27) { 
        close_link(); 
    }   // esc
});
