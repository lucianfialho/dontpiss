# Troubleshooting - DontPiss

## Notificações Desktop não funcionam (macOS)

**Erro**: `ModuleNotFoundError: No module named 'pyobjus'`

### Solução:

As notificações desktop no macOS funcionam mas exigem dependência adicional. Você tem duas opções:

#### Opção 1: Desabilitar notificações desktop (mais simples)

Edite `src/config.py`:
```python
NOTIFICATIONS = {
    'enabled': True,
    'sound': True,
    'desktop_notification': False,  # Desabilitado
    'save_snapshot': True
}
```

**OU** rode o setup novamente:
```bash
python setup.py
```
E escolha "n" para notificações desktop.

#### Opção 2: Instalar dependência para notificações (avançado)

```bash
# Tente instalar pyobjus (pode não funcionar)
pip install pyobjus

# Alternativa: usar osascript (macOS nativo)
```

### Nota Importante:
- ✅ **Snapshots continuam funcionando** - fotos são salvas em `data/snapshots/`
- ✅ **Alertas sonoros funcionam** - você ouve quando detecta
- ✅ **Log funciona** - todas detecções em `logs/detections.csv`
- ⚠️ Apenas a notificação visual do macOS não aparece

---

## Câmera trava ou fica preta

### Sintomas:
- Preview abre mas fica preto
- Programa congela ao selecionar câmera
- FPS muito baixo

### Soluções:

1. **Feche outros apps usando a câmera**
   ```bash
   # Verifique apps usando câmera
   lsof | grep -i camera
   ```

2. **Teste com resolução menor**

   Edite `src/config.py`:
   ```python
   CAMERA_WIDTH = 640
   CAMERA_HEIGHT = 480
   FPS = 15
   ```

3. **Tente outro índice de câmera**
   ```bash
   python setup.py
   ```
   E escolha câmera diferente.

4. **Reinicie permissões**
   - Configurações → Privacidade → Câmera
   - Remova e adicione novamente o Terminal

---

## Detecção não está funcionando

### Sintoma: Skeleton aparece mas nunca detecta xixi

### Debug:

1. **Ative modo debug**

   Pressione **'D'** enquanto o programa roda

   OU edite `src/config.py`:
   ```python
   DISPLAY = {
       'debug_mode': True
   }
   ```

2. **Observe o painel DEBUG INFO** no canto direito:
   - **Leg Lift**: deve ficar verde quando levantar perna
   - **Squat**: deve ficar verde quando agachar
   - **Frames**: contador de frames consecutivos
   - **Barra de progresso**: precisa encher completamente

3. **Ajuste sensibilidade**

   Se não detecta, edite `src/config.py`:
   ```python
   PEE_DETECTION = {
       'min_frames_threshold': 10,  # Reduzir (padrão: 15)
       'leg_lift_angle_threshold': 50,  # Aumentar (padrão: 45)
       'squat_height_ratio': 0.6,  # Aumentar (padrão: 0.5)
   }
   ```

4. **Execute setup e escolha "Alta sensibilidade"**
   ```bash
   python setup.py
   ```

---

## Muitos falsos positivos

### Sintoma: Detecta quando cachorro não está fazendo xixi

### Solução:

1. **Aumente o threshold de frames**
   ```python
   PEE_DETECTION = {
       'min_frames_threshold': 30,  # Aumentar (padrão: 15)
   }
   ```

2. **Execute setup e escolha "Baixa sensibilidade"**
   ```bash
   python setup.py
   ```

3. **Verifique iluminação**
   - Muita sombra pode confundir detecção
   - Tente melhorar iluminação da área

---

## Skeleton não aparece

### Sintoma: Vídeo funciona mas não detecta cachorro

### Possíveis causas:

1. **Cachorro muito longe da câmera**
   - Aproxime a câmera ou cachorro

2. **Cachorro parcialmente escondido**
   - Modelo precisa ver corpo todo

3. **Confiança muito alta**

   Edite `src/config.py`:
   ```python
   CONFIDENCE_THRESHOLD = 0.3  # Reduzir (padrão: 0.5)
   ```

4. **Modelo não detecta cachorros**
   - YOLOv8-pose foi treinado com humanos e alguns animais
   - Pode não funcionar bem com raças muito pequenas/grandes

---

## Performance lenta (FPS baixo)

### Sintoma: FPS < 10

### Soluções:

1. **Use modelo nano** (padrão já usa)
   ```python
   YOLO_MODEL = "yolov8n-pose.pt"  # 'n' = nano (mais rápido)
   ```

2. **Reduza resolução**
   ```python
   CAMERA_WIDTH = 640
   CAMERA_HEIGHT = 480
   ```

3. **Reduza FPS da câmera**
   ```python
   FPS = 15
   ```

4. **Feche outros programas** pesados

---

## Erro: "No module named 'ultralytics'"

### Solução:
```bash
pip install ultralytics
```

---

## Erro: "Failed to open camera/video source"

### macOS:
1. Configurações → Privacidade → Câmera
2. Habilite Terminal/iTerm/VS Code
3. Feche e reabra o terminal

### Outra câmera:
```bash
python setup.py
```
Escolha câmera diferente.

---

## Ver logs de detecção

```bash
# Ver últimas detecções
tail logs/detections.csv

# Ver log completo
cat logs/dog_pee_detector.log

# Ver snapshots salvos
open data/snapshots/
```

---

## Reset completo

```bash
# Deletar configurações
rm user_config.json

# Rodar setup novamente
python setup.py

# Limpar logs
rm -rf logs/*
rm -rf data/snapshots/*
```

---

## Suporte

Se nenhuma solução funcionou:

1. **Verifique requisitos**:
   - Python 3.8+
   - Câmera funcionando
   - Permissões corretas

2. **Teste com vídeo** ao invés de câmera:
   ```bash
   python setup.py
   # Escolha [0] para usar arquivo de vídeo
   ```

3. **Ative debug e tire screenshot** do erro:
   ```bash
   python src/dog_pee_detector.py 2>&1 | tee error.log
   ```

---

**Dica**: A maioria dos problemas é resolvida ajustando a sensibilidade no `config.py` ou usando o modo debug ('D') para ver o que está acontecendo!
