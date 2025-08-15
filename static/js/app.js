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

	// Copy to clipboard buttons
	document.querySelectorAll(".copy-btn").forEach((btn) => {
		btn.addEventListener("click", async (e) => {
			e.preventDefault();
			const target = btn.getAttribute("data-copy-target");
			if (!target) return;
			const el = document.querySelector(target);
			if (!el) return;
			const text = el.innerText || el.textContent || "";
			try {
				await navigator.clipboard.writeText(text);
				btn.textContent = "Copied!";
				setTimeout(() => (btn.textContent = "Copy"), 1500);
			} catch (err) {
				// Fallback
				const area = document.createElement("textarea");
				area.value = text;
				document.body.appendChild(area);
				area.select();
				document.execCommand("copy");
				document.body.removeChild(area);
				btn.textContent = "Copied!";
				setTimeout(() => (btn.textContent = "Copy"), 1500);
			}
		});
	});
});