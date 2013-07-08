$(document).ready(function() {
	$("form.qr").submit(function(event) {
		$(".notice").addClass("hidden");
		var qr = $("input#qr").val();
		/* Only allow proper QR codes to be submitted. Proper codes are:
		 * 1. 6 consecutive alphanumeric characters
		 * 2. a URL ending with a slash followed by 6 consecutive alphanumeric characters (assumed to be the look-up URL)
		 * This will of course be re-checked in the backend.
		 */
		if (! /^(?:(?:http(?:s)?\:\/\/?)?(?:[a-z0-9_&\.-]+\/)+)?[a-z0-9]{6}$/i.test(qr)) {
			$("tr.error#qr_invalid").removeClass("hidden");
			event.preventDefault();
		} else {
			$("tr.notice#qr_associating").removeClass("hidden");
		}
	});
});
