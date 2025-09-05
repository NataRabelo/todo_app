import customtkinter as ctk
import json
import os
from tkinter import messagebox

# Define o tema e as cores do aplicativo
ctk.set_appearance_mode("System")  # Pode ser "Light", "Dark"
ctk.set_default_color_theme("blue") # Tema de cor padrão

class Task:
    """
    Representa uma única tarefa com título, descrição e estado de conclusão.
    """
    def __init__(self, title, description, is_completed=False):
        self.title = title
        self.description = description
        self.is_completed = is_completed

    def to_dict(self):
        """Converte o objeto Task para um dicionário para serialização JSON."""
        return {
            "title": self.title,
            "description": self.description,
            "is_completed": self.is_completed
        }

    @staticmethod
    def from_dict(data):
        """Cria um objeto Task a partir de um dicionário."""
        return Task(data["title"], data["description"], data["is_completed"])

class TaskManager:
    """
    Gerencia a lógica de adicionar, remover, atualizar e persistir tarefas.
    """
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """Carrega as tarefas do arquivo JSON. Se o arquivo não existir, retorna uma lista vazia."""
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

    def add_task(self, title, description):
        """Adiciona uma nova tarefa à lista."""
        if title:
            new_task = Task(title, description)
            self.tasks.append(new_task)
            return new_task
        return None

    def delete_task(self, task_to_delete):
        """Remove uma tarefa da lista."""
        self.tasks = [task for task in self.tasks if task is not task_to_delete]

    def toggle_task_completion(self, task_to_toggle):
        """Alterna o estado de 'concluída' de uma tarefa."""
        task_to_toggle.is_completed = not task_to_toggle.is_completed


class App(ctk.CTk):
    """
    Classe principal da aplicação que gerencia a interface gráfica.
    """
    def __init__(self, task_manager):
        super().__init__()
        self.task_manager = task_manager

        # --- Configurações da Janela Principal ---
        self.title("Gerenciador de Tarefas")
        self.geometry("900x600")
        self.minsize(700, 450)

        # --- Configuração do Grid Layout ---
        self.grid_columnconfigure(0, weight=1, minsize=250) # Coluna de entrada
        self.grid_columnconfigure(1, weight=3)             # Coluna da lista de tarefas
        self.grid_rowconfigure(0, weight=1)

        # --- Frames ---
        self.input_frame = self._create_input_frame()
        self.tasks_frame = self._create_tasks_display_frame()

        # --- Inicialização ---
        self.refresh_tasks_display()
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Salvar ao fechar

    def _create_input_frame(self):
        """Cria o painel esquerdo para adicionar novas tarefas."""
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        frame.grid_rowconfigure(4, weight=1)

        # Título do Painel
        label = ctk.CTkLabel(frame, text="Nova Tarefa", font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Campo de Título
        self.title_entry = ctk.CTkEntry(frame, placeholder_text="Título da tarefa", font=ctk.CTkFont(size=14))
        self.title_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Campo de Descrição
        self.desc_textbox = ctk.CTkTextbox(frame, height=150, font=ctk.CTkFont(size=13))
        self.desc_textbox.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.desc_textbox.insert("0.0", "Descrição...")
        self.desc_textbox.bind("<FocusIn>", self.clear_placeholder)
        self.desc_textbox.bind("<FocusOut>", self.add_placeholder)

        # Botão de Adicionar
        add_button = ctk.CTkButton(frame, text="Adicionar Tarefa", command=self.add_task_callback, corner_radius=8)
        add_button.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        
        return frame
        
    def _create_tasks_display_frame(self):
        """Cria o painel direito para listar as tarefas."""
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        
        label = ctk.CTkLabel(frame, text="Minhas Tarefas", font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Frame rolável para a lista de tarefas
        self.scrollable_frame = ctk.CTkScrollableFrame(frame, label_text="")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        return frame

    def refresh_tasks_display(self):
        """Limpa e recria os widgets de tarefa na tela com base nos dados atuais."""
        # Limpa widgets antigos
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Cria novos widgets para cada tarefa
        for i, task in enumerate(self.task_manager.tasks):
            self.create_task_widget(task, i)

    def create_task_widget(self, task, index):
        """Cria um widget individual para uma tarefa."""
        task_widget_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=8)
        task_widget_frame.pack(fill="x", padx=5, pady=5)

        task_widget_frame.grid_columnconfigure(0, weight=1)

        # Checkbox com o título da tarefa
        check_var = ctk.StringVar(value="on" if task.is_completed else "off")
        font_style = ctk.CTkFont(size=14, weight="bold", slant="italic" if task.is_completed else "roman")
        
        checkbox = ctk.CTkCheckBox(
            task_widget_frame, 
            text=task.title,
            variable=check_var, 
            onvalue="on", 
            offvalue="off",
            font=font_style,
            command=lambda t=task: self.toggle_complete_callback(t)
        )
        checkbox.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Altera o visual se estiver concluída
        if task.is_completed:
            checkbox.configure(text_color="gray")
            checkbox.select()

        # Descrição da tarefa
        if task.description:
            desc_label = ctk.CTkLabel(
                task_widget_frame, 
                text=task.description, 
                wraplength=450, 
                justify="left",
                font=ctk.CTkFont(size=12),
                text_color="gray60"
            )
            desc_label.grid(row=1, column=0, padx=40, pady=(0, 10), sticky="w")

        # Botão de excluir
        delete_button = ctk.CTkButton(
            task_widget_frame,
            text="Excluir",
            width=80,
            corner_radius=6,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=lambda t=task: self.delete_task_callback(t)
        )
        delete_button.grid(row=0, column=1, rowspan=2 if task.description else 1, padx=10, pady=10)


    def add_task_callback(self):
        """Callback para o botão de adicionar tarefa."""
        title = self.title_entry.get().strip()
        description = self.desc_textbox.get("1.0", "end-1c").strip()
        
        if not title:
            messagebox.showwarning("Campo Vazio", "O título da tarefa é obrigatório.")
            return

        if description == "Descrição...":
            description = ""
            
        self.task_manager.add_task(title, description)
        self.refresh_tasks_display()
        
        # Limpar campos de entrada
        self.title_entry.delete(0, "end")
        self.desc_textbox.delete("1.0", "end")
        self.add_placeholder(None) # Recoloca o placeholder
        self.title_entry.focus()
        
    def delete_task_callback(self, task):
        """Callback para o botão de excluir tarefa."""
        self.task_manager.delete_task(task)
        self.refresh_tasks_display()

    def toggle_complete_callback(self, task):
        """Callback para o checkbox de conclusão da tarefa."""
        self.task_manager.toggle_task_completion(task)
        self.refresh_tasks_display()
    
    # --- Funções auxiliares para o placeholder da descrição ---
    def clear_placeholder(self, event):
        if self.desc_textbox.get("1.0", "end-1c") == "Descrição...":
            self.desc_textbox.delete("1.0", "end")

    def add_placeholder(self, event):
        if not self.desc_textbox.get("1.0", "end-1c"):
            self.desc_textbox.insert("1.0", "Descrição...")

    def on_closing(self):
        """Salva as tarefas antes de fechar a aplicação."""
        self.task_manager.save_tasks()
        self.destroy()

# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    task_manager = TaskManager()
    app = App(task_manager)
    app.mainloop()