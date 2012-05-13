var delay_get = (function(){
    var timer = 0;
    return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
    };
})();

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

var content_ready = false;
var post_url = "";
var history_url = false;

function desc_length(string) {
    desc_limit = $("#id_post_txt").val().length;
    $("#desc_limit").html(255 - desc_limit);
    
    if ((255 - desc_limit) < 0) {
        $("#label_post_txt").css({ 'color' : "#ff2222" });
    } else {
        $("#label_post_txt").css({ 'color' : "#ffffff" });
    }
}

function close_link_form() {
        $("#post_preview_form").slideUp('slow');
        $("#post_preview_loading").html("");
        $("#cancel_link").fadeOut("slow");
        $("#preview_ttl").html("");
        $("#preview_med").html("");
        $("#preview_txt").html("");  
        $("#id_post_url").val("");
}
    
function link_validator() {
    
    $("#id_post_url").val($.trim($("#id_post_url").val()));
    var content = $("#id_post_url").val();
    var urlRegex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    // Filtering URL from the content using regular expressions
    var url = content.match(urlRegex);
    
    if ((url && url.length > 0) && (content != post_url) && content != "e.g. http://www.youtube.com/watch?v=oHg5SJYRHA0") {
        post_url = url;
        
        $("#post_preview_form").slideDown('slow');
        $("#post_preview_loading").fadeIn("slow");
        $("#cancel_link").fadeIn("slow");
        $("#post_preview_loading").html("<img src='/static/link5/img/load.gif' >");
        $("#preview_ttl").html("");
        $("#preview_med").html("");
        $("#preview_txt").html("");
        
        embed_url = "/url/extracting/?url="+escape(url);
        
        $.getJSON(embed_url, {},function(data) {
            
            $("#post_preview").fadeIn('slow'); 
            $("#post_preview_loading").fadeOut("slow");
            
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
            } else if (data.type == "link" && data.images != "") {
                preview_med  = "";
                var x = 0;
                for (x in data.images){
                    preview_med = preview_med + "<img src='"+data.images[x].url+"' id='list_img_"+x+"' style='max-width:185px;";
                    if (x !=0) {
                        preview_med = preview_med + "display:none;"
                    }
                    preview_med = preview_med + "' />";
                }
                var list_current = 0;
                var list_lenght = x;
                preview_med = "<div id='list_image'>" + preview_med;
                if (list_lenght > 0)
                    preview_med = preview_med + "<p id='selection'><a id='left_a'></a><a id='right_a'></a></p>";
                preview_med = preview_med + "</div>";
                
                $("#preview_med").html(preview_med);
                $("#user_url").val($("#list_img_0").attr('src'));
                $("#list_image").click(function(e){
                    if (e.target.id == "right_a" || e.target.id == "list_img_"+list_current) {
                        $("#list_img_"+list_current).css({"position": "absolute"});
                        $("#list_img_"+list_current).hide();
                        if (list_current == list_lenght)
                            list_current = 0;
                        else
                            list_current++;
                        
                        $("#list_img_"+list_current).fadeIn();
                        $("#list_img_"+list_current).css({"position": "inherit"});
                        $("#user_url").val($("#list_img_"+list_current).attr('src'));
                    }                        
                });
                $("#left_a").click(function(){
                        $("#list_img_"+list_current).css({"position": "absolute"});
                        $("#list_img_"+list_current).hide();
                        if (list_current == 0)
                            list_current = list_lenght;
                        else
                            list_current--;
                        
                        $("#list_img_"+list_current).css({"position": "inherit"});
                        $("#list_img_"+list_current).fadeIn();
                        //$("#list_img_1").css({"position": "inherit"});
                        //$("#list_img_1").fadeIn();
                        $("#user_url").val($("#list_img_"+list_current).attr('src'));
                });                
            }
            
            $("#preview_txt").html(data.description);
            
            desc_length();
        });
    }
}

function close_link(){
    if (history_url) {
        window.history.back();
    }
    $("#link_overlay").fadeOut("slow");
    $("#full_view").fadeOut("slow");
    $("#full_view_content").html("");
    $("body").css({"overflow": "auto"});
}

function manual_submit(url) {
    
    if (content_ready) { 
        document.link_form.submit();    
    } 
}

