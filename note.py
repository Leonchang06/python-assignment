import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk  # use to setup the picture
import json
import webbrowser
import os
import re

# ================== Note Data Classes ================== #

class Note:
    def __init__(self, title):
        self._title = title   # private
        self._content_blocks = []  # private
        self._tags = []  # 新增标签属性
        self._link = []  # 新增标签属性

    # getter/setter 封装
    def get_title(self):
        return self._title
    
    def set_title(self, title):
        self._title = title

    def get_content_blocks(self):
        return self._content_blocks

    def set_content_blocks(self, blocks):
        self._content_blocks = blocks

    def get_tags(self):
        return self._tags

    def set_tags(self, tags):
        self._tags = tags

    def get_link(self):
        return self._link

    def set_link(self, link):
        self._link = link

    # 多态接口
    def to_dict(self):
        return {
            "type": "note",
            "title": self._title,
            "content_blocks": self._content_blocks,
            "tags": self._tags,  # 保存标签
            "link": self._link
        }

    @staticmethod
    def from_dict(data):
        n = Note(data.get("title", ""))
        n.set_content_blocks(data.get("content_blocks", []))
        n.set_tags(data.get("tags", []))  # 读取标签
        n.set_link(data.get("link", []))   
        return n

class NoteApp:
      #Main application class for the NoteApp.

     def __init__(self):
          
          #Initialize the app, load data, and set up UI frames.
          self.root = tk.Tk()
          self.root.title("Note APP")
          self.root.geometry("500x700")

           # private-like attributes
          self._folders = {} #store variable of folders
          self._current_folder = None
          self._current_note_index = None

          # Load data from file
          self.load_from_file()

          #Frame setup
          self.folder_frame = FolderFrame(self.root, self)
          self.editor_frame = EditorFrame(self.root, self)
          self.note_frame = NoteFrame(self.root, self)

          self.show_folder_frame()
          self.root.mainloop()

 # ===== Getter / Setter  ===== #

     def get_folders(self):
        return self._folders

     def set_folders(self, folders):
         self._folders = folders
 
     def get_current_folder(self):
         return self._current_folder
 
     def set_current_folder(self, folder):
         self._current_folder = folder
 
     def get_current_note_index(self):
         return self._current_note_index
 
     def set_current_note_index(self, index):
        self._current_note_index = index

# ================== File handling ================== #

     def load_from_file(self):
          """Load data from the JSON file."""
          if os.path.exists("notes_data.json"):
               try:
                    with open("notes_data.json", "r") as file:
                          raw_data = json.load(file)
                          self._folders = {
                              folder: [Note.from_dict(note) for note in notes]
                              for folder, notes in raw_data.items()
                          }
               except json.JSONDecodeError:
                    messagebox.showerror("Error", "Failed to load data. The file may be corrupted.")
                    self.folders = {}

     def save_to_file(self):
          # Save data to the JSON file.
          try: 
              with open("notes_data.json", "w") as file:
                  folders_to_save = {
                       folder: [note.to_dict() for note in notes]
                       for folder, notes in self._folders.items()
                  }
                  json.dump(folders_to_save, file, indent=4)
    
          except (OSError, PermissionError) as e:
               messagebox.showerror("Error", f"Failed to save notes: {e}")

#================ Frame switching =================#

     def show_folder_frame(self):
          # Display folder frame and refresh folder list
          self.root.config(menu=self.folder_frame.menubar)
          self.note_frame.hide()
          self.editor_frame.hide()
          self.folder_frame.show()
          self.folder_frame.refresh_folder_list()

     def show_note_frame(self):
          # Display note frame for current folder
          self.root.config(menu="") 
          self.note_frame.show()
          self.editor_frame.hide()
          self.folder_frame.hide()
          
          # 更新标题
          if self.get_current_folder():
              self.note_frame.note_title_label.config(text=f"📂 {self.get_current_folder()}")
              
          self.folder_frame.refresh_folder_list()

     def show_editor_frame(self):
          # Display editor frame for editing selected note
          self.folder_frame.hide()
          self.note_frame.hide()
          self.editor_frame.show()
          self.editor_frame.back_btn_editor.config(text=f"← {self.get_current_folder()}")

#==================== Base Frame =======================#

class BaseFrame(tk.Frame):
    
    #Base frame with show/hide methods for consistency.#
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()

