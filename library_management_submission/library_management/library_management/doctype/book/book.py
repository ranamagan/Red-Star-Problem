import frappe
from frappe.model.document import Document


class Book(Document):
    """
    Book DocType Controller.
    Handles validation and available copies management.
    """

    def validate(self):
        """Run all validations."""
        self.validate_copies()
        self.validate_isbn()

    def validate_copies(self):
        """
        Ensure total_copies >= 1 and available_copies <= total_copies.
        """
        if self.total_copies < 1:
            frappe.throw("Total Copies must be at least 1.")

        # On new document, set available_copies = total_copies
        if self.is_new():
            self.available_copies = self.total_copies

        if self.available_copies < 0:
            frappe.throw("Available Copies cannot be negative.")

        if self.available_copies > self.total_copies:
            frappe.throw(
                "Available Copies cannot exceed Total Copies."
            )

        # Auto-update status based on available copies
        if self.available_copies == 0 and self.status == "Available":
            self.status = "Issued"
        elif self.available_copies > 0 and self.status == "Issued":
            self.status = "Available"

    def validate_isbn(self):
        """Validate ISBN length if provided (ISBN-10 or ISBN-13)."""
        if self.isbn:
            isbn_clean = self.isbn.replace("-", "").replace(" ", "")
            if len(isbn_clean) not in [10, 13]:
                frappe.throw(
                    f"ISBN '{self.isbn}' is invalid. "
                    "ISBN must be 10 or 13 digits long."
                )
