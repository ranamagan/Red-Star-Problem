import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_days


class BookTransaction(Document):
    """
    Book Transaction DocType Controller.

    Handles the core library logic:
    - Issue: checks member is active, book is available, updates available_copies
    - Return: validates the transaction, updates available_copies back
    """

    def validate(self):
        """Run all validations before saving."""
        self.validate_member()
        self.validate_book()
        self.validate_dates()

        if self.transaction_type == "Issue":
            self.validate_issue()
        elif self.transaction_type == "Return":
            self.validate_return()

    def validate_member(self):
        """Ensure the member's membership is Active."""
        member = frappe.get_doc("Library Member", self.library_member)
        if member.membership_status != "Active":
            frappe.throw(
                f"Member '{member.full_name}' has a '{member.membership_status}' membership. "
                "Only Active members can borrow books."
            )

    def validate_book(self):
        """Ensure the book exists and is not Lost/Damaged."""
        book = frappe.get_doc("Book", self.book)
        if book.status in ["Lost", "Damaged"]:
            frappe.throw(
                f"Book '{book.title}' is marked as '{book.status}' "
                "and cannot be issued."
            )

    def validate_dates(self):
        """Ensure transaction_date is not in the future."""
        if getdate(self.transaction_date) > getdate(today()):
            frappe.throw("Transaction Date cannot be in the future.")

        if self.due_date and getdate(self.due_date) < getdate(self.transaction_date):
            frappe.throw("Due Date cannot be before Transaction Date.")

    def validate_issue(self):
        """
        For an Issue transaction:
        - Ensure the book has available copies
        - Ensure the member doesn't already have this book issued
        - Auto-set due_date to 14 days from transaction_date
        """
        book = frappe.get_doc("Book", self.book)

        if book.available_copies < 1:
            frappe.throw(
                f"No copies of '{book.title}' are currently available."
            )

        # Check if member already has this book issued
        existing = frappe.db.exists(
            "Book Transaction",
            {
                "library_member": self.library_member,
                "book": self.book,
                "transaction_type": "Issue",
                "status": "Open",
                "name": ("!=", self.name),
            },
        )
        if existing:
            frappe.throw(
                f"Member already has an open issue for book '{book.title}'. "
                "Please return it before issuing again."
            )

        # Auto-set due date if not set
        if not self.due_date:
            self.due_date = add_days(self.transaction_date, 14)

        self.status = "Open"

    def validate_return(self):
        """
        For a Return transaction:
        - Ensure there is an open Issue transaction for this member + book
        """
        existing_issue = frappe.db.exists(
            "Book Transaction",
            {
                "library_member": self.library_member,
                "book": self.book,
                "transaction_type": "Issue",
                "status": "Open",
            },
        )
        if not existing_issue:
            frappe.throw(
                f"No open Issue transaction found for member '{self.library_member}' "
                f"and book '{self.book}'. Cannot process return."
            )

        self.return_date = today()
        self.status = "Completed"

    def on_submit(self):
        """
        After saving, update the Book's available_copies count
        and close the related Issue on return.
        """
        book = frappe.get_doc("Book", self.book)

        if self.transaction_type == "Issue":
            # Decrement available copies
            book.available_copies -= 1
            frappe.msgprint(
                f"Book '{book.title}' issued successfully. "
                f"Remaining copies: {book.available_copies}",
                alert=True,
            )

        elif self.transaction_type == "Return":
            # Increment available copies
            book.available_copies += 1

            # Mark the related open Issue as Completed
            open_issue = frappe.get_all(
                "Book Transaction",
                filters={
                    "library_member": self.library_member,
                    "book": self.book,
                    "transaction_type": "Issue",
                    "status": "Open",
                },
                fields=["name"],
                limit=1,
            )
            if open_issue:
                frappe.db.set_value(
                    "Book Transaction",
                    open_issue[0]["name"],
                    "status",
                    "Completed",
                )

            frappe.msgprint(
                f"Book '{book.title}' returned successfully. "
                f"Available copies: {book.available_copies}",
                alert=True,
            )

        book.save(ignore_permissions=True)
