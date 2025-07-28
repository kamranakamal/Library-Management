import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from tkcalendar import DateEntry
from models.book import Book
from models.student import Student
from models.book_borrowing import BookBorrowing
from utils.validators import Validators, ValidationError

class BookManagementFrame(ttk.Frame):
    """Book management interface"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup user interface"""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        self.create_books_tab()
        self.create_borrowings_tab()
    
    def create_books_tab(self):
        """Create books management tab"""
        books_frame = ttk.Frame(self.notebook)
        self.notebook.add(books_frame, text="Books")
        paned_window = ttk.PanedWindow(books_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        self.create_book_form(paned_window)
        self.create_book_list(paned_window)
    
    def create_book_form(self, parent):
        """Create book form"""
        form_frame = ttk.LabelFrame(parent, text="Book Information", padding=10)
        parent.add(form_frame, weight=1)
        row = 0
        ttk.Label(form_frame, text="Title *:").grid(row=row, column=0, sticky='w', pady=2)
        self.title_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.title_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="Author:").grid(row=row, column=0, sticky='w', pady=2)
        self.author_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.author_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="ISBN:").grid(row=row, column=0, sticky='w', pady=2)
        self.isbn_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.isbn_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="Category:").grid(row=row, column=0, sticky='w', pady=2)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, width=28, values=['Fiction', 'Non-Fiction', 'Science', 'History', 'Biography', 'Reference', 'Other'])
        category_combo.grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="Total Copies *:").grid(row=row, column=0, sticky='w', pady=2)
        self.total_copies_var = tk.StringVar(value="1")
        ttk.Entry(form_frame, textvariable=self.total_copies_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="Available Copies *:").grid(row=row, column=0, sticky='w', pady=2)
        self.available_copies_var = tk.StringVar(value="1")
        ttk.Entry(form_frame, textvariable=self.available_copies_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Save Book", command=self.save_book).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_book_form).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Book", command=self.delete_book).grid(row=0, column=2, padx=5)
        form_frame.columnconfigure(1, weight=1)
        self.current_book_id = None
    
    def create_book_list(self, parent):
        """Create book list"""
        list_frame = ttk.LabelFrame(parent, text="Books", padding=10)
        parent.add(list_frame, weight=2)
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky='w')
        self.book_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.book_search_var)
        search_entry.grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_books).grid(row=0, column=2, padx=2)
        ttk.Button(search_frame, text="Refresh", command=self.load_books).grid(row=0, column=3, padx=2)
        search_frame.columnconfigure(1, weight=1)
        book_columns = ('ID', 'Title', 'Author', 'Category', 'Total', 'Available', 'Status')
        self.book_tree = ttk.Treeview(list_frame, columns=book_columns, show='headings', height=15)
        for col in book_columns:
            self.book_tree.heading(col, text=col)
            if col == 'Title': self.book_tree.column(col, width=200)
            elif col == 'Author': self.book_tree.column(col, width=150)
            else: self.book_tree.column(col, width=80)
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.book_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.book_tree.xview)
        self.book_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.book_tree.grid(row=1, column=0, sticky='nsew')
        v_scrollbar.grid(row=1, column=1, sticky='ns')
        h_scrollbar.grid(row=2, column=0, sticky='ew')
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        self.book_tree.bind('<<TreeviewSelect>>', self.on_book_select)
    
    def create_borrowings_tab(self):
        """Create borrowings management tab"""
        borrowings_frame = ttk.Frame(self.notebook)
        self.notebook.add(borrowings_frame, text="Borrowings")
        paned_window = ttk.PanedWindow(borrowings_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        self.create_borrowing_form(paned_window)
        self.create_borrowing_list(paned_window)
    
    def create_borrowing_form(self, parent):
        """Create borrowing form"""
        form_frame = ttk.LabelFrame(parent, text="Book Borrowing", padding=10)
        parent.add(form_frame, weight=1)
        row = 0
        ttk.Label(form_frame, text="Student Name:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.student_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.student_name_var).grid(row=row, column=1, padx=5, pady=5, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="Father's Name:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.father_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.father_name_var).grid(row=row, column=1, padx=5, pady=5, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="Phone Number:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.phone_var).grid(row=row, column=1, padx=5, pady=5, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="Book:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.book_var = tk.StringVar()
        self.book_combo = ttk.Combobox(form_frame, textvariable=self.book_var, state='readonly', width=28)
        self.book_combo.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="Borrowing Date:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.borrow_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.borrow_date_entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
        row += 1
        ttk.Label(form_frame, text="Number of Days:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.days_var = tk.StringVar(value='15')
        ttk.Entry(form_frame, textvariable=self.days_var).grid(row=row, column=1, padx=5, pady=5, sticky='ew')
        row += 1
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Borrow Book", command=self.borrow_book).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Return Book", command=self.return_book).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Borrowing", command=self.delete_borrowing).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_borrowing_form).grid(row=0, column=3, padx=5)
        form_frame.columnconfigure(1, weight=1)

    def create_borrowing_list(self, parent):
        """Create borrowing list"""
        list_frame = ttk.LabelFrame(parent, text="Borrowings", padding=10)
        parent.add(list_frame, weight=2)
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        ttk.Label(filter_frame, text="Filter:").grid(row=0, column=0, sticky='w')
        self.borrowing_filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.borrowing_filter_var, values=['All', 'Active', 'Returned', 'Overdue'], state='readonly')
        filter_combo.grid(row=0, column=1, padx=5, sticky='ew')
        ttk.Button(filter_frame, text="Apply Filter", command=self.load_borrowings).grid(row=0, column=2, padx=5)
        filter_frame.columnconfigure(1, weight=1)
        borrowing_columns = ('ID', 'Student', "Father's Name", 'Phone', 'Book', 'Borrow Date', 'Due Date', 'Days', 'Return Date', 'Fine', 'Status')
        self.borrowing_tree = ttk.Treeview(list_frame, columns=borrowing_columns, show='headings', height=15)
        for col in borrowing_columns:
            self.borrowing_tree.heading(col, text=col)
            if col in ['Student', 'Book', "Father's Name"]: self.borrowing_tree.column(col, width=150)
            elif col == 'Phone': self.borrowing_tree.column(col, width=100)
            elif col in ['Borrow Date', 'Due Date', 'Return Date']: self.borrowing_tree.column(col, width=100)
            elif col == 'Days': self.borrowing_tree.column(col, width=50)
            else: self.borrowing_tree.column(col, width=80)
        v_scrollbar2 = ttk.Scrollbar(list_frame, orient='vertical', command=self.borrowing_tree.yview)
        h_scrollbar2 = ttk.Scrollbar(list_frame, orient='horizontal', command=self.borrowing_tree.xview)
        self.borrowing_tree.configure(yscrollcommand=v_scrollbar2.set, xscrollcommand=h_scrollbar2.set)
        self.borrowing_tree.grid(row=1, column=0, sticky='nsew')
        v_scrollbar2.grid(row=1, column=1, sticky='ns')
        h_scrollbar2.grid(row=2, column=0, sticky='ew')
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        self.borrowing_tree.bind('<<TreeviewSelect>>', self.on_borrowing_select)

    def load_data(self):
        """Load all data"""
        self.load_books()
        self.load_borrowings()
        self.load_books_for_borrowing()

    def load_books(self):
        """Load books into tree"""
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
        try:
            books = Book.get_all()
            for book in books:
                status = "Available" if book.is_available() else "Out of Stock"
                self.book_tree.insert('', 'end', values=(book.id, book.title, book.author or "N/A", book.category or "N/A", book.total_copies, book.available_copies, status))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load books: {str(e)}")

    def load_borrowings(self):
        """Load borrowings into tree"""
        for item in self.borrowing_tree.get_children():
            self.borrowing_tree.delete(item)
        try:
            borrowings = BookBorrowing.get_all_details()
            for borrowing in borrowings:
                status = "Returned" if borrowing['is_returned'] else ("Overdue" if borrowing['due_date'] < str(date.today()) else "Active")
                self.borrowing_tree.insert('', 'end', values=(borrowing['id'], borrowing['student_name'], borrowing['father_name'], borrowing['student_phone'], borrowing['book_title'], borrowing['borrow_date'], borrowing['due_date'], borrowing['days_borrowed'], borrowing['return_date'] or "N/A", f"Rs. {borrowing['fine_amount']}" if borrowing['fine_amount'] else "Rs. 0", status))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load borrowings: {str(e)}")

    def load_books_for_borrowing(self):
        """Load available books for borrowing combo"""
        try:
            books = Book.get_all()
            available_books = [book for book in books if book.is_available()]
            book_values = [f"{book.title} by {book.author or 'Unknown'}" for book in available_books]
            self.book_combo['values'] = book_values
            self.books = {f"{book.title} by {book.author or 'Unknown'}": book for book in available_books}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load books: {str(e)}")

    def on_book_select(self, event):
        """Handle book selection"""
        selection = self.book_tree.selection()
        if not selection: return
        try:
            item = self.book_tree.item(selection[0])
            book = Book.get_by_id(item['values'][0])
            if book:
                self.current_book_id = book.id
                self.title_var.set(book.title)
                self.author_var.set(book.author or "")
                self.isbn_var.set(book.isbn or "")
                self.category_var.set(book.category or "")
                self.total_copies_var.set(str(book.total_copies))
                self.available_copies_var.set(str(book.available_copies))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load book details: {str(e)}")

    def on_borrowing_select(self, event):
        pass

    def save_book(self):
        """Save book"""
        try:
            title = self.title_var.get().strip()
            if not title: raise ValidationError("Title is required")
            if self.current_book_id:
                book = Book.get_by_id(self.current_book_id)
                book.title = title
                book.author = self.author_var.get().strip() or None
                book.isbn = Validators.validate_isbn(self.isbn_var.get())
                book.category = self.category_var.get().strip() or None
                book.total_copies = Validators.validate_book_copies(self.total_copies_var.get())
                book.available_copies = Validators.validate_book_copies(self.available_copies_var.get())
            else:
                book = Book(title=title, author=self.author_var.get().strip() or None, isbn=Validators.validate_isbn(self.isbn_var.get()), category=self.category_var.get().strip() or None, total_copies=Validators.validate_book_copies(self.total_copies_var.get()), available_copies=Validators.validate_book_copies(self.available_copies_var.get()))
            errors = book.validate()
            if errors: messagebox.showerror("Validation Error", "\n".join(errors)); return
            book.save()
            messagebox.showinfo("Success", "Book saved successfully!")
            self.refresh()
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save book: {str(e)}")

    def clear_book_form(self):
        """Clear book form"""
        self.current_book_id = None
        self.title_var.set("")
        self.author_var.set("")
        self.isbn_var.set("")
        self.category_var.set("")
        self.total_copies_var.set("1")
        self.available_copies_var.set("1")

    def delete_book(self):
        """Delete book"""
        if not self.current_book_id: messagebox.showwarning("Warning", "Please select a book to delete"); return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this book?"):
            try:
                Book.get_by_id(self.current_book_id).delete()
                messagebox.showinfo("Success", "Book deleted successfully!")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete book: {str(e)}")

    def search_books(self):
        """Search books"""
        search_term = self.book_search_var.get().strip()
        if not search_term: self.load_books(); return
        for item in self.book_tree.get_children(): self.book_tree.delete(item)
        try:
            books = Book.search(search_term)
            for book in books:
                status = "Available" if book.is_available() else "Out of Stock"
                self.book_tree.insert('', 'end', values=(book.id, book.title, book.author or "N/A", book.category or "N/A", book.total_copies, book.available_copies, status))
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def borrow_book(self):
        """Handle book borrowing"""
        try:
            student_name = self.student_name_var.get().strip()
            father_name = self.father_name_var.get().strip()
            phone = self.phone_var.get().strip()
            book_selection = self.book_var.get()
            borrow_date = self.borrow_date_entry.get_date()
            days_to_borrow_str = self.days_var.get().strip()

            if not all([student_name, phone, book_selection, days_to_borrow_str]): messagebox.showerror("Input Error", "Student Name, Phone, Book, and Number of Days are required."); return
            if not phone.isdigit() or len(phone) < 10: messagebox.showerror("Input Error", "Please enter a valid phone number."); return
            if not days_to_borrow_str.isdigit() or int(days_to_borrow_str) <= 0: messagebox.showerror("Input Error", "Number of Days must be a positive integer."); return

            days_to_borrow = int(days_to_borrow_str)
            book = self.books.get(book_selection)
            if not book or not book.is_available(): messagebox.showerror("Book Error", "Selected book is not available."); self.load_books_for_borrowing(); return

            student = Student.find_by_phone(phone)
            if not student:
                student = Student(name=student_name, father_name=father_name, mobile_number=phone, address='N/A').save()
                messagebox.showinfo("Student Created", f"New student '{student_name}' has been created.")
            
            due_date = borrow_date + timedelta(days=days_to_borrow)
            BookBorrowing(student_id=student.id, book_id=book.id, borrow_date=borrow_date.strftime('%Y-%m-%d'), due_date=due_date.strftime('%Y-%m-%d')).save()
            book.borrow()
            messagebox.showinfo("Success", f"Book '{book.title}' borrowed by '{student.name}'.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while borrowing the book: {e}")

    def delete_borrowing(self):
        """Delete a borrowing record"""
        selection = self.borrowing_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a borrowing to delete")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to permanently delete this borrowing record?"):
            try:
                borrowing_id = self.borrowing_tree.item(selection[0])['values'][0]
                BookBorrowing.delete_by_id(borrowing_id)
                messagebox.showinfo("Success", "Borrowing record deleted successfully!")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete borrowing record: {str(e)}")

    def return_book(self):
        """Return book"""
        selection = self.borrowing_tree.selection()
        if not selection: messagebox.showwarning("Warning", "Please select a borrowing to return"); return
        if messagebox.askyesno("Confirm", "Mark this book as returned?"):
            try:
                borrowing_id = self.borrowing_tree.item(selection[0])['values'][0]
                borrowing = BookBorrowing.get_by_id(borrowing_id)
                borrowing.return_book()
                messagebox.showinfo("Success", "Book returned successfully!")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to return book: {str(e)}")

    def clear_borrowing_form(self):
        """Clear the borrowing form fields"""
        self.student_name_var.set("")
        self.father_name_var.set("")
        self.phone_var.set("")
        self.book_var.set("")
        self.borrow_date_entry.set_date(date.today())
        self.days_var.set("15")

    def refresh(self):
        """Refresh the interface"""
        self.load_data()
