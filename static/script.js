$(document).ready(function(){
    $(".details").forEach(function(){
        this.css("width", $(".links ul")[0].width);
    });
});