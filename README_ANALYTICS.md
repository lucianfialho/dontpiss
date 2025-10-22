# 📊 DontPiss Analytics - Análise de Treinamento

Sistema de análise de progresso do treinamento do cachorro ao longo do tempo.

## Como usar

### 1. Instale dependências de analytics (se ainda não instalou)

```bash
pip install pandas matplotlib seaborn
```

### 2. Execute a análise

```bash
python analyze_training.py
```

Você verá um relatório completo no terminal:

```
📊 RELATÓRIO DE TREINAMENTO - DontPiss
====================================================================

📈 ESTATÍSTICAS GERAIS
--------------------------------------------------------------------
Total de violações: 145
Período monitorado: 7 dias
Primeira detecção: 22/10/2024 13:45
Última detecção: 29/10/2024 18:30
Média por dia: 20.7 violações
Horário mais comum: 14:00
Dia da semana mais comum: Monday

📅 VIOLAÇÕES POR DIA
--------------------------------------------------------------------
22/10/2024: ██████████████████ (35)
23/10/2024: ██████████████ (28)
24/10/2024: █████████████ (26)
25/10/2024: ████████████ (24)
26/10/2024: ██████████ (20)
27/10/2024: ████████ (16)
28/10/2024: █████ (10)

🕐 VIOLAÇÕES POR HORA DO DIA
--------------------------------------------------------------------
00:00: █ (2)
01:00: (0)
...
14:00: ██████████████████████████████ (42)
15:00: ████████████████████████ (35)
...

📆 VIOLAÇÕES POR DIA DA SEMANA
--------------------------------------------------------------------
Mon: ██████████████████████████████ (45)
Tue: ████████████████████████ (38)
Wed: ████████████████████ (32)
Thu: ██████████████ (25)
Fri: ████████████ (22)
Sat: ████████ (15)
Sun: ██████ (12)

🎯 PROGRESSO DO TREINAMENTO
--------------------------------------------------------------------
✅ Melhora de 71.4% (primeira semana vs última semana)
   O cachorro está subindo MENOS no sofá! 🎉

🔥 ÚLTIMAS 5 DETECÇÕES
--------------------------------------------------------------------
  • 29/10/2024 18:30:15
  • 29/10/2024 17:15:42
  • 29/10/2024 16:05:23
  • 29/10/2024 14:45:10
  • 29/10/2024 13:20:05
```

### 3. Gerar gráficos visuais

```bash
python analyze_training.py --charts
```

Isso cria:
- `analytics/training_progress.png` - 4 gráficos visuais
- `analytics/training_summary.json` - Dados em JSON

## 📊 Gráficos gerados

O arquivo `training_progress.png` contém 4 gráficos:

### 1. Violações ao longo do tempo
- Barras azuis: violações diárias
- Linha vermelha: média móvel de 7 dias (mostra tendência)

### 2. Violações por hora do dia
- Identifica em que horário o cachorro sobe mais no sofá
- Útil para saber quando reforçar o treinamento

### 3. Violações por dia da semana
- Segunda-feira vs domingo, etc.
- Pode mostrar padrões de comportamento

### 4. Violações acumuladas
- Total acumulado ao longo do tempo
- Mostra crescimento total

## 📈 Métricas importantes

### Taxa de melhora
```
Melhora % = (Violações semana 1 - Violações última semana) / Violações semana 1 * 100
```

**Interpretação:**
- **> 50%**: Treinamento muito efetivo! 🎉
- **20-50%**: Progresso bom 👍
- **0-20%**: Progresso lento 🐌
- **Negativo**: Cachorro está piorando ⚠️

### Média por dia
- **> 30 violações/dia**: Alto (treinamento inicial)
- **10-30 violações/dia**: Médio (progresso)
- **< 10 violações/dia**: Baixo (quase treinado!)
- **< 3 violações/dia**: Excelente! 🌟

## 🎯 Como interpretar os resultados

### Cenário 1: Progresso positivo
```
Dia 1: 45 violações
Dia 7: 12 violações
Melhora: 73.3%
```
✅ **Ótimo!** Continue com o treinamento atual.

### Cenário 2: Sem progresso
```
Dia 1: 30 violações
Dia 7: 28 violações
Melhora: 6.7%
```
⚠️ **Ajustar estratégia:**
- Aumentar recompensas quando cachorro fica fora do sofá
- Ser mais consistente com correções
- Verificar se zona está bem configurada

### Cenário 3: Piora
```
Dia 1: 20 violações
Dia 7: 35 violações
Melhora: -75%
```
🚨 **Revisar treinamento:**
- Cachorro pode estar confuso
- Reforçar comandos básicos
- Considerar consultar um treinador profissional

## 📊 Análise avançada

### Identificar padrões

**Horário pico:**
```
14:00-16:00: 80 violações
```
→ Reforce treinamento nesses horários

**Dia da semana:**
```
Segunda: 50 violações
Domingo: 10 violações
```
→ Talvez aos domingos você esteja mais presente

### Correlações úteis

1. **Hora vs violações**: Quando cachorro fica sozinho?
2. **Dia vs violações**: Rotina semanal afeta?
3. **Tendência geral**: Está melhorando ou piorando?

## 🔄 Monitoramento contínuo

### Recomendação de análise

- **Diária**: Não recomendado (variação natural)
- **Semanal**: ✅ **Ideal** - mostra tendências claras
- **Mensal**: Para acompanhamento de longo prazo

### Exportar dados

```bash
python analyze_training.py --charts
```

Depois você pode:
```python
import json

with open('analytics/training_summary.json') as f:
    data = json.load(f)

print(f"Melhora: {data['improvement_percentage']:.1f}%")
```

## 📱 Integração com apps

O arquivo `training_summary.json` pode ser usado para:
- Dashboards web
- Apps mobile
- Planilhas Google Sheets
- Notificações automáticas

## 🎓 Dicas de treinamento baseadas em dados

### Se violações aumentam no fim do dia
→ Cachorro pode estar entediado
**Solução**: Mais passeios/brincadeiras tarde

### Se violações aumentam em dias específicos
→ Mudança de rotina
**Solução**: Manter consistência

### Se violações diminuem mas depois estabilizam
→ Cachorro atingiu "platô"
**Solução**: Novos estímulos/recompensas

## 🔧 Troubleshooting

### "Arquivo de log não encontrado"
→ Execute o `zone_detector.py` primeiro para gerar dados

### "Dados insuficientes para calcular tendência"
→ Precisa de pelo menos 7 dias de dados

### Gráficos não aparecem
```bash
pip install matplotlib pandas seaborn
```

## 📊 Exemplo de uso semanal

```bash
# Segunda-feira
python analyze_training.py

# Ver se melhorou desde semana passada
# Ajustar treinamento se necessário

# Domingo (fim de semana)
python analyze_training.py --charts

# Gerar gráficos semanais
# Compartilhar progresso com família
```

## 🎯 Meta de treinamento

**Objetivo típico:**
```
Semana 1: 30+ violações/dia
Semana 2: 15-20 violações/dia
Semana 3: 8-12 violações/dia
Semana 4: < 5 violações/dia
```

**Quando considerar treinado:**
- < 3 violações por dia
- Por 7 dias consecutivos
- = **Sucesso!** 🎉

---

**DontPiss Analytics** - Treinamento baseado em dados! 📊🐕