#==================== Folder Frame =======================#

class FolderFrame(BaseFrame):
     def __init__(self, parent, app):
          super().__init__(parent, app)

          # Set up folder management UI (add, delete, search, rename).
          self.folder_title_label = tk.Label(self, text="📂 Folders", font=("Arial", 14, "bold"))
          self.folder_title_label.pack(pady=(10, 5))

          # Menubar
          self.menubar = tk.Menu(self.app.root)
          self.menubar.add_command(label="Add Folder", command=self.add_folder)
          self.menubar.add_command(label="Delete Folder", command=self.delete_folder)
          self.app.root.config(menu=self.menubar) 

          # Top frame
          self.top_frame = tk.Frame(self)
          self.top_frame.pack(fill="both")
          self.top_frame.columnconfigure(0, weight=1) 

          # Search bar and Button
          self.search_entry = tk.Entry(self.top_frame, font=('Arial', 10))
          self.search_entry.grid(row=0, column=0,sticky="nsew", padx=(10, 0), pady= 5)
          # 绑定 KeyRelease 事件，实现实时搜索
          self.search_entry.bind("<KeyRelease>", lambda event: self.search_folder())
          self.search_button = tk.Button(self.top_frame, text="Search", command=self.search_folder)
          self.search_button.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady= 5)

          # Folder list
          self.folder_listbox = tk.Listbox(self, font=('Arial', 10))
          self.folder_listbox.pack(fill="both", expand=True, padx=10, pady=(5, 10))
          self.folder_listbox.bind("<Double-Button-1>", self.enter_folder)
          
          self.folder_menu = tk.Menu(self.folder_listbox, tearoff=0)
          self.folder_menu.add_command(label="Rename Folder", command=self.rename_folder) 
          self.folder_menu.add_command(label="Delete Folder", command=self.delete_folder)
          self.folder_listbox.bind("<Button-3>", self.show_folder_menu)

     def rename_folder(self):
          selection = self.folder_listbox.curselection()
          if not selection:
              return
          old_name = self.folder_listbox.get(selection[0])
          new_name = simpledialog.askstring("Rename Folder", "Enter new name:", initialvalue=old_name)
          if new_name and new_name != old_name:
              folders = self.app.get_folders()
              if new_name in folders:
                  messagebox.showerror("Error", "Folder name already exists!")
                  return
              # 重命名：移动数据
              folders[new_name] = folders.pop(old_name)
              self.app.set_folders(folders)
              self.app.save_to_file()
              self.refresh_folder_list()

     def show_folder_menu(self, event):
          try:
              index = self.folder_listbox.nearest(event.y)
              self.folder_listbox.selection_clear(0, tk.END)
              self.folder_listbox.selection_set(index)
              self.folder_listbox.activate(index)
              self.folder_menu.tk_popup(event.x_root, event.y_root)
          finally:
              self.folder_menu.grab_release()

     def delete_folder(self):
         # Delete selected folder with confirmation.
         selection = self.folder_listbox.curselection()
         if not selection:
             messagebox.showwarning("Delete Folder", "Please select a folder to delete.")
             return
         
         folder_name = self.folder_listbox.get(selection[0])
         confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete folder '{folder_name}' and all its notes?")
         if confirm:
             folders = self.app.get_folders()
             del folders[folder_name]
             self.app.set_folders(folders)
             self.app.save_to_file()
             self.refresh_folder_list()

     def add_folder(self):
          folderName = simpledialog.askstring("New Folder", "Folder Name: ", parent=self.app.root)
          if not folderName or not folderName.strip():   # 空值检测
              messagebox.showwarning("Warning", "Folder name cannot be empty.")
              return
          folderName = folderName.strip()

          folders = self.app.get_folders()
          if folderName in folders:   # 重复检测
              messagebox.showerror("Error", "Folder name already exists!")
              return
          
          folders[folderName] = []
          self.app.set_folders(folders)
          self.refresh_folder_list()
          self.app.save_to_file()

     def refresh_folder_list(self, folders = None):
          self.folder_listbox.delete(0, tk.END)
          show_folders = folders if folders is not None else self.app.get_folders()
          for folder in show_folders:
            self.folder_listbox.insert(tk.END, folder)

     def search_folder(self):
          keyword = self.search_entry.get().strip()
          folders = self.app.get_folders()
          if not keyword:
               self.refresh_folder_list()
               return
          result = [f for f in folders if keyword.lower() in f.lower()]
          self.refresh_folder_list(result)

     def enter_folder(self, event):
          selection = self.folder_listbox.curselection()
          if selection:
               folder_name = self.folder_listbox.get(selection[0])
               self.app.set_current_folder(folder_name)
               self.app.note_frame.refresh_note_list()
               self.app.show_note_frame()

