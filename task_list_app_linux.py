#!/usr/bin/python

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk, Listbox, scrolledtext
import datetime
import webbrowser

tasks = []
completed_status = []
deleted_items = []
restored_items = []  
temp_restored_items = []

deleted_items_text = None

CREATED_BG_COLOR = '#d0e1e1'
MODIFIED_BG_COLOR = '#b3c6ff'
DELETED_BG_COLOR = '#ff9999'  
COMPLETED_BG_COLOR = "#9fff80"
    
def add_task():
    task = task_entry.get()  # Ottieni il testo dall'Entry
    if task:
        now = datetime.datetime.now()
        task_with_status = f"{task}   (Created: {now.strftime('%Y-%m-%d %H:%M:%S')})"
        tasks.append(task_with_status)
        completed_status.append(False)  
        update_listbox()
        task_entry.delete(0, tk.END)  
        save_tasks() 
    else:
        messagebox.showwarning("Warning", "Please enter a task.")

def disable_paste(event):
    messagebox.showwarning("Warning", "Paste function is disabled.")
    return "break"

def edit_task():
    selected_index = task_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Warning", "Select a task to edit.")
        return

    index = selected_index[0]

    if index < len(tasks):
        selected_text = task_listbox.get(index)
        if "Completed" not in selected_text:
            edited_text = simpledialog.askstring("Edit Task", "Edit task:", initialvalue=selected_text.split('(Created:')[0].strip())

            if edited_text is not None:
                now = datetime.datetime.now()
                modified_text = f"{edited_text} (Created:{selected_text.split('(Created:')[1].strip()}  (Modified: {now.strftime('%Y-%m-%d %H:%M:%S')})"
                tasks[index] = modified_text

                update_listbox()
                save_tasks()

                task_listbox.itemconfig(index, {'bg': MODIFIED_BG_COLOR})  
        else:
            messagebox.showwarning("Warning", "Task is already completed and cannot be edited.")


def delete_task():
    selected_index = task_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Warning", "Select a task to delete.")
        return

    confirm = messagebox.askyesno("Info", "Are you sure you want to delete this task?")
    if confirm:
        deleted_item = tasks.pop(selected_index[0])
        now = datetime.datetime.now()
        deleted_items.append(f"{deleted_item}   (Deleted: {now.strftime('%Y-%m-%d %H:%M:%S')})")
        update_listbox()
        save_tasks()
        save_deleted_items()

def mark_task():
    selected_index = task_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Warning", "Select a task to mark as completed.")
        return

    index = selected_index[0]

    if index < len(tasks):
        selected_text = task_listbox.get(index)
        if "Completed" not in selected_text:
            now = datetime.datetime.now()
            modified_text = f"{selected_text}  (Completed: {now.strftime('%Y-%m-%d %H:%M:%S')})"
            tasks[index] = modified_text
            update_listbox()
            save_tasks()
        else:
            messagebox.showwarning("Warning", "Task is already completed.")

def preview_tasks():
    if task_listbox.size() == 0:
        messagebox.showwarning("Warning", "The task list is empty.")
        return

    preview_window = tk.Toplevel(window)
    preview_window.title("Preview")
    preview_window.geometry("900x700+500+150")
    preview_text = tk.Text(preview_window, wrap=tk.WORD)
    preview_text.pack(fill=tk.BOTH, expand=True)

    for i in range(task_listbox.size()):
        selected_text = task_listbox.get(i)
        preview_text.insert(tk.END, selected_text + "\n")

def preview_deleted_items():
    global deleted_items_text
    if not deleted_items:
        messagebox.showwarning("Warning", "The deleted list is empty.")
        return
    deleted_items_window = tk.Toplevel(window)
    deleted_items_window.title("Deleted Items")
    deleted_items_window.geometry("800x790+550+200")
    deleted_items_window.resizable(False, False)
    deleted_items_window.configure(background="#bfbfbf")
    deleted_items_window.columnconfigure(0, weight=1)

    deleted_items_text = tk.Listbox(deleted_items_window, height=30)
    deleted_items_text.grid(row=0, column=0, padx=10, pady=1, sticky="NSEW")

    deleted_items_scrollbar_x = ttk.Scrollbar(deleted_items_window, orient="horizontal", command=deleted_items_text.xview)
    deleted_items_scrollbar_x.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="EW")
    deleted_items_text.configure(xscrollcommand=deleted_items_scrollbar_x.set)

    deleted_items_scrollbar_y = ttk.Scrollbar(deleted_items_window, orient="vertical", command=deleted_items_text.yview)
    deleted_items_scrollbar_y.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="NS")
    deleted_items_text.configure(yscrollcommand=deleted_items_scrollbar_y.set)

    update_deleted_items_listbox()

    restore_button = tk.Button(deleted_items_window, text="Restore", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=restore_deleted_items)
    restore_button.grid(row=2, column=0, padx=10, pady=5, sticky="WE")

    restore_all_button = tk.Button(deleted_items_window, text="Restore all", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=restore_all_deleted_items)
    restore_all_button.grid(row=3, column=0, padx=10, pady=5, sticky="WE")

    delete_definitely_button = tk.Button(deleted_items_window, text="Delete definitely items", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=delete_definitely_items)
    delete_definitely_button.grid(row=4, column=0, padx=10, pady=5, sticky="WE")

    reset_list_button = tk.Button(deleted_items_window, text="Reset List", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=reset_deleted_items)
    reset_list_button.grid(row=5, column=0, padx=10, pady=5, sticky="WE")

