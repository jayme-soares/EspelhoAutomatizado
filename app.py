import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import zipfile
import base64
from datetime import datetime

# =====================================================================
# 1. DICIONÁRIOS DE MAPEAMENTO
# =====================================================================

PREFIXOS_DICT = {
    'NI201LFP-B': 'PRE-VENDA', 'NI201LLP-B': 'NOVAS LIGAÇÕES', 'NI201LRP-B': 'CORTE',
    'NI201SLP-B': 'NOVAS LIGAÇÕES', 'NI202LFP-B': 'PRE-VENDA', 'NI202LLP-B': 'NOVAS LIGAÇÕES',
    'NI202LRP-B': 'CORTE', 'NI202SLP-B': 'NOVAS LIGAÇÕES', 'NI203LFP-B': 'PRE-VENDA',
    'NI203LLP-B': 'NOVAS LIGAÇÕES', 'NI203LRP-B': 'CORTE', 'NI203SLP-B': 'NOVAS LIGAÇÕES',
    'NI204LFP-B': 'PRE-VENDA', 'NI204LLP-B': 'NOVAS LIGAÇÕES', 'NI204LRP-B': 'CORTE',
    'NI204SLP-B': 'NOVAS LIGAÇÕES', 'NI205LRP-B': 'CORTE', 'NI205SLP-B': 'NOVAS LIGAÇÕES',
    'NI206LRP-B': 'CORTE', 'NI206SLP-B': 'NOVAS LIGAÇÕES', 'NI207SLP-B': 'NOVAS LIGAÇÕES',
    'NI207SRP-B': 'CORTE', 'NI208LRP-B': 'CORTE', 'NI209LRP-B': 'CORTE',
    'NI210SRP-B': 'CORTE', 'NI211LRP-B': 'CORTE', 'NI212LRP-B': 'CORTE',
    'NI213LRP-B': 'CORTE', 'NI214LRP-B': 'CORTE', 'NI215LRP-B': 'CORTE',
    'NI216LRP-B': 'CORTE', 'NI217LRP-B': 'CORTE', 'NI218LRP-B': 'CORTE',
    'NI219LLP-B': 'NOVAS LIGAÇÕES', 'NI220LLP-B': 'NOVAS LIGAÇÕES', 'NI221LLP-B': 'NOVAS LIGAÇÕES',
    'NI222LLP-B': 'NOVAS LIGAÇÕES', 'NI223LLP-B': 'NOVAS LIGAÇÕES', 'NI224LLP-B': 'NOVAS LIGAÇÕES',
    'NI225LLP-B': 'NOVAS LIGAÇÕES', 'NI226SLP-B': 'NOVAS LIGAÇÕES'
}

