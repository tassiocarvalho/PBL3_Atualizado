"""
Módulo de Cálculos para Filtros FIR
Contém todas as funções matemáticas e algoritmos de projeto de filtros
"""

import numpy as np
from scipy import signal


class FilterCalculator:
    """
    Classe responsável por todos os cálculos de projeto de filtros FIR
    """
    
    def __init__(self):
        """Inicializa o calculador com parâmetros das janelas"""
        self.window_parameters = {
            'Retangular': {
                'largura_transicao_normalizada': 0.9,
                'ondulacao_banda_passante_db': 0.7416,
                'lobulo_principal_lateral_db': 13,
                'atenuacao_banda_rejeicao_db': 21,
                'expressao': "w(n) = 1"
            },
            'Bartlett': {
                'largura_transicao_normalizada': 2.3,
                'ondulacao_banda_passante_db': 0.185,
                'lobulo_principal_lateral_db': 25,
                'atenuacao_banda_rejeicao_db': 25,
                'expressao': "w(n) = 2 - 2n/M"
            },
            'Hanning': {
                'largura_transicao_normalizada': 3.1,
                'ondulacao_banda_passante_db': 0.0546,
                'lobulo_principal_lateral_db': 31,
                'atenuacao_banda_rejeicao_db': 44,
                'expressao': "w(n) = 0.5 + 0.5*cos(2πn/N)"
            },
            'Hamming': {
                'largura_transicao_normalizada': 3.3,
                'ondulacao_banda_passante_db': 0.0194,
                'lobulo_principal_lateral_db': 41,
                'atenuacao_banda_rejeicao_db': 53,
                'expressao': "w(n) = 0.54 + 0.46*cos(2πn/N)"
            },
            'Blackman': {
                'largura_transicao_normalizada': 5.5,
                'ondulacao_banda_passante_db': 0.0017,
                'lobulo_principal_lateral_db': 57,
                'atenuacao_banda_rejeicao_db': 75,
                'expressao': "w(n) = 0.42 + 0.5*cos(2πn/N) + 0.08*cos(4πn/(N-1))"
            },
            'Kaiser_beta_4.54': {
                'largura_transicao_normalizada': 2.93,
                'ondulacao_banda_passante_db': 0.0274,
                'lobulo_principal_lateral_db': None,
                'atenuacao_banda_rejeicao_db': 50,
                'beta': 4.54,
                'expressao': "I₀(β√(1-(2n/(N-1))²))/I₀(β)"
            },
            'Kaiser_beta_6.76': {
                'largura_transicao_normalizada': 4.32,
                'ondulacao_banda_passante_db': 0.00275,
                'lobulo_principal_lateral_db': None,
                'atenuacao_banda_rejeicao_db': 70,
                'beta': 6.76,
                'expressao': "I₀(β√(1-(2n/(N-1))²))/I₀(β)"
            },
            'Kaiser_beta_8.96': {
                'largura_transicao_normalizada': 5.71,
                'ondulacao_banda_passante_db': 0.000275,
                'lobulo_principal_lateral_db': None,
                'atenuacao_banda_rejeicao_db': 90,
                'beta': 8.96,
                'expressao': "I₀(β√(1-(2n/(N-1))²))/I₀(β)"
            }
        }
    
    def get_available_windows(self, required_attenuation):
        """
        Retorna as janelas que atendem à especificação de atenuação
        
        Args:
            required_attenuation (float): Atenuação mínima requerida em dB
            
        Returns:
            list: Lista de nomes das janelas disponíveis
        """
        available_windows = []
        for window_name, params in self.window_parameters.items():
            if params['atenuacao_banda_rejeicao_db'] >= required_attenuation:
                available_windows.append(window_name)
        return available_windows
    
    def calculate_cutoff_frequencies(self, filter_type, fp_values, transition_width, fs):
        """
        Calcula as frequências de corte baseadas no tipo de filtro
        
        Args:
            filter_type (str): Tipo do filtro
            fp_values (float or list): Frequências da banda passante
            transition_width (float): Largura de transição
            fs (float): Frequência de amostragem
            
        Returns:
            list: Lista das frequências de corte
        """
        fc_list = []
        
        if filter_type == "Passa-Baixa":
            if fp_values >= fs/2:
                raise ValueError("Frequência da banda passante deve ser menor que Fs/2")
            # fc posicionada no centro da banda de transição (prática comum para FIR)
            fs_freq = fp_values + transition_width
            fc = (fp_values + fs_freq) / 2
            fc_list = [fc]
            
        elif filter_type == "Passa-Alta":
            if fp_values >= fs/2:
                raise ValueError("Frequência da banda passante deve ser menor que Fs/2")
            fs_freq = fp_values - transition_width
            if fs_freq <= 0:
                raise ValueError("Para passa-alta: fp - largura_transição deve ser > 0")
            fc = (fs_freq + fp_values) / 2
            fc_list = [fc]
            
        elif filter_type == "Passa-Banda":
            fp1, fp2 = fp_values
            if fp1 >= fp2:
                raise ValueError("Frequência inferior deve ser menor que a superior")
            if fp2 >= fs/2:
                raise ValueError("Frequência superior deve ser menor que Fs/2")
            if fp1 <= 0:
                raise ValueError("Frequência inferior deve ser positiva")
                
            fs1 = fp1 - transition_width
            fs2 = fp2 + transition_width
            if fs1 <= 0:
                raise ValueError("Para passa-banda: fp1 - largura_transição deve ser > 0")
            if fs2 >= fs/2:
                raise ValueError("Para passa-banda: fp2 + largura_transição deve ser < Fs/2")
                
            fc1 = (fs1 + fp1) / 2
            fc2 = (fp2 + fs2) / 2
            fc_list = [fc1, fc2]
            
        elif filter_type == "Rejeita-Banda":
            fp1, fp2 = fp_values
            if fp1 >= fp2:
                raise ValueError("Frequência inferior deve ser menor que a superior")
            if fp2 >= fs/2:
                raise ValueError("Frequência superior deve ser menor que Fs/2")
            if fp1 <= 0:
                raise ValueError("Frequência inferior deve ser positiva")
                
            fs1 = fp1 - transition_width
            fs2 = fp2 + transition_width
            if fs1 <= 0:
                raise ValueError("Para rejeita-banda: fp1 - largura_transição deve ser > 0")
            if fs2 >= fs/2:
                raise ValueError("Para rejeita-banda: fp2 + largura_transição deve ser < Fs/2")
                
            fc1 = (fs1 + fp1) / 2
            fc2 = (fp2 + fs2) / 2
            fc_list = [fc1, fc2]
            
        return fc_list
    
    def calculate_filter_order(self, transition_width, fs, window_name, stopband_atten=None):
        """
        Calcula a ordem do filtro baseada na janela e especificações
        
        Args:
            transition_width (float): Largura de transição em Hz
            fs (float): Frequência de amostragem
            window_name (str): Nome da janela
            stopband_atten (float): Atenuação desejada (para Kaiser)
            
        Returns:
            int: Ordem do filtro
        """
        delta_f_norm = transition_width / fs
        window_params = self.window_parameters[window_name]
        
        if 'Kaiser' in window_name:
            A = stopband_atten if stopband_atten else window_params['atenuacao_banda_rejeicao_db']
            beta = window_params['beta']
            M = (A - 8) / (2.285 * 2 * np.pi * delta_f_norm)
            order = int(np.ceil(M))
        else:
            factor = window_params['largura_transicao_normalizada']
            N_calc = factor / delta_f_norm
            order = int(np.ceil(N_calc))
        
        # Garantir ordem ímpar para simetria
        if order % 2 == 0:
            order += 1
        
        # Limitar ordem
        order = max(11, min(10001, order))
        
        return order
    
    def ideal_lowpass(self, N, fc_norm):
        """Calcula filtro passa-baixa ideal"""
        M = N - 1
        n = np.arange(N)
        h = np.zeros(N)
        
        for i in range(N):
            n_centered = n[i] - M/2
            
            if abs(n_centered) < 1e-10:
                h[i] = 2 * fc_norm
            else:
                omega_c = fc_norm * np.pi
                h[i] = 2 * fc_norm * np.sin(omega_c * n_centered) / (omega_c * n_centered)
        
        return h
    
    def ideal_highpass(self, N, fc_norm):
        """Calcula filtro passa-alta ideal - ADAPTADO"""
        M = N - 1
        n = np.arange(N)
        h = np.zeros(N)
        
        for i in range(N):
            n_centered = n[i] - M/2
            
            if abs(n_centered) < 1e-10:
                h[i] = 1.0 - fc_norm
            else:
                # Impulso delta menos passa-baixa
                delta_impulse = np.sin(np.pi * n_centered) / (np.pi * n_centered)
                sinc_arg = fc_norm * n_centered
                lowpass = fc_norm * np.sin(np.pi * sinc_arg) / (np.pi * sinc_arg)
                h[i] = delta_impulse - lowpass

        return h

    def ideal_bandpass(self, N, fc1_norm, fc2_norm):
        """Calcula filtro passa-banda ideal"""
        M = N - 1
        n = np.arange(N)
        h = np.zeros(N)
        
        for i in range(N):
            n_centered = n[i] - M/2
            
            if abs(n_centered) < 1e-10:
                h[i] = (fc2_norm - fc1_norm)
            else:
                omega_c1 = fc1_norm * np.pi
                omega_c2 = fc2_norm * np.pi
                h[i] = (fc2_norm * np.sin(omega_c2 * n_centered) / (omega_c2 * n_centered) - 
                        fc1_norm * np.sin(omega_c1 * n_centered) / (omega_c1 * n_centered))
        
        return h
    
    def ideal_bandstop(self, N, fc1_norm, fc2_norm):
        """Calcula filtro rejeita-banda ideal"""
        M = N - 1
        n = np.arange(N)
        h = np.zeros(N)
        
        for i in range(N):
            n_centered = n[i] - M / 2
            
            if abs(n_centered) < 1e-10:
                h[i] = 1 - (fc2_norm - fc1_norm)
            else:
                
                pass_all = np.sin(np.pi * n_centered) / (np.pi * n_centered)
                stop_band = (np.sin(np.pi * fc2_norm * n_centered) - 
                           np.sin(np.pi * fc1_norm * n_centered)) / (np.pi * n_centered)
                h[i] = pass_all - stop_band               
                
        return h
    
    def create_window(self, window_name, order, fftbins= False):
        """
        Cria a função de janelamento
        
        Args:
            window_name (str): Nome da janela
            order (int): Ordem do filtro
            
        Returns:
            numpy.ndarray: Janela gerada
        """
        if 'Kaiser' in window_name:
            beta = self.window_parameters[window_name]['beta']
            window = signal.get_window(('kaiser', beta), order, fftbins= False)
        elif window_name == 'Retangular':
            window = signal.get_window('boxcar', order, fftbins= False)
        elif window_name == 'Bartlett':
            window = signal.get_window('bartlett', order, fftbins= False)
        elif window_name == 'Hanning':
            window = signal.get_window('hann', order, fftbins= False)
        elif window_name == 'Hamming':
            window = signal.get_window('hamming', order, fftbins= False)
        elif window_name == 'Blackman':
            window = signal.get_window('blackman', order, fftbins= False)
        else:
            raise ValueError(f"Janela não suportada: {window_name}")
            
        return window
    
    def design_filter(self, filter_type, fs, fp_values, transition_width, 
                     stopband_atten, window_name):
        """
        Projeta o filtro FIR completo
        
        Args:
            filter_type (str): Tipo do filtro
            fs (float): Frequência de amostragem
            fp_values: Frequências da banda passante
            transition_width (float): Largura de transição
            stopband_atten (float): Atenuação na banda de rejeição
            window_name (str): Nome da janela
            
        Returns:
            dict: Dicionário com todos os resultados do projeto
        """
        # Calcular frequências de corte
        fc_list = self.calculate_cutoff_frequencies(filter_type, fp_values, 
                                                   transition_width, fs)
        
        # Calcular ordem do filtro
        order = self.calculate_filter_order(transition_width, fs, window_name, 
                                          stopband_atten)
        
        # Projetar filtro ideal
        nyquist = fs / 2
        
        if filter_type == "Passa-Baixa":
            fc_norm = fc_list[0] / nyquist
            h_ideal = self.ideal_lowpass(order, fc_norm)
        elif filter_type == "Passa-Alta":
            fc_norm = fc_list[0] / nyquist
            h_ideal = self.ideal_highpass(order, fc_norm)
        elif filter_type == "Passa-Banda":
            fc1_norm = fc_list[0] / nyquist
            fc2_norm = fc_list[1] / nyquist
            h_ideal = self.ideal_bandpass(order, fc1_norm, fc2_norm)
        else:  # Rejeita-Banda
            fc1_norm = fc_list[0] / nyquist
            fc2_norm = fc_list[1] / nyquist
            h_ideal = self.ideal_bandstop(order, fc1_norm, fc2_norm)
        
        # Criar janela
        window = self.create_window(window_name, order)
        
        # Aplicar janelamento
        h_windowed = h_ideal * window
        
        # Calcular resposta em frequência
        w, H = signal.freqz(h_windowed, worN=8192, fs=fs)
        
        # Retornar todos os resultados
        return {
            'coefficients': h_windowed,
            'ideal_response': h_ideal,
            'window': window,
            'order': order,
            'cutoff_frequencies': fc_list,
            'frequency_response': (w, H),
            'delta_f_norm': transition_width / fs,
            'window_params': self.window_parameters[window_name]
        }
    
    def generate_detailed_report(self, filter_specs, results):
        """
        Gera relatório detalhado dos cálculos
        
        Args:
            filter_specs (dict): Especificações do filtro
            results (dict): Resultados do projeto
            
        Returns:
            str: Relatório formatado
        """
        fs = filter_specs['fs']
        fp_values = filter_specs['fp_values']
        transition_width = filter_specs['transition_width']
        stopband_atten = filter_specs['stopband_atten']
        filter_type = filter_specs['filter_type']
        window_name = filter_specs['window_name']
        
        order = results['order']
        fc_list = results['cutoff_frequencies']
        h_windowed = results['coefficients']
        delta_f_norm = results['delta_f_norm']
        
        report = f"""PROJETO DE FILTRO FIR - RESULTADOS DETALHADOS
{'='*60}

ESPECIFICAÇÕES FORNECIDAS:
• Tipo de Filtro: {filter_type}
• Frequência de Amostragem: {fs:.0f} Hz"""
        
        if filter_type in ["Passa-Baixa", "Passa-Alta"]:
            report += f"""
• Frequência da Borda da Banda Passante: {fp_values:.0f} Hz"""
        else:
            report += f"""
• Frequência Inferior da Banda: {fp_values[0]:.0f} Hz
• Frequência Superior da Banda: {fp_values[1]:.0f} Hz
• Largura da Banda: {fp_values[1] - fp_values[0]:.0f} Hz"""
        
        report += f"""
• Largura de Transição: {transition_width:.0f} Hz
• Atenuação na Banda de Rejeição: ≥{stopband_atten} dB
• Janela Selecionada: {window_name}

CÁLCULOS REALIZADOS:"""
        
        # Adicionar cálculos específicos por tipo de filtro
        if filter_type == "Passa-Baixa":
            fs_freq = fp_values + transition_width
            report += f"""
• Frequência de Stopband: fs = {fp_values:.0f} + {transition_width:.0f} = {fs_freq:.0f} Hz
• Frequência de Corte (centrada): fc = ({fp_values:.0f} + {fs_freq:.0f})/2 = {fc_list[0]:.0f} Hz"""
            
        elif filter_type == "Passa-Alta":
            fs_freq = fp_values - transition_width
            report += f"""
• Frequência de Stopband: fs = {fp_values:.0f} - {transition_width:.0f} = {fs_freq:.0f} Hz
• Frequência de Corte (centrada): fc = ({fs_freq:.0f} + {fp_values:.0f})/2 = {fc_list[0]:.0f} Hz"""
            
        elif filter_type == "Passa-Banda":
            fs1 = fp_values[0] - transition_width
            fs2 = fp_values[1] + transition_width
            report += f"""
• Frequência de Stopband Inferior: fs1 = {fp_values[0]:.0f} - {transition_width:.0f} = {fs1:.0f} Hz
• Frequência de Stopband Superior: fs2 = {fp_values[1]:.0f} + {transition_width:.0f} = {fs2:.0f} Hz
• Frequência de Corte Inferior: fc1 = ({fs1:.0f} + {fp_values[0]:.0f})/2 = {fc_list[0]:.0f} Hz
• Frequência de Corte Superior: fc2 = ({fp_values[1]:.0f} + {fs2:.0f})/2 = {fc_list[1]:.0f} Hz"""
            
        else:  # Rejeita-Banda
            fs1 = fp_values[0] - transition_width
            fs2 = fp_values[1] + transition_width
            report += f"""
• Frequência de Transição Inferior: fs1 = {fp_values[0]:.0f} - {transition_width:.0f} = {fs1:.0f} Hz
• Frequência de Transição Superior: fs2 = {fp_values[1]:.0f} + {transition_width:.0f} = {fs2:.0f} Hz
• Frequência de Corte Inferior: fc1 = ({fs1:.0f} + {fp_values[0]:.0f})/2 = {fc_list[0]:.0f} Hz
• Frequência de Corte Superior: fc2 = ({fp_values[1]:.0f} + {fs2:.0f})/2 = {fc_list[1]:.0f} Hz
• Banda Rejeitada: {fp_values[0]:.0f} Hz a {fp_values[1]:.0f} Hz
• Bandas Passantes: 0 Hz a {fs1:.0f} Hz e {fs2:.0f} Hz a {fs/2:.0f} Hz"""
        
        report += f"""
• Largura de Transição Normalizada: Δf = {transition_width:.0f}/{fs:.0f} = {delta_f_norm:.6f}

CÁLCULO DA ORDEM DO FILTRO:
• Janela: {window_name}
• Fator da Janela: {results['window_params']['largura_transicao_normalizada']}
• N = {results['window_params']['largura_transicao_normalizada']}/Δf = {results['window_params']['largura_transicao_normalizada']}/{delta_f_norm:.6f} = {results['window_params']['largura_transicao_normalizada']/delta_f_norm:.1f}
• Ordem escolhida (ímpar): N = {order}

CARACTERÍSTICAS DO FILTRO PROJETADO:
• Tipo: FIR Fase Linear Tipo I
• Ordem: M = {order-1}
• Comprimento: N = {order}"""
        
        if len(fc_list) == 1:
            report += f"""
• Frequência de Corte Normalizada: fc = {fc_list[0]/(fs/2):.6f}"""
        else:
            report += f"""
• Frequências de Corte Normalizadas: 
  - fc1 = {fc_list[0]/(fs/2):.6f}
  - fc2 = {fc_list[1]/(fs/2):.6f}"""
        
        report += f"""
• Atraso de Grupo: {(order-1)/2:.1f} amostras
• Simetria: h(n) = h(N-1-n) ✓

PRIMEIROS COEFICIENTES CALCULADOS:"""
        
        # Mostrar alguns coeficientes
        center = (order - 1) // 2
        for i in range(min(6, len(h_windowed))):
            report += f"""
h({i}) = {h_windowed[i]:.8f}"""
        
        if len(h_windowed) > 6:
            report += f"""
...
h({center}) = {h_windowed[center]:.8f} (centro)
...
h({len(h_windowed)-1}) = {h_windowed[-1]:.8f}"""
        
        report += f"""

PROPRIEDADES DA JANELA {window_name.upper()}:
• Atenuação na Banda de Rejeição: {results['window_params']['atenuacao_banda_rejeicao_db']} dB
• Largura de Transição: {results['window_params']['largura_transicao_normalizada']}/N
• Ondulação na Banda Passante: {results['window_params']['ondulacao_banda_passante_db']} dB"""
        
        if results['window_params'].get('lobulo_principal_lateral_db'):
            report += f"""
• Lóbulo Principal vs Lateral: {results['window_params']['lobulo_principal_lateral_db']} dB"""
        
        report += f"""
• Expressão Matemática: {results['window_params']['expressao']}

O filtro resultante deve atender às especificações de desempenho
conforme verificado na resposta em frequência.
"""
        
        return report