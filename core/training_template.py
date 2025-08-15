from typing import Any, Dict, Optional

from utils.validators import sanitize_name


def _full_name(first_name: Optional[str], last_name: Optional[str]) -> str:
	first = sanitize_name(first_name)
	last = sanitize_name(last_name)
	if first and last:
		return f"{first.title()} {last.title()}"
	return (first or last).title() if (first or last) else ""


def generate_training_email_template(
	first_name: Optional[str],
	last_name: Optional[str],
	domain: Optional[str],
	provider: Optional[str],
	builtwith_summary: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
	"""
	Produce a neutral, training-only email template. Does NOT impersonate third-party brands.
	- Uses caller's domain for From address
	- Personalizes greeting if names provided
	- Provides both text and HTML bodies with placeholders
	"""
	from_address_domain = domain or "example.com"
	display_from = f"Security Awareness <security@{from_address_domain}>"
	to_example = None
	if domain:
		if first_name or last_name:
			first = sanitize_name(first_name) or "firstname"
			last = sanitize_name(last_name) or "lastname"
			to_example = f"{first}.{last}@{domain}"
		else:
			to_example = f"firstname.lastname@{domain}"

	recipient_name = _full_name(first_name, last_name)
	greeting = f"Hi {recipient_name}," if recipient_name else "Hello," 

	subject = "Action required: Verify your contact info by Friday"
	preheader = "This is part of our routine security awareness program."

	# Very light-touch context note for the operator, based on provider or builtwith
	context_note = None
	if provider:
		context_note = f"Detected mail provider: {provider}."
	elif builtwith_summary:
		context_note = "Technology context available from BuiltWith."

	text_lines = [
		greeting,
		"\nWe are running a scheduled security awareness exercise. Please take a moment to confirm your preferred contact method and acknowledge the policy update.",
		"\nOpen the training portal (internal): https://www.google.com",
		"\nThis simulation is for internal training only. If you did not expect this message, report it to the security team.",
		"\nThanks,",
		"Security Awareness Team",
		f"{from_address_domain}",
	]
	body_text = "\n".join(text_lines)

	body_html = (
		f"<p>{greeting}</p>"
		"<p>We are running a scheduled security awareness exercise. Please take a moment to confirm your preferred contact method and acknowledge the policy update.</p>"
		"<p>Open the training portal (internal): <a href=\"https://www.google.com\" target=\"_blank\" rel=\"noopener noreferrer\">Google</a></p>"
		"<p style=\"font-size:12px;color:#999\">This simulation is for internal training only. If you did not expect this message, report it to the security team.</p>"
		f"<p>Thanks,<br/>Security Awareness Team<br/>{from_address_domain}</p>"
		
	)

	return {
		"from": display_from,
		"to_example": to_example,
		"subject": subject,
		"preheader": preheader,
		"body_text": body_text,
		"body_html": body_html,
		"notes": {
			"context": context_note,
			"placeholders": {
				"training_link": "Use an authorized training URL (e.g., your LMS)",
			},
			"compliance": "Use only for authorized security awareness simulations. Do not impersonate third-party brands.",
		},
	}