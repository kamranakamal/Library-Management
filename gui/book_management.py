"""
Book management interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from models.book import Book
from models.student import Student
from utils.validators import Validators, ValidationError


class BookManagementFrame(ttk.Frame):
    """Book management interface"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Books tab
        self.create_books_tab()
        
        # Borrowings tab
        self.create_borrowings_tab()
    
    def create_books_tab(self):
        """Create books management tab"""
        books_frame = ttk.Frame(self.notebook)
        self.notebook.add(books_frame, text="Books")
        
        # Paned window for form and list
        paned_window = ttk.PanedWindow(books_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Book form
        self.create_book_form(paned_window)
        
        # Book list
        self.create_book_list(paned_window)
    
    def create_book_form(self, parent):
        """Create book form"""
        form_frame = ttk.LabelFrame(parent, text="Book Information", padding=10)
        parent.add(form_frame, weight=1)
        
        row = 0
        
        # Title
        ttk.Label(form_frame, text="Title *:").grid(row=row, column=0, sticky='w', pady=2)
        self.title_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.title_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Author
        ttk.Label(form_frame, text="Author:").grid(row=row, column=0, sticky='w', pady=2)
        self.author_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.author_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # ISBN
        ttk.Label(form_frame, text="ISBN:").grid(row=row, column=0, sticky='w', pady=2)
        self.isbn_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.isbn_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Category
        ttk.Label(form_frame, text="Category:").grid(row=row, column=0, sticky='w', pady=2)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, width=28,
                                    values=['Fiction', 'Non-Fiction', 'Science', 'History', 'Biography', 'Reference', 'Other'])
        category_combo.grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Total Copies
        ttk.Label(form_frame, text="Total Copies *:").grid(row=row, column=0, sticky='w', pady=2)
        self.total_copies_var = tk.StringVar(value="1")
        ttk.Entry(form_frame, textvariable=self.total_copies_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Available Copies
        ttk.Label(form_frame, text="Available Copies *:").grid(row=row, column=0, sticky='w', pady=2)
        self.available_copies_var = tk.StringVar(value="1")
        ttk.Entry(form_frame, textvariable=self.available_copies_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save Book", command=self.save_book).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_book_form).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Book", command=self.delete_book).grid(row=0, column=2, padx=5)
        
        # Configure column weights
        form_frame.columnconfigure(1, weight=1)
        
        # Current book ID
        self.current_book_id = None
    
    def create_book_list(self, parent):
        """Create book list"""
        list_frame = ttk.LabelFrame(parent, text="Books", padding=10)
        parent.add(list_frame, weight=2)
        
        # Search frame
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky='w')
        self.book_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.book_search_var)
        search_entry.grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_books).grid(row=0, column=2, padx=2)
        ttk.Button(search_frame, text="Refresh", command=self.load_books).grid(row=0, column=3, padx=2)
        
        # Configure search frame column weights
        search_frame.columnconfigure(1, weight=1)
        
        # Book tree
        book_columns = ('ID', 'Title', 'Author', 'Category', 'Total', 'Available', 'Status')
        self.book_tree = ttk.Treeview(list_frame, columns=book_columns, show='headings', height=15)
        
        for col in book_columns:
            self.book_tree.heading(col, text=col)
            if col == 'Title':
                self.book_tree.column(col, width=200)
            elif col == 'Author':
                self.book_tree.column(col, width=150)
            else:
                self.book_tree.column(col, width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.book_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.book_tree.xview)
        self.book_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.book_tree.grid(row=1, column=0, sticky='nsew')
        v_scrollbar.grid(row=1, column=1, sticky='ns')
        h_scrollbar.grid(row=2, column=0, sticky='ew')
        
        # Configure grid weights
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Bind selection event
        self.book_tree.bind('<<TreeviewSelect>>', self.on_book_select)
    
    def create_borrowings_tab(self):
        """Create borrowings management tab"""
        borrowings_frame = ttk.Frame(self.notebook)
        self.notebook.add(borrowings_frame, text="Borrowings")
        
        # Paned window
        paned_window = ttk.PanedWindow(borrowings_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Borrowing form
        self.create_borrowing_form(paned_window)
        
        # Borrowing list
        self.create_borrowing_list(paned_window)
    
    def create_borrowing_form(self, parent):
        """Create borrowing form"""
        form_frame = ttk.LabelFrame(parent, text="Book Borrowing", padding=10)
        parent.add(form_frame, weight=1)
        
        row = 0
        
        # Student selection
        ttk.Label(form_frame, text="Student:").grid(row=row, column=0, sticky='w', pady=2)
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(form_frame, textvariable=self.student_var, state='readonly', width=28)
        self.student_combo.grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Book selection
        ttk.Label(form_frame, text="Book:").grid(row=row, column=0, sticky='w', pady=2)
        self.book_var = tk.StringVar()
        self.book_combo = ttk.Combobox(form_frame, textvariable=self.book_var, state='readonly', width=28)
        self.book_combo.grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Due date
        ttk.Label(form_frame, text="Due Date:").grid(row=row, column=0, sticky='w', pady=2)
        self.due_date_var = tk.StringVar(value=(date.today() + timedelta(days=14)).strftime('%Y-%m-%d'))
        ttk.Entry(form_frame, textvariable=self.due_date_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Borrow Book", command=self.borrow_book).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Return Book", command=self.return_book).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_borrowing_form).grid(row=0, column=2, padx=5)
        
        # Configure column weights
        form_frame.columnconfigure(1, weight=1)
    
    def create_borrowing_list(self, parent):
        """Create borrowing list"""
        list_frame = ttk.LabelFrame(parent, text="Borrowings", padding=10)
        parent.add(list_frame, weight=2)
        
        # Filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").grid(row=0, column=0, sticky='w')
        self.borrowing_filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.borrowing_filter_var,
                                  values=['All', 'Active', 'Returned', 'Overdue'], state='readonly')
        filter_combo.grid(row=0, column=1, padx=5, sticky='ew')
        ttk.Button(filter_frame, text="Apply Filter", command=self.load_borrowings).grid(row=0, column=2, padx=5)
        
        # Configure filter frame column weights
        filter_frame.columnconfigure(1, weight=1)
        
        # Borrowing tree
        borrowing_columns = ('ID', 'Student', 'Book', 'Borrow Date', 'Due Date', 'Return Date', 'Fine', 'Status')
        self.borrowing_tree = ttk.Treeview(list_frame, columns=borrowing_columns, show='headings', height=15)
        
        for col in borrowing_columns:
            self.borrowing_tree.heading(col, text=col)
            if col in ['Student', 'Book']:
                self.borrowing_tree.column(col, width=150)
            elif col in ['Borrow Date', 'Due Date', 'Return Date']:
                self.borrowing_tree.column(col, width=100)
            else:
                self.borrowing_tree.column(col, width=80)
        
        # Scrollbars
        v_scrollbar2 = ttk.Scrollbar(list_frame, orient='vertical', command=self.borrowing_tree.yview)
        h_scrollbar2 = ttk.Scrollbar(list_frame, orient='horizontal', command=self.borrowing_tree.xview)
        self.borrowing_tree.configure(yscrollcommand=v_scrollbar2.set, xscrollcommand=h_scrollbar2.set)
        
        # Grid layout
        self.borrowing_tree.grid(row=1, column=0, sticky='nsew')
        v_scrollbar2.grid(row=1, column=1, sticky='ns')
        h_scrollbar2.grid(row=2, column=0, sticky='ew')
        
        # Configure grid weights
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Bind selection event
        self.borrowing_tree.bind('<<TreeviewSelect>>', self.on_borrowing_select)
    
    def load_data(self):
        """Load all data"""
        self.load_books()
        self.load_borrowings()
        self.load_students_for_borrowing()
        self.load_books_for_borrowing()
    
    def load_books(self):
        """Load books into tree"""
        # Clear existing items
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
        
        try:
            books = Book.get_all()
            for book in books:
                status = "Available" if book.is_available() else "Out of Stock"
                
                self.book_tree.insert('', 'end', values=(
                    book.id,
                    book.title,
                    book.author or "N/A",
                    book.category or "N/A",
                    book.total_copies,
                    book.available_copies,
                    status
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load books: {str(e)}")
    
    def load_borrowings(self):
        """Load borrowings into tree"""
        # Clear existing items
        for item in self.borrowing_tree.get_children():
            self.borrowing_tree.delete(item)
        
        try:
            from config.database import DatabaseManager
            db_manager = DatabaseManager()
            
            # Build query based on filter
            filter_value = self.borrowing_filter_var.get()
            query = '''
                SELECT bb.id, s.name as student_name, b.title as book_title,
                       bb.borrow_date, bb.due_date, bb.return_date, bb.fine_amount, bb.is_returned
                FROM book_borrowings bb
                JOIN students s ON bb.student_id = s.id
                JOIN books b ON bb.book_id = b.id
            '''
            
            if filter_value == "Active":
                query += " WHERE bb.is_returned = 0"
            elif filter_value == "Returned":
                query += " WHERE bb.is_returned = 1"
            elif filter_value == "Overdue":
                query += " WHERE bb.is_returned = 0 AND bb.due_date < date('now')"
            
            query += " ORDER BY bb.borrow_date DESC"
            
            borrowings = db_manager.execute_query(query)
            
            for borrowing in borrowings:
                # Determine status
                if borrowing['is_returned']:
                    status = "Returned"
                elif borrowing['due_date'] < str(date.today()):
                    status = "Overdue"
                else:
                    status = "Active"
                
                self.borrowing_tree.insert('', 'end', values=(
                    borrowing['id'],
                    borrowing['student_name'],
                    borrowing['book_title'],
                    borrowing['borrow_date'],
                    borrowing['due_date'],
                    borrowing['return_date'] or "N/A",
                    f"₹{borrowing['fine_amount']}" if borrowing['fine_amount'] else "₹0",
                    status
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load borrowings: {str(e)}")
    
    def load_students_for_borrowing(self):
        """Load students for borrowing combo"""
        try:
            students = Student.get_all()
            student_values = [f"{student.name} ({student.mobile_number})" for student in students]
            self.student_combo['values'] = student_values
            
            # Store student objects for reference
            self.students = {f"{student.name} ({student.mobile_number})": student for student in students}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {str(e)}")
    
    def load_books_for_borrowing(self):
        """Load available books for borrowing combo"""
        try:
            books = Book.get_all()
            available_books = [book for book in books if book.is_available()]
            book_values = [f"{book.title} by {book.author or 'Unknown'}" for book in available_books]
            self.book_combo['values'] = book_values
            
            # Store book objects for reference
            self.books = {f"{book.title} by {book.author or 'Unknown'}": book for book in available_books}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load books: {str(e)}")
    
    def on_book_select(self, event):
        """Handle book selection"""
        selection = self.book_tree.selection()
        if not selection:
            return
        
        try:
            item = self.book_tree.item(selection[0])
            book_id = item['values'][0]
            
            book = Book.get_by_id(book_id)
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
        """Handle borrowing selection"""
        # This could be used for editing borrowings or showing details
        pass
    
    def save_book(self):
        """Save book"""
        try:
            # Validate input
            title = self.title_var.get().strip()
            if not title:
                raise ValidationError("Title is required")
            
            author = self.author_var.get().strip() or None
            isbn = Validators.validate_isbn(self.isbn_var.get())
            category = self.category_var.get().strip() or None
            total_copies = Validators.validate_book_copies(self.total_copies_var.get())
            available_copies = Validators.validate_book_copies(self.available_copies_var.get())
            
            if available_copies > total_copies:
                raise ValidationError("Available copies cannot exceed total copies")
            
            # Create or update book
            if self.current_book_id:
                book = Book.get_by_id(self.current_book_id)
                if not book:
                    raise Exception("Book not found")
                
                book.title = title
                book.author = author
                book.isbn = isbn
                book.category = category
                book.total_copies = total_copies
                book.available_copies = available_copies
            else:
                book = Book(
                    title=title,
                    author=author,
                    isbn=isbn,
                    category=category,
                    total_copies=total_copies,
                    available_copies=available_copies
                )
            
            errors = book.validate()
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            
            book.save()
            
            messagebox.showinfo("Success", "Book saved successfully!")
            self.load_books()
            self.load_books_for_borrowing()
            self.clear_book_form()
            
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
        if not self.current_book_id:
            messagebox.showwarning("Warning", "Please select a book to delete")
            return
        
        try:
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this book?"):
                book = Book.get_by_id(self.current_book_id)
                if book:
                    book.delete()
                    messagebox.showinfo("Success", "Book deleted successfully!")
                    self.load_books()
                    self.load_books_for_borrowing()
                    self.clear_book_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete book: {str(e)}")
    
    def search_books(self):
        """Search books"""
        search_term = self.book_search_var.get().strip()
        if not search_term:
            self.load_books()
            return
        
        try:
            for item in self.book_tree.get_children():
                self.book_tree.delete(item)
            
            books = Book.search(search_term)
            for book in books:
                status = "Available" if book.is_available() else "Out of Stock"
                
                self.book_tree.insert('', 'end', values=(
                    book.id,
                    book.title,
                    book.author or "N/A",
                    book.category or "N/A",
                    book.total_copies,
                    book.available_copies,
                    status
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
    
    def borrow_book(self):
        """Borrow book"""
        try:
            if not self.student_var.get():
                messagebox.showwarning("Warning", "Please select a student")
                return
            
            if not self.book_var.get():
                messagebox.showwarning("Warning", "Please select a book")
                return
            
            # Get selected student and book
            student = self.students[self.student_var.get()]
            book = self.books[self.book_var.get()]
            
            # Validate due date
            due_date = Validators.validate_date(self.due_date_var.get(), "Due date")
            if due_date <= date.today():
                raise ValidationError("Due date must be in the future")
            
            # Create borrowing record
            from config.database import DatabaseManager
            db_manager = DatabaseManager()
            
            query = '''
                INSERT INTO book_borrowings (student_id, book_id, borrow_date, due_date)
                VALUES (?, ?, ?, ?)
            '''
            
            db_manager.execute_query(query, (student.id, book.id, date.today(), due_date))
            
            # Update book availability
            book.borrow()
            
            messagebox.showinfo("Success", "Book borrowed successfully!")
            self.load_borrowings()
            self.load_books()
            self.load_books_for_borrowing()
            self.clear_borrowing_form()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to borrow book: {str(e)}")
    
    def return_book(self):
        """Return book"""
        selection = self.borrowing_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a borrowing to return")
            return
        
        try:
            item = self.borrowing_tree.item(selection[0])
            borrowing_id = item['values'][0]
            
            # Confirm return
            if messagebox.askyesno("Confirm", "Mark this book as returned?"):
                from config.database import DatabaseManager
                db_manager = DatabaseManager()
                
                # Get borrowing details
                query = "SELECT book_id FROM book_borrowings WHERE id = ?"
                result = db_manager.execute_query(query, (borrowing_id,))
                
                if result:
                    book_id = result[0]['book_id']
                    
                    # Update borrowing record
                    query = '''
                        UPDATE book_borrowings 
                        SET is_returned = 1, return_date = date('now')
                        WHERE id = ?
                    '''
                    db_manager.execute_query(query, (borrowing_id,))
                    
                    # Update book availability
                    book = Book.get_by_id(book_id)
                    if book:
                        book.return_book()
                    
                    messagebox.showinfo("Success", "Book returned successfully!")
                    self.load_borrowings()
                    self.load_books()
                    self.load_books_for_borrowing()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return book: {str(e)}")
    
    def clear_borrowing_form(self):
        """Clear borrowing form"""
        self.student_var.set("")
        self.book_var.set("")
        self.due_date_var.set((date.today() + timedelta(days=14)).strftime('%Y-%m-%d'))
    
    def refresh(self):
        """Refresh the interface"""
        self.load_data()
