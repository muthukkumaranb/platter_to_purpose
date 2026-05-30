import os

os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"
import django

django.setup()

from django.template.loader import get_template  # noqa: E402

fail_templates = [
    "accounts/signup.html",
    "dashboard/hotel_dashboard.html",
    "dashboard/orphanage_dashboard.html",
]
output = []

for name in fail_templates:
    try:
        t = get_template(name)
        output.append(f"OK: {name}")
    except Exception as e:
        output.append(f"FAIL: {name}")
        output.append(f"ERROR: {str(e)[:500]}")
        output.append("---")

with open("template_errors.txt", "w") as f:
    f.write("\n".join(output))

print("Done - check template_errors.txt")
