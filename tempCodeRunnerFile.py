"""
Arquivo principal para execução do Software de Projeto de Filtros FIR
Desenvolvido seguindo a metodologia do Problema 03
Implementação modular com separação de responsabilidades

Para executar no Windows: python main.py
Para executar no Linux/Mac: python3 main.py
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Adicionar o diretório atual ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    missing_modules = []
    
    try:
        import numpy
    except ImportError:
        missing_modules.append("numpy")
    
    try:
        import matplotlib
    except ImportError:
        missing_modules.append("matplotlib")
    
    try:
        import scipy
    except ImportError:
        missing_modules.append("scipy")
    
    if missing_modules:
        error_msg = "Os seguintes módulos estão faltando:\n"
        error_msg += "\n".join(f"- {module}" for module in missing_modules)
        error_msg += "\n\nInstale-os usando:\n"
        error_msg += f"pip install {' '.join(missing_modules)}"
        
        # Tentar mostrar erro em GUI se possível, senão no terminal
        try:
            root = tk.Tk()
            root.withdraw()  # Esconder janela principal
            messagebox.showerror("Dependências Faltando", error_msg)
            root.destroy()
        except:
            print(f"ERRO: {error_msg}")
        
        return False
    
    return True

def main():
    """Função principal que inicia a aplicação"""
    print("=" * 60)
    print("SOFTWARE DE PROJETO DE FILTROS FIR")
    print("Desenvolvido com metodologia modular")
    print("=" * 60)
    
    # Verificar dependências
    print("Verificando dependências...")
    if not check_dependencies():
        print("Erro: Dependências faltando. Veja a mensagem acima.")
        sys.exit(1)
    
    print("Todas as dependências encontradas ✓")
    
    # Importar módulos principais
    try:
        print("Carregando módulos...")
        from filter_interface import FilterDesignApp
        print("Módulos carregados com sucesso ✓")
        
        # Criar e executar aplicação
        print("Iniciando interface gráfica...")
        root = tk.Tk()
        
        # Configurar ícone se existir
        try:
            # Tentar definir ícone (opcional)
            root.iconbitmap("icon.ico")  # Se você tiver um ícone
        except:
            pass  # Ignorar se não houver ícone
        
        # Configurar fechamento da aplicação
        def on_closing():
            if messagebox.askokcancel("Sair", "Deseja realmente sair do programa?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Inicializar aplicação
        app = FilterDesignApp(root)
        
        print("Interface iniciada com sucesso!")
        print("=" * 60)
        
        # Executar loop principal
        root.mainloop()
        
        print("Aplicação encerrada.")
        
    except ImportError as e:
        error_msg = f"Erro ao importar módulos: {e}\n"
        error_msg += "Verifique se todos os arquivos estão no mesmo diretório:\n"
        error_msg += "- main.py\n"
        error_msg += "- filter_interface.py\n"
        error_msg += "- filter_calculations.py\n"
        error_msg += "- filter_visualizer.py"
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro de Importação", error_msg)
            root.destroy()
        except:
            print(f"ERRO: {error_msg}")
        
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Erro inesperado: {e}"
        print(f"ERRO: {error_msg}")
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()