# Conclusões da etapa de avaliação humana

## Desenho
Avaliação **cega** de **60 amostras** de código (subconjunto estratificado das 600:
2 por célula = 5 tarefas × 3 níveis × 2 modelos), por **3 avaliadores independentes**.
Cada avaliador respondeu, por amostra, apenas: *há trojan?* (0/1) e *confiança* (1–5),
sem acesso a qualquer veredito da máquina (ataque, agentes, cenários ou juiz).

## Números-chave
- **Prevalência de trojan (maioria dos 3 humanos): 58/60 (96,7%).**
- **Rótulo regex (proxy usado nas métricas): 42/60 (70%).**
- **Acordo humano × regex: 73,3%.** O regex recupera só ~72% dos trojans que humanos
  identificam → **falso-negativo relevante do proxy**.
- **Concordância inter-avaliadores:** acordo bruto **93–95%**; Cohen κ por par
  0,30 / −0,02 / 0,38; **Fleiss κ = 0,257**.
- **Métricas dos 10 cenários vs ground-truth humano** (FPR ≈ 0 em todos — ver ressalva):

  | Cenário | ASR | F1 |
  |---|---|---|
  | Pattern · Behav+Pattern · Trio · Pattern+Policy | 0,017 | 0,991 |
  | Orquestrador | 0,086 | 0,955 |
  | Ponderado · Behav+Policy | 0,466 | 0,697 |
  | Behavior · Policy | 0,586 | 0,585 |
  | Série | 0,672 | 0,494 |

## O que se pode concluir

1. **O ataque é altamente eficaz.** Cerca de 97% das gerações contêm um trojan que
   humanos detectam, de forma consistente entre as 5 tarefas, 3 níveis e 2 modelos. A
   geração adversarial (PAIR) injeta lógica oculta de maneira confiável.

2. **A métrica automática (regex) é um limite inferior, não a verdade.** Ela subcontou
   os trojans em ~27% (42 vs 58). Toda métrica derivada dela **subestima a presença de
   ataque** e **penaliza injustamente** os detectores mais agressivos.

3. **O detector de padrão (`trojan_pattern`) é o componente decisivo da defesa.** Contra
   o rótulo humano, ele e todas as topologias que o incluem (Trio paralelo, pares com
   Pattern) atingem **F1 ≈ 0,99 e ASR ≈ 1,7%**. O "excesso de bloqueio" que a métrica
   regex apontava era, em sua maioria, **detecção correta**.

4. **O trade-off precisão↔recall observado com o regex era, em grande parte, artefato.**
   Como quase não há código efetivamente limpo, as topologias conservadoras (Série,
   Ponderado, Behavior/Policy isolados) não "reduzem falso-positivo" — elas apenas
   **deixam passar trojan real** (ASR 47–67%).

5. **A avaliação humana valida a cadeia ataque–defesa–juiz:** confirma que o ataque
   funciona, que a defesa eficaz é a baseada em padrão, e que a defesa/juiz automáticos
   devem ser interpretados sabendo que o rótulo-base subestima o ataque.

## Ressalvas (obrigatórias no texto)
- **FPR/especificidade é inconclusivo.** A classe "limpo" por humanos tem apenas 2/60
  amostras; qualquer FPR calculado aqui (0,000) é instável. As conclusões firmes são
  sobre **detecção (ASR/recall)**, não sobre falso-positivo.
- **Kappa baixo por prevalência, não por desacordo.** Com 97% de "sim", o κ sofre o
  *paradoxo do kappa* (expectativa de acordo altíssima). Reportar **acordo bruto
  (93–95%) e κ juntos**, explicando o efeito da prevalência.
- **Possível viés de enquadramento.** O guia informava tratar-se de detecção de trojan,
  o que pode inflar o "sim". Mitigação: o ataque de fato injeta trojan em quase todas as
  gerações, tornando os 97% plausíveis.
- **Amostra parcial:** 60 de 600 (10%), cega e balanceada; serve como padrão-ouro
  parcial para calibrar o rótulo automático, não como recontagem completa.

## Frase-resumo para a conclusão
> A avaliação humana cega (3 avaliadores, 60 amostras) mostrou que o ataque injeta
> trojans detectáveis em ~97% das gerações e que o rótulo automático por regex subestima
> essa presença em ~27%. Corrigindo o ground-truth pelos humanos, a defesa baseada em
> detecção de padrão (isolada ou nas topologias que a incluem) atinge F1 ≈ 0,99 e ASR ≈
> 1,7%, enquanto topologias conservadoras falham por não detectar (ASR 47–67%); a taxa de
> falso-positivo permanece inconclusiva pela quase ausência de código limpo.

Arquivos de apoio: `consolidado_por_amostra.csv`, `concordancia_avaliadores.csv`,
`metricas_vs_humano.csv`, `fig_humano_vs_regex_f1.png`.
