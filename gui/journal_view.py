"""
Financial Journal / Daily Notes View for Mopex.
"""
import datetime
import customtkinter as ctk
from typing import Optional, Callable
from database import DatabaseManager
from models import JournalNote, MOOD_OPTIONS


class JournalDialog(ctk.CTkToplevel):
    """Modal dialog to create or edit a journal note."""

    def __init__(self, master, db: DatabaseManager, budget_id: int,
                 note: Optional[JournalNote] = None, on_save: Optional[Callable] = None):
        super().__init__(master)
        self.db = db
        self.budget_id = budget_id
        self.note = note
        self.on_save = on_save

        self.title("Edit Note" if note else "New Journal Entry")
        self.geometry("480x480")
        self.resizable(False, False)
        self.grab_set()
        self.after(10, self._center_window)

        ctk.CTkLabel(self, text="✏️ Edit Entry" if note else "📔 New Journal Entry",
                     font=("Segoe UI", 18, "bold")).pack(pady=(18, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24)

        # Title
        ctk.CTkLabel(form, text="Title:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.title_entry = ctk.CTkEntry(form, placeholder_text="E.g. End of Month Review, Payday Notes", height=36)
        if note:
            self.title_entry.insert(0, note.title)
        self.title_entry.pack(fill="x", pady=(0, 10))

        # Date
        ctk.CTkLabel(form, text="Date (YYYY-MM-DD):", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.date_entry = ctk.CTkEntry(form, placeholder_text="YYYY-MM-DD", height=36)
        self.date_entry.insert(0, note.date if note else datetime.date.today().isoformat())
        self.date_entry.pack(fill="x", pady=(0, 10))

        # Mood
        ctk.CTkLabel(form, text="Financial Mood:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        mood_values = list(MOOD_OPTIONS.values())
        self.mood_dropdown = ctk.CTkOptionMenu(form, values=mood_values, height=36)
        if note:
            self.mood_dropdown.set(MOOD_OPTIONS.get(note.mood, "😐 Neutral"))
        else:
            self.mood_dropdown.set("😐 Neutral")
        self.mood_dropdown.pack(fill="x", pady=(0, 10))

        # Content
        ctk.CTkLabel(form, text="Notes / Journal Entry:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.content_box = ctk.CTkTextbox(form, height=120, corner_radius=8, border_width=1,
                                           border_color=("#E2E8F0", "#334155"))
        if note and note.content:
            self.content_box.insert("1.0", note.content)
        self.content_box.pack(fill="x", pady=(0, 10))

        self.error_label = ctk.CTkLabel(form, text="", text_color="#EF4444", font=("Segoe UI", 11))
        self.error_label.pack(fill="x", pady=(0, 4))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 18))
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="transparent", border_width=1,
                      text_color=("#475569", "#CBD5E1"), command=self.destroy, height=38, width=100).pack(side="left")
        ctk.CTkButton(btn_frame, text="💾 Save Note", fg_color="#3B82F6", hover_color="#2563EB",
                      command=self._save, height=38, width=140, font=("Segoe UI", 12, "bold")).pack(side="right")

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth()//2)-(w//2)}+{(self.winfo_screenheight()//2)-(h//2)}")

    def _save(self):
        title = self.title_entry.get().strip()
        date = self.date_entry.get().strip()
        mood_label = self.mood_dropdown.get()
        content = self.content_box.get("1.0", "end").strip()

        if not title:
            self.error_label.configure(text="Please enter a title.")
            return
        if len(date) != 10:
            self.error_label.configure(text="Date must be YYYY-MM-DD.")
            return

        # Reverse-lookup mood key from label
        mood_key = next((k for k, v in MOOD_OPTIONS.items() if v == mood_label), "neutral")

        if self.note:
            self.note.title = title
            self.note.date = date
            self.note.mood = mood_key
            self.note.content = content
            self.db.update_journal_note(self.note)
        else:
            new_note = JournalNote(
                budget_id=self.budget_id,
                date=date,
                title=title,
                content=content,
                mood=mood_key,
            )
            self.db.add_journal_note(new_note)

        if self.on_save:
            self.on_save()
        self.destroy()


class JournalView(ctk.CTkFrame):
    """
    Financial Journal view — create, browse and manage daily notes and reflections.
    """

    def __init__(self, master, db: DatabaseManager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.selected_note: Optional[JournalNote] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        ctk.CTkLabel(header, text="Financial Journal 📔", font=("Segoe UI", 22, "bold"), anchor="w").pack(side="left")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")
        ctk.CTkButton(actions, text="+ New Entry", font=("Segoe UI", 12, "bold"),
                      fg_color="#10B981", hover_color="#059669", height=36,
                      command=self._open_add_dialog).pack(side="left", padx=3)
        ctk.CTkButton(actions, text="✏️ Edit", font=("Segoe UI", 12),
                      fg_color="#3B82F6", hover_color="#2563EB", height=36, width=80,
                      command=self._open_edit_dialog).pack(side="left", padx=3)
        ctk.CTkButton(actions, text="🗑️ Delete", font=("Segoe UI", 12),
                      fg_color="#EF4444", hover_color="#DC2626", height=36, width=85,
                      command=self._delete_note).pack(side="left", padx=3)

        # Search
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 6))
        self.search_entry = ctk.CTkEntry(search_row, placeholder_text="🔍 Search notes...", height=34)
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        # Main layout: list on left, detail on right
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Left: Note list
        self.list_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=("white", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            label_text="📋 Notes List"
        )
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Right: Detail view
        self.detail_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=("white", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.detail_frame.grid(row=0, column=1, sticky="nsew")

        self.detail_placeholder = ctk.CTkLabel(
            self.detail_frame,
            text="📖 Select a note to read it here",
            font=("Segoe UI", 13),
            text_color=("#94A3B8", "#64748B")
        )
        self.detail_placeholder.pack(expand=True)

        self.detail_title_lbl = ctk.CTkLabel(
            self.detail_frame, text="", font=("Segoe UI", 17, "bold"), anchor="w", wraplength=420
        )
        self.detail_meta_lbl = ctk.CTkLabel(
            self.detail_frame, text="", font=("Segoe UI", 11),
            text_color=("#64748B", "#94A3B8"), anchor="w"
        )
        self.detail_content = ctk.CTkTextbox(
            self.detail_frame, font=("Segoe UI", 12), border_width=0, fg_color="transparent",
            wrap="word", state="disabled"
        )

        self.refresh()

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        budget = self.db.get_active_budget()
        if not budget:
            return

        search = self.search_entry.get().strip()
        notes = self.db.get_journal_notes(budget.id, search=search)

        if not notes:
            ctk.CTkLabel(self.list_frame, text="No journal entries yet.",
                         font=("Segoe UI", 12), text_color=("#94A3B8", "#64748B")).pack(pady=30, padx=10)
            return

        for note in notes:
            mood_label = MOOD_OPTIONS.get(note.mood, "😐")
            card = ctk.CTkButton(
                self.list_frame,
                text=f"{mood_label.split()[0]}  {note.title}\n{note.date}",
                font=("Segoe UI", 11),
                anchor="w",
                fg_color="transparent",
                hover_color=("#E2E8F0", "#334155"),
                text_color=("#0F172A", "#F8FAFC"),
                height=56,
                command=lambda n=note: self._show_note(n)
            )
            card.pack(fill="x", pady=2, padx=4)

    def _show_note(self, note: JournalNote):
        self.selected_note = note
        self.detail_placeholder.pack_forget()

        self.detail_title_lbl.configure(text=f"{note.icon if hasattr(note, 'icon') else ''}{note.title}")
        self.detail_title_lbl.pack(fill="x", padx=16, pady=(16, 4))

        mood_label = MOOD_OPTIONS.get(note.mood, "😐 Neutral")
        self.detail_meta_lbl.configure(text=f"{mood_label}   |   {note.date}")
        self.detail_meta_lbl.pack(fill="x", padx=16, pady=(0, 8))

        self.detail_content.configure(state="normal")
        self.detail_content.delete("1.0", "end")
        self.detail_content.insert("1.0", note.content or "(No content)")
        self.detail_content.configure(state="disabled")
        self.detail_content.pack(fill="both", expand=True, padx=12, pady=(0, 14))

    def _open_add_dialog(self):
        budget = self.db.get_active_budget()
        if budget:
            JournalDialog(self, self.db, budget.id, on_save=self.refresh)

    def _open_edit_dialog(self):
        if not self.selected_note:
            return
        budget = self.db.get_active_budget()
        if budget:
            JournalDialog(self, self.db, budget.id, note=self.selected_note, on_save=self.refresh)

    def _delete_note(self):
        if not self.selected_note:
            return
        self.db.delete_journal_note(self.selected_note.id)
        self.selected_note = None
        self._reset_detail()
        self.refresh()

    def _reset_detail(self):
        self.detail_title_lbl.pack_forget()
        self.detail_meta_lbl.pack_forget()
        self.detail_content.pack_forget()
        self.detail_placeholder.pack(expand=True)
