import tkinter as tk
from tkinter import simpledialog, messagebox

class NoteApp:

     def __init__(self):
    
          self.root = tk.Tk()
          self.root.title("Note APP")
          self.root.geometry("500x700")

          self.folders = {} #store variable of folders
          self.current_folder = None
          self.current_note_index = None

          #Frame setup
          self.folder_frame = tk.Frame(self.root)
          self.note_frame = tk.Frame(self.root)
          self.editor_frame = tk.Frame(self.root)

          self.folder_ui()
          self.note_ui()
          self.editor_ui()

          self.show_folder_frame()
          self.root.mainloop()

#==================== Folder Frame =======================#

     def folder_ui(self):
          # Menubar
          self.menubar = tk.Menu(self.root)
          self.menubar.add_command(label="Add Folder", command=self.add_folder)
          self.root.config(menu=self.menubar) 

          # Top frame
          self.top_frame = tk.Frame(self.folder_frame)
          self.top_frame.pack(fill="both")
          self.top_frame.columnconfigure(0, weight=1) 

          # Search bar and Button
          self.search_entry = tk.Entry(self.top_frame, font=('Arial', 10))
          self.search_entry.grid(row=0, column=0,sticky="nsew", padx=(10, 0), pady= 5)
          self.search_button = tk.Button(self.top_frame, text="Search", command=self.search_folder)
          self.search_button.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady= 5)

          # Folder list
          self.folder_listbox = tk.Listbox(self.folder_frame, font=('Arial', 10))
          self.folder_listbox.pack(fill="both", expand=True, padx=10, pady=(5, 10))
          self.folder_listbox.bind("<Double-Button-1>", self.enter_folder)

     def add_folder(self):
          folderName = simpledialog.askstring("New Folder", "Folder Name: ", parent=self.root)
          if folderName and folderName not in self.folders:
               self.folders[folderName] = []
               self.refresh_folder_list()

     def refresh_folder_list(self, folders = None):
          self.folder_listbox.delete(0, tk.END)
          show_folders = folders if folders is not None else self.folders
          for folder in show_folders:
            self.folder_listbox.insert(tk.END, folder)

     def search_folder(self):
          keyword = self.search_entry.get().strip()
          if not keyword:
               self.refresh_folder_list()
               return
          result = [f for f in self.folders if keyword.lower() in f.lower()]
          self.refresh_folder_list(result)

     def enter_folder(self, event):
          selection = self.folder_listbox.curselection()
          if selection:
               self.current_folder = self.folder_listbox.get(selection[0])
               self.refresh_note_list()
               self.show_note_frame()

#==================== Note Frame =======================#

     def note_ui(self):
           # Top_frame
           self.top_note = tk.Frame(self.note_frame)
           self.top_note.pack(fill="x", pady=(10, 0))

           self.top_note.columnconfigure(0, weight=1)
           self.top_note.columnconfigure(0, weight=1)

           # back button
           self.back_btn = tk.Button(self.top_note, text="← Folders", command=self.show_folder_frame)
           self.back_btn.grid(row=0, column=0, sticky="w", padx=(10, 5))

           # add note button
           self.add_note = tk.Button(self.top_note, text="Add Note", command=self.add_note)
           self.add_note.grid(row=0, column=1, sticky="e", padx=(5, 10))

           # Search Bar 
           self.search_entry_note = tk.Entry(self.top_note, font=('Arial', 10))
           self.search_entry_note.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(10, 5))

           # Search button
           self.search_button_note = tk.Button(self.top_note, text="Search", command=self.search_note)
           self.search_button_note.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=(10, 5))

           # Note listbox
           self.note_list = tk.Listbox(self.note_frame, font=('Arial', 10))
           self.note_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
           self.note_list.bind("<Double-Button-1>", self.open_note_editor)

     def add_note(self):
          note_title = simpledialog.askstring("New Note", f"Note for {self.current_folder}:", parent=self.root)
          if note_title:
               new_note = {'title': note_title, 'content': ''}
               self.folders[self.current_folder].append(new_note)
               self.refresh_note_list()

     def refresh_note_list(self, notes=None):
          self.note_list.delete(0, tk.END)
          if self.current_folder:
               notes_to_show = notes if notes is not None else self.folders[self.current_folder]
               for note in notes_to_show:
                    self.note_list.insert(tk.END, note['title'])

     def search_note(self):
          keyword = self.search_entry_note.get().strip()
          if not keyword:
               self.refresh_note_list()
               return
          
          all_note = self.folders.get(self.current_folder, [])
          result = [note for note in all_note if keyword.lower() in note['title'].lower()]
          self.refresh_note_list(result)
                    
#================ editor frame =================#
     def editor_ui(self):
          # Top_frame
          self.top_editor_frame = tk.Frame(self.editor_frame)
          self.top_editor_frame.pack(fill="both", pady=(10, 0))

          self.note_title_var = tk.StringVar()
          self.title_entry = tk.Entry(self.top_editor_frame, textvariable=self.note_title_var, font=('Arial', 12, 'bold'))
          self.title_entry.pack(side="bottom", fill="x", padx=(10, 10), pady=(10, 0))

          self.back_btn_editor = tk.Button(self.top_editor_frame, text="", command= self.show_note_frame)
          self.back_btn_editor.pack(side="left", padx=(10, 0))

          self.save_btn = tk.Button(self.top_editor_frame, text="Done", command= self.save_note_content)
          self.save_btn.pack(side="right", padx=(0, 10))

          self.note_text = tk.Text(self.editor_frame, wrap="word", font=('Arial', 11))
          self.note_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

     def open_note_editor(self, event):
          selection = self.note_list.curselection()
          if selection:
               index = selection[0]
               self.current_note_index = index
               note = self.folders[self.current_folder][index]

               self.note_title_var.set(note['title'])
               self.note_text.delete("1.0", tk.END)
               self.note_text.insert("1.0", note['content'])

               self.show_editor_frame()

     def save_note_content(self):
          if self.current_folder is not None and self.current_note_index is not None:
               note = self.folders[self.current_folder][self.current_note_index]
               note['title'] = self.note_title_var.get()
               note['content'] = self.note_text.get("1.0", "end-1c")
               self.refresh_note_list()
               self.show_note_frame()

#================ Frame switching =================#

     def show_folder_frame(self):
          self.root.config(menu=self.menubar)
          self.note_frame.forget()
          self.editor_frame.forget()
          self.folder_frame.pack(fill="both", expand=True)
          self.refresh_folder_list()

     def show_note_frame(self):
          self.root.config(menu="") 
          self.folder_frame.forget()
          self.editor_frame.forget()
          self.note_frame.pack(fill="both", expand=True)
          self.refresh_note_list()
     
     def show_editor_frame(self):
          self.editor_frame.pack(fill="both", expand=True)
          self.folder_frame.forget()
          self.note_frame.forget()
          self.back_btn_editor.config(text=f"< {self.current_folder}")

NoteApp()

