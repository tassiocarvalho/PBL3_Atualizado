"""
Interface Gráfica para Projeto de Filtros FIR
Módulo principal que integra cálculos e visualização
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
        self.root.geometry("1650x900")
        self.root.minsize(1000, 600)
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Customizar cores e estilos
        self.style.configure("Title.TLabel", font=('Arial', 14, 'bold'), foreground='#2E5266')
        self.style.configure("Subtitle.TLabel", font=('Arial', 11, 'bold'), foreground='#2E5266')
        self.style.configure("Header.TLabel", font=('Arial', 10, 'bold'), foreground='#1F3B4D')
        self.style.configure("Action.TButton", font=('Arial', 10, 'bold'))
        
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
        # Frame principal com padding reduzido
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de entrada (esquerda) - com scroll
        input_outer_frame = ttk.LabelFrame(main_frame, text="  Especificações e Controles  ", 
                                          style="Title.TLabel")
        input_outer_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        input_outer_frame.configure(width=620)
        input_outer_frame.pack_propagate(False)  # Manter largura fixa
        
        # Canvas e scrollbar para o painel de entrada
        canvas = tk.Canvas(input_outer_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(input_outer_frame, orient="vertical", command=canvas.yview)
        input_frame = ttk.Frame(canvas, padding=12)
        
        # Configurar scroll
        input_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=input_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        def unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            
        input_outer_frame.bind('<Enter>', bind_to_mousewheel)
        input_outer_frame.bind('<Leave>', unbind_from_mousewheel)
        
        # Frame de visualização (direita)
        viz_frame = ttk.LabelFrame(main_frame, text="  Visualização dos Resultados  ", 
                                 padding=10, style="Title.TLabel")
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_input_section(input_frame)
        self.create_visualization_section(viz_frame)
    
    def create_input_section(self, parent):
        """Cria a seção de entrada de dados"""
        row = 0
        
        # Título principal
        title_label = ttk.Label(parent, text="PROJETO DE FILTROS FIR", 
                               style="Title.TLabel")
        title_label.grid(row=row, column=0, columnspan=2, pady=(0, 15))
        row += 1
        
        # ========== BLOCO 1: TIPO DE FILTRO ==========
        type_frame = ttk.LabelFrame(parent, text="  Tipo de Filtro  ", padding=10)
        type_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 1
        
        ttk.Label(type_frame, text="Selecione o tipo:", style="Header.TLabel").pack(anchor=tk.W)
        filter_combo = ttk.Combobox(type_frame, textvariable=self.filter_type_var, 
                                   values=["Passa-Baixa", "Passa-Alta", "Passa-Banda", "Rejeita-Banda"],
                                   state="readonly", width=25, font=('Arial', 10))
        filter_combo.pack(pady=(8, 0), fill=tk.X)
        filter_combo.bind("<<ComboboxSelected>>", self.on_filter_type_changed)
        
        # ========== BLOCO 2: ESPECIFICAÇÕES BÁSICAS ==========
        spec_frame = ttk.LabelFrame(parent, text="  Especificações Básicas  ", padding=10)
        spec_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 1
        
        # Frequência de amostragem
        fs_subframe = ttk.Frame(spec_frame)
        fs_subframe.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(fs_subframe, text="Frequência de Amostragem:", 
                 style="Header.TLabel").pack(anchor=tk.W)
        fs_input_frame = ttk.Frame(fs_subframe)
        fs_input_frame.pack(anchor=tk.W, pady=(3, 0))
        ttk.Entry(fs_input_frame, textvariable=self.fs_var, width=12, 
                 font=('Arial', 10)).pack(side=tk.LEFT)
        ttk.Label(fs_input_frame, text=" Hz", font=('Arial', 10)).pack(side=tk.LEFT)
        
        # Largura de transição
        tw_subframe = ttk.Frame(spec_frame)
        tw_subframe.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(tw_subframe, text="Largura de Transição:", 
                 style="Header.TLabel").pack(anchor=tk.W)
        tw_input_frame = ttk.Frame(tw_subframe)
        tw_input_frame.pack(anchor=tk.W, pady=(3, 0))
        ttk.Entry(tw_input_frame, textvariable=self.transition_width_var, width=12,
                 font=('Arial', 10)).pack(side=tk.LEFT)
        ttk.Label(tw_input_frame, text=" Hz", font=('Arial', 10)).pack(side=tk.LEFT)
        
        # Atenuação
        atten_subframe = ttk.Frame(spec_frame)
        atten_subframe.pack(fill=tk.X)
        ttk.Label(atten_subframe, text="Atenuação na Banda de Rejeição:", 
                 style="Header.TLabel").pack(anchor=tk.W)
        atten_input_frame = ttk.Frame(atten_subframe)
        atten_input_frame.pack(anchor=tk.W, pady=(3, 0))
        ttk.Entry(atten_input_frame, textvariable=self.stopband_atten_var, width=12,
                 font=('Arial', 10)).pack(side=tk.LEFT)
        ttk.Label(atten_input_frame, text=" dB", font=('Arial', 10)).pack(side=tk.LEFT)
        
        # ========== BLOCO 3: FREQUÊNCIAS ==========
        self.freq_main_frame = ttk.LabelFrame(parent, text="  Frequências de Corte  ", padding=10)
        self.freq_main_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 1
        
        # Frame dinâmico para frequências (dentro do LabelFrame)
        self.freq_frame = ttk.Frame(self.freq_main_frame)
        self.freq_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== BLOCO 4: VERIFICAÇÃO DE JANELAS ==========
        check_frame = ttk.LabelFrame(parent, text="  Verificação de Compatibilidade  ", padding=10)
        check_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 1
        
        ttk.Label(check_frame, text="Verificar janelas que atendem as especificações:",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 8))
        check_button = ttk.Button(check_frame, text="VERIFICAR JANELAS DISPONÍVEIS", 
                                 command=self.check_available_windows,
                                 style="Action.TButton")
        check_button.pack(fill=tk.X)
        
        # ========== BLOCO 5: SELEÇÃO DE JANELA ==========
        self.window_frame = ttk.LabelFrame(parent, text="  Seleção da Função de Janelamento  ", 
                                          padding=10)
        self.window_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 1
        
        # ========== BLOCO 6: PROJETO DO FILTRO ==========
        design_frame = ttk.LabelFrame(parent, text="  Execução do Projeto  ", padding=10)
        design_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 1
        
        ttk.Label(design_frame, text="Projetar o filtro com as especificações definidas:",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 8))
        self.calc_button = ttk.Button(design_frame, text="PROJETAR FILTRO", 
                                     command=self.design_filter,
                                     state=tk.DISABLED,
                                     style="Action.TButton")
        self.calc_button.pack(fill=tk.X)
        
        # ========== BLOCO 7: EXPORTAÇÃO DOS COEFICIENTES ==========
        export_frame = ttk.LabelFrame(parent, text="  Exportar Coeficientes  ", padding=10)
        export_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        row += 1
        
        ttk.Label(export_frame, text="Salvar coeficientes calculados em arquivo:",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 8))
        
        # Frame para botões de exportação
        export_buttons_frame = ttk.Frame(export_frame)
        export_buttons_frame.pack(fill=tk.X)
        
        self.export_button = ttk.Button(export_buttons_frame, text="EXPORTAR TXT",
                                       command=self.export_coefficients,
                                       state=tk.DISABLED,
                                       style="Action.TButton")
        self.export_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
    
        # ========== BLOCO 8: RESULTADOS ==========
        self.results_frame = ttk.LabelFrame(parent, text="  Informações Calculadas  ", padding=10)
        self.results_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=(0, 5))
        
        # Text widget com scrollbar
        text_frame = ttk.Frame(self.results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(text_frame, height=10, wrap=tk.WORD, 
                                   font=('Consolas', 9), bg='#f8f9fa',
                                   relief=tk.SUNKEN, bd=1)
        scrollbar_results = ttk.Scrollbar(text_frame, orient="vertical", 
                                         command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar_results.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_results.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar expansão
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Inicializar campos de frequência
        self.update_frequency_fields()

    def create_visualization_section(self, parent):
        """Cria a seção de visualização"""
        # Notebook para múltiplas visualizações com estilo melhorado
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Criar abas com nomes mais descritivos
        self.window_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.window_tab, text="  Função de Janelamento  ")
        
        self.coef_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.coef_tab, text="  Coeficientes do Filtro  ")
        
        self.freq_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.freq_tab, text="  Resposta em Frequência  ")
        
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
            # Para passa-baixa e passa-alta: apenas uma frequência
            freq_subframe = ttk.Frame(self.freq_frame)
            freq_subframe.pack(fill=tk.X)
            
            label_text = "Frequência da Borda da Banda Passante:"
            ttk.Label(freq_subframe, text=label_text, style="Header.TLabel").pack(anchor=tk.W)
            
            fp_input_frame = ttk.Frame(freq_subframe)
            fp_input_frame.pack(anchor=tk.W, pady=(3, 0))
            ttk.Entry(fp_input_frame, textvariable=self.fp1_var, width=12,
                     font=('Arial', 10)).pack(side=tk.LEFT)
            ttk.Label(fp_input_frame, text=" Hz", font=('Arial', 10)).pack(side=tk.LEFT)
            
        elif filter_type in ["Passa-Banda", "Rejeita-Banda"]:
            if filter_type == "Passa-Banda":
                label_text1 = "Frequência Inferior da Banda Passante:"
                label_text2 = "Frequência Superior da Banda Passante:"
            else:  # Rejeita-Banda
                label_text1 = "Frequência Inferior da Banda Rejeitada:"
                label_text2 = "Frequência Superior da Banda Rejeitada:"
            
            # Primeira frequência
            fp1_subframe = ttk.Frame(self.freq_frame)
            fp1_subframe.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(fp1_subframe, text=label_text1, style="Header.TLabel").pack(anchor=tk.W)
            fp1_input_frame = ttk.Frame(fp1_subframe)
            fp1_input_frame.pack(anchor=tk.W, pady=(3, 0))
            ttk.Entry(fp1_input_frame, textvariable=self.fp1_var, width=12,
                     font=('Arial', 10)).pack(side=tk.LEFT)
            ttk.Label(fp1_input_frame, text=" Hz", font=('Arial', 10)).pack(side=tk.LEFT)
            
            # Segunda frequência
            fp2_subframe = ttk.Frame(self.freq_frame)
            fp2_subframe.pack(fill=tk.X)
            ttk.Label(fp2_subframe, text=label_text2, style="Header.TLabel").pack(anchor=tk.W)
            fp2_input_frame = ttk.Frame(fp2_subframe)
            fp2_input_frame.pack(anchor=tk.W, pady=(3, 0))
            ttk.Entry(fp2_input_frame, textvariable=self.fp2_var, width=12,
                     font=('Arial', 10)).pack(side=tk.LEFT)
            ttk.Label(fp2_input_frame, text=" Hz", font=('Arial', 10)).pack(side=tk.LEFT)
    
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
            
            # Criar interface para seleção
            ttk.Label(self.window_frame, 
                     text=f"Janelas compatíveis (≥{required_atten} dB):", 
                     style="Header.TLabel").pack(anchor=tk.W, pady=(0, 8))
            
            window_combo = ttk.Combobox(self.window_frame, textvariable=self.selected_window_var,
                                       values=self.available_windows, state="readonly", 
                                       width=30, font=('Arial', 10))
            window_combo.pack(pady=(0, 8), fill=tk.X)
            window_combo.bind("<<ComboboxSelected>>", self.on_window_selected)
            
            # Mostrar informações das janelas disponíveis
            self.show_available_windows_info(required_atten)
            
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor válido para a atenuação.")
    
    def show_available_windows_info(self, required_atten):
        """Mostra informações das janelas disponíveis"""
        info_text = "=" * 50 + "\n"
        info_text += "       JANELAS COMPATÍVEIS ENCONTRADAS\n"
        info_text += "=" * 50 + "\n\n"
        
        for i, window_name in enumerate(self.available_windows, 1):
            params = self.calculator.window_parameters[window_name]
            info_text += f"{i}. {window_name}\n"
            info_text += f"   • Atenuação: {params['atenuacao_banda_rejeicao_db']} dB\n"
            info_text += f"   • Largura de Transição: {params['largura_transicao_normalizada']}/N\n"
            info_text += f"   • Ondulação Banda Passante: {params['ondulacao_banda_passante_db']} dB\n"
            if params.get('lobulo_principal_lateral_db'):
                info_text += f"   • Lóbulo Principal vs Lateral: {params['lobulo_principal_lateral_db']} dB\n"
            info_text += f"   • Expressão: {params['expressao']}\n\n"
        
        info_text += "=" * 50 + "\n"
        info_text += "Selecione uma janela acima para continuar o projeto.\n"
        
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
            
            # Habilitar botões de exportação
            self.export_button.config(state=tk.NORMAL)
            
            messagebox.showinfo("Sucesso", "Filtro projetado com sucesso!\nVerifique as abas de visualização.")
            
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no projeto: {e}")
    
    def export_coefficients(self):
        """Exporta os coeficientes do filtro para arquivo txt simples"""
        if self.current_results is None:
            messagebox.showwarning("Aviso", "Nenhum filtro foi projetado ainda.")
            return
        
        try:
            from tkinter import filedialog
            import datetime
            
            # Obter coeficientes
            coefficients = self.current_results['coefficients']
            
            # Diálogo para salvar arquivo
            filename = filedialog.asksaveasfilename(
                title="Salvar Coeficientes do Filtro",
                defaultextension=".txt",
                filetypes=[
                    ("Arquivo de texto", "*.txt"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            
            if not filename:
                return
            
            # Escrever arquivo
            with open(filename, 'w', encoding='utf-8') as f:
            
                f.write("h = [")
                for i, coef in enumerate(coefficients):
                    if i == 0:
                        f.write(f"{coef:.10f}")
                    else:
                        f.write(f", {coef:.10f}")
                    # Quebrar linha a cada 4 coeficientes para melhor leitura
                    #if (i + 1) % 4 == 0 and i < len(coefficients) - 1:
                    #    f.write("\n     ")
                f.write("];\n")
            
            messagebox.showinfo("Sucesso", f"Coeficientes salvos com sucesso!\nArquivo: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo: {e}")

    def export_coefficients_matlab(self):
        """Exporta os coeficientes em formato compatível com MATLAB/Octave"""
        if self.current_results is None:
            messagebox.showwarning("Aviso", "Nenhum filtro foi projetado ainda.")
            return
        
        try:
            from tkinter import filedialog
            import datetime
            
            # Obter coeficientes e especificações
            coefficients = self.current_results['coefficients']
            filter_specs = {
                'filter_type': self.filter_type_var.get(),
                'fs': float(self.fs_var.get()),
                'window_name': self.selected_window_var.get(),
                'order': self.current_results['order']
            }
            
            # Diálogo para salvar arquivo
            filename = filedialog.asksaveasfilename(
                title="Salvar Coeficientes (Formato MATLAB)",
                defaultextension=".m",
                filetypes=[
                    ("Arquivo MATLAB", "*.m"),
                    ("Arquivo de texto", "*.txt"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            
            if not filename:
                return
            
            # Escrever arquivo no formato MATLAB
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("% COEFICIENTES DE FILTRO FIR\n")
                f.write("% Gerado automaticamente pelo Software de Projeto de Filtros FIR\n")
                f.write(f"% Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("% " + "=" * 60 + "\n\n")
                
                f.write("% Especificações do filtro:\n")
                f.write(f"% Tipo: {filter_specs['filter_type']}\n")
                f.write(f"% Janela: {filter_specs['window_name']}\n")
                f.write(f"% Frequência de amostragem: {filter_specs['fs']} Hz\n")
                f.write(f"% Ordem: {filter_specs['order']}\n")
                f.write(f"% Número de coeficientes: {len(coefficients)}\n\n")
                
                f.write("% Coeficientes do filtro:\n")
                f.write("h = [")
                for i, coef in enumerate(coefficients):
                    if i == 0:
                        f.write(f"{coef:.12e}")
                    else:
                        f.write(f", {coef:.12e}")
                    # Quebrar linha a cada 3 coeficientes
                    if (i + 1) % 3 == 0 and i < len(coefficients) - 1:
                        f.write(" ...\n     ")
                f.write("];\n\n")
                
                f.write("% Exemplo de uso:\n")
                f.write("% Fs = {}; % Frequência de amostragem\n".format(filter_specs['fs']))
                f.write("% [H, w] = freqz(h, 1, 1024, Fs); % Resposta em frequência\n")
                f.write("% plot(w, 20*log10(abs(H))); % Plotar magnitude em dB\n")
                f.write("% y = filter(h, 1, x); % Filtrar sinal x\n")
            
            messagebox.showinfo("Sucesso", f"Coeficientes salvos em formato MATLAB!\nArquivo: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo: {e}")
    
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