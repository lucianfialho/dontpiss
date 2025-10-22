# 🎓 DontPiss - Sistema de Treinamento Ativo

Sistema completo para **treinar ativamente** seu cachorro a não subir no sofá usando alertas em tempo real.

## 🔊 Como funciona

Quando o cachorro sobe no sofá, o sistema emite:
- 🔔 **Sons de alerta** (beeps, buzzer)
- 🗣️ **Comandos de voz** ("No!", "Off!", "Get down!")
- ⬆️ **Escalação progressiva** (alertas mais intensos quanto mais tempo no sofá)
- ✅ **Reforço positivo** (som agradável quando sai do sofá)

## 🎯 Modos de Treinamento

### 1. **Gentle** (Suave) - Para cachorros sensíveis
```bash
cd src
python zone_detector.py --mode gentle
```

**Características:**
- Aguarda 2 segundos antes de alertar
- Sons suaves (beeps curtos)
- Sem escalação
- 1 alerta por vez

**Melhor para:**
- Cachorros ansiosos ou medrosos
- Filhotes
- Primeira semana de treinamento

---

### 2. **Standard** (Padrão) - Uso geral ⭐ RECOMENDADO
```bash
cd src
python zone_detector.py --mode standard
# ou simplesmente
python zone_detector.py
```

**Características:**
- Resposta rápida (0.5s)
- Escalação de alertas:
  - 0-1s: Beep suave
  - 1-3s: Comando de voz ("No!")
  - 3-5s: Buzzer + voz
  - 5s+: Múltiplos alertas
- 2 alertas por detecção

**Melhor para:**
- Maioria dos cachorros
- Treinamento regular
- Uso diário

---

### 3. **Intensive** (Intensivo) - Para casos difíceis
```bash
cd src
python zone_detector.py --mode intensive
```

**Características:**
- Resposta IMEDIATA (sem delay)
- Escalação agressiva
- 3 alertas consecutivos
- Volume alto

**Melhor para:**
- Cachorros teimosos
- Quando outros modos não funcionam
- **Use com cuidado** - pode estressar o cachorro

---

### 4. **Silent** (Silencioso) - Apenas monitoramento
```bash
cd src
python zone_detector.py --mode silent
# ou
python zone_detector.py --no-trainer
```

**Características:**
- SEM alertas sonoros
- Apenas registra violações
- Útil para análise posterior

**Melhor para:**
- Cachorro já treinado (só monitorar)
- Testar sem incomodar
- Análise de dados

## 📊 Escalação de Alertas (Standard/Intensive)

```
Tempo no sofá | Alerta
-------------|----------------------------
0-1 segundo  | 🔔 Beep suave
1-3 segundos | 🗣️ "No!" (voz)
3-5 segundos | 📢 Buzzer + "No!"
5+ segundos  | 🚨 Ultrassonic + Buzzer + Voz
```

## ✅ Reforço Positivo

Quando o cachorro **sai do sofá** após ser alertado:
- 🎵 Som agradável (Hero.aiff)
- 🗣️ "Good dog!" (30% das vezes)
- Reforça comportamento correto

## 🎓 Estratégia de Treinamento Recomendada

### Semana 1-2: Modo Gentle
```bash
python zone_detector.py --mode gentle
```
- Cachorro está aprendendo
- Seja paciente
- Consistência é chave
- **Espere:** 20-30 violações/dia

### Semana 3-4: Modo Standard
```bash
python zone_detector.py --mode standard
```
- Cachorro já entende o conceito
- Reforçar comportamento
- **Espere:** 10-15 violações/dia

### Semana 5+: Modo Standard ou Silent
```bash
python zone_detector.py --mode standard
# ou quando bem treinado:
python zone_detector.py --mode silent
```
- Manutenção
- Monitorar regressões
- **Espere:** < 5 violações/dia

## 🔧 Personalizar Sons

### Usar comandos de voz personalizados

Edite `src/dog_trainer.py` linha ~57:

```python
commands = {
    "No": ["Fora!", "Sai!", "Não pode!"],  # Português
    "Warning": ["Cuidado!", "Olha lá!"],
    "Good": ["Muito bem!", "Bom garoto!"]
}
```

### Gravar seus próprios sons

```bash
# Criar sons com sua voz (macOS)
say -o ~/Code/personal/dontpiss/sounds/alert.aiff "Não pode! Sai daí!"
say -o ~/Code/personal/dontpiss/sounds/good.aiff "Muito bem! Bom cachorro!"

# Ajustar voz e velocidade
say -v Luciana -r 180 -o alert.aiff "Fora do sofá!"
```

### Sons disponíveis no macOS