#==================== Note Frame =======================#

class NoteFrame(BaseFrame):
     def __init__(self, parent, app):
           super().__init__(parent, app)

           # Set up note management UI inside a folder.
           self.note_title_label = tk.Label(self, text="", font=("Arial", 14, "bold"))
           self.note_title_label.pack(pady=(5, 0))

           # Top_frame
           self.top_note = tk.Frame(self)
           self.top_note.pack(fill="x", pady=(0, 0))

           self.top_note.columnconfigure(0, weight=1)
           self.top_note.columnconfigure(0, weight=1)

           # back button
           self.back_btn = tk.Button(self.top_note, text="← Folders", command=self.app.show_folder_frame)
           self.back_btn.grid(row=0, column=0, sticky="w", padx=(10, 5))

           # add note button
           self.add_note = tk.Button(self.top_note, text="Add Note", command=self.add_note)
           self.add_note.grid(row=0, column=0, sticky="e", padx=(5, 0))

           # delete note button  
           self.delete_note_btn = tk.Button(self.top_note, text="Delete Note", command=self.delete_note)
           self.delete_note_btn.grid(row=0, column=1, sticky="e", padx=(5, 10))

           # Search Bar 
           self.search_entry_note = tk.Entry(self.top_note, font=('Arial', 10))
           self.search_entry_note.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(10, 5))
           # 绑定 KeyRelease 事件，实现实时搜索
           self.search_entry_note.bind("<KeyRelease>", lambda event: self.search_note())

           # Search button
           self.search_button_note = tk.Button(self.top_note, text="Search", command=self.search_note)
           self.search_button_note.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=(10, 5))

           # Note listbox
           self.note_list = tk.Listbox(self, font=('Arial', 10))
           self.note_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
           self.note_list.bind("<Double-Button-1>", self.app.editor_frame.open_note_editor)

           # ==== 右键菜单 ====
           self.note_menu = tk.Menu(self.note_list, tearoff=0)
           self.note_menu.add_command(label="Delete Note", command=self.delete_note)

           # 绑定右键点击事件
           self.note_list.bind("<Button-3>", self.show_note_menu)

     def show_note_menu(self, event):
          try:
              index = self.note_list.nearest(event.y)
              self.note_list.selection_clear(0, tk.END)
              self.note_list.selection_set(index)
              self.note_list.activate(index)
              self.note_menu.tk_popup(event.x_root, event.y_root)
          finally:
              self.note_menu.grab_release()
  
     def delete_note(self):
           selection = self.note_list.curselection()
           if not selection:
               messagebox.showwarning("Delete Note", "Please select a note to delete.")
               return
       
           index = selection[0]
           current_folder = self.app.get_current_folder()
           folders = self.app.get_folders()
           note = folders[current_folder][index]

           confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete note '{note.get_title()}'?")
           if confirm:
               del folders[current_folder][index]
               self.app.set_folders(folders)
               self.app.save_to_file()
               self.refresh_note_list()

     def add_note(self):
          current_folder = self.app.get_current_folder()
          note_title = simpledialog.askstring("New Note", f"Note for {current_folder}:", parent=self.app.root)
          if note_title:
               folders = self.app.get_folders()
               new_note = Note(note_title) 
               folders[current_folder].append(new_note)
               self.app.set_folders(folders)
               self.refresh_note_list()
               self.app.save_to_file()

     def refresh_note_list(self, notes=None, highlight_keyword=None):
          self.note_list.delete(0, tk.END)
          current_folder = self.app.get_current_folder()
          if not current_folder:
              return
          
          folders = self.app.get_folders()
          notes_to_show = notes if notes is not None else folders.get(current_folder, [])
          
          for i, note in enumerate(notes_to_show):
               tags_text = f" [ {' ] [ '.join(note.get_tags())} ]" if note.get_tags() else ""
               display_text = f"{note.get_title()}{tags_text}"  # 确保每次循环都赋值
               self.note_list.insert(tk.END, display_text)
               # 重置背景颜色
               self.note_list.itemconfig(i, {'bg':'SystemWindow'})

                # 高亮整行（Listbox 不支持部分文字高亮）
               if highlight_keyword and highlight_keyword.lower() in display_text.lower():
                   self.note_list.itemconfig(i, {'bg':'yellow'})

     def search_note(self):
          keyword = self.search_entry_note.get().strip().lower()
          current_folder = self.app.get_current_folder()
          if not keyword:
               self.refresh_note_list()
               return
          
          folders = self.app.get_folders()
          all_note = folders.get(current_folder, [])
          result = [note for note in all_note if keyword.lower() in note.get_title().lower() or any(keyword in t.lower() for t in note.get_tags())]
          self.refresh_note_list(result, highlight_keyword=keyword)
                    
