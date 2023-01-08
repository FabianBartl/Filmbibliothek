$(document).ready(function(){
    $(".title").click(function(){
		window.open(this.attr("data-path"), "_blank");
    });
});