O sistema usa sons do macOS:
- `Funk.aiff` - Beep suave
- `Sosumi.aiff` - Buzzer
- `Tink.aiff` - Ultrassonic
- `Hero.aiff` - Reforço positivo

## 📊 Monitorar Progresso

### Durante execução
O terminal mostra alertas em tempo real:
```
🎓 Training mode: STANDARD
   Active training alerts enabled
```

### Análise semanal
```bash
python analyze_training.py
```

Veja:
- Quantas violações por dia
- Horários mais problemáticos
- % de melhora

## 🎯 Dicas de Treinamento

### ✅ Faça

1. **Seja consistente**
   - Use SEMPRE o mesmo modo
   - Deixe sistema rodando o dia todo

2. **Recompense comportamento correto**
   - Dê petisco quando cachorro ignora sofá
   - Elogie verbalmente

3. **Alternativa confortável**
   - Ofereça cama/almofada confortável no chão
   - Cachorro precisa de opção melhor

4. **Paciência**
   - Treinamento leva 2-4 semanas
   - Alguns cachorros são mais rápidos

### ❌ Evite

1. **Não misture modos**
   - Escolha UM modo e mantenha por 1-2 semanas

2. **Não use Intensive muito tempo**
   - Pode estressar cachorro
   - Use só se realmente necessário

3. **Não puna manualmente**
   - Deixe sistema fazer o trabalho
   - Intervenção humana pode confundir

4. **Não desista cedo**
   - Primeiros dias podem ter MUITAS violações
   - Normal! Continue firme

## 📈 Evolução Típica

```
Dia 1-3:   😰 Muitas violações (30+/dia)
           Cachorro não entende ainda

Dia 4-7:   📉 Redução gradual (20-25/dia)
           Começando a associar som com ação

Dia 8-14:  📊 Melhora significativa (10-15/dia)
           Cachorro hesita antes de subir

Dia 15-21: ✅ Quase lá! (5-8/dia)
           Poucos "testes" do cachorro

Dia 22+:   🎉 Treinado! (< 3/dia)
           Raras violações, já entendeu
```

## 🔊 Volumes e Intensidade

### Gentle Mode
- 🔈 Volume baixo
- Delay 2s
- Sons curtos

### Standard Mode
- 🔉 Volume médio
- Delay 0.5s
- Escalação moderada

### Intensive Mode
- 🔊 Volume alto
- Delay 0s (imediato)
- Escalação agressiva

## 💡 Problemas Comuns

### "Cachorro ignora alertas"
→ Troque para modo **Intensive**
→ Aumente volume do Mac
→ Teste sons manualmente

### "Cachorro fica assustado"
→ Troque para modo **Gentle**
→ Aumente delay inicial
→ Use apenas beeps suaves

### "Funciona mas depois volta"
→ Normal! Cachorros testam limites
→ Mantenha consistência
→ Não desista

### "Funciona quando estou presente, não quando ausente"
→ Cachorro associou SUA presença
→ Deixe sistema rodando sozinho
→ Saia de casa com sistema ligado

## 🎵 Sons Personalizados (Avançado)

### Criar biblioteca de sons

```bash
# 1. Criar diretório
mkdir -p sounds

# 2. Gerar sons
say -o sounds/no1.aiff "Não pode!"
say -o sounds/no2.aiff "Fora!"
say -o sounds/no3.aiff "Sai daí!"
say -o sounds/good1.aiff "Muito bem!"
say -o sounds/good2.aiff "Bom cachorro!"

# 3. Editar dog_trainer.py para usar seus sons
```

### Vozes disponíveis (macOS)
```bash
say -v ? | grep pt_BR  # Vozes em português
say -v Luciana "Teste"  # Voz feminina brasileira
```

## 📱 Automação

### Iniciar automaticamente (macOS)

1. Crie arquivo `start_trainer.sh`:
```bash
#!/bin/bash
cd /Users/seu_usuario/Code/personal/dontpiss
source venv/bin/activate
cd src
python zone_detector.py --mode standard
```

2. Torne executável:
```bash
chmod +x start_trainer.sh
```

3. Adicione ao Login Items do Mac

## 🎯 Metas de Sucesso

**Semana 1:** < 20 violações/dia
**Semana 2:** < 10 violações/dia
**Semana 3:** < 5 violações/dia
**Semana 4:** **< 3 violações/dia = TREINADO! 🎉**

---

## 🚀 Começar Agora

```bash
# 1. Configure zonas (se ainda não fez)
python quick_zone_setup.py

# 2. Escolha modo e inicie
cd src
python zone_detector.py --mode standard

# 3. Deixe rodando e monitore
# (pressione Q para sair)

# 4. Analise progresso semanalmente
python ../analyze_training.py --charts
```

---

**DontPiss Training** - Treinamento inteligente e efetivo! 🐕🎓