CICLOS_DICT = {
    'AE_CONSUMIDOR_INDIVIDUAL': 'Emergência', 'AE_CONSUMIDOR_PRIORITÀRIO': 'Emergência',
    'AE_PERIGO_IMINENTE_2.0': 'Emergência', 'AE_PERIGO_IMINENTE_2.1': 'Emergência',
    'AE_PERIGO_IMINENTE_2.2': 'Emergência', 'AE_POSTE_RAMAL_ARRED': 'Emergência',
    'AE_VITAL_ACID_VITIMA': 'Emergência', 'AdE_INC_07_Incidencia MT_Ramal': 'Emergência',
    'Ciclo 1 - Desligamento a Pedido Ret Medidor e Ramal Aerea': 'Corte', 'Ciclo 1.1 - Desligamento a Pedido Ret Medidor e Ramal DAT': 'Corte',
    'Ciclo 1.2 - Desligamento Ligação Temporária Aerea': 'Novas', 'Ciclo 1.3 - Desligamento Ligação Temporária DAT': 'Novas',
    'Ciclo 10 - Religação - Poste Aérea': 'Religa', 'Ciclo 11 - Religação - Poste DAT': 'Religa',
    'Ciclo 12 - Religação - Instalação de Ramal Aérea': 'Religa', 'Ciclo 13 - Religação - Instalação de Ramal DAT': 'Religa',
    'Ciclo 14 - Religação - Leiturista': 'Religa', 'Ciclo 15 - Corte Prioridade 1 - Medidor': 'Corte',
    'Ciclo 15 - Religação Negociador Digital': 'Religa', 'Ciclo 16 - Corte Prioridade 2 - Medidor': 'Corte',
    'Ciclo 17 - Corte Prioridade 3 - Medidor': 'Corte', 'Ciclo 2 - Recorte - Aérea': 'Corte',
    'Ciclo 2.1 - Recorte - DAT': 'Corte', 'Ciclo 2.2 - Recorte - Medidor': 'Corte',
    'Ciclo 22 - Corte - Prioridade 1 - Poste Aérea': 'Corte', 'Ciclo 23 - Corte - Prioridade 2 - Poste Aérea': 'Corte',
    'Ciclo 24 - Corte - Prioridade 3 - Poste Aérea': 'Corte', 'Ciclo 29 - Corte - Prioridade 1 - Poste DAT': 'Corte',
    'Ciclo 3 - Corte  - Massivo medidor': 'Corte', 'Ciclo 3.1 - Corte  - Massivo poste Aérea': 'Corte',
    'Ciclo 3.2 - Corte  - Massivo poste DAT': 'Corte', 'Ciclo 3.3 - Corte  - Massivo Ret Ramal Aérea': 'Corte',
    'Ciclo 30 - Corte - Prioridade 2 - Poste DAT': 'Corte', 'Ciclo 32 - Lig Nova Monofásica em rede Convencional Venda de PDR-AM01_NC3.1': 'Novas',
    'Ciclo 32 - Lig Nova Monofásica em rede Convencional sem Venda de PDR': 'Novas', 'Ciclo 36 - Corte - Prioridade 1 - Retirada de Ramal Aérea': 'Corte',
    'Ciclo 36 - Lig Nova Monofásica em rede não Convencional Venda de PDR_AM02_NC3.1': 'Novas', 'Ciclo 37 - Corte - Prioridade 2 - Retirada de Ramal Aérea': 'Corte',
    'Ciclo 38 - Lig Nova Polifásica em rede Convencional Venda de PDR_AM01_NC3.1': 'Novas', 'Ciclo 38 - Lig Nova Polifásica em rede Convencional sem Venda de PDR': 'Novas',
    'Ciclo 40 - Lig Nova Polifásica em rede não Convencional Venda de PDR_AM02_NC3.6': 'Novas', 'Ciclo 42 - Lig Nova Polifásica em rede não Convencional Venda de PDR_AM02_NC3.1': 'Novas',
    'Ciclo 43 - Corte - Prioridade 1 - Retirada de Ramal DAT': 'Corte', 'Ciclo 44 - Corte - Prioridade 2 - Retirada de Ramal DAT': 'Corte',
    'Ciclo 45 - Conexão de Novas Ligações': 'Novas', 'Ciclo 46 - Acréscimo De CARGA em rede Convencional sem Venda de PDR': 'Novas',
    'Ciclo 46 - Acréscimo De CARGA em rede Convencional sem Venda de PDR_AM01_NC3.2': 'Novas', 'Ciclo 48 - Acréscimo De CARGA em rede Convencional sem Venda de PDR_AM01_NC3.7': 'Novas',
    'Ciclo 48 - Acréscimo De CARGA em rede não Convencional sem Venda de PDR': 'Novas', 'Ciclo 5 - Fiscalização': 'Corte',
    'Ciclo 5.1 - Fiscalização DAT': 'Corte', 'Ciclo 50 - Acréscimo De CARGA em rede não Convenc. sem Venda de PDR_AM02_NC3.2': 'Novas',
    'Ciclo 50 - Acréscimo De CARGA em rede não Convencional sem Venda de PDR': 'Novas', 'Ciclo 51 - Corte - Prioridade 1 Sentinela MI': 'Corte',
    'Ciclo 52 - Corte - Prioridade 2 Sentinela MI': 'Corte', 'Ciclo 53 - Corte - Prioridade 3 Sentinela MI': 'Corte',
    'Ciclo 53 - Decréscimo De CARGA em rede Convencional AM01_NC3.2': 'Novas', 'Ciclo 54 - Decréscimo De CARGA em rede Convencional AM01_NC3.7': 'Novas',
    'Ciclo 55 - Decréscimo De CARGA em rede não Convencional AM02_NC3.2': 'Novas', 'Ciclo 57 - MML e RP M-MONOFÁSICO em rede Convenc. sem VENDA DE PADRÃO AM01_NC3.3': 'Novas',
    'Ciclo 58 - Corte - Massivo - Leiturista': 'Corte', 'Ciclo 59 - MML e RP M-MONOF. em rede não Convenc. sem VENDA DE PADRÃO AM02_NC3.8': 'Novas',
    'Ciclo 59 - MML e RP M-MONOFÁSICO em rede não Convencional sem VENDA DE PADRÃO': 'Novas', 'Ciclo 6 - Sem contrato': 'Corte',
    'Ciclo 6.1 - Sem contrato DAT': 'Corte', 'Ciclo 61 - MML e RP M-MONOF. em rede não Convenc. sem VENDA DE PADRÃO AM02_NC3.3': 'Novas',
    'Ciclo 63 - MML e RP Polifásico em rede Convenc. sem VENDA DE PADRÃO AM01_NC3.3': 'Novas', 'Ciclo 65 - MML e RP Polifásico em rede Convenc. sem VENDA DE PADRÃO AM01_NC3.8': 'Novas',
    'Ciclo 67 - MML e RP Polifás. em rede não Convenc. sem VENDA DE PADRÃO AM02_NC3.3': 'Novas', 'Ciclo 68 - RRL e SR em rede Convencional': 'Novas',
    'Ciclo 68 - RRL e SR em rede Convencional AM01_NC3.3': 'Novas', 'Ciclo 69 - RRL e SR em rede não Convencional AM02_NC3.8': 'Novas',
    'Ciclo 71 - Exteriorização de Medidor em rede Convencional': 'Novas', 'Ciclo 71 - Exteriorização de Medidor em rede Convencional AM01_NC3.3': 'Novas',
    'Ciclo 72 - Exteriorização de Medidor em rede não Convencional': 'Novas', 'Ciclo 72 - Exteriorização de Medidor em rede não Convencional AM02_NC3.3': 'Novas',
    'Ciclo 73 - Geração Distribuída em rede Convencional': 'Novas', 'Ciclo 73 - Geração Distribuída em rede Convencional AM01_NC3.5': 'Novas',
    'Ciclo 74 - Geração Distribuída em rede não Convencional': 'Novas', 'Ciclo 74 - Geração Distribuída em rede não Convencional AM02_NC3.5': 'Novas',
    'Ciclo 75 - Instalação e Desinstalação de Provisória em rede Convec. AM01_NC1.3': 'Novas', 'Ciclo 78 - Vistoria de Medidor em rede Convencional': 'Novas',
    'Ciclo 78 - Vistoria de Medidor em rede Convencional AM01_NC1.2': 'Novas', 'Ciclo 79 - Vistoria de Medidor em rede não convencional': 'Novas',
    'Ciclo 79 - Vistoria de Medidor em rede não convencional AM02_NC1.4': 'Novas', 'Ciclo 80 - Aferição de Medidor em rede Convencional': 'Aferição',
    'Ciclo 80 - Aferição de Medidor em rede Convencional AM03_NC1.2': 'Aferição', 'Ciclo 81 - Aferição de Medidor em rede não Convencional': 'Aferição',
    'Ciclo 81 - Aferição de Medidor em rede não Convencional AM04_NC1.4': 'Aferição', 'Ciclo 82 - Substituição de Medidor em rede Convencional': 'Novas',
    'Ciclo 82 - Substituição de Medidor em rede Convencional AM01_NC3.5': 'Novas', 'Ciclo 83 - Substituição de Medidor em rede não Convencional': 'Novas',
    'Ciclo 83 - Substituição de Medidor em rede não Convencional AM02_NC3.5': 'Novas', 'Ciclo 84 - Reclamação de Serviço de Ligação Nova AM01_NC3.3': 'Novas',
    'Ciclo 87 - Geração Distribuída em rede Convencional - Vistoria': 'Pre Venda', 'Ciclo 89 - Serviços de Vistoria da LN': 'Pre Venda',
    'Ciclo 9 - Religação - Medidor': 'Religa', 'Ciclo 90 - RP e MML': 'Pre Venda',
    'Ciclo 92 - Serviços de Cobrança e Inadimplência': 'Vistoria', 'OPE_SCR_01_7.1_ Inspeção Caminhão - Retirada de Ramal': 'N/A'
}