def saved_tasks():
    if not tasks:
        messagebox.showwarning("Warning", "The task list is empty. Cannot save an empty list.")
        return

    percorso_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("File di testo", "*.txt")])
    if percorso_file:
        try:
            with open(percorso_file, "w", encoding="utf-8") as file:
                for attività in tasks:
                    if "Completed" in attività:
                        if attività.startswith("• "):
                            attività = attività[2:]
                        file.write("• " + attività + "\n")
                    elif "Modified" in attività:                     
                        if "Completed" in attività:
                            if attività.startswith("• "):
                                attività = attività[2:]
                            file.write(attività + "\n")
                        else:
                            if not attività.startswith("• "):
                                attività = "• " + attività
                            file.write(attività + "\n")
                    else:
                        if not attività.startswith("• "):
                            attività = "• " + attività
                        file.write(attività + "\n")
        except Exception as e:
            messagebox.showerror("Errore", f"Si è verificato un errore: {str(e)}")

def update_listbox():
    task_listbox.delete(0, tk.END)
    for task in tasks:
        formatted_task = task
        if not formatted_task.startswith("• "):
            formatted_task = "• " + formatted_task
        task_listbox.insert(tk.END, formatted_task)
        if "Completed" in task:
            task_listbox.itemconfig(tk.END, {'bg': COMPLETED_BG_COLOR})
        elif "Modified" in task:
            task_listbox.itemconfig(tk.END, {'bg': MODIFIED_BG_COLOR})
        elif "Created" in task:
            task_listbox.itemconfig(tk.END, {'bg': CREATED_BG_COLOR})

def save_tasks():
    with open("tasks.txt", "w") as file:
        for task in tasks:
            file.write(task + "\n")

def save_deleted_items():
    with open("deleted_items.txt", "w") as file:
        for deleted_item in deleted_items:
            file.write(deleted_item + "\n")

def save_restored_items():
    with open("restored_items.txt", "w") as file:
        for restored_item in restored_items:
            file.write(restored_item + "\n")

def load_tasks():
    try:
        with open("tasks.txt", "r") as file:
            global tasks
            tasks.clear() 
            for line in file:
                tasks.append(line.strip()) 
        update_listbox() 
    except FileNotFoundError:
        pass

def load_deleted_items():
    try:
        with open("deleted_items.txt", "r") as file:
            deleted_items.extend(file.read().splitlines())
    except FileNotFoundError:
        pass

def load_restored_items():
    try:
        with open("restored_items.txt", "r") as file:
            restored_items.extend(file.read().splitlines())
    except FileNotFoundError:
        pass

def delete_list_all():
    global tasks
    global deleted_items

    if not tasks:
        messagebox.showwarning("Warning", "The task list is empty.")
        return

    confirm = messagebox.askyesno("Info", "Are you sure you want to delete all deleted items? These items will go into the deleted items file to be recovered later")

    if confirm:
        for task in tasks:
            now = datetime.datetime.now()
            deleted_items.append(f"{task}   (Deleted: {now.strftime('%Y-%m-%d %H:%M:%S')})")

        tasks = [] 
        update_listbox()  
        save_tasks() 
        save_deleted_items() 

def reset_deleted_items():
    global deleted_items
    confirm = messagebox.askyesno("Info", "Are you sure you want to delete all deleted items permanently?")
    if confirm:
        deleted_items = []  
        save_deleted_items() 
        update_deleted_items_listbox() 

def restore_all_deleted_items():
    global tasks
    global deleted_items

    confirm = messagebox.askyesno("Info", "Are you sure you want to restore all deleted items?")

    if confirm:
        for deleted_item in deleted_items:
            now = datetime.datetime.now()
            restored_item = f"{deleted_item}   (Restored: {now.strftime('%Y-%m-%d %H:%M:%S')})"
            tasks.append(restored_item)
        deleted_items.clear() 
        update_listbox()  
        save_tasks() 
        save_deleted_items() 
        update_deleted_items_listbox()

