
$(document).ready(function(){
    creditsName_maxWidth = 0;
    $('.credit-name').each(function(){
        creditsName_maxWidth = max($(this).width(), creditsName_maxWidth);
    });
    $('.credit-name').each(function(){
        $(this).width(creditsName_maxWidth + 8);
    });
});


function playAsFullscreen(selector) {
    video = document.querySelector(selector);
    video.scrollIntoView();
    setTimeout(function(){
        video.requestFullscreen();
        video.play();
    }, 500);
}


function max(a, b) { return a > b ? a : b; }
function min(a, b) { return a < b ? a : b; }