function link_vote(url, link_id, tag_id) {
    link_id = link_id.split('_');
    $("#"+tag_id+link_id[1]).html("<span class='vote_loading'>Loading...</span>");
    $(".vote_message").html("");
    
    setTimeout(function() {$.ajax({
      url: url,
      success: function(data) {
        $("#"+tag_id+link_id[1]).html("");
        $("#"+tag_id+link_id[1]).fadeIn("slow");
        $("#"+tag_id+link_id[1]).html(data);
      }
    });}, 300);
}

function open_link(url_link_open) {
    $("#link_overlay").fadeIn("slow");
    $("#full_view_content").html("<p class='link_loading'><img src='/static/link5/img/load.gif' ></p>");
    $("#full_view").fadeIn("slow");
    $("body").css({"overflow": "hidden"});
    $("#full_view").css({"overflow": "auto"});
    
    var url = url_link_open;
    $.ajax({
      url: url,
      success: function(data) {
        $('#full_view_content').html(data);
      }
    });
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
      itemWidth: 220,
      container: $('#jquerywall_height')
    });
  };
}

$(document).ready(function() {

    url_value = window.location.pathname.split('/');
    
    $(".link_load").live("click",function(){
        history.pushState({path: window.location.pathname}, '', this.href);
        history_url = true;
        open_link($(this).attr('href')+"?ajax=true");
        return false;
    });
    
    $("#cancel_link").click(function(){
        close_link_form(); 
    }); 
    
    $("#id_post_url").focus(function() {
        if ($("#id_post_url").val() == "e.g. http://www.youtube.com/watch?v=oHg5SJYRHA0") {
            $("#id_post_url").val("");
        }   
    });
    $("#id_post_url").focusout(function() {
        if ($("#id_post_url").val() == "") {
            $("#id_post_url").val("e.g. http://www.youtube.com/watch?v=oHg5SJYRHA0");
        }
    });
    $("#id_post_url").keyup(function() {
        delay_get(function(){ link_validator() }, 500 );
    });
    
    $("#id_post_txt").keyup(function() { desc_length(); $("#preview_txt").html($("#id_post_txt").val()); });
    
    $("#id_post_ttl").keyup(function() { desc_length(); $("#preview_ttl").html($("#id_post_ttl").val()); });   
    
    $(".likeornot a").live("click",function(){
        var url = $(this).attr('href');
        var link_id = $(this).attr('id');
        link_vote(url, link_id, 'likeornot_');
        return false;
    });
    
    $("#full_view").click(function(e){
        if (e.target.id == "full_view") {close_link();}
    });
    
    $("#link_nav a").live("click",function(){
        var url = $(this).attr('href') + "?ajax=true";
        $("#link_nav").html('<img src="/static/link5/img/load-inf.gif" width="66" heigth="66" alt="loading..." border="0" />');
        
        $.ajax({
          url: url,
          success: function(data) {
            $("#jquerywall").append(data);
            $('.link').wookmark({
              offset: 10,
              itemWidth: 220,
              container: $('#jquerywall_height')
            });
          }
        });
        return false;
    });
    
    setTimeout(function() { $('#flash_messages').slideUp('slow'); }, 3000);
    
    // Init the layout presentation tool
    instance = new gbks.jQueryPlugin();
    instance.init();
    // If the link is not empty at page loading we have to display the preview
    if ($("#id_post_url").val() && $("#id_post_url").val() !="") link_validator();
    
	$(function () {
		$(window).scroll(function () {
			if ($(this).scrollTop() > 200) {$('#scroll_top').fadeIn();
			} else { $('#scroll_top').fadeOut(); }
			
			if ($(this).scrollTop() > 98) {$('#link_form_around').addClass("fixed");
            } else {$('#link_form_around').removeClass("fixed");}
            
			if ($(document).height() - $(window).height() - $(this).scrollTop() < 20) {
                $('#scroll_top').css({"margin-top": "-105px", "float": "right", "position": "relative", "margin-right": "-20px"});
            } else {$('#scroll_top').css({"margin-top": "auto", "float": "none", "position": "fixed", "margin-right": "auto"});}
		});

		// scroll body to 0px on click
		$('#scroll_top a').click(function () {
			$('body,html').animate({
				scrollTop: 0
			}, 600);
			return false;
		});
	});
});

$(document).keyup(function(e) {
    if (e.keyCode == 27) { 
        close_link(); 
    }   // esc
});
