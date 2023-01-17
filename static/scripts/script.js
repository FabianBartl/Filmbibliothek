
$(document).ready(function(){
    
});


function playAsFullscreen(selector) {
    video = document.querySelector(selector);
    video.scrollIntoView();
    setTimeout(function(){
        video.requestFullscreen();
        video.play();
    }, 500);
}
