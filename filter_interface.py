"""
Interface Gráfica para Projeto de Filtros FIR
Módulo principal que integra cálculos e visualização
"""

import tkinter as tk
from tkinter import ttk, messagebox
from filter_calculations import FilterCalculator
from filter_visualizer import FilterVisualizer


class FilterDesignApp:
    """
    Aplicativo principal para projeto de filtros FIR com janelamento
    """
    
    def __init__(self, root):
        """Inicializa a aplicação"""
        self.root = root
        self.root.title("Projeto de Filtros FIR - Janelamento da Função Seno Cardinal")
        self.root.geometry("1600x900")
        self.root.minsize(1400, 800)
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Instanciar módulos
        self.calculator = FilterCalculator()
        self.visualizer = None  # Será inicializado após criar os frames
        
        # Variáveis de entrada
        self.filter_type_var = tk.StringVar(value="Passa-Baixa")
        self.fs_var = tk.StringVar(value="8000")
        self.fp1_var = tk.StringVar(value="1500")
        self.fp2_var = tk.StringVar(value="2500")
        self.transition_width_var = tk.StringVar(value="500")
        self.stopband_atten_var = tk.StringVar(value="50")
        self.selected_window_var = tk.StringVar()
        
        # Variáveis de controle
        self.available_windows = []
        self.current_results = None
        
        self.create_interface()
        
    def create_interface(self):
        """Cria a interface completa"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de entrada (esquerda)
        input_frame = ttk.LabelFrame(main_frame, text="Especificações e Controles", padding=15)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        input_frame.configure(width=400)
        
        # Frame de visualização (direita)
        viz_frame = ttk.LabelFrame(main_frame, text="Visualização dos Resultados", padding=10)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_input_section(input_frame)
        self.create_visualization_section(viz_frame)
    
    def create_input_section(self, parent):
        """Cria a seção de entrada de dados"""
        row = 0
        
        # Título
        title_label = ttk.Label(parent, text="PROJETO DE FILTROS FIR", 
                               font=('Arial', 12, 'bold'))
        title_label.grid(row=row, column=0, columnspan=2, pady=(0, 20))
        row += 1
        
        # Tipo de filtro
        ttk.Label(parent, text="Tipo de Filtro:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        filter_combo = ttk.Combobox(parent, textvariable=self.filter_type_var, 
                                   values=["Passa-Baixa", "Passa-Alta", "Passa-Banda", "Rejeita-Banda"],
                                   state="readonly", width=20)
        filter_combo.grid(row=row, column=1, sticky=tk.W+tk.E, pady=5, padx=(10,0))
        filter_combo.bind("<<ComboboxSelected>>", self.on_filter_type_changed)
        row += 1
        
        # Separador
        ttk.Separator(parent, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                       sticky="ew", pady=15)
        row += 1
        
        # Título das especificações
        spec_title = ttk.Label(parent, text="ESPECIFICAÇÕES DO FILTRO", 
                              font=('Arial', 11, 'bold'))
        spec_title.grid(row=row, column=0, columnspan=2, pady=(0, 10))
        row += 1
        
        # Frequência de amostragem
        ttk.Label(parent, text="Frequência de Amostragem:", font=('Arial', 10)).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        fs_frame = ttk.Frame(parent)
        fs_frame.grid(row=row, column=1, sticky=tk.W+tk.E, pady=5, padx=(10,0))
        ttk.Entry(fs_frame, textvariable=self.fs_var, width=10).pack(side=tk.LEFT)
        ttk.Label(fs_frame, text="Hz").pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        # Frame dinâmico para frequências
        self.freq_frame = ttk.Frame(parent)
        self.freq_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        row += 1
        
        # Largura de transição
        ttk.Label(parent, text="Largura de Transição:", font=('Arial', 10)).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        tw_frame = ttk.Frame(parent)
        tw_frame.grid(row=row, column=1, sticky=tk.W+tk.E, pady=5, padx=(10,0))
        ttk.Entry(tw_frame, textvariable=self.transition_width_var, width=10).pack(side=tk.LEFT)
        ttk.Label(tw_frame, text="Hz").pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        # Atenuação na banda de rejeição
        ttk.Label(parent, text="Atenuação na Banda\nde Rejeição:", font=('Arial', 10)).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        atten_frame = ttk.Frame(parent)
        atten_frame.grid(row=row, column=1, sticky=tk.W+tk.E, pady=5, padx=(10,0))
        ttk.Entry(atten_frame, textvariable=self.stopband_atten_var, width=10).pack(side=tk.LEFT)
        ttk.Label(atten_frame, text="dB").pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        # Botão para verificar janelas disponíveis
        check_button = ttk.Button(parent, text="Verificar Janelas Disponíveis", 
                                 command=self.check_available_windows)
        check_button.grid(row=row, column=0, columnspan=2, pady=20)
        row += 1
        
        # Frame para seleção de janelas
        self.window_frame = ttk.LabelFrame(parent, text="Funções de Janelamento Disponíveis", 
                                          padding=10)
        self.window_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # Botão para calcular filtro
        self.calc_button = ttk.Button(parent, text="PROJETAR FILTRO", 
                                     command=self.design_filter,
                                     state=tk.DISABLED)
        self.calc_button.grid(row=row, column=0, columnspan=2, pady=20)
        row += 1
        
        # Frame de resultados calculados
        self.results_frame = ttk.LabelFrame(parent, text="Informações Calculadas", padding=10)
        self.results_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=10)
        
        self.results_text = tk.Text(self.results_frame, height=15, width=50, wrap=tk.WORD, 
                                   font=('Consolas', 9))
        scrollbar_results = ttk.Scrollbar(self.results_frame, orient="vertical", 
                                         command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar_results.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_results.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar expansão
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
        # Inicializar campos de frequência
        self.update_frequency_fields()
    
    def create_visualization_section(self, parent):
        """Cria a seção de visualização"""
        # Notebook para múltiplas visualizações
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Criar abas
        self.window_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.window_tab, text="Função de Janelamento")
        
        self.coef_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.coef_tab, text="Coeficientes do Filtro")
        
        self.freq_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.freq_tab, text="Resposta em Frequência")
        
        # Inicializar visualizador
        parent_frames = {
            'window': self.window_tab,
            'coefficients': self.coef_tab,
            'frequency': self.freq_tab
        }
        self.visualizer = FilterVisualizer(parent_frames)
    
    def on_filter_type_changed(self, event=None):
        """Callback quando o tipo de filtro muda"""
        self.update_frequency_fields()
        
    def update_frequency_fields(self):
        """Atualiza os campos de frequência baseado no tipo de filtro"""
        # Limpar frame anterior
        for widget in self.freq_frame.winfo_children():
            widget.destroy()
        
        filter_type = self.filter_type_var.get()
        
        if filter_type in ["Passa-Baixa", "Passa-Alta"]:
            # Para passa-baixa e passa-alta: apenas uma frequência de borda
            freq_label = ttk.Label(self.freq_frame, text="Frequência da Borda da\nBanda Passante:", 
                                  font=('Arial', 10))
            freq_label.grid(row=0, column=0, sticky=tk.W, pady=5)
            
            fp_frame = ttk.Frame(self.freq_frame)
            fp_frame.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(10,0))
            ttk.Entry(fp_frame, textvariable=self.fp1_var, width=10).pack(side=tk.LEFT)
            ttk.Label(fp_frame, text="Hz").pack(side=tk.LEFT, padx=(5, 0))
            
        elif filter_type in ["Passa-Banda", "Rejeita-Banda"]:
            if filter_type == "Passa-Banda":
                label_text1 = "Frequência Inferior\nda Banda Passante:"
                label_text2 = "Frequência Superior\nda Banda Passante:"
            else:  # Rejeita-Banda
                label_text1 = "Frequência Inferior\nda Banda a ser Rejeitada:"
                label_text2 = "Frequência Superior\nda Banda a ser Rejeitada:"
                
            fp1_label = ttk.Label(self.freq_frame, text=label_text1, font=('Arial', 10))
            fp1_label.grid(row=0, column=0, sticky=tk.W, pady=5)
            
            fp1_frame = ttk.Frame(self.freq_frame)
            fp1_frame.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(10,0))
            ttk.Entry(fp1_frame, textvariable=self.fp1_var, width=10).pack(side=tk.LEFT)
            ttk.Label(fp1_frame, text="Hz").pack(side=tk.LEFT, padx=(5, 0))
            
            fp2_label = ttk.Label(self.freq_frame, text=label_text2, font=('Arial', 10))
            fp2_label.grid(row=1, column=0, sticky=tk.W, pady=5)
            
            fp2_frame = ttk.Frame(self.freq_frame)
            fp2_frame.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5, padx=(10,0))
            ttk.Entry(fp2_frame, textvariable=self.fp2_var, width=10).pack(side=tk.LEFT)
            ttk.Label(fp2_frame, text="Hz").pack(side=tk.LEFT, padx=(5, 0))
        
        # Configurar expansão
        self.freq_frame.grid_columnconfigure(1, weight=1)
    
    def check_available_windows(self):
        """Verifica quais janelas atendem a especificação de atenuação"""
        try:
            required_atten = float(self.stopband_atten_var.get())
            
            # Limpar frame anterior
            for widget in self.window_frame.winfo_children():
                widget.destroy()
            
            # Obter janelas disponíveis do calculador
            self.available_windows = self.calculator.get_available_windows(required_atten)
            
            if not self.available_windows:
                messagebox.showwarning("Aviso", 
                    f"Nenhuma janela disponível atende a especificação de {required_atten} dB.\n"
                    "Considere reduzir a exigência de atenuação.")
                return
            
            # Criar dropdown com janelas disponíveis
            ttk.Label(self.window_frame, 
                     text=f"Janelas que atendem ≥{required_atten} dB:", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
            
            window_combo = ttk.Combobox(self.window_frame, textvariable=self.selected_window_var,
                                       values=self.available_windows, state="readonly", width=25)
            window_combo.pack(pady=5)
            window_combo.bind("<<ComboboxSelected>>", self.on_window_selected)
            
            # Mostrar informações das janelas disponíveis
            self.show_available_windows_info(required_atten)
            
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor válido para a atenuação.")
    
    def show_available_windows_info(self, required_atten):
        """Mostra informações das janelas disponíveis"""
        info_text = "\n=== JANELAS DISPONÍVEIS ===\n"
        for window_name in self.available_windows:
            params = self.calculator.window_parameters[window_name]
            info_text += f"\n{window_name}:\n"
            info_text += f"• Atenuação: {params['atenuacao_banda_rejeicao_db']} dB\n"
            info_text += f"• Largura de Transição: {params['largura_transicao_normalizada']}/N\n"
            info_text += f"• Ondulação Banda Passante: {params['ondulacao_banda_passante_db']} dB\n"
            if params.get('lobulo_principal_lateral_db'):
                info_text += f"• Lóbulo Principal vs Lateral: {params['lobulo_principal_lateral_db']} dB\n"
            info_text += f"• Expressão: {params['expressao']}\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, info_text)
    
    def on_window_selected(self, event=None):
        """Callback quando uma janela é selecionada"""
        if self.selected_window_var.get():
            self.calc_button.config(state=tk.NORMAL)
    
    def design_filter(self):
        """Projeta o filtro com as especificações fornecidas"""
        try:
            # Coletar especificações
            filter_specs = self.collect_filter_specifications()
            
            # Projetar filtro usando o calculador
            results = self.calculator.design_filter(**filter_specs)
            
            # Armazenar resultados
            self.current_results = results
            
            # Atualizar visualizações
            self.visualizer.update_all_plots(results, filter_specs['window_name'], filter_specs)
            
            # Gerar e mostrar relatório detalhado
            report = self.calculator.generate_detailed_report(filter_specs, results)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, report)
            
            messagebox.showinfo("Sucesso", "Filtro projetado com sucesso!")
            
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no projeto: {e}")
    
    def collect_filter_specifications(self):
        """Coleta e valida as especificações do filtro"""
        fs = float(self.fs_var.get())
        transition_width = float(self.transition_width_var.get())
        stopband_atten = float(self.stopband_atten_var.get())
        filter_type = self.filter_type_var.get()
        window_name = self.selected_window_var.get()
        
        # Validações básicas
        if fs <= 0:
            raise ValueError("Frequência de amostragem deve ser positiva")
        if transition_width <= 0:
            raise ValueError("Largura de transição deve ser positiva")
        if stopband_atten <= 0:
            raise ValueError("Atenuação deve ser positiva")
        if not window_name:
            raise ValueError("Selecione uma janela")
        
        # Coletar frequências baseadas no tipo
        if filter_type in ["Passa-Baixa", "Passa-Alta"]:
            fp_values = float(self.fp1_var.get())
            if fp_values <= 0:
                raise ValueError("Frequência deve ser positiva")
        else:  # Passa-Banda ou Rejeita-Banda
            fp1 = float(self.fp1_var.get())
            fp2 = float(self.fp2_var.get())
            if fp1 <= 0 or fp2 <= 0:
                raise ValueError("Frequências devem ser positivas")
            fp_values = [fp1, fp2]
        
        return {
            'filter_type': filter_type,
            'fs': fs,
            'fp_values': fp_values,
            'transition_width': transition_width,
            'stopband_atten': stopband_atten,
            'window_name': window_name
        }


def main():
    """Função principal da aplicação"""
    root = tk.Tk()
    app = FilterDesignApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()