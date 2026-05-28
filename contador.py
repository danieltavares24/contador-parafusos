import cv2
import numpy as np

def preprocessar_imagem(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blur = cv2.GaussianBlur(enhanced, (7, 7), 0)
    return blur

def segmentar_parafusos(blur, area_total):
    _, thresh = cv2.threshold(blur, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel_small = np.ones((3, 3), np.uint8)
    kernel_large = np.ones((15, 15), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,
                               kernel_small, iterations=2)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE,
                               kernel_large, iterations=3)
    contours_all, hierarchy = cv2.findContours(closing, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
    mask_clean = np.zeros_like(closing)
    if hierarchy is not None:
        hierarchy = hierarchy[0]
        for i, (cnt, hier) in enumerate(zip(contours_all, hierarchy)):
            area = cv2.contourArea(cnt)
            parent_idx = hier[3]
            eh_tamanho_parafuso = area_total * 0.001 < area < area_total * 0.12
            dentro_de_objeto_grande = False
            if parent_idx >= 0:
                area_pai = cv2.contourArea(contours_all[parent_idx])
                dentro_de_objeto_grande = area_pai > area_total * 0.10
            if eh_tamanho_parafuso or (dentro_de_objeto_grande
                                       and area > area_total * 0.0005):
                cv2.drawContours(mask_clean, [cnt], -1, 255, -1)
    return mask_clean, closing

def calcular_area_referencia(img_bytes):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    area_total = h * w
    blur = preprocessar_imagem(img)
    _, thresh = cv2.threshold(blur, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel_large = np.ones((15, 15), np.uint8)
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE,
                               kernel_large, iterations=3)
    area_branca = int(np.sum(closing == 255))
    return area_branca

def calcular_confianca(contagem_contornos, contagem_area, area_fragmentos):
    if contagem_contornos == 0:
        return 0, 'Baixa'
    diferenca = abs(contagem_contornos - contagem_area)
    if diferenca == 0:
        score = 95
    elif diferenca <= 1:
        score = 80
    elif diferenca <= 2:
        score = 65
    elif diferenca <= 3:
        score = 50
    else:
        score = 30
    if area_fragmentos > 0.3:
        score = max(score - 15, 10)
    if score >= 80:
        nivel = 'Alta'
    elif score >= 55:
        nivel = 'Media'
    else:
        nivel = 'Baixa'
    return score, nivel

def contar_e_desenhar(img, mask_clean, area_total, sensibilidade=1.0):
    contours_final, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)
    min_area = area_total * 0.001 / sensibilidade
    max_area = area_total * 0.12
    parafusos = []
    for cnt in contours_final:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            parafusos.append(cnt)
    img_resultado = img.copy()
    for j, cnt in enumerate(parafusos):
        cv2.drawContours(img_resultado, [cnt], -1, (0, 255, 0), 2)
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.putText(img_resultado, str(j + 1),
                        (cx - 10, cy + 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 0, 255), 2)
    return len(parafusos), img_resultado

def pipeline_from_bytes(img_bytes, sensibilidade=1.0, area_ref=None):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError('Nao foi possivel decodificar a imagem.')
    h, w = img.shape[:2]
    area_total = h * w
    blur = preprocessar_imagem(img)
    mask, closing = segmentar_parafusos(blur, area_total)
    contagem_contornos, img_result = contar_e_desenhar(img, mask,
                                                        area_total, sensibilidade)
    # Estimativa por area
    area_branca = int(np.sum(closing == 255))
    if area_ref and area_ref > 0:
        contagem_area = max(1, round(area_branca / area_ref))
    else:
        contagem_area = contagem_contornos
    # Score de confianca
    area_fragmentos = 1.0 - (np.sum(mask == 255) / (area_branca + 1))
    score, nivel = calcular_confianca(contagem_contornos,
                                      contagem_area, area_fragmentos)
    img_original_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resultado_rgb = cv2.cvtColor(img_result, cv2.COLOR_BGR2RGB)
    img_mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    return {
        'contagem_contornos': contagem_contornos,
        'contagem_area': contagem_area,
        'contagem_final': contagem_area if area_ref else contagem_contornos,
        'score_confianca': score,
        'nivel_confianca': nivel,
        'area_branca': area_branca,
        'img_original': img_original_rgb,
        'img_resultado': img_resultado_rgb,
        'img_mask': img_mask_rgb
    }