#================ editor frame =================#
class EditorFrame(BaseFrame):
    """
    Editor frame for creating and editing notes.
    Provides functionality to add text, images, links, and tags.
    """
    def __init__(self, parent, app):
        super().__init__(parent, app)

        self.tags = []  # list of tags for the current note

        # ===== Top control frame (Back, Save, Tags, Attach Image) ===== #
        self.top_editor_frame = tk.Frame(self)
        self.top_editor_frame.pack(fill="both", pady=(10, 0))

        # Back button to return to note list
        self.back_btn_editor = tk.Button(self.top_editor_frame, text="", command=self.app.show_note_frame)
        self.back_btn_editor.pack(side="left", padx=(10, 0))

        # Save/Done button
        self.save_btn = tk.Button(self.top_editor_frame, text="Save", command=self.save_note_content)
        self.save_btn.pack(side="right", padx=(0, 10))

        # Button to add/edit tags
        self.tag_btn = tk.Button(self.top_editor_frame, text="Add Tags", command=self.edit_tags)
        self.tag_btn.pack(side="left", anchor="w", padx=(10, 0), pady=(5, 5))

        # Button to attach image
        self.attach_image_btn = tk.Button(self.top_editor_frame, text="Attach Image", command=self.attach_image)
        self.attach_image_btn.pack(side="left", padx=(10, 5))

        # ===== Title section ===== #
        title_frame = tk.Frame(self)
        title_frame.pack(fill="x", padx=10, pady=(5, 5))

        title_label = tk.Label(title_frame, text="Title:")
        title_label.pack(side="left", padx=(0, 5))

        self.note_title_var = tk.StringVar()
        self.title_entry = tk.Entry(title_frame, textvariable=self.note_title_var, font=('Arial', 12, 'bold'))
        self.title_entry.pack(side="left", fill="x", expand=True)

        # Main text widget for note content
        self.note_text = tk.Text(self, wrap="word", font=('Arial', 11))
        self.note_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Link style and event binding
        self.note_text.tag_config("link", foreground="blue", underline=True)
        self.note_text.tag_bind("link", "<Button-1>", self._on_link_click)

        # Detect changes to identify links dynamically
        self.note_text.bind("<<Modified>>", self._detect_links)

    def edit_tags(self):
        """ Open dialog to edit tags for the note. """
        current_tags = ", ".join(self.tags) if self.tags else ""
        result = simpledialog.askstring("Add Tags", "Enter tags (comma separated):", initialvalue=current_tags)
        if result is not None:
            # Split by commas and strip spaces
            self.tags = [tag.strip() for tag in result.split(",") if tag.strip()]
            # Update button text to reflect number of tags
            self.tag_btn.config(text=f"Add Tags ({len(self.tags)})")

    def attach_image(self):
        """ Allow user to select and attach an image into the note. """
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if not file_path:
            return
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Invalid image file or path.")
            return

        try:
            # Load and resize image
            img = Image.open(file_path)
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            return

        # Ensure image references are kept to avoid garbage collection
        if not hasattr(self.note_text, "image_refs"):
            self.note_text.image_refs = []
        self.note_text.image_refs.append(photo)

        # Map image object name to file path for saving
        if not hasattr(self.note_text, "image_name_to_path"):
            self.note_text.image_name_to_path = {}
        self.note_text.image_name_to_path[str(photo)] = file_path

        # Insert image at current cursor position
        self.note_text.image_create(tk.INSERT, image=photo)

    def _detect_links(self, event=None):
        """ Detect and highlight URLs in the note text. """
        self.note_text.tag_remove("link", "1.0", tk.END)
        url_pattern = re.compile(r"https?://[^\s]+")

        line_index = 1
        while True:
            line_start = f"{line_index}.0"
            line_end = f"{line_index}.end"
            if self.note_text.compare(line_start, ">=", tk.END):
                break

            line_text = self.note_text.get(line_start, line_end)
            for match in url_pattern.finditer(line_text):
                start = f"{line_index}.{match.start()}"
                end = f"{line_index}.{match.end()}"
                self.note_text.tag_add("link", start, end)

            line_index += 1

        # Reset modified flag
        self.note_text.edit_modified(False)

    def _on_link_click(self, event):
        """ Open clicked link in the default web browser. """
        index = self.note_text.index(f"@{event.x},{event.y}")
        ranges = self.note_text.tag_prevrange("link", index + "+1c")
        if ranges:
            url = self.note_text.get(ranges[0], ranges[1])
            try:
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open link: {e}")

    def open_note_editor(self, event):
        """ Open selected note for editing. """
        selection = self.app.note_frame.note_list.curselection()
        if not selection:
            return

        index = selection[0]
        self.app.set_current_note_index(index)

        current_folder = self.app.get_current_folder()
        folders = self.app.get_folders()
        note = folders[current_folder][index]

        # Switch to editor view first (important for tag rendering)
        self.app.show_editor_frame()

        self.note_title_var.set(note.get_title())
        self.note_text.delete("1.0", tk.END)

        # Prepare references for images
        self.note_text.image_refs = []
        self.note_text.image_name_to_path = {}

         # 插入笔记内容
        for block in note.get_content_blocks():
            if block['type'] == "text":
                # Insert content depending on note type
                self.note_text.insert(tk.END, block['content'])

            elif block['type'] == "image":
                 if os.path.exists(block['path']):
                     try:
                         img = Image.open(block['path'])
                         img.thumbnail((300, 300))
                         photo = ImageTk.PhotoImage(img)
                         self.note_text.image_refs.append(photo)
                         self.note_text.image_name_to_path[str(photo)] = block['path']
                         self.note_text.image_create(tk.END, image=photo)
                     except Exception as e:
                         self.note_text.insert(tk.END, f"[Error loading image: {e}]")
                 else:
                       self.note_text.insert(tk.END, f"[Image not found: {block['path']}]")

            elif block['type'] == "link":
                self.link = note.get_link()
                start_index = self.note_text.index(tk.END)
                self.note_text.insert(tk.END, self.link)
                end_index = self.note_text.index(tk.END)
                self.note_text.tag_add("link", start_index, end_index)
                self.note_text.tag_bind("link", "<Button-1>", self._on_link_click)

            # Load existing tags for note
            self.tags = note.get_tags()
            self.tag_btn.config(text=f"Add Tags ({len(self.tags)})" if self.tags else "Add Tags")
        
            # Re-detect links after loading
            self._detect_links()

    def save_note_content(self):
        """ Save the current note content and metadata back to storage. """
        current_folder = self.app.get_current_folder()
        current_note_index = self.app.get_current_note_index()
        if current_folder is None or current_note_index is None:
            return

        folders = self.app.get_folders()
        note = folders[current_folder][current_note_index]
        note.set_title(self.note_title_var.get())

        if isinstance(note, Note):
            # Build content blocks from text widget dump
            blocks = []
            for kind, value, index in self.note_text.dump("1.0", "end-1c", text=True, image=True, tag=True):
                if kind == "text" and value:
                    blocks.append({"type": "text", "content": value})
                elif kind == "image":
                    path = getattr(self.note_text, "image_name_to_path", {}).get(value)
                    if path:
                        blocks.append({"type": "image", "path": path})
                elif kind == "tagon" and value == "link":
                    url = self.note_text.get(index, f"{index} lineend").strip()
                    if url.startswith("http"):
                        blocks.append({"type": "link", "url": url})

        # Save content blocks and tags
        note.set_content_blocks(blocks)
        self.app.set_folders(folders)
        note.set_tags(self.tags)
        self.app.save_to_file()
        self.app.note_frame.refresh_note_list()
        self.app.show_note_frame()

NoteApp()

