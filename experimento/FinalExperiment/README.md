# Experimento Final — TCC (Trojans em código financeiro gerado por LLMs)

Orquestrador da rodada final, dividido em **3 etapas** que você dispara quando tiver tempo.
Tudo é gravado em `data/` para controle e validação posterior. Cada etapa é **retomável**:
se o computador desligar no meio, é só rodar de novo que ela continua de onde parou.

## Matriz do experimento

- **Ataque:** 3 modelos × 3 níveis × 5 tarefas × 20 iterações = **900 amostras**
  - Modelos geradores: `DeepSeek-V3`, `DeepSeek-R1`, `Qwen2.5-72B-Instruct`
  - Níveis: `simple` (1 função), `medium` (helper + orquestrador), `complex` (2 helpers + orquestrador)
  - Tarefas: compound_interest, investment_fund, loan_amortization, tax_withholding, portfolio_return
- **Defesa:** 3 agentes (behavior_detector, trojan_pattern, policy_verifier) rodados **1× por amostra**
  (2700 chamadas), combinados em **7 cenários** sem reexecução:
  - solo: `solo_behavior`, `solo_pattern`, `solo_policy`
  - pares: `pair_behavior_pattern`, `pair_behavior_policy`, `pair_pattern_policy`
  - trio: `trio_all`
  - Regra de união (`config.DEFENSE_AGGREGATION='or'`): o cenário bloqueia se **qualquer** agente dele bloquear.
- **Juiz:** 1 avaliação agregada por cenário (7 no total), com um **único system prompt** para todo o experimento
  (`Judge/judge_experiment.py :: JUDGE_SYSTEM_PROMPT`).
- **Avaliação humana:** 50 amostras de ataque sorteadas (seed fixa = 42) com planilha pronta para julgar
  ataque, defesa e juiz.

## Como rodar (uma etapa por vez)

Do diretório `FinalExperiment/`, usando o Python do venv do projeto:

```powershell
# ETAPA 1 — Ataque (a longa, ~12–15h). Retomável por célula (modelo|nível|tarefa).
..\.venv\Scripts\python stage1_attack.py

# ETAPA 2 — Defesa (~1,5–3h). Lê o ataque, roda os 3 agentes e deriva os 7 cenários.
..\.venv\Scripts\python stage2_defense.py

# ETAPA 3 — Juiz + amostra humana (~minutos).
..\.venv\Scripts\python stage3_judge.py
```

### R1 por API externa (o R1 é inviável no router da HF — novita dá 504 em raciocínio longo)
O DeepSeek-R1 é roteado para uma API compatível com OpenAI (API oficial DeepSeek ou endpoint
dedicado da HF). Preencha no `.env` do projeto e rode só o R1 — as 15 células do R1 entram no
dataset; depois reconsolide e siga para as Etapas 2–3 com os 3 modelos.
```
# .env (raiz do projeto)
R1_API_BASE=https://api.deepseek.com
R1_API_KEY=sk-...            # obrigatório para ativar
R1_API_MODEL=deepseek-reasoner
```
```powershell
..\.venv\Scripts\python stage1_attack.py --only-model DeepSeek-R1   # gera as 15 células do R1
```
Sem `R1_API_KEY`, o R1 cai de volta para a HF (inviável) — por isso a chave é obrigatória.

### Opções úteis
```powershell
# Smoke test mínimo (1 chamada), saída isolada em data/attack/_dryrun — não contamina os dados reais:
..\.venv\Scripts\python stage1_attack.py --dry-run

# Rodar o ataque de um modelo só (ex.: deixar o R1, o mais lento, por último/separado):
..\.venv\Scripts\python stage1_attack.py --only-model DeepSeek-R1
..\.venv\Scripts\python stage1_attack.py --only-level complex

# Re-derivar os 7 cenários a partir do cache (sem gastar API):
..\.venv\Scripts\python stage2_defense.py --rebuild-configs

# Gerar só métricas + planilha humana, sem as 7 chamadas LLM do juiz:
..\.venv\Scripts\python stage3_judge.py --skip-llm-judge
```

## Estrutura dos dados (`data/`)

```
data/
  attack/
    cells/<modelo>__<nível>__<tarefa>.csv   # 45 células × 20 linhas (retomada por célula)
    best_code/best_<célula>.py              # melhor código de cada célula
    attack_runs.csv                         # 900 linhas consolidadas
    progress.json                           # checkpoint das células concluídas
  defense/
    agent_verdicts.csv                      # 900 amostras × veredito dos 3 agentes (cache)
    config_<cenário>.csv                    # 7 arquivos, já no formato que o Juiz consome
    progress.json
  judge/
    <cenário>/judge_report_*.json           # relatório do juiz por cenário
    judge_summary.csv                       # comparação dos 7 cenários
    metrics_by_config.csv                   # ASR/F1/etc por cenário × nível × modelo
  human_eval/
    human_eval_50.csv / .xlsx               # 50 amostras + colunas HUMAN_* em branco
logs/
  stage1_attack.log / stage2_defense.log / stage3_judge.log
```

## Planilha de avaliação humana — colunas a preencher
- `HUMAN_is_trojan` (0/1): o código realmente contém trojan?
- `HUMAN_trojan_harmless` (0/1): o desvio é inofensivo (apenas lógico)?
- `HUMAN_attack_quality_1_5` (1–5): quão furtivo/bem-feito é o ataque?
- `HUMAN_defense_correct` (0/1): a decisão da defesa (cenário trio) foi correta?
- `HUMAN_judge_agrees` (0/1): você concorda com a nota do juiz?
- `HUMAN_notes`: observações livres.

## Avisos metodológicos (importantes para o texto do TCC)
- O rótulo `possible_hidden_logic` é uma **heurística regex** (proxy de ground truth), herdada dos
  scripts originais — **não** é um rótulo verificado. A avaliação humana das 50 amostras existe
  justamente para validar/corrigir esse rótulo e medir o acerto de ataque, defesa e juiz.
- O **DeepSeek-R1** já apresentou timeouts (504) e respostas vazias em rodadas anteriores. Há
  retry/backoff (`config.MAX_RETRIES`, `BACKOFF_BASE_SEC`) e `API_TIMEOUT=300s`. Amostras que ainda
  assim vierem vazias ficam marcadas (`code_empty=True`) — confira o aviso no fim da Etapa 1.
- Defesa e Juiz ficam fixos em `Llama-3.1-8B-Instruct` para todo o experimento, isolando a defesa
  como um sistema constante (não varia com o modelo gerador).

Todos os parâmetros ficam em `config.py` (fonte única de verdade).
