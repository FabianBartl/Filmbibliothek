
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
	var expires = `expires=${time.toUTCString()}`;
	document.cookie = `${cookieName}=${cookieValue};${expires};path=/`;
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


// extend HTML Media Element by the new attribute "playing"
// https://stackoverflow.com/questions/6877403/how-to-tell-if-a-video-element-is-currently-playing
Object.defineProperty(HTMLMediaElement.prototype, "playing", {
	get: function(){
		return !!(this.currentTime > 0 && !this.paused && !this.ended && this.readyState > 2);
	}
})


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
	$(".video-wrapper").each(function(index){
		var jQ_video_wrapper = $(this);
		var video = jQ_video_wrapper.children("video").get(0);

		// play video if clicked on video it-self
		$(video).click(()=>{ video_play_pause(jQ_video_wrapper, video); });

		// left
		jQ_video_wrapper.find(".controls .fullscreen").click(()=>{ video_fullscreen(jQ_video_wrapper, video); });
		// center
		jQ_video_wrapper.find(".controls .backward").click(()=>{ video_backward(jQ_video_wrapper, video); });
		jQ_video_wrapper.find(".controls .play-pause").click(()=>{ video_play_pause(jQ_video_wrapper, video); });
		jQ_video_wrapper.find(".controls .forward").click(()=>{ video_forward(jQ_video_wrapper, video); });
		// right
		jQ_video_wrapper.find(".controls .volume").click(()=>{ video_volume(jQ_video_wrapper, video); });
		jQ_video_wrapper.find(".controls .subtitle").click(()=>{ video_subtitle(jQ_video_wrapper, video); });
		// progress 
		jQ_video_wrapper.find(".controls .timeline input[type='range']").change((evt)=>{ video_timeline(jQ_video_wrapper, video, evt.target); });

		// init video controls
		video.addEventListener("loadedmetadata", ()=>{
			video_update_UI(jQ_video_wrapper);
			$(jQ_video_wrapper).find(".controls .timeline input[type='range']").attr("max", Math.floor(video.duration));
		});
		// update progress continuously if video is playing
		video.addEventListener("playing", function listener_update_progress(evt) {
			video_update_progress(jQ_video_wrapper);
			setInterval(() => {
				if (!evt.target.paused) video_update_progress(jQ_video_wrapper);
			}, 500);
			video.removeEventListener("playing", listener_update_progress);
		});

		// bind hotkeys to video controls
		// apply only to first video wrapper
		if (index === 0) {
			$(document).bind("keydown", (evt)=>{
				var key = evt.originalEvent.key;
				console.log(key);
				switch (key) {
					case "f":
						video_fullscreen(jQ_video_wrapper, video);
						break;
					case "ArrowLeft":
					case "j":
						video_backward(jQ_video_wrapper, video);
						break;
					case " ":
					case "k":
						video_play_pause(jQ_video_wrapper, video);
						break;
					case "ArrowRight":
					case "l":
						video_forward(jQ_video_wrapper, video);
						break;
					case "m":
						video_volume(jQ_video_wrapper, video);
						break;
					case "c":
						video_subtitle(jQ_video_wrapper, video);
						break;
				}
			});
		}
	});
});


// functions for custom video controls
function video_update_progress(video_wrapper) {
	var jQ_video_wrapper = $(video_wrapper);
	var video = jQ_video_wrapper.children("video").get(0);
	var timeline = jQ_video_wrapper.find(".controls .timeline input[type='range']");
	var elapsed_time = jQ_video_wrapper.find(".controls .elapsed-time");
	var remaining_time = jQ_video_wrapper.find(".controls .remaining-time");
	// update video progress bar and timers
	timeline.attr("value", Math.floor(video.currentTime));
	elapsed_time.text(seconds_to_time(video.currentTime));
	remaining_time.text(seconds_to_time(video.duration - video.currentTime));
}
function video_update_UI(video_wrapper) {
	var video = $(video_wrapper).children("video").get(0);
	var video_wrapper = $(video_wrapper).get(0);
	// update video wrapper classes
	video.fullscreen ? video_wrapper.classList.add("fullscreen") : video_wrapper.classList.remove("fullscreen");
	video.playing ? video_wrapper.classList.remove("paused") : video_wrapper.classList.add("paused");
	video.muted ? video_wrapper.classList.add("muted") : video_wrapper.classList.remove("muted");
	// update video controls progress
	video_update_progress(video_wrapper);
}

function video_fullscreen(video_wrapper, video) {
	video_wrapper = $(video_wrapper).get(0);
	document.webkitIsFullScreen ? document.webkitExitFullscreen : video_wrapper.webkitRequestFullscreen();
	video_update_UI(video_wrapper);
}
function video_backward(video_wrapper, video, seconds=10) {
	video.currentTime -= seconds;
	video_update_UI(video_wrapper);
}
function video_play_pause(video_wrapper, video) {
	if (video.ended) video.load();
	video.playing ? video.pause() : video.play();
	video_update_UI(video_wrapper);
}
function video_forward(video_wrapper, video, seconds=10) {
	video.currentTime += seconds;
	video_update_UI(video_wrapper);
}
function video_volume(video_wrapper, video) {
	video.muted ? $(video).prop("muted", false) : $(video).prop("muted", true);
	video_update_UI(video_wrapper);
}
function video_subtitle(video_wrapper, video) {
	// TODO
	video_update_UI(video_wrapper);
}
function video_timeline(video_wrapper, video, timeline) {
	video.currentTime = parseInt(timeline.value);
	video_update_UI(video_wrapper);
}


// show and play the video in full screen mode
function playAsFullscreen(selector) {
	video = document.querySelector(selector);
	setTimeout(function(){
		video.requestFullscreen();
		video.play();
	}, 600);
}


// convert seconds to time format of HH:MM:SS
function seconds_to_time(seconds) {
	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	const remainingSeconds = Math.floor(seconds % 60);
	return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`;
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
		objectArray.filter((object) => {
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

		}).forEach((object) => {
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
