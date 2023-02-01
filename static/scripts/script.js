
// just simple min & max functions
function max(a, b) { return a > b ? a : b; }
function min(a, b) { return a < b ? a : b; }

// cookies
function setCookie(cookieName, cookieValue, expiredTime=1, unit="h") {
	const time = new Date();
	let factor = 1;
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
	let expires = "expires=" + time.toUTCString();
	document.cookie = cookieName + "=" + cookieValue + ";" + expires + ";path=/";
}
function getCookie(cookieName) {
	let name = cookieName + "=";
	let cookieArray = document.cookie.split(";");
	for (let i=0; i<cookieArray.length; i++) {
		let cookieChar = cookieArray[i];
		while (cookieChar.charAt(0) === " ") {
			cookieChar = cookieChar.substring(1);
		}
		if (cookieChar.indexOf(name) === 0) {
			return cookieChar.substring(name.length, cookieChar.length);
		}
	}
	return null;
}


// https://stackoverflow.com/questions/6877403/how-to-tell-if-a-video-element-is-currently-playing
Object.defineProperty(HTMLMediaElement.prototype, 'playing', {
	get: function(){
		return !!(this.currentTime > 0 && !this.paused && !this.ended && this.readyState > 2);
	}
})


// on page ready
$(document).ready(function(){
	// remove age restriction classes if age restriction disabled
	if (getCookie("age_restriction_unlocked") === "true") {
		$(".age-restricted").each(function(){
			$(this).removeClass("age-restricted");
			$(this).removeClass("not-allowed");
		});
	}

	// add click events to age restricted elements
	// query the configured pin and (if correct) disable the age restriction
	$(".age-restricted").click(function(){
		var pinInput = prompt("PIN eingeben, um die Altersbeschränkung aufzuheben:");
		var pinInputHash = CryptoJS.MD5(pinInput).toString();
		if (pinInputHash === window.ageRestriction_PinHash) {
			setCookie("age_restriction_unlocked", "true", window.ageRestriction_SessionDuration, "h");
			alert("Die Altersbeschränkung ist für " + window.ageRestriction_SessionDuration.toString() + " Stunden aufgehoben.");
			window.history.go(0);
		} else {
			alert("Falsche PIN.");
		}
	});

	// events for custom video controls
	$(".video-wrapper").each(function(){
		var jQ_video_wrapper = $(this);
		var video = jQ_video_wrapper.children("video").get(0);
		// left
		$(this).find(".controls .fullscreen").click(() => { video_fullscreen(jQ_video_wrapper, video); });
		// center
		$(this).find(".controls .backward").click(() => { video_backward(jQ_video_wrapper, video); });
		$(this).find(".controls .play-pause").click(() => { video_play_pause(jQ_video_wrapper, video); });
		$(this).find(".controls .forward").click(() => { video_forward(jQ_video_wrapper, video); });
		// right
		$(this).find(".controls .volume").click(() => { video_volume(jQ_video_wrapper, video); });
		$(this).find(".controls .subtitle").click(() => { video_subtitle(jQ_video_wrapper, video); });

		// update UI and progress bar
		video_update_UI(jQ_video_wrapper);
	});
});


// functions for custom video controls
function video_update_progress(jQ_video_wrapper) {
	var video = jQ_video_wrapper.children("video").get(0);
	var timeline = jQ_video_wrapper.find(".controls .timeline input[type='range']");
	var elapsed_time = jQ_video_wrapper.find(".controls .elapsed-time");
	var remaining_time = jQ_video_wrapper.find(".controls .remaining-time");
	// update video progress bar and timers
	timeline.attr("value", video.currentTime);
	timeline.attr("max", video.duration);
	elapsed_time.text(video.currentTime);
	remaining_time.text(video.duration - video.currentTime);
}
function video_update_UI(jQ_video_wrapper) {
	var video_wrapper = jQ_video_wrapper.get(0);
	var video = jQ_video_wrapper.children("video").get(0);
	// update video wrapper classes
	video.playing ? video_wrapper.classList.remove("paused") : video_wrapper.classList.add("pause");
	video.fullscreen ? video_wrapper.classList.add("fullscreen") : video_wrapper.classList.remove("fullscreen");
	video_update_progress(jQ_video_wrapper);
}

function video_fullscreen(jQ_video_wrapper, video) {
	video.fullscreen ? video.exitFullscreen() : video.requestFullscreen();
	video_update_UI(jQ_video_wrapper);
}
function video_backward(jQ_video_wrapper, video, seconds=10) {
	video.currentTime -= seconds;
	video_update_UI(jQ_video_wrapper);
}
function video_play_pause(jQ_video_wrapper, video) {
	video.playing ? video.pause() : video.play();
	video_update_UI(jQ_video_wrapper);
}
function video_forward(jQ_video_wrapper, video, seconds=10) {
	video.currentTime += seconds;
	video_update_UI(jQ_video_wrapper);
}
function video_volume(jQ_video_wrapper, video, seconds=10) {
	// 
	video_update_UI(jQ_video_wrapper);
}
function video_subtitle(jQ_video_wrapper, video, seconds=10) {
	// 
	video_update_UI(jQ_video_wrapper);
}


// show and play the video in full screen mode
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
