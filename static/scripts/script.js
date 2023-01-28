
$(document).ready(function(){
	
});

// scroll-to video, make fullscreen, play it
function playAsFullscreen(selector) {
	video = document.querySelector(selector);
	setTimeout(function(){
		video.requestFullscreen();
		video.play();
	}, 600);
}


// search for query in array and add css classes to results
function searchResults(event, objectArray, inputElement, toArray, notResultClasses, minLenght=1) {
	var invalidChars = /[^a-z0-9\-]/gi;
	var query = inputElement.val().toLowerCase();
	var validQuery = query.replace(invalidChars, "");
	
	// remove previous added search classes
	objectArray.forEach((object) => {
		notResultClasses.forEach(function(resultClass) {
			document.getElementById("movie-"+object.movieID).classList.remove(resultClass);
		});
	});

	if (validQuery.length >= minLenght) {
		// search for query in array
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
			// add search classes
			notResultClasses.forEach(function(resultClass) {
				document.getElementById("movie-"+object.movieID).classList.add(resultClass);
			});
		});
	}

	// save search query in url
	if (event.keyCode === 13 || validQuery.length % ((minLenght+1)*2) === 0) {
		window.history.pushState({},
			document.title,
			window.location.origin+window.location.pathname+"?query="+query.replace(/ +/g,"+")
		);
	}
}


// just simple min & max functions
function max(a, b) { return a > b ? a : b; }
function min(a, b) { return a < b ? a : b; }