def restore_deleted_items():
    global deleted_items_text
    selected_indices = deleted_items_text.curselection()
    if not selected_indices:
        messagebox.showwarning("Warning", "Select deleted items to restore.")
        return

    for index in selected_indices:
        index = int(index)
        if index < len(deleted_items):
            restored_item = deleted_items.pop(index)
            if restored_item not in restored_items:
                restored_items.append(restored_item) 
            now = datetime.datetime.now()
            item_with_status = f"{restored_item}   (Restored: {now.strftime('%Y-%m-%d %H:%M:%S')})"
            tasks.append(item_with_status)
            update_listbox()
            save_tasks()
            update_deleted_items_listbox()
            save_deleted_items()
            save_restored_items()  

def delete_definitely_items():
    global deleted_items_text
    selected_indices = deleted_items_text.curselection()
    if not selected_indices:
        messagebox.showwarning("Warning", "Select deleted items to delete definitely.")
        return

    confirmed = messagebox.askyesno("Info", "Are you sure you want to delete these items permanently?")
    if not confirmed:
        return

    selected_indices = list(selected_indices)
    selected_indices.sort(reverse=True)

    for index in selected_indices:
        index = int(index)
        if index < len(deleted_items):
            deleted_items.pop(index)

    save_deleted_items()
    update_deleted_items_listbox()
    restored_items.clear()

def update_deleted_items_listbox():
    global deleted_items_text
    deleted_items_text.delete(0, tk.END)
    for deleted_item in deleted_items:
        if not deleted_item.startswith("• "):
            deleted_item = f"• {deleted_item}"
        if "Completed" in deleted_item:
            deleted_item = deleted_item.replace("••", "•")
        elif "Modified" in deleted_item:
            deleted_item = deleted_item.replace("••", "•")
        deleted_items_text.insert(tk.END, deleted_item)
        if "Deleted" in deleted_item:
            deleted_items_text.itemconfig(tk.END, {'bg': DELETED_BG_COLOR})

def get_index_of_item(item, item_list):
    for index, list_item in enumerate(item_list):
        if item in list_item:
            return index
    return None

def on_enter(event):
    event.widget.config(fg="#FF0000")  

def on_leave(event):
    event.widget.config(fg="#000000")  

def open_disclaimer():
    disclaimer_window = tk.Toplevel(window)
    disclaimer_window.title("Disclaimer")
    disclaimer_window.geometry("450x350+550+220")
    disclaimer_window.resizable(False, False)
    disclaimer_window.configure(background="#bfbfbf")
    disclaimer_window.grid_columnconfigure(0, weight=1)
    disclaimer_window.grid_rowconfigure(0, weight=1)

    frame = tk.Frame(disclaimer_window, bg="#bfbfbf")
    frame.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")

    disclaimer_text = """
    Il mondo è di tutti e ogni individuo è libero.
    Ognuno deve avere il diritto di informarsi liberamente con
    coscienza e intelligenza.
    Siate sempre umili e siate sempre aperti con la mente
    e continuate a sognare...sempre
    ---------------------------------------------
    The world belongs to everyone and every individual is free.
    Everyone must have the right to freely inform themselves with
    consciousness and intelligence.
    Always be humble and always be open minded
    and keep dreaming...always

    contacts:
    email: accybertech@outlook.it\n
    my site:
    www.accybertech.it
    """

    label = tk.Label(frame, text=disclaimer_text, bg="#bfbfbf", justify="left", wraplength=450, padx=10, pady=10)
    label.pack(fill="both", expand=True)

    manifesto_link = tk.Label(disclaimer_window, text="read our manifesto", font=("Helvetica", 12, "bold"), bg="#bfbfbf", cursor="hand2")
    manifesto_link.grid(row=1, column=0, padx=40, pady=(0, 5), sticky="S")
    manifesto_link.bind("<Button-1>", lambda event: open_manifesto())

def open_email():
    webbrowser.open("mailto:accybertech@outlook.it")

def open_disclaimer_wrapper(event):
    open_disclaimer()

def open_email_wrapper(event):
    open_email()

def open_site():
    webbrowser.open("https://www.accybertech.it")

def open_manifesto():
    webbrowser.open("https://www.accybertech.it/manifesto")

def open_condizioni():
    webbrowser.open("https://www.accybertech.it/task-list-app")

window = tk.Tk()
window.geometry("800x790+500+120")
window.title("task list")
window.resizable(False, False)
window.configure(background="#bfbfbf")
window.grid_columnconfigure(0, weight=1)

welcome_label = tk.Label(window, text="enter text to add to the list:", font=("Helvetica", 15), bg="#bfbfbf")
welcome_label.grid(row=0, column=0, sticky="N", padx=20, pady=(10, 1))

task_entry = tk.Entry()
task_entry.grid(row=1, column=0, padx=(30, 5), pady=10, sticky="WE")
task_entry.bind("<Control-v>", disable_paste)

add_button = tk.Button(text="add Task", fg="#0a1010", bg="#d0e1e1",cursor="hand2", command=add_task)
add_button.grid(row=2, column=0, padx=(30, 5), pady=(2, 5), sticky="WE")

task_listbox = tk.Listbox(window, height=20)
task_listbox.grid(row=3, column=0, sticky="WE", padx=(30, 5), pady=5)

task_scrollbar_x = ttk.Scrollbar(window, orient="horizontal", command=task_listbox.xview)
task_scrollbar_x.grid(row=4, column=0, padx=(30, 8), pady=(0, 0), sticky="WE")
task_listbox.configure(xscrollcommand=task_scrollbar_x.set)

task_scrollbar_y = ttk.Scrollbar(window, orient="vertical", command=task_listbox.yview)
task_scrollbar_y.grid(row=3, column=1, padx=(1, 8), pady=5, sticky="NS")
task_listbox.configure(yscrollcommand=task_scrollbar_y.set)

edit_button = tk.Button(text="Edit", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=edit_task)
edit_button.grid(row=5, column=0, sticky="WE", padx=(30, 5), pady=(7, 1))

delete_button = tk.Button(text="Delete", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=delete_task)
delete_button.grid(row=6, column=0, sticky="WE", padx=(30, 5), pady=1)

mark_button = tk.Button(text="Mark", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=mark_task)
mark_button.grid(row=7, column=0, sticky="WE", padx=(30, 5), pady=1)

preview_button = tk.Button(text="Preview", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=preview_tasks)
preview_button.grid(row=8, column=0, sticky="WE", padx=(30, 5), pady=1)

print_button = tk.Button(text="Save", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=saved_tasks)
print_button.grid(row=9, column=0, sticky="WE", padx=(30, 5), pady=1)

delete_list_button = tk.Button(text="Show deleted List", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=preview_deleted_items)
delete_list_button.grid(row=10, column=0, sticky="WE", padx=(30, 5), pady=1)

delete_list_button = tk.Button(text="Cancel all List", fg="#0a1010", bg="#d0e1e1", cursor="hand2", command=delete_list_all)
delete_list_button.grid(row=11, column=0, sticky="WE", padx=(30, 5), pady=1)

empty_Label = tk.Label(bg="#bfbfbf")
empty_Label.grid(row=12, column=0, padx=10, pady=0, sticky="EW")

accybertech_link = tk.Label(window, text="accybertech.it", font=("Helvetica", 12, "bold"), bg="#bfbfbf", cursor="hand2")
accybertech_link.grid(row=13, column=0, padx=(250, 10), pady=(0, 10), sticky="WS")
accybertech_link.bind("<Button-1>", lambda event: open_site())

disclaimer_link = tk.Label(window, text="Disclaimer", fg="#000000", cursor="hand2", bg="#bfbfbf", font=("Helvetica", 10))
disclaimer_link.grid(row=13, column=0, padx=(370, 10),pady=(0, 12), sticky="WS")
disclaimer_link.bind("<Button-1>", lambda event: open_disclaimer())

email_link = tk.Label(window, text="Email", fg="#000000", cursor="hand2", bg="#bfbfbf", font=("Helvetica", 10))
email_link.grid(row=13, column=0, padx=(437, 10),pady=(0, 12), sticky="WS")
email_link.bind("<Button-1>", lambda event: open_email())

condizioni_link = tk.Label(window, text="Conditions", fg="#000000", cursor="hand2", bg="#bfbfbf", font=("Helvetica", 10))
condizioni_link.grid(row=13, column=0, padx=(476, 10),pady=(0, 12), sticky="WS")
condizioni_link.bind("<Button-1>", lambda event: open_condizioni())

disclaimer_link.bind("<Enter>", on_enter)
disclaimer_link.bind("<Leave>", on_leave)
disclaimer_link.bind("<Button-1>", lambda event: open_disclaimer())

email_link.bind("<Enter>", on_enter)
email_link.bind("<Leave>", on_leave)
email_link.bind("<Button-1>", lambda event: open_email())

condizioni_link.bind("<Enter>", on_enter)
condizioni_link.bind("<Leave>", on_leave)
condizioni_link.bind("<Button-1>", lambda event: open_condizioni())

load_tasks()
load_deleted_items()
load_restored_items()
update_listbox()
window.mainloop()
