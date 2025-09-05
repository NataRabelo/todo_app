import customtkinter as ctk
import json
import os
from tkinter import messagebox
from datetime import datetime, date

# --- Configurações da Aplicação ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
FILENAME = "tasks_v2.json"

class Task:
    """
    Representa uma única tarefa com todos os seus atributos.
    """
    def __init__(self, title, description, priority="Média", due_date=None, category="Geral", is_completed=False):
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.category = category
        self.is_completed = is_completed

    def to_dict(self):
        """Converte o objeto Task para um dicionário para serialização JSON."""
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "category": self.category,
            "is_completed": self.is_completed
        }

    @staticmethod
    def from_dict(data):
        """Cria um objeto Task a partir de um dicionário."""
        return Task(
            data["title"],
            data["description"],
            data.get("priority", "Média"),
            data.get("due_date"),
            data.get("category", "Geral"),
            data["is_completed"]
        )

class TaskManager:
    """
    Gerencia a lógica de negócios e a persistência das tarefas.
    """
    def __init__(self, filename=FILENAME):
        self.filename = filename
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """Carrega as tarefas do arquivo JSON."""
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, IOError):
            return []

    def save_tasks(self):
        """Salva a lista atual de tarefas no arquivo JSON."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4, ensure_ascii=False)

    def add_task(self, title, description, priority, due_date, category):
        """Adiciona uma nova tarefa."""
        if title:
            task = Task(title, description, priority, due_date, category)
            self.tasks.append(task)
            return task
        return None
    
    def update_task(self, task, new_title, new_desc, new_priority, new_due_date, new_category):
        """Atualiza os dados de uma tarefa existente."""
        task.title = new_title
        task.description = new_desc
        task.priority = new_priority
        task.due_date = new_due_date
        task.category = new_category

    def delete_task(self, task_to_delete):
        """Remove uma tarefa da lista."""
        self.tasks.remove(task_to_delete)

    def toggle_task_completion(self, task_to_toggle):
        """Alterna o estado de 'concluída' de uma tarefa."""
        task_to_toggle.is_completed = not task_to_toggle.is_completed

    def get_all_categories(self):
        """Retorna uma lista de todas as categorias únicas."""
        categories = {"Geral"} # Garante que "Geral" sempre exista
        for task in self.tasks:
            categories.add(task.category)
        return sorted(list(categories))


class App(ctk.CTk):
    """
    Classe principal da aplicação que gerencia a interface gráfica.
    """
    def __init__(self, task_manager):
        super().__init__()
        self.task_manager = task_manager
        self.current_filter = "Todas"

        # --- Configurações da Janela Principal ---
        self.title("Gerenciador de Tarefas Avançado")
        self.geometry("1100x700")
        self.minsize(800, 500)

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1, minsize=300)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- Frames ---
        self.input_frame = self._create_input_frame()
        self.tasks_frame = self._create_tasks_display_frame()

        # --- Inicialização ---
        self.refresh_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_input_frame(self):
        """Cria o painel esquerdo para adicionar novas tarefas."""
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(frame, text="Nova Tarefa", font=ctk.CTkFont(size=20, weight="bold")).pack(padx=20, pady=(20, 10), anchor="w")
        
        self.title_entry = ctk.CTkEntry(frame, placeholder_text="Título da tarefa")
        self.title_entry.pack(fill="x", padx=20, pady=5)
        
        self.desc_textbox = ctk.CTkTextbox(frame, height=120)
        self.desc_textbox.pack(fill="x", padx=20, pady=5)
        self.desc_textbox.insert("0.0", "Descrição...")
        
        ctk.CTkLabel(frame, text="Prioridade:").pack(padx=20, pady=(10, 0), anchor="w")
        self.priority_menu = ctk.CTkComboBox(frame, values=["Baixa", "Média", "Alta"])
        self.priority_menu.set("Média")
        self.priority_menu.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(frame, text="Data de Vencimento (AAAA-MM-DD):").pack(padx=20, pady=(10, 0), anchor="w")
        self.due_date_entry = ctk.CTkEntry(frame, placeholder_text="Opcional")
        self.due_date_entry.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(frame, text="Categoria:").pack(padx=20, pady=(10, 0), anchor="w")
        self.category_entry = ctk.CTkEntry(frame, placeholder_text="Ex: Trabalho, Pessoal")
        self.category_entry.pack(fill="x", padx=20, pady=5)

        add_button = ctk.CTkButton(frame, text="Adicionar Tarefa", command=self.add_task_callback)
        add_button.pack(padx=20, pady=20, fill="x")

        return frame

    def _create_tasks_display_frame(self):
        """Cria o painel direito para listar as tarefas."""
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header_frame, text="Minhas Tarefas", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(header_frame, text="Filtrar por Categoria:").grid(row=1, column=0, pady=(10,0), sticky="w")
        self.filter_menu = ctk.CTkComboBox(header_frame, command=self.filter_tasks_callback)
        self.filter_menu.grid(row=2, column=0, sticky="w")
        
        self.scrollable_frame = ctk.CTkScrollableFrame(frame, label_text="")
        self.scrollable_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        return frame

    def refresh_ui(self):
        """Atualiza a interface por completo: lista de tarefas e filtro de categorias."""
        self.update_category_filter()
        self.refresh_tasks_display()

    def update_category_filter(self):
        """Atualiza as opções do menu de filtro de categorias."""
        categories = ["Todas"] + self.task_manager.get_all_categories()
        self.filter_menu.configure(values=categories)
        if self.current_filter not in categories:
            self.current_filter = "Todas"
        self.filter_menu.set(self.current_filter)

    def refresh_tasks_display(self):
        """Limpa e recria os widgets de tarefa na tela com base nos dados e no filtro."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        tasks_to_show = self.task_manager.tasks
        if self.current_filter != "Todas":
            tasks_to_show = [task for task in tasks_to_show if task.category == self.current_filter]

        # Ordenar: tarefas não concluídas primeiro
        sorted_tasks = sorted(tasks_to_show, key=lambda t: t.is_completed)

        for task in sorted_tasks:
            self.create_task_widget(task)

    def create_task_widget(self, task):
        """Cria um widget individual para uma tarefa."""
        PRIORITY_COLORS = {"Alta": "#D32F2F", "Média": "#FFA000", "Baixa": "#1976D2"}
        task_frame = ctk.CTkFrame(self.scrollable_frame)
        task_frame.pack(fill="x", padx=5, pady=5)
        task_frame.grid_columnconfigure(1, weight=1)

        # Indicador de Prioridade
        priority_indicator = ctk.CTkFrame(task_frame, width=10, fg_color=PRIORITY_COLORS.get(task.priority, "grey"))
        priority_indicator.grid(row=0, column=0, rowspan=3, sticky="ns", padx=(5,0), pady=5)

        # Checkbox e Título
        check_var = ctk.StringVar(value="on" if task.is_completed else "off")
        font_style = ctk.CTkFont(size=14, weight="bold", slant="italic" if task.is_completed else "roman")
        checkbox = ctk.CTkCheckBox(
            task_frame, text=task.title, variable=check_var, font=font_style,
            command=lambda t=task: self.toggle_complete_callback(t)
        )
        checkbox.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")
        
        # Descrição
        if task.description:
            desc_label = ctk.CTkLabel(task_frame, text=task.description, wraplength=500, justify="left", font=ctk.CTkFont(size=12))
            desc_label.grid(row=1, column=1, padx=20, pady=(0, 5), sticky="w")

        # Info: Categoria, Data de Vencimento
        info_text = f"Categoria: {task.category}"
        due_date_str = ""
        is_overdue = False
        if task.due_date:
            try:
                due_date_obj = date.fromisoformat(task.due_date)
                due_date_str = due_date_obj.strftime("%d/%m/%Y")
                if not task.is_completed and due_date_obj < date.today():
                    is_overdue = True
                info_text += f"  |  Vencimento: {due_date_str}"
            except (ValueError, TypeError):
                pass # Data inválida, ignora
        
        info_label = ctk.CTkLabel(task_frame, text=info_text, font=ctk.CTkFont(size=11), text_color="gray50")
        info_label.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="w")
        
        # Botões de Ação
        action_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        action_frame.grid(row=0, column=2, rowspan=3, padx=10)
        
        edit_button = ctk.CTkButton(action_frame, text="Editar", width=60, command=lambda t=task: self.open_edit_window(t))
        edit_button.pack(pady=2)
        delete_button = ctk.CTkButton(action_frame, text="Excluir", width=60, fg_color="#D32F2F", hover_color="#B71C1C", command=lambda t=task: self.delete_task_callback(t))
        delete_button.pack(pady=2)
        
        # Destaques visuais
        if task.is_completed:
            checkbox.configure(text_color="gray")
        if is_overdue:
            task_frame.configure(border_width=2, border_color="#D32F2F")
            info_label.configure(text_color="#D32F2F", font=ctk.CTkFont(size=11, weight="bold"))

    def add_task_callback(self):
        """Callback para o botão de adicionar tarefa."""
        title = self.title_entry.get().strip()
        description = self.desc_textbox.get("1.0", "end-1c").strip()
        priority = self.priority_menu.get()
        due_date = self.due_date_entry.get().strip() or None
        category = self.category_entry.get().strip() or "Geral"

        if not title:
            messagebox.showwarning("Campo Vazio", "O título da tarefa é obrigatório.")
            return

        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Formato Inválido", "A data deve estar no formato AAAA-MM-DD.")
                return

        self.task_manager.add_task(title, description, priority, due_date, category)
        self.refresh_ui()
        
        # Limpar campos
        self.title_entry.delete(0, "end")
        self.desc_textbox.delete("1.0", "end")
        self.due_date_entry.delete(0, "end")
        self.category_entry.delete(0, "end")
        self.title_entry.focus()
        
    def delete_task_callback(self, task):
        """Callback para o botão de excluir tarefa."""
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a tarefa '{task.title}'?"):
            self.task_manager.delete_task(task)
            self.refresh_ui()

    def toggle_complete_callback(self, task):
        """Callback para o checkbox de conclusão da tarefa."""
        self.task_manager.toggle_task_completion(task)
        self.refresh_tasks_display()
    
    def filter_tasks_callback(self, selected_category):
        """Callback para o menu de filtro."""
        self.current_filter = selected_category
        self.refresh_tasks_display()

    def open_edit_window(self, task):
        """Abre uma nova janela para editar uma tarefa."""
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Editar Tarefa")
        edit_window.geometry("400x450")
        edit_window.transient(self) # Mantém a janela no topo
        edit_window.grab_set() # Bloqueia interação com a janela principal
        
        ctk.CTkLabel(edit_window, text="Título:").pack(padx=20, pady=(10,0), anchor="w")
        title_entry = ctk.CTkEntry(edit_window)
        title_entry.pack(fill="x", padx=20, pady=5)
        title_entry.insert(0, task.title)
        
        ctk.CTkLabel(edit_window, text="Descrição:").pack(padx=20, pady=(10,0), anchor="w")
        desc_box = ctk.CTkTextbox(edit_window, height=100)
        desc_box.pack(fill="x", padx=20, pady=5)
        desc_box.insert("0.0", task.description)

        ctk.CTkLabel(edit_window, text="Prioridade:").pack(padx=20, pady=(10,0), anchor="w")
        priority_menu = ctk.CTkComboBox(edit_window, values=["Baixa", "Média", "Alta"])
        priority_menu.set(task.priority)
        priority_menu.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(edit_window, text="Data de Vencimento (AAAA-MM-DD):").pack(padx=20, pady=(10,0), anchor="w")
        due_date_entry = ctk.CTkEntry(edit_window)
        due_date_entry.pack(fill="x", padx=20, pady=5)
        if task.due_date:
            due_date_entry.insert(0, task.due_date)

        ctk.CTkLabel(edit_window, text="Categoria:").pack(padx=20, pady=(10,0), anchor="w")
        category_entry = ctk.CTkEntry(edit_window)
        category_entry.pack(fill="x", padx=20, pady=5)
        category_entry.insert(0, task.category)

        def save_changes():
            new_title = title_entry.get().strip()
            new_desc = desc_box.get("1.0", "end-1c").strip()
            new_priority = priority_menu.get()
            new_due_date = due_date_entry.get().strip() or None
            new_category = category_entry.get().strip() or "Geral"

            if not new_title:
                messagebox.showerror("Erro", "O título não pode ficar vazio.", parent=edit_window)
                return
            
            self.task_manager.update_task(task, new_title, new_desc, new_priority, new_due_date, new_category)
            edit_window.destroy()
            self.refresh_ui()

        save_button = ctk.CTkButton(edit_window, text="Salvar Alterações", command=save_changes)
        save_button.pack(padx=20, pady=20)


    def on_closing(self):
        """Salva as tarefas antes de fechar a aplicação."""
        self.task_manager.save_tasks()
        self.destroy()

# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    task_manager = TaskManager()
    app = App(task_manager)
    app.mainloop()