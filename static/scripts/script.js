
$(document).ready(function(){
    // justify lenghts to length of widest element 
    creditsName_maxWidth = 0;
    $('.credit-name').each(function(){
        creditsName_maxWidth = max($(this).width(), creditsName_maxWidth);
    });
    $('.credit-name').each(function(){
        $(this).width(creditsName_maxWidth + 8);
    });
});


// scroll-to video, make fullscreen, play it
function playAsFullscreen(selector) {
    video = document.querySelector(selector);
    video.scrollIntoView();
    setTimeout(function(){
        video.requestFullscreen();
        video.play();
    }, 500);
}


// search for query in array and add css classes to results
function searchResults(event, objectArray, inputElement, toArray, notResultClasses=["hidden"], minLenght=3) {
	var invalidChars = /[^a-z0-9\-]/gi;
	var query=inputElement.val().toLowerCase(), validQuery=query.replace(invalidChars, "");
	
    objectArray.forEach((object) => {
        notResultClasses.forEach(function(resultClass) {
            document.getElementById("movie-"+object.movieID).classList.remove(resultClass);
        });
    });

	if (validQuery.length >= minLenght) {
		objectArray.filter((object) => {
			objectArray = toArray(object).map((attribute) => {
				return attribute.toLowerCase().replace(invalidChars, "");
			});
			
			var anyIsTrue = false;
			objectArray.forEach((attribute) => {
				if (attribute.includes(validQuery)) {
					anyIsTrue = true;
					return;
				}
			});
			return !anyIsTrue;
		
		}).forEach((object) => {
            notResultClasses.forEach(function(resultClass) {
                document.getElementById("movie-"+object.movieID).classList.add(resultClass);
            });
        });
    }

    if (event.keyCode === 13 || validQuery.length % ((minLenght+1)*2) === 0) {
		window.history.pushState({},
			document.title,
			window.location.origin + window.location.pathname + "?query=" + query.replace(/ /g, "+")
		);
    }
}


// just simple min & max functions
function max(a, b) { return a > b ? a : b; }
function min(a, b) { return a < b ? a : b; }
