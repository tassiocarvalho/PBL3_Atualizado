"""
Módulo de Visualização para Filtros FIR
Contém todas as funções de plotagem e visualização
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy import signal
import matplotlib
matplotlib.use("TkAgg")


class FilterVisualizer:
    """
    Classe responsável por todas as visualizações dos filtros FIR
    """
    
    def __init__(self, parent_frames):
        """
        Inicializa o visualizador
        
        Args:
            parent_frames (dict): Dicionário com os frames para cada tipo de gráfico
                                 Chaves: 'window', 'coefficients', 'frequency'
        """
        self.parent_frames = parent_frames
        self.setup_plots()
    
    def setup_plots(self):
        """Configura os gráficos iniciais"""
        # Gráfico da função de janelamento
        self.window_fig = Figure(figsize=(12, 6), dpi=100)
        self.window_canvas = FigureCanvasTkAgg(self.window_fig, 
                                              master=self.parent_frames['window'])
        self.window_canvas.get_tk_widget().pack(fill='both', expand=True)
        NavigationToolbar2Tk(self.window_canvas, self.parent_frames['window'])
        
        # Gráfico de coeficientes
        self.coef_fig = Figure(figsize=(12, 8), dpi=100)
        self.coef_canvas = FigureCanvasTkAgg(self.coef_fig, 
                                            master=self.parent_frames['coefficients'])
        self.coef_canvas.get_tk_widget().pack(fill='both', expand=True)
        NavigationToolbar2Tk(self.coef_canvas, self.parent_frames['coefficients'])
        
        # Gráfico de resposta em frequência
        self.freq_fig = Figure(figsize=(12, 8), dpi=100)
        self.freq_canvas = FigureCanvasTkAgg(self.freq_fig, 
                                            master=self.parent_frames['frequency'])
        self.freq_canvas.get_tk_widget().pack(fill='both', expand=True)
        NavigationToolbar2Tk(self.freq_canvas, self.parent_frames['frequency'])
    
    def plot_window(self, window, window_name):
        """
        Plota a função de janelamento
        
        Args:
            window (numpy.ndarray): Janela a ser plotada
            window_name (str): Nome da janela
        """
        self.window_fig.clear()
        ax = self.window_fig.add_subplot(111)
        
        n = np.arange(len(window))
        ax.plot(n, window, 'b-', linewidth=2, label='Função de Janelamento')
        
        # Stem plot
        markerline, stemlines, baseline = ax.stem(n, window, linefmt='b-', 
                                                 markerfmt='bo', basefmt='k-')
        plt.setp(stemlines, alpha=0.7)
        plt.setp(markerline, alpha=0.7)
        
        ax.set_title(f'Função de Janelamento: {window_name}', 
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('Índice da Amostra (n)')
        ax.set_ylabel('Amplitude w(n)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Destacar centro
        center = len(window) // 2
        ax.axvline(center, color='red', linestyle='--', alpha=0.5, 
                  label=f'Centro (n={center})')
        
        self.window_fig.tight_layout()
        self.window_canvas.draw()
    
    def plot_coefficients(self, h_windowed, h_ideal):
        """
        Plota os coeficientes do filtro - VERSÃO COM APENAS UM GRÁFICO
        
        Args:
            h_windowed (numpy.ndarray): Coeficientes janelados
            h_ideal (numpy.ndarray): Resposta ideal
        """
        self.coef_fig.clear()
        
        # Apenas um subplot ocupando toda a figura
        ax = self.coef_fig.add_subplot(111)
        n = np.arange(len(h_windowed))
        
        # Coeficientes janelados
        markerline, stemlines, baseline = ax.stem(n, h_windowed, linefmt='b-', 
                                                markerfmt='bo', basefmt='k-', 
                                                label='Coeficientes Janelados h(n)')
        plt.setp(markerline, markersize=4)
        plt.setp(stemlines, linewidth=1.5)
        
        # Coeficientes ideais (linha)
        ax.plot(n, h_ideal, 'r--', alpha=0.8, linewidth=2, label='Resposta Ideal')
        
        ax.set_title('Coeficientes do Filtro FIR', fontsize=12, fontweight='bold')
        ax.set_xlabel('Índice da Amostra (n)')
        ax.set_ylabel('Amplitude h(n)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Destacar centro
        center = len(h_windowed) // 2
        ax.axvline(center, color='gray', linestyle=':', alpha=0.5, 
                label=f'Centro (n={center})')
        
        # Adicionar informações úteis como texto
        # Mostrar alguns valores importantes
        max_coeff = np.max(np.abs(h_windowed))
        center_coeff = h_windowed[center]
        
        # Caixa de texto com informações
        info_text = f'Ordem: {len(h_windowed)-1}\n'
        info_text += f'Centro: n={center}\n'
        info_text += f'h({center}) = {center_coeff:.4f}\n'
        info_text += f'Max |h(n)|: {max_coeff:.4f}'
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', 
            facecolor='lightblue', alpha=0.8),
            fontsize=9)
        
        self.coef_fig.tight_layout()
        self.coef_canvas.draw()
    
    def plot_frequency_response(self, h_windowed, fs, fc_list, filter_specs):
        """
        Plota a resposta em frequência
        
        Args:
            h_windowed (numpy.ndarray): Coeficientes do filtro
            fs (float): Frequência de amostragem
            fc_list (list): Lista das frequências de corte
            filter_specs (dict): Especificações do filtro
        """
        self.freq_fig.clear()
        
        # Calcular resposta em frequência
        w, H = signal.freqz(h_windowed, worN=8192, fs=fs)
        
        # Subplot 1: Magnitude em dB
        ax1 = self.freq_fig.add_subplot(211)
        H_db = 20 * np.log10(np.abs(H) + 1e-10)
        ax1.plot(w, H_db, 'b-', linewidth=2, label='Resposta do Filtro Projetado')
        
        ax1.set_title('Resposta em Magnitude', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Magnitude (dB)')
        ax1.set_ylim(-120, 10)
        ax1.grid(True, alpha=0.3)
        
        # Adicionar linhas de referência
        self._add_reference_lines(ax1, filter_specs, fc_list, fs)
        
        ax1.legend(fontsize=8, loc='upper right')
        
        # Subplot 2: Fase
        ax2 = self.freq_fig.add_subplot(212)
        phase = np.unwrap(np.angle(H))
        ax2.plot(w, phase, 'b-', linewidth=2)
        ax2.set_xlabel('Frequência (Hz)')
        ax2.set_ylabel('Fase (rad)')
        ax2.set_title('Resposta em Fase')
        ax2.grid(True, alpha=0.3)
        
        # Adicionar linha de referência do atraso de grupo
        if 'order' in filter_specs:
            group_delay = (filter_specs['order'] - 1) / 2
            expected_phase = -w * 2 * np.pi * group_delay / fs
            ax2.plot(w, expected_phase, 'r--', alpha=0.6, 
                    label=f'Fase Linear Ideal (Atraso = {group_delay:.1f})')
            ax2.legend()
        
        self.freq_fig.tight_layout()
        self.freq_canvas.draw()
    
    def _add_reference_lines(self, ax, filter_specs, fc_list, fs):
        """
        Adiciona linhas de referência no gráfico de magnitude
        
        Args:
            ax: Eixo do matplotlib
            filter_specs (dict): Especificações do filtro
            fc_list (list): Frequências de corte
            fs (float): Frequência de amostragem
        """
        try:
            filter_type = filter_specs['filter_type']
            transition_width = filter_specs['transition_width']
            stopband_atten = filter_specs['stopband_atten']
            
            if filter_type == "Passa-Baixa":
                fp = filter_specs['fp_values']
                fs_freq = fp + transition_width
                ax.axvline(fp, color='g', linestyle='--', alpha=0.8, 
                          label=f'fp = {fp:.0f} Hz')
                ax.axvline(fs_freq, color='r', linestyle='--', alpha=0.8, 
                          label=f'fs = {fs_freq:.0f} Hz')
                ax.axvline(fc_list[0], color='orange', linestyle=':', alpha=0.8, 
                          label=f'fc = {fc_list[0]:.0f} Hz')
                          
            elif filter_type == "Passa-Alta":
                fp = filter_specs['fp_values']
                fs_freq = fp - transition_width
                ax.axvline(fs_freq, color='r', linestyle='--', alpha=0.8, 
                          label=f'fs = {fs_freq:.0f} Hz')
                ax.axvline(fp, color='g', linestyle='--', alpha=0.8, 
                          label=f'fp = {fp:.0f} Hz')
                ax.axvline(fc_list[0], color='orange', linestyle=':', alpha=0.8, 
                          label=f'fc = {fc_list[0]:.0f} Hz')
                          
            elif filter_type == "Passa-Banda":
                fp1, fp2 = filter_specs['fp_values']
                fs1 = fp1 - transition_width
                fs2 = fp2 + transition_width
                
                ax.axvline(fs1, color='r', linestyle='--', alpha=0.8, 
                          label=f'fs1 = {fs1:.0f} Hz')
                ax.axvline(fp1, color='g', linestyle='--', alpha=0.8, 
                          label=f'fp1 = {fp1:.0f} Hz')
                ax.axvline(fp2, color='g', linestyle='--', alpha=0.8, 
                          label=f'fp2 = {fp2:.0f} Hz')
                ax.axvline(fs2, color='r', linestyle='--', alpha=0.8, 
                          label=f'fs2 = {fs2:.0f} Hz')
                ax.axvline(fc_list[0], color='orange', linestyle=':', alpha=0.8, 
                          label=f'fc1 = {fc_list[0]:.0f} Hz')
                ax.axvline(fc_list[1], color='orange', linestyle=':', alpha=0.8, 
                          label=f'fc2 = {fc_list[1]:.0f} Hz')
                          
            elif filter_type == "Rejeita-Banda":
                fp1, fp2 = filter_specs['fp_values']
                fs1 = fp1 - transition_width
                fs2 = fp2 + transition_width
            
            ax.axhline(-stopband_atten, color='r', linestyle=':', alpha=0.7, 
                      label=f'Spec: -{stopband_atten:.0f} dB')
            ax.axhline(-3, color='purple', linestyle=':', alpha=0.7, label='-3 dB')
            
        except:
            pass
    
    def update_all_plots(self, results, window_name, filter_specs):
        """
        Atualiza todos os gráficos com novos resultados
        
        Args:
            results (dict): Resultados do projeto do filtro
            window_name (str): Nome da janela
            filter_specs (dict): Especificações do filtro
        """
        self.plot_window(results['window'], window_name)
        self.plot_coefficients(results['coefficients'], results['ideal_response'])
        
        # Adicionar ordem às especificações para o gráfico de fase
        filter_specs_with_order = filter_specs.copy()
        filter_specs_with_order['order'] = results['order']
        
        self.plot_frequency_response(results['coefficients'], filter_specs['fs'], 
                                   results['cutoff_frequencies'], filter_specs_with_order)
    
    def clear_all_plots(self):
        """Limpa todos os gráficos"""
        self.window_fig.clear()
        self.window_canvas.draw()
        
        self.coef_fig.clear()
        self.coef_canvas.draw()
        
        self.freq_fig.clear()
        self.freq_canvas.draw()