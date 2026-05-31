# Contador de Parafusos — Desafio 1

Sistema automático de contagem de parafusos para o processo de picking industrial, desenvolvido com visão computacional clássica em Python.

**Autor:** Daniel Tavares de França  
**Programa:** Residência em Inteligência Artificial  
**Bootcamp:** Ciência de Dados e Inteligência Artificial  
**Data:** Maio de 2026

---

## Aplicação Web

Acesse o sistema diretamente pelo navegador, sem instalação:

**https://contador-parafusos.streamlit.app**

Compatível com PC, smartphone e tablet.

---

## Sobre o Projeto

Uma empresa metal-mecânica precisava automatizar a contagem de parafusos no processo de picking, realizada manualmente por funcionários via smartphone. O sistema desenvolvido utiliza visão computacional clássica com OpenCV, sem necessidade de GPU, executável em dispositivos de baixo recurso computacional.

### Resultado

| Imagem | Real | Detectado | Status |
|---|---|---|---|
| img1.jpg | 8 | 8 | Correto |
| img2.jpg | 1 | 2 | Supercontagem |
| img3.jpg | 4 | 4 | Correto |
| img4.jpg | 2 | 2 | Correto |
| img5.jpg | 11 | 6 | Subcontagem |

**3 de 5 imagens com contagem exata (60%)**

---

## Pipeline

1. **CLAHE** — melhoria adaptativa de contraste para objetos metálicos
2. **Filtro Gaussiano** — redução de ruído
3. **Threshold manual (T=100)** — binarização calibrada para parafusos
4. **Morfologia matemática** — abertura e fechamento para limpar e unir objetos
5. **Detecção de contornos** — identificação dos candidatos
6. **Filtro geométrico** — aceitação por área e razão de aspecto
7. **Seletor automático** — escolhe o melhor resultado entre múltiplas configurações

---

## Funcionalidades do App

- Upload de imagem pelo navegador (PC ou smartphone)
- Calibração opcional com foto de 1 parafuso de referência
- Slider de sensibilidade para ajuste fino
- Dois métodos de contagem simultâneos: contornos e estimativa por área
- Score de confiança: Alta, Média ou Baixa
- Dashboard com histórico de contagens e gráficos comparativos

---

## Estrutura do Repositório

```
contador-parafusos/
├── app.py              # Interface web Streamlit
├── contador.py         # Motor de visão computacional
├── requirements.txt    # Dependências
├── logo.png            # Logo da aplicação
└── prafusos.jpg        # Imagem da sidebar
```

---

## Como Executar Localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Dependências

```
streamlit
opencv-python-headless
numpy
pandas
plotly
```

---

## Limitações

- Parafusos sobrepostos formam grupos indivisíveis pelo algoritmo clássico
- Baixo contraste entre parafuso e fundo dificulta a segmentação
- Para produção com alta acurácia, recomenda-se YOLOv8 Nano com 500+ imagens rotuladas

---

© 2026 Daniel Tavares de França | Residência em Inteligência Artificial
