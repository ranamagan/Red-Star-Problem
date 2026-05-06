import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class LibraryMember(Document):
    """
    Library Member DocType Controller.
    Handles validation and auto-population of member data.
    """

    def before_save(self):
        """Auto-populate full_name before saving."""
        self.full_name = f"{self.first_name} {self.last_name}".strip()

    def validate(self):
        """Run all validation checks."""
        self.validate_membership_dates()
        self.validate_email()

    def validate_membership_dates(self):
        """
        Ensure membership_expiry is after membership_date.
        Raises a validation error if not.
        """
        if self.membership_expiry and self.membership_date:
            if getdate(self.membership_expiry) < getdate(self.membership_date):
                frappe.throw(
                    "Membership Expiry Date cannot be before Membership Date."
                )

        # Auto-expire membership if expiry date has passed
        if self.membership_expiry and self.membership_status == "Active":
            if getdate(self.membership_expiry) < getdate(today()):
                self.membership_status = "Expired"
                frappe.msgprint(
                    "Membership status has been automatically set to 'Expired' "
                    "because the expiry date has passed.",
                    alert=True,
                )

    def validate_email(self):
        """Basic email format validation."""
        if self.email_address and "@" not in self.email_address:
            frappe.throw(
                f"'{self.email_address}' is not a valid email address."
            )
