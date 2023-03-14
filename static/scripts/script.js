
// just simple min & max functions
function max(a, b) { return a > b ? a : b; }
function min(a, b) { return a < b ? a : b; }

// cookies
function setCookie(cookieName, cookieValue, expiredTime=1, unit="h") {
	const time = new Date();
	var factor = 1;
	switch (unit) {
		case "y":
			factor = 60 * 60 * 24 * 365.25
			break;
		case "d":
			factor = 60 * 60 * 24;
			break;
		case "m":
			factor = 60;
			break;
		case "s":
			factor = 1;
			break;
		case "h":
		default:
			factor = 60 * 60;
	}
	time.setTime(time.getTime() + (expiredTime * factor * 1000));
	document.cookie = `${cookieName}=${cookieValue};expires=${time.toUTCString()};path=/`;
}
function getCookie(cookieName) {
	var name = cookieName + "=";
	var cookieArray = document.cookie.split(";");
	for (var i=0; i<cookieArray.length; i++) {
		var cookieChar = cookieArray[i];
		while (cookieChar.charAt(0) === " ") cookieChar = cookieChar.substring(1);
		if (cookieChar.indexOf(name) === 0) return cookieChar.substring(name.length, cookieChar.length);
	}
	return null;
}


// convert seconds to time format of HH:MM:SS
function secondsToTime(seconds) {
	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	const remainingSeconds = Math.floor(seconds % 60);
	return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`;
}

// check if element is in viewport (by ChatGPT)
function isCompleteInViewport(element) {
	const bounding = element.getBoundingClientRect();
	const windowHeight = (window.innerHeight || document.documentElement.clientHeight);
	const windowWidth = (window.innerWidth || document.documentElement.clientWidth);
	return (
		bounding.top >= 0 &&
		bounding.left >= 0 &&
		bounding.bottom <= windowHeight &&
		bounding.right <= windowWidth
	);
};
function isPartiallyInViewport(element) {
	const bounding = element.getBoundingClientRect();
	const windowHeight = (window.innerHeight || document.documentElement.clientHeight);
	const windowWidth = (window.innerWidth || document.documentElement.clientWidth);
	return (
		bounding.top < windowHeight &&
		bounding.bottom >= 0 &&
		bounding.left < windowWidth &&
		bounding.right >= 0
	);
}


// search for query in array and add css classes to results
function searchResults(event, objectArray, inputElement, toArray, notResultClasses, minLenght=1) {
	var invalidChars = /[^a-z0-9\-]/gi;
	var query = inputElement.val().toLowerCase();
	var validQuery = query.replace(invalidChars, "");
	
	// remove previous added search classes
	objectArray.forEach((object) => {
		notResultClasses.forEach(function(resultClass) {
			document.getElementById(`movie-${object.movieID}`).classList.remove(resultClass);
		});
	});

	if (validQuery.length >= minLenght) {
		// search for query in array
		objectArray.filter((object)=>{
			objectArray = toArray(object).map((attribute)=>{
				return attribute.toLowerCase().replace(invalidChars, "");
			});
			
			var anyIsTrue = false;
			objectArray.forEach((attribute)=>{
				if (attribute.includes(validQuery)) {
					anyIsTrue = true;
					return;
				}
			});
			return !anyIsTrue;

		}).forEach((object)=>{
			// add search classes
			notResultClasses.forEach((resultClass)=>{
				document.getElementById(`movie-${object.movieID}`).classList.add(resultClass);
			});
		});
	}

	// save search query in url
	if (event.keyCode === 13 || validQuery.length % ((minLenght+1)*2) === 0) {
		window.history.pushState({},
			document.title,
			`${window.location.origin}${window.location.pathname}?query=${query.replace(/ +/g,"+")}`
		);
	}
}


// extend HTML Media Element by the new attribute "playing"
// https://stackoverflow.com/questions/6877403/how-to-tell-if-a-video-element-is-currently-playing
Object.defineProperty(HTMLMediaElement.prototype, "playing", {
	get: function(){
		return !!(this.currentTime > 0 && !this.paused && !this.ended && this.readyState > 2);
	}
})


// functions for to control the video playback with hotkeys 
// video actions
function video_fullscreen(video_wrapper) {
	var video = $(video_wrapper).children("video").get(0);
	video_wrapper = $(video_wrapper).get(0);
	//                                                                note: use default video fullscreen for mobile
	document.webkitIsFullScreen ? document.webkitExitFullscreen() : ( document.documentElement.clientWidth < 850 ? video.webkitRequestFullscreen() : video.webkitRequestFullscreen() );
}
function video_backward(video_wrapper, seconds=10) {
	var video = $(video_wrapper).children("video").get(0);
	video.currentTime -= seconds;
}
function video_play_pause(video_wrapper) {
	var video = $(video_wrapper).children("video").get(0);
	if (video.ended) video.load();
	video.playing ? video.pause() : video.play();
}
function video_forward(video_wrapper, seconds=10) {
	var video = $(video_wrapper).children("video").get(0);
	video.currentTime += seconds;
}
function video_volume(video_wrapper) {
	var video = $(video_wrapper).children("video").get(0);
	video.muted ? $(video).prop("muted", false) : $(video).prop("muted", true);
}

// play specific video in fullscreen
function playInFullscreen(video_wrapper, delay_ms=0) {
	setTimeout(()=>{
		video_fullscreen(video_wrapper);
		video_play_pause(video_wrapper);
	}, delay_ms);
}


// on page ready
$(document).ready(()=>{
	// remove age restriction classes if age restriction disabled
	if (getCookie("age_restriction_unlocked") === "true") {
		$(".age-restricted").each(()=>{
			$(this).removeClass("age-restricted");
			$(this).removeClass("not-allowed");
		});
	}

	// add click events to age restricted elements
	// query the configured pin and (if correct) disable the age restriction
	$(".age-restricted").click(()=>{
		var pinInput = prompt("PIN eingeben, um die Altersbeschränkung aufzuheben:");
		var pinInputHash = CryptoJS.MD5(pinInput).toString();
		if (pinInputHash === window.ageRestriction_PinHash) {
			setCookie("age_restriction_unlocked", "true", window.ageRestriction_SessionDuration, "h");
			alert(`Die Altersbeschränkung ist für ${window.ageRestriction_SessionDuration.toString()} Stunden aufgehoben.`);
			window.history.go(0);
		} else {
			alert("Falsche PIN.");
		}
	});

	// add events and hotkeys for custom video controls
	// init video controls and add UI updater
	$(".video-wrapper").each(function(index, value){
		var jQ_video_wrapper = $(this);
		var video = jQ_video_wrapper.children("video").get(0);
		var click_bindings = "click touch";

		// play video if clicked on video element
		// note: only if custom controls are applies
		$(video).bind(`${click_bindings}`, (evt)=>{
			if (document.documentElement.clientWidth >= 850) video_play_pause(jQ_video_wrapper);
		});

		// bind hotkeys to video controls
		// apply only to first video wrapper
		if (index === 0) {
			$(document).bind("keydown", (evt)=>{
				if (isPartiallyInViewport(video)) {
					switch (evt.originalEvent.key || evt.keyCode) {
						case 70:
						case "f":
							video_fullscreen(jQ_video_wrapper);
							break;
						case 37:
						case "ArrowLeft":
						case 74:
						case "j":
							video_backward(jQ_video_wrapper);
							break;
						// case 32:
						// case " ":
						case 75:
						case "k":
							video_play_pause(jQ_video_wrapper);
							break;
						case 39:
						case "ArrowRight":
						case 76:
						case "l":
							video_forward(jQ_video_wrapper);
							break;
						case 77:
						case "m":
							video_volume(jQ_video_wrapper);
							break;
					}
				}
			});
		}
	});

	// add hover and click events for user rating (on movie pages)
	$(".user.rating").each(function(){
		var user_rating_el = $(this);

		// mark selected stars
		user_rating_el.find(".icon[data-star-action='set']").on("mouseover", (evt)=>{
			var this_star_el = evt.target;
			var this_star_pos = parseInt($(this_star_el).attr("data-star-position"));

			for (var pos=1; pos<=this_star_pos; pos++) {
				var star = user_rating_el.find(`.icon[data-star-position='${pos}']`);
				star.attr("class", user_rating_el.attr("data-star-filled"));
			}
			for (var pos=this_star_pos+1; pos<=5; pos++) {
				var star = user_rating_el.find(`.icon[data-star-position='${pos}']`);
				star.attr("class", user_rating_el.attr("data-star-empty"));
			}
		});
		
		// reset selected stars to loaded state
		user_rating_el.on("mouseleave", (evt)=>{
			for (var pos=1; pos<=5; pos++) {
				var star = user_rating_el.find(`.icon[data-star-position='${pos}'][data-star-action='set']`);
				star.attr("class", star.attr("data-star-default"));
			}
		});

		// send selected stars to the api and if no error occurs, update the stars' default data attribute
		user_rating_el.find(".icon[data-star-action='set']").on("click touch", (evt)=>{
			var this_star_el = evt.target;
			var this_star_pos = parseInt($(this_star_el).attr("data-star-position"));
			var url = `${window.location.pathname}user-rating/set/${this_star_pos}`;
			
			$.ajax({
				url: url,
				error: ()=>{ alert("Failed to save user rating."); },
				success: ()=>{
					for (var pos=1; pos<=5; pos++) {
						var star = user_rating_el.find(`.icon[data-star-position='${pos}'][data-star-action='set']`);
						star.attr("data-star-default", star.attr("class"));
					}
				}
			});
		});

		// reset user rating (send 0 stars to the api) and if no error occurs, update the stars' default data attribute
		user_rating_el.find(".icon[data-star-action='reset']").on("click touch", (evt)=>{
			var url = `${window.location.pathname}user-rating/set/0`;
			
			$.ajax({
				url: url,
				error: ()=>{ alert("Failed to reset user rating."); },
				success: ()=>{
					for (var pos=1; pos<=5; pos++) {
						var star = user_rating_el.find(`.icon[data-star-position='${pos}'][data-star-action='set']`);
						star.attr("data-star-default", user_rating_el.attr("data-star-empty"));
						user_rating_el.trigger("mouseleave");
					}
				}
			});
		});
	});
});
