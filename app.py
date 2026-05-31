import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from contador import pipeline_from_bytes, calcular_area_referencia

st.set_page_config(page_title='Contador de Parafusos', page_icon='🔩', layout='wide')

if 'historico' not in st.session_state:
    st.session_state.historico = []

st.image('logo.png', use_column_width=True)
st.divider()

with st.sidebar:
    st.image('prafusos.jpg', use_column_width=True)
    st.divider()
    st.header('Configuracoes')
    sensibilidade = st.slider('Sensibilidade', 0.5, 3.0, 1.0, 0.1)
    st.divider()
    st.header('Calibracao (opcional)')
    st.write('Envie uma foto com 1 parafuso para calibrar.')
    arquivo_ref = st.file_uploader('Foto de referencia (1 parafuso)',
                                    type=['jpg','jpeg','png'], key='ref')
    area_ref = None
    if arquivo_ref is not None:
        area_ref = calcular_area_referencia(arquivo_ref.read())
        st.success('Calibracao concluida!')
    st.divider()
    st.header('Como usar')
    st.write('1. Calibre com 1 parafuso (opcional)')
    st.write('2. Faca upload da foto')
    st.write('3. Ajuste a sensibilidade')
    st.write('4. Clique em Contar Parafusos')
    st.divider()
    st.caption('Bootcamp de Ciencia de Dados e IA')
    st.caption('Desafio 1 - Residencia em IA')

aba1, aba2 = st.tabs(['Contagem', 'Dashboard'])

with aba1:
    col1, col2 = st.columns([1, 1], gap='large')
    with col1:
        st.subheader('Upload da imagem')
        arquivo = st.file_uploader('Selecione uma foto',
                                    type=['jpg', 'jpeg', 'png'])
        if arquivo is not None:
            st.image(arquivo, caption='Imagem enviada', width=400)
            st.success('Imagem carregada! Clique em Contar Parafusos.')
            processar = st.button('Contar Parafusos',
                                   type='primary',
                                   use_container_width=True)
        else:
            st.info('Nenhuma imagem carregada. Faca upload para comecar.')
            processar = False

    with col2:
        st.subheader('Resultado')
        if arquivo is not None and processar:
            with st.spinner('Processando imagem...'):
                try:
                    img_bytes = arquivo.read()
                    resultado = pipeline_from_bytes(img_bytes, sensibilidade, area_ref)
                    contagem = resultado['contagem_final']
                    score = resultado['score_confianca']
                    nivel = resultado['nivel_confianca']
                    contagem_area = resultado['contagem_area']
                    contagem_contornos = resultado['contagem_contornos']
                    if nivel == 'Alta':
                        cor_score = 'green'
                    elif nivel == 'Media':
                        cor_score = 'orange'
                    else:
                        cor_score = 'red'
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric('Parafusos detectados', contagem)
                    with m2:
                        st.metric('Metodo contornos', contagem_contornos)
                    with m3:
                        st.metric('Metodo area', contagem_area)
                    st.markdown('<b>Score de Confianca: </b>' +
                                '<span style="color:' + cor_score +
                                ';font-size:1.2rem;font-weight:bold">' +
                                str(score) + '% — ' + nivel + '</span>',
                                unsafe_allow_html=True)
                    st.divider()
                    tab1, tab2, tab3 = st.tabs(['Deteccoes', 'Mascara', 'Original'])
                    with tab1:
                        st.image(resultado['img_resultado'],
                                  caption=str(contagem) + ' parafuso(s)', width=400)
                    with tab2:
                        st.image(resultado['img_mask'],
                                  caption='Mascara', width=400)
                    with tab3:
                        st.image(resultado['img_original'],
                                  caption='Original', width=400)
                    if nivel == 'Baixa':
                        st.warning('Confianca baixa. Ajuste a sensibilidade ou calibre o sistema.')
                    elif nivel == 'Media':
                        st.info('Confianca media. Calibre para maior precisao.')
                    else:
                        st.success('Contagem realizada com alta confianca!')
                    st.session_state.historico.append({
                        'Horario': datetime.now().strftime('%H:%M:%S'),
                        'Arquivo': arquivo.name,
                        'Contagem': contagem,
                        'Contornos': contagem_contornos,
                        'Area': contagem_area,
                        'Confianca': score,
                        'Nivel': nivel
                    })
                except Exception as e:
                    st.error('Erro ao processar: ' + str(e))
        elif arquivo is None:
            st.info('Faca o upload de uma imagem para ver o resultado.')
        else:
            st.info('Clique em Contar Parafusos para processar.')

with aba2:
    st.subheader('Dashboard de Estatisticas')
    if len(st.session_state.historico) == 0:
        st.info('Nenhuma contagem realizada ainda. Processe imagens na aba Contagem.')
    else:
        df = pd.DataFrame(st.session_state.historico)
        st.markdown('### Resumo da Sessao')
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric('Total de imagens', len(df))
        with c2:
            st.metric('Total de parafusos', int(df['Contagem'].sum()))
        with c3:
            st.metric('Media por imagem', round(df['Contagem'].mean(), 1))
        with c4:
            st.metric('Confianca media', str(round(df['Confianca'].mean(), 1)) + '%')
        st.divider()
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown('#### Contagem por Imagem')
            fig1 = px.bar(df, x='Arquivo', y='Contagem', color='Nivel',
                color_discrete_map={'Alta': '#00c853', 'Media': '#ff9800', 'Baixa': '#f44336'},
                labels={'Contagem': 'Parafusos', 'Arquivo': 'Imagem'}, text='Contagem')
            fig1.update_traces(textposition='outside')
            fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                font=dict(family='Arial'), legend_title='Confianca')
            st.plotly_chart(fig1, use_container_width=True)
        with col_g2:
            st.markdown('#### Score de Confianca por Imagem')
            fig2 = px.line(df, x='Arquivo', y='Confianca', markers=True,
                labels={'Confianca': 'Score (%)', 'Arquivo': 'Imagem'},
                color_discrete_sequence=['#1a1a2e'])
            fig2.add_hline(y=80, line_dash='dash', line_color='green',
                           annotation_text='Alta confianca')
            fig2.add_hline(y=55, line_dash='dash', line_color='orange',
                           annotation_text='Confianca media')
            fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                font=dict(family='Arial'), yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('#### Comparativo: Metodo Contornos vs Metodo Area')
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name='Contornos', x=df['Arquivo'],
                               y=df['Contornos'], marker_color='#1a1a2e'))
        fig3.add_trace(go.Bar(name='Estimativa por Area', x=df['Arquivo'],
                               y=df['Area'], marker_color='#00d4aa'))
        fig3.update_layout(barmode='group', plot_bgcolor='white',
            paper_bgcolor='white', font=dict(family='Arial'),
            xaxis_title='Imagem', yaxis_title='Parafusos detectados',
            legend_title='Metodo')
        st.plotly_chart(fig3, use_container_width=True)
        st.divider()
        st.markdown('#### Historico Completo')
        st.dataframe(df, use_container_width=True)
        if st.button('Limpar historico'):
            st.session_state.historico = []
            st.rerun()

st.divider()
st.markdown('<p style="text-align:center;color:#888;font-size:0.85rem">© 2026 Daniel Tavares de França | Sistema de Contagem Automática de Parafusos</p>', unsafe_allow_html=True)
