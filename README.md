# Defesa Multiagente contra Inserção de Trojans em Código Gerado por LLMs em Aplicações Financeiras

Trabalho de Conclusão de Curso — Engenharia de Computação, Escola Politécnica da
Universidade de São Paulo (PCS).

**Autor:** Ygor Acacio Maria
**Orientadores:** Prof. Dr. Victor Takashi Hayashi · Prof. Dr. Marcos Antonio Simplicio Junior

> **Repositório privado.** Contém o TCC completo: monografia, artigo, entregas, o
> experimento (código + dados + análise) e a fonte do site. O site público e a demonstração
> ficam em um repositório separado.

---

## Pergunta de pesquisa

LLMs podem inserir **trojans de lógica** (desvios numéricos silenciosos, disparados por
entradas raras, sem rede/arquivo/execução) em código financeiro. Uma **defesa multiagente**
consegue detectá-los — e a forma como os agentes são combinados muda o resultado?

O ataque usa **PAIR** (refinamento iterativo automático de prompts). A defesa usa 3 agentes
(detector de comportamento, padrão de trojan, verificador de política) sobre Llama-3.1-8B,
combinados em 10 topologias (isolados, pares, união/trio, voto ponderado, cascata serial,
orquestrador LLM).

## Como o repositório está organizado

| Pasta | Conteúdo |
|---|---|
| **`monografia/`** | `ENTREGA_FINAL_MONOGRAFIA_TCC.md` (texto completo para a plataforma) + `FIGURAS_MONOGRAFIA/` |
| **`artigo-estendido/`** | `ARTIGO_ESTENDIDO_EN.md` (versão estendida em inglês, ACM) + `FIGURAS_ARTIGO_EN/` |
| **`entregas-pcs3860/`** | Banner (.pptx/.pdf) e press release (.docx) — PT e EN |
| **`experimento/`** | O experimento final. `FinalExperiment/` (código + `data/` + `analysis/` + logs) com `Defense/` e `Judge/` como **irmãos** (o código resolve esses caminhos — não separe) |
| **`site/`** | Fonte do site estático (cópia de desenvolvimento; o repo público vem daqui) |
| **`workshop-anterior/`** | `Attack/` e `Workshop/` — notebooks e código da fase do workshop AISec Dev |
| **`referencias/`** | Diretrizes da PCS para monografia e o PDF do workshop (CBSOFT) |
| **`notas-tecnicas/`** | Descrição técnica, rascunhos de atualização e o notebook de execução |

## Rodar o experimento

```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
cp .env.example .env            # preencha HF_TOKEN
cd experimento/FinalExperiment
python stage1_attack.py         # ataque PAIR  -> data/attack
python stage2_defense.py        # defesa 3 agentes -> data/defense
python stage3_judge.py          # juiz final -> data/judge
```

Figuras e tabelas: `experimento/FinalExperiment/analysis/`.

## Principais resultados

- Avaliação humana (60 amostras × 3 avaliadores): prevalência real de trojan ~96,7%, contra
  ~70% do regex — o regex sozinho **subestima** o problema (recall ~72%).
- Melhor configuração (padrão-de-trojan / trio) sob rótulos humanos: **F1 = 0,991**, ASR = 1,7%.
- Voto ponderado ≡ maioria simples (425 bloqueios idênticos); a cascata com bloqueio
  antecipado nunca disparou (nenhum caso suspeito ≥ 0,90). A combinação importa, mas as
  variantes "sofisticadas" degeneraram nas condizentes.

Estatística: ICs de Wilson, McNemar exato, tendência de Cochran-Armitage, kappa de
Cohen/Fleiss. Trojans são inofensivos por construção (apenas desvio numérico).

## Envio dos repositórios

Veja **`_ENVIO_REPOS.md`** — passo a passo para publicar este repo (privado) e o do site
(público) no seu nome.

---

Resultados parciais apresentados no workshop AISec Dev (CBSoft 2026).
