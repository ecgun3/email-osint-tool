document.addEventListener("DOMContentLoaded", function () {
	const form = document.getElementById("osint-form");
	const jsonBtn = document.getElementById("view-json");
	if (form && jsonBtn) {
		jsonBtn.addEventListener("click", function (e) {
			e.preventDefault();
			const params = new URLSearchParams();
			const domain = document.getElementById("domain").value.trim();
			const email = document.getElementById("email").value.trim();
			const first = document.getElementById("first_name").value.trim();
			const last = document.getElementById("last_name").value.trim();
			if (domain) params.set("domain", domain);
			if (email) params.set("email", email);
			if (first) params.set("first_name", first);
			if (last) params.set("last_name", last);
			params.set("format", "json");
			const url = `/analyze?${params.toString()}`;
			window.open(url, "_blank");
		});
	}
});