# =====================================================================
# 2. CLASSES E FUNÇÕES DE GERAÇÃO DE PDF
# =====================================================================
class PDFEspelho(FPDF):
    def __init__(self, data_atual):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.data_atual = data_atual
        self.equipe = ""
        self.chefe = ""
        self.setor_equipe = ""
        self.print_table_header = True 
        self.set_auto_page_break(auto=True, margin=10)
        
    def header(self):
        pass

def desenhar_equipe(pdf, equipe, df_equipe, ordens_manuais, hoje_date):
    """Função encapsulada que desenha o espelho de UMA equipe inteira no PDF passado."""
    pdf.equipe = equipe
    pdf.chefe = str(df_equipe['Chefe/Responsável de Equipe'].iloc[0])
    pdf.setor_equipe = PREFIXOS_DICT.get(equipe, "Desconhecido")
    pdf.print_table_header = True
    
    pdf.add_page() # Inicia uma nova folha para esta equipe

    headers = ['Cód TdC', 'Nº Serviço', 'Tipo Serviço', 'Cód Cliente', 'Nome Cliente', 'Endereço', 'Bairro', 'Coord', 'Medidor', 'Prazo', 'Setor']
    col_widths = [13, 17, 39, 15, 42, 50, 25, 17, 20, 15, 22]
    
    linhas_processadas = []
    for _, row in df_equipe.iterrows():
        c_tdc = str(row.get('Código TdC', ''))
        n_servico = str(row.get('Numero de Serviço', ''))
        
        tipo_servico_raw = str(row.get('Tipo Remessa WIN', ''))
        tipo_servico = tipo_servico_raw.split('-', 1)[-1].strip()
        
        c_cliente = str(row.get('Código Cliente', ''))
        n_cliente = str(row.get('Nome e Sobrenome Cliente', ''))
        endereco = str(row.get('Endereço Completo', ''))
        bairro = str(row.get('Bairro', ''))
        coords = str(row.get('Coordenadas', ''))
        medidor = str(row.get('Número De Fabricação Do Medidor', ''))
        prazo = str(row.get('Prazo ANS Legal', ''))[:10] 
        setor_op = str(row.get('Setor Operacao', ''))
        
        linha_dados = [c_tdc, n_servico, tipo_servico, c_cliente, n_cliente, endereco, bairro, coords, medidor, prazo, setor_op]
        
        linhas_processadas.append({
            'dados': linha_dados,
            'data_ordem': row.get('Data_Prazo_Obj'),
            'tipo_servico_raw': tipo_servico_raw,
            'n_servico': n_servico
        })

    # =========================================================
    # --- GERAÇÃO DO CABEÇALHO DA PÁGINA ---
    # =========================================================
    pdf.set_font('Arial', 'B', 19)
    pdf.set_fill_color(220, 220, 220) 
    pdf.cell(0, 20, 'Espelho Diário de Serviços', border=3, ln=1, align='C', fill=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, f"Data: {pdf.data_atual}", border=0, ln=1, align='R')
    pdf.cell(0, 5, f"Equipe: {pdf.equipe} - {pdf.chefe}", border=0, ln=1, align='L')
    pdf.cell(0, 5, f"Setor da Equipe: {pdf.setor_equipe}", border=0, ln=1, align='L')
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 7)
    pdf.set_fill_color(220, 220, 220) 
    for i in range(len(headers)):
        pdf.cell(col_widths[i], 6, headers[i], border=3, align='C', fill=True)
    pdf.ln()
    
    # =========================================================
    # --- GERAÇÃO DA TABELA (ZEBRADO E DESTAQUES) ---
    # =========================================================
    lista_resumo_prioridades = []
    
    for idx, item in enumerate(linhas_processadas):
        linha_dados = item['dados']
        data_ordem = item['data_ordem']
        tipo_servico_raw = item['tipo_servico_raw']
        n_servico = item['n_servico']
        
        motivos_destaque = []
        if data_ordem == hoje_date:
            motivos_destaque.append("Vencimento")
        if 'juizado' in tipo_servico_raw.lower():
            motivos_destaque.append("Juizado")
        if n_servico in ordens_manuais:
            motivos_destaque.append("Solicitada")
        
        if motivos_destaque:
            string_motivo = " / ".join(motivos_destaque)
            lista_resumo_prioridades.append((n_servico, string_motivo))

            pdf.set_font('Arial', 'B', 7) 
            pdf.set_fill_color(255, 200, 200) 
            aplicar_fill = True
        else:
            pdf.set_font('Arial', '', 7) 
            if idx % 2 == 0:
                pdf.set_fill_color(245, 245, 245) 
                aplicar_fill = True
            else:
                aplicar_fill = False 

        altura_texto = 4 
        max_linhas = 1
        for i in range(len(linha_dados)):
            largura_texto = pdf.get_string_width(linha_dados[i])
            secao = int(largura_texto / (col_widths[i] - 1)) + 1
            if secao > max_linhas:
                max_linhas = secao
                
        altura_celula = max_linhas * altura_texto
        
        if pdf.get_y() + altura_celula > 195:
            pdf.add_page()
            if pdf.print_table_header:
                pdf.set_font('Arial', 'B', 7)
                pdf.set_fill_color(220, 220, 220)
                for i in range(len(headers)):
                    pdf.cell(col_widths[i], 6, headers[i], border=1, align='C', fill=True)
                pdf.ln()
            
            if motivos_destaque:
                pdf.set_font('Arial', 'B', 7) 
                pdf.set_fill_color(255, 200, 200)
            elif idx % 2 == 0:
                pdf.set_font('Arial', '', 7) 
                pdf.set_fill_color(245, 245, 245)
            else:
                pdf.set_font('Arial', '', 7) 
            
        x_inicial = pdf.get_x()
        y_inicial = pdf.get_y()
        
        for i in range(len(linha_dados)):
            x_atual = pdf.get_x()
            pdf.cell(col_widths[i], altura_celula, txt="", border=1, fill=aplicar_fill)
            pdf.set_xy(x_atual, y_inicial)
            pdf.multi_cell(col_widths[i], altura_texto, txt=linha_dados[i], border=0, align='C')
            pdf.set_xy(x_atual + col_widths[i], y_inicial)
            
        pdf.set_y(y_inicial + altura_celula)

    # =========================================================
    # --- RODAPÉ: RESUMO E OBSERVAÇÕES ---
    # =========================================================
    pdf.print_table_header = False 
    
    altura_estimada_rodape = max(35, 20 + (len(lista_resumo_prioridades) * 6))
    if pdf.get_y() + altura_estimada_rodape > 195:
        pdf.add_page()
    
    pdf.ln(5)
    y_rodape = pdf.get_y()

    pdf.set_font('Arial', 'B', 8)
    pdf.set_fill_color(220, 220, 220) 
    pdf.cell(100, 6, "RESUMO DE ORDENS DA EQUIPE", border=1, ln=1, align='C', fill=True)
    
    pdf.set_font('Arial', '', 8)
    pdf.cell(100, 5, f"Total de ordens atribuídas: {len(df_equipe)}", border='LR', ln=1)
    pdf.cell(100, 5, f"Total de ordens prioritárias: {len(lista_resumo_prioridades)}", border='LRB', ln=1)
    pdf.ln(2)

    if len(lista_resumo_prioridades) > 0:
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(220, 220, 220) 
        pdf.cell(30, 5, "Nº Serviço", border=1, align='C', fill=True)
        pdf.cell(70, 5, "Tipo de Prioridade", border=1, align='C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 8)
        for prio_servico, prio_motivo in lista_resumo_prioridades:
            pdf.cell(30, 5, prio_servico, border=1, align='C')
            pdf.cell(70, 5, prio_motivo, border=1, align='C')
            pdf.ln()

    pdf.set_xy(115, y_rodape)
    pdf.set_font('Arial', 'B', 8)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(170, 6, "OBSERVAÇÕES E ANOTAÇÕES", border=1, ln=1, align='C', fill=True)

    linhas_pauta = max(7, len(lista_resumo_prioridades) + 5)
    for i in range(linhas_pauta):
        pdf.set_x(115)
        borda = 'LRB' if i == linhas_pauta - 1 else 'LR'
        pdf.cell(170, 6, "", border=borda, ln=1)
        if i < linhas_pauta - 1:
            pdf.line(117, pdf.get_y(), 283, pdf.get_y())

def gerar_pdf_individual(equipe, df_equipe, ordens_manuais, hoje_date, data_hoje_str):
    pdf = PDFEspelho(data_atual=data_hoje_str)
    desenhar_equipe(pdf, equipe, df_equipe, ordens_manuais, hoje_date)
    return pdf.output(dest='S').encode('latin1')

def gerar_pdf_mestre(equipes_agrupadas, ordens_manuais, hoje_date, data_hoje_str):
    pdf = PDFEspelho(data_atual=data_hoje_str)
    for equipe, df_equipe in equipes_agrupadas:
        desenhar_equipe(pdf, equipe, df_equipe, ordens_manuais, hoje_date)
    return pdf.output(dest='S').encode('latin1')

# =====================================================================
# 3. INTERFACE STREAMLIT E LÓGICA DE PROCESSAMENTO
# =====================================================================

st.set_page_config(page_title="Gerador de Espelhos", layout="wide")
st.title("Gerador de Espelhos de Serviço")

uploaded_file = st.file_uploader("Faça o upload da base (Excel)", type=["xlsx"])

st.markdown("### Configurações Adicionais")
ordens_input = st.text_area(
    "Ordens Prioridade Manual (Opcional):",
    placeholder="Cole os números das ordens solicitadas manualmente. (Separe por vírgula, espaço ou quebra de linha)"
)

if uploaded_file is not None:
    try:
        with st.spinner("Estruturando os dados base..."):
            df_tdc = pd.read_excel(uploaded_file, sheet_name='TdC', dtype=str)
            df_med = pd.read_excel(uploaded_file, sheet_name='Medidores', dtype=str)
            
            ordens_manuais = [x.strip() for x in ordens_input.replace(',', ' ').split() if x.strip()]
            hoje_date = datetime.now().date()
            data_hoje_str = datetime.now().strftime("%d/%m/%Y")

            df_med = df_med[['Código TdC', 'Número De Fabricação Do Medidor']].drop_duplicates()
            df_final = pd.merge(df_tdc, df_med, on='Código TdC', how='left')
            df_final.fillna('', inplace=True)
            
            df_final = df_final[df_final['Equipe'].isin(PREFIXOS_DICT.keys())]
            
            col_ciclo = 'Ciclo de trabalho' if 'Ciclo de trabalho' in df_final.columns else 'Tipo TdC'
            df_final['Setor Operacao'] = df_final[col_ciclo].map(CICLOS_DICT).fillna('N/A')
            
            if 'Latitude' in df_final.columns and 'Longitude' in df_final.columns:
                df_final['Coordenadas'] = df_final['Latitude'].astype(str) + ", " + df_final['Longitude'].astype(str)
            else:
                df_final['Coordenadas'] = ''

            df_final['Data_Prazo_Obj'] = pd.to_datetime(df_final['Prazo ANS Legal'], errors='coerce', dayfirst=True).dt.date
            
            df_final['Setor_Equipe'] = df_final['Equipe'].map(PREFIXOS_DICT)
            setores_disponiveis = sorted([str(s) for s in df_final['Setor_Equipe'].unique() if pd.notna(s)])

        st.success("Base processada com sucesso!")
        st.markdown("---")

        # =========================================================
        # --- SELEÇÃO DE FILTROS: SETOR ➔ EQUIPES ---
        # =========================================================
        st.markdown("#### Filtros de Impressão")
        
        setores_selecionados = st.multiselect(
            "1. Filtrar por Setor (Opcional):",
            options=setores_disponiveis,
            placeholder="Selecione um ou mais setores para filtrar as equipes..."
        )
        
        if setores_selecionados:
            df_filtrado_setor = df_final[df_final['Setor_Equipe'].isin(setores_selecionados)]
        else:
            df_filtrado_setor = df_final
            
        equipes_disponiveis = sorted(df_filtrado_setor['Equipe'].unique())
        
        st.write("2. Selecionar Equipes:")
        
        # CHAVE MESTRA: Opção de Selecionar Tudo
        selecionar_todas = st.checkbox("**Selecionar tudo**", value=False)
        st.write("") 
        
        equipes_selecionadas = []
        cols = st.columns(4) 
        
        for idx, equipe in enumerate(equipes_disponiveis):
            with cols[idx % 4]: 
                if selecionar_todas:
                    # Trava visualmente as opções como verdadeiras se o botão Mestre estiver ativo
                    st.checkbox(equipe, value=True, disabled=True, key=f"lock_{equipe}")
                    equipes_selecionadas.append(equipe)
                else:
                    # Deixa livre para o utilizador escolher
                    if st.checkbox(equipe, value=False, key=f"free_{equipe}"):
                        equipes_selecionadas.append(equipe)

        # Se o utilizador desmarcar todas, o programa para a interface aqui mesmo de forma suave
        if not equipes_selecionadas:
            st.info("👆 Selecione pelo menos uma equipe acima para liberar as opções de visualização e exportação.")
            st.stop()

        df_geracao = df_filtrado_setor[df_filtrado_setor['Equipe'].isin(equipes_selecionadas)]
        equipes_agrupadas_geracao = df_geracao.groupby('Equipe')

        st.markdown("---")

        # =========================================================
        # --- SEÇÃO DE EXPORTAÇÃO E VISUALIZAÇÃO ---
        # =========================================================
        col1, col2 = st.columns([2.5, 1])

        with col1:
            st.markdown("#### Pré-visualização")
            # A pré-visualização agora só mostra as equipes ativas no filtro acima
            equipe_preview = st.selectbox("Selecione a Equipe para visualizar:", sorted(equipes_selecionadas))

            if equipe_preview:
                df_equipe_preview = df_final[df_final['Equipe'] == equipe_preview]
                
                pdf_bytes_preview = gerar_pdf_individual(equipe_preview, df_equipe_preview, ordens_manuais, hoje_date, data_hoje_str)
                base64_pdf = base64.b64encode(pdf_bytes_preview).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#view=FitH" width="100%" height="500" type="application/pdf" style="border: 1px solid #ccc; border-radius: 5px;"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

        with col2:
            st.markdown("#### 🖨️ Exportação dos espelhos (pdf)")
            qtd_geracao = len(equipes_agrupadas_geracao)
            st.write(f"Gerando espelhos para **{qtd_geracao}** equipe(s).")
            
            st.markdown("**Opção 1:** O sistema junta tudo em um único arquivo PDF. Ideal para imprimir de uma vez.")
            if st.button("Gerar Arquivo Único (Para Impressão)", use_container_width=True):
                with st.spinner("Gerando PDF Mestre com as equipes selecionadas..."):
                    pdf_bytes_mestre = gerar_pdf_mestre(equipes_agrupadas_geracao, ordens_manuais, hoje_date, data_hoje_str)
                    
                    st.download_button(
                        label="📥 Descarregar PDF Único para Impressão",
                        data=pdf_bytes_mestre,
                        file_name=f"Impressao_Total_Espelhos_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            st.markdown("---")
            st.markdown("**Opção 2:** O sistema separa os PDFs por equipe e compacta todos num arquivo .ZIP")
            if st.button("Gerar Arquivos Separados (ZIP)", use_container_width=True):
                with st.spinner("Empacotando os espelhos separados..."):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for equipe, df_equipe in equipes_agrupadas_geracao:
                            setor_equipe = PREFIXOS_DICT.get(equipe, "Desconhecido")
                            pdf_bytes = gerar_pdf_individual(equipe, df_equipe, ordens_manuais, hoje_date, data_hoje_str)
                            
                            nome_arquivo_pdf = f"{equipe.replace('/', '_')}_{setor_equipe.replace(' ', '_')}.pdf"
                            zip_file.writestr(nome_arquivo_pdf, pdf_bytes)

                    st.download_button(
                        label="📥 Descarregar Espelhos (.ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name=f"Espelhos_Separados_{datetime.now().strftime('%Y%m%d')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar a planilha: {e}")