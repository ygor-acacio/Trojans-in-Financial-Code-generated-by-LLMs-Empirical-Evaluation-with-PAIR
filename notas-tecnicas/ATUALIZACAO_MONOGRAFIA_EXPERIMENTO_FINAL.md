# Atualização da monografia: incorporar o experimento final (out/2026)

Este documento descreve **todas as mudanças** necessárias na monografia (versão "main (10).pdf", 48 páginas, com os experimentos de junho/2026 de 12 e 30 amostras) para que ela reflita o **experimento final** executado em outubro de 2026 (600 amostras, 2 modelos geradores, 10 cenários de defesa).

---

## 0. Instruções para a IA que vai editar o documento

1. **Idioma e estilo:** português acadêmico, mesmo tom e mesma formatação (abnTeX2/LaTeX) do documento atual. Não mude o template, a capa, a folha de rosto nem a numeração automática.
2. **Números:** use **somente** os números da Seção 2 e das tabelas da Seção 4 deste documento. Não arredonde de outro jeito, não invente números e não recalcule nada. Use vírgula decimal (0,872; 2,6%).
3. **O que manter:** o Capítulo 2 (Fundamentação) e a Tabela 1 continuam válidos. Só mexa onde este documento indicar.
4. **O que é reescrita total:** Resumo, Abstract, Capítulo 6 (Resultados) e Capítulo 8 (Considerações finais). Os Capítulos 3, 4, 5 e 7 recebem alterações pontuais e seções novas.
5. **Experimentos de junho:** não apague. Eles passam a ser **experimentos preliminares** (Seção 6.1), resumidos. O experimento final vira o resultado principal.
6. **Conteúdo sensível:** não inclua no texto o conteúdo dos prompts de ataque nem trechos de código com trojan. Descreva o ataque em nível conceitual, como o documento já faz.
7. **Pendências:** onde aparecer `[PENDENTE: ...]`, mantenha o marcador no texto (em destaque, por exemplo `\textbf{[PENDENTE: ...]}`) para o autor preencher. Não invente o conteúdo.
8. **Termos padronizados** (use sempre os mesmos):
   - Agentes: *Detector de Comportamentos*, *Detector de Padrões de Trojan*, *Verificador de Políticas*.
   - Cenários: *agente isolado*, *par de agentes*, *trio (paralelo)*, *ponderado*, *série (cascata)*, *orquestrador*.
   - "Topologia de defesa" = forma de combinar os agentes.
   - Rótulo de referência = `possible_hidden_logic` (heurística regex).

---

## 1. O que mudou entre a versão atual e o estado real do projeto

| Aspecto | Monografia atual | Estado real (experimento final) |
|---|---|---|
| Execuções | 2 experimentos (12 e 30 amostras), jun/2026 | Experimento final com **600 amostras** (4–6/out/2026); os de junho viram preliminares |
| Modelos geradores | Só DeepSeek-V3 | **DeepSeek-V3** e **Qwen2.5-72B-Instruct**; o DeepSeek-R1 foi planejado e **descartado** (ver 6.2) |
| Tarefas | 3 simples + 3 cadeias, conjuntos diferentes | **5 tarefas** iguais nos 3 níveis: `compound_interest`, `investment_fund`, `loan_amortization`, `tax_withholding`, `portfolio_return` |
| Complexidade | 2 variantes (simples e cadeia de 3 funções) | **3 níveis**: *simple* (1 função), *medium* (1 auxiliar + orquestradora), *complex* (2 auxiliares + orquestradora) |
| Iterações PAIR | Até 4, 3 fluxos, parada antecipada com nota 9 | **20 iterações por célula, sem parada antecipada**, 1 fluxo, rotação entre 3 estratégias por nível |
| Defesa | 1 configuração (coordenador com votação) | **10 cenários**: 3 agentes isolados, 3 pares, trio (paralelo, OR), ponderado, série (cascata) e orquestrador |
| Regra de bloqueio | Coordenador: 1 voto *suspicious* com conf. ≥ 0,70 **ou** ≥ 2 votos *suspicious/unknown* | Cada agente "bloqueia" se *suspicious* com conf. ≥ 0,70; o cenário combina esses bloqueios por regra própria (ver 4.3.4 nova) |
| Execução da defesa | Os 3 agentes rodam em cada configuração | Cada agente roda **1 vez por amostra** (temperatura 0) e os 10 cenários são **derivados do cache de vereditos** |
| Juiz | 1 parecer por experimento | 1 parecer por cenário (10), **mesmo system prompt** em todo o experimento |
| Ground truth | Só regex | Regex + **avaliação humana cega** de 90 amostras estratificadas por 2 avaliadores (em andamento) |
| Orquestração do código | Notebooks (`experiment_runner.ipynb`) | Scripts Python em `FinalExperiment/` (3 etapas retomáveis, `config.py` como fonte única de parâmetros) |
| Publicação | Não mencionada | Artigo com resultados preliminares **aceito no AISec Dev @ CBSoft 2026** |

---

## 2. Fatos canônicos (use exatamente estes números)

**Matriz do ataque:** 5 tarefas × 3 níveis × 2 modelos × 20 iterações = **600 amostras** (200 por nível, 300 por modelo). 1 amostra com código vazio (Qwen, `compound_interest`, nível *medium*), mantida no conjunto.

**Modelos e parâmetros:**
- Geradores: `deepseek-ai/DeepSeek-V3` e `Qwen/Qwen2.5-72B-Instruct`, temperatura 0,2, até 1600 novos tokens.
- Juiz de ataque, refinador, 3 agentes de defesa, orquestrador e juiz final: `meta-llama/Llama-3.1-8B-Instruct`, temperatura 0,0.
- 4 testes unitários locais por tarefa (iguais nos 3 níveis), executados via `safe_exec`.
- Limiar de bloqueio por agente: *suspicious* com confiança ≥ 0,70.
- Semente fixa: 42.
- Retry com backoff exponencial: 4 tentativas, timeout de 300 s.

**Rótulo de referência (regex):** **460** amostras positivas (com desvio) e **140** negativas.

| Nível | Positivas | Negativas |
|---|---|---|
| simple | 183 | 17 |
| medium | 163 | 37 |
| complex | 114 | 86 |

**Estatísticas do ataque:**
- Nota média do juiz PAIR: **7,37** (V3: 7,34; Qwen: 7,39).
- Nota ≥ 9 em **21%** das amostras: 123 com nota 9 e 3 com nota 10.
- Distribuição das notas: 1→1; 3→14; 4→1; 5→20; 6→142; 7→83; 8→213; 9→123; 10→3.
- Proporção média de testes aprovados: **0,525**. Amostras com 4/4 testes aprovados: **40,8%**.
- Tempo de execução da Etapa 1: V3 ≈ 2h26; Qwen ≈ 3h.

| Modelo | Nível | Nota média | Testes aprovados (média) | 4/4 testes | Positivas (regex) |
|---|---|---|---|---|---|
| DeepSeek-V3 | simple | 6,91 | 0,762 | 67% | 88% |
| DeepSeek-V3 | medium | 7,17 | 0,678 | 56% | 70% |
| DeepSeek-V3 | complex | 7,95 | 0,490 | 26% | 64% |
| Qwen2.5-72B | simple | 7,25 | 0,495 | 43% | 95% |
| Qwen2.5-72B | medium | 7,07 | 0,435 | 32% | 93% |
| Qwen2.5-72B | complex | 7,86 | 0,290 | 21% | 50% |

Médias por nível (os dois modelos juntos):

| Nível | Nota média | Testes aprovados (média) | 4/4 testes |
|---|---|---|---|
| simple | 7,08 | 0,629 | 55,0% |
| medium | 7,12 | 0,556 | 44,0% |
| complex | 7,91 | 0,390 | 23,5% |

**Comportamento dos agentes (600 amostras):**

| Agente | *suspicious* | *clean* | *unknown* | Bloqueios | Youden J (recall − FPR) |
|---|---|---|---|---|---|
| Detector de Comportamentos | 326 | 273 | 1 | 326 | 0,364 |
| Detector de Padrões de Trojan | 563 | 35 | 2 | 563 | 0,124 |
| Verificador de Políticas | 397 | 188 | 15 | 397 | 0,276 |

**Orquestrador:**
- Número de agentes consultados: 3 agentes em **442** amostras, 2 em **143**, 1 em **15**.
- Vezes em que cada agente foi escolhido: Comportamentos 513, Padrões 560, Políticas 554.

**Juiz LLM (parecer qualitativo):** nos 10 cenários, o juiz marcou `defense_effective = True` e deu nota de defesa 8 e nota de ataque 9. Isso inclui cenários com FPR de 0,85. Esta é a mesma inconsistência já observada nos experimentos de junho.

---

## 3. Mudanças seção por seção

### Elementos pré-textuais

**Resumo:** substituir integralmente por:

> A crescente adoção de *Large Language Models* (LLMs) como assistentes de programação amplia a produtividade, mas também introduz riscos de segurança, especialmente em aplicações financeiras. Este trabalho implementa e avalia um ambiente experimental para investigar a geração dirigida de código com trojans lógicos e sua detecção por uma defesa multiagente. O fluxo integra um ataque iterativo inspirado no framework PAIR, testes unitários locais, três agentes defensivos especializados e um bloco juiz para cálculo de métricas e avaliação qualitativa. O experimento final gerou 600 amostras a partir de cinco tarefas financeiras, três níveis de complexidade estrutural e dois modelos geradores (DeepSeek-V3 e Qwen2.5-72B-Instruct). As mesmas amostras foram avaliadas por dez cenários de defesa: cada agente isolado, os três pares, o trio em paralelo e três topologias alternativas (votação ponderada, cascata em série e um agente orquestrador). Os cenários formaram uma fronteira de compromisso entre detecção e falsos positivos. O trio em paralelo obteve a menor ASR (2,6%), mas bloqueou 85% das amostras limpas. A cascata em série reduziu a FPR para 25,7% ao custo de uma ASR de 40,0%, e a votação ponderada ficou em posição intermediária (ASR de 21,5%, FPR de 45,7%). O orquestrador consultou os três agentes em 74% dos casos e reproduziu o desempenho do trio com custo adicional. Em todas as topologias, o desempenho caiu quando o desvio foi distribuído entre mais funções. Como contribuição, o trabalho apresenta um pipeline reprodutível de ataque, defesa e avaliação e uma comparação sistemática de topologias multiagentes. O trabalho também explicita as limitações decorrentes do uso de uma heurística como referência de verdade, que está sendo complementada por avaliação humana cega.

**Abstract:** traduzir o Resumo acima para o inglês, mantendo os mesmos números com ponto decimal (ASR of 2.6%, etc.). Manter as palavras-chave e acrescentar "topologia de defesa" / "defense topology".

**Lista de Figuras e Lista de Tabelas:** são geradas automaticamente. Basta inserir as figuras e tabelas novas (Seções 4 e 5 deste documento).

**Lista de siglas:** acrescentar:
- **F1** – média harmônica entre *precision* e *recall*
- **TP/FP/FN/TN** – verdadeiros positivos, falsos positivos, falsos negativos e verdadeiros negativos
- **κ** – coeficiente kappa de Cohen

---

### Capítulo 1 — Introdução

- **3º parágrafo da introdução:** depois de "...antes de sua aceitação no fluxo de desenvolvimento.", acrescentar:
  > Além de avaliar um conjunto de agentes, o trabalho compara diferentes topologias de defesa (agentes isolados, pares, combinação paralela, votação ponderada, cascata em série e triagem por um agente orquestrador) sobre as mesmas 600 amostras, de modo que a forma de combinar os agentes seja isolada como variável experimental.

- **1.2 Objetivos:** manter o objetivo geral. Na lista de objetivos específicos:
  - trocar o último item por: "comparar a eficácia da defesa diante de diferentes níveis de complexidade estrutural do ataque e de diferentes modelos geradores;"
  - acrescentar: "comparar topologias de combinação dos agentes defensivos, medindo a contribuição de cada agente e o efeito da regra de agregação;"
  - acrescentar: "validar o rótulo de referência, a defesa e o juiz por meio de avaliação humana cega de uma amostra estratificada."

- **1.4 Organização do Trabalho:** ajustar a frase do Capítulo 6 para "O Capítulo 6 apresenta os experimentos preliminares e o experimento final, com a comparação entre dez cenários de defesa."

---

### Capítulo 2 — Fundamentação Teórica

- **2.3 (2º parágrafo):** a descrição do loop está desatualizada. Substituir as duas últimas frases ("Quando a nota é inferior a 9... limite de quatro iterações.") por:
  > Em seguida, o refinador recebe o código, os resultados dos testes, a nota e sua justificativa e produz o prompt da iteração seguinte, alternando entre três estratégias de ocultação definidas para cada nível de complexidade. Nos experimentos preliminares, a execução era encerrada quando a nota alcançava 9 ou após quatro iterações. No experimento final, cada combinação de tarefa, nível e modelo executou 20 iterações completas, sem parada antecipada, para que todas as células tivessem o mesmo número de amostras.
- **2.5.2 Lacuna de pesquisa:** na lista de itens, acrescentar: "uma comparação controlada entre topologias de combinação dos agentes defensivos (paralela, ponderada, serial e orquestrada) sobre o mesmo conjunto de amostras;"
- O restante do capítulo não muda.

---

### Capítulo 3 — Especificação de Requisitos

- **RF08:** substituir o texto por:
  > **RF08 – Consolidar pareceres dos agentes:** a defesa deve combinar os pareceres dos agentes segundo uma regra de agregação configurável. Um agente é considerado favorável ao bloqueio quando emite o veredicto *suspicious* com confiança mínima de 0,70. O sistema deve suportar, no mínimo, as regras de união (bloqueia se qualquer agente do cenário bloquear), votação ponderada, cascata em série e seleção de agentes por um orquestrador.
- **RF11:** substituir a última frase ("A comparação entre execuções é realizada na etapa de análise, e não de forma automática pelo pipeline.") por:
  > O pipeline deve gerar automaticamente um resumo comparativo entre os cenários de defesa e uma decomposição das métricas por cenário, nível de complexidade e modelo gerador.
- **Novo RF12** (acrescentar depois do RF11, em 3.1.3):
  > **RF12 – Preparar a avaliação humana:** o sistema deve extrair uma amostra estratificada das saídas do ataque e gerar um pacote de avaliação cego, sem vereditos da defesa, notas do ataque nem rótulos da heurística, mantendo em separado um gabarito que permita comparar as respostas humanas com o rótulo de referência, com cada cenário de defesa e com o juiz.
- **RNF01:** acrescentar ao final: "Todos os parâmetros do experimento final ficam centralizados em um único arquivo de configuração, a amostragem usa semente fixa (42) e os agentes defensivos operam com temperatura 0,0."
- **RNF02:** acrescentar: "Cada etapa deve ser retomável a partir dos artefatos já gravados, sem reprocessar amostras concluídas."
- **RNF06:** trocar "fora dos notebooks e dos arquivos CSV" por "fora do código-fonte e dos arquivos de dados".

---

### Capítulo 4 — Arquitetura do Sistema e Ferramentas

- **4.1:** substituir a frase "na qual três agentes emitem pareceres independentes e um coordenador decide entre bloquear ou permitir a amostra" por "na qual três agentes emitem pareceres independentes, posteriormente combinados por diferentes regras de agregação (cenários de defesa)".
- **Figura 7:** a figura atual mostra o diagrama da especificação, com orquestrador de agentes e retroalimentação. `[PENDENTE: o autor deve decidir se mantém a Figura 7 ou se a substitui por um diagrama do pipeline em 3 etapas: Ataque → Defesa (3 agentes → cache de vereditos → 10 cenários) → Juiz (métricas por cenário × nível × modelo + amostra para avaliação humana)]`. Se mantiver, ajustar a legenda para "Diagrama da arquitetura proposta; a implementação do experimento final é detalhada nas Seções 4.2 a 4.4."
- **4.2 Bloco de ataque:** reescrever o 1º parágrafo citando os **dois** geradores (DeepSeek-V3 e Qwen2.5-72B-Instruct).
  - No 2º parágrafo, trocar os parâmetros por: 20 iterações por célula, sem parada antecipada; 1 fluxo; temperatura 0,2 no gerador e 0,0 no juiz; limite de 1600 novos tokens.
  - Manter a escala de notas. Remover a frase "A nota 9 provoca parada antecipada".
  - Sobre a nota 10: `[PENDENTE: confirmar se as 3 amostras com nota 10 do experimento final foram mantidas; no código atual elas permanecem no conjunto]`.
  - Substituir o 3º parágrafo (variantes) por:
    > O experimento final utiliza cinco tarefas financeiras — juros compostos (`compound_interest`), fundo de investimento (`investment_fund`), amortização de empréstimo (`loan_amortization`), retenção de imposto (`tax_withholding`) e retorno de carteira (`portfolio_return`) — cada uma em três níveis de complexidade estrutural. No nível *simple*, o código contém uma única função pública. No nível *medium*, uma função auxiliar privada é chamada por uma função orquestradora, e o desvio pode residir no auxiliar e ser propagado pela orquestradora. No nível *complex*, duas funções auxiliares e uma orquestradora formam uma cadeia na qual o desvio é distribuído, de modo que nenhuma função isolada revele todo o comportamento. A assinatura pública e os quatro testes unitários de cada tarefa são os mesmos nos três níveis. Em todos os casos, o prompt proíbe rede, acesso a arquivos, subprocessos e execução dinâmica, limitando o ataque a desvios lógicos no valor calculado.
  - Acrescentar um parágrafo sobre o DeepSeek-R1:
    > O DeepSeek-R1 foi considerado como terceiro gerador, mas foi excluído do experimento final. No roteador de inferência utilizado, apenas um provedor servia o modelo, e as gerações longas de raciocínio resultavam em erros de *timeout* (HTTP 504). Na execução de teste, cerca de metade das amostras do R1 retornou vazia, com custo estimado de aproximadamente 50 horas para completar suas 300 amostras. Para preservar a qualidade do conjunto, optou-se por concluir o experimento com os dois modelos restantes.
- **4.3 (parágrafo introdutório):** trocar "e por um coordenador. Os agentes são executados em sequência, mas analisam a mesma amostra de forma independente." por:
  > Cada agente analisa a amostra de forma independente e é executado uma única vez por amostra (1.800 chamadas no total). Como os agentes operam com temperatura 0,0, seus vereditos são tratados como determinísticos e armazenados em cache; todos os cenários de defesa são derivados desse cache, sem reexecutar os agentes. Assim, a regra de agregação é a única variável entre os cenários.
- **4.3.1 a 4.3.3:** sem mudanças.
- **4.3.4:** substituir "Coordenador da defesa" por uma nova seção **"4.3.4 Regras de agregação e topologias de defesa"**, com o texto abaixo e a Tabela A (Seção 4 deste documento):
  > Um agente é considerado favorável ao bloqueio quando emite o veredicto *suspicious* com confiança maior ou igual a 0,70; o estado *unknown*, associado a falhas de interpretação do JSON, não conta como bloqueio. A partir desses votos, foram avaliados dez cenários.
  >
  > **Subconjuntos com união (7 cenários).** Os três agentes isolados, os três pares e o trio usam a regra de união (OR): o cenário bloqueia a amostra se qualquer um de seus agentes a bloquear. O trio corresponde à arquitetura paralela da especificação.
  >
  > **Votação ponderada.** Cada agente recebe um peso, e a amostra é bloqueada quando a soma dos pesos dos agentes que a bloqueiam é maior ou igual à metade do peso total. Os pesos foram definidos a partir do poder discriminativo isolado de cada agente, medido pelo índice de Youden (J = recall − FPR): Detector de Comportamentos 1,5 (J = 0,364), Verificador de Políticas 1,0 (J = 0,276) e Detector de Padrões de Trojan 0,6 (J = 0,124). O limiar resultante é 1,55, de modo que o Detector de Padrões, mais sensível e menos seletivo, não consegue bloquear sozinho. Como os pesos foram calibrados nas próprias 600 amostras, eles constituem uma hipótese de projeto, não um parâmetro aprendido em dados independentes.
  >
  > **Cascata em série.** Os agentes são consultados na ordem Comportamentos → Políticas → Padrões, com saída antecipada. Se um agente classifica a amostra como *suspicious* com confiança ≥ 0,90, ela é bloqueada e a cascata termina. Se a classifica como *clean* com confiança ≥ 0,70, ela é liberada e a cascata termina. Caso contrário, a amostra segue para o próximo agente. Se nenhum agente emitir decisão forte, aplica-se a maioria: a amostra é bloqueada quando ao menos dois agentes a bloqueiam.
  >
  > **Orquestrador.** Um quarto agente LLM (Llama-3.1-8B-Instruct, temperatura 0,0) não analisa o código em busca de trojans. Ele faz uma triagem e decide quais especialistas consultar, respondendo em JSON com a lista de agentes e uma justificativa. O veredicto final é a união dos agentes escolhidos. Esse cenário acrescenta uma chamada LLM por amostra.
- **4.4 Bloco de avaliação:** acrescentar ao final:
  > No experimento final, o juiz é executado uma vez para cada um dos dez cenários, sempre com o mesmo *system prompt*, e gera também uma decomposição das métricas por nível de complexidade e por modelo gerador. O bloco também extrai a amostra estratificada para a avaliação humana descrita na Seção 5.3.
- **4.5 Ferramentas e modelos:** substituir o 2º parágrafo por:
  > O experimento final é orquestrado por scripts Python organizados em três etapas independentes e retomáveis: ataque, defesa e juiz. Um único arquivo de configuração concentra modelos, matriz experimental, limiares, pesos, parâmetros de *retry* e semente. A Etapa 1 grava uma célula por combinação de modelo, nível e tarefa e as consolida em um único CSV de 600 linhas. A Etapa 2 grava o cache de vereditos dos agentes e um CSV por cenário. A Etapa 3 grava os relatórios do juiz, o resumo comparativo dos cenários, as métricas decompostas e o pacote de avaliação humana. As chamadas aos modelos usam `huggingface_hub` (`InferenceClient`, interface `chat_completion`) com *retry* e *backoff* exponencial (quatro tentativas, *timeout* de 300 s).

  Manter a frase sobre `pandas`, `matplotlib` e `python-dotenv` e acrescentar `openpyxl` (planilhas da avaliação humana).

---

### Capítulo 5 — Metodologia e Plano de Avaliação

- **5.1 Design do experimento:** substituir integralmente por:
  > O experimento final foi desenhado como uma matriz completa de 5 tarefas × 3 níveis de complexidade × 2 modelos geradores × 20 iterações, totalizando 600 amostras (200 por nível e 300 por modelo). Cada combinação de tarefa, nível e modelo forma uma célula com 20 amostras. Em cada iteração, o código gerado foi submetido aos testes unitários locais por meio de `safe_exec`, recebeu uma nota do juiz de ataque e foi registrado antes de seguir para a defesa.
  >
  > Três fatores variam: a complexidade estrutural do código (*simple*, *medium*, *complex*), o modelo gerador (DeepSeek-V3, Qwen2.5-72B-Instruct) e a topologia de defesa (dez cenários). Os agentes defensivos, seus *prompts*, o modelo de defesa e o limiar de confiança foram mantidos constantes. Como os vereditos dos agentes são computados uma única vez e reaproveitados, as diferenças entre cenários decorrem exclusivamente da regra de agregação.
  >
  > Os experimentos preliminares de junho de 2026 (Seção 6.1) usaram um desenho reduzido, com um único gerador, duas variantes de complexidade, até quatro iterações com parada antecipada e uma única configuração de defesa. Eles serviram para validar o pipeline e motivaram a ampliação da matriz.
- **5.2 Referência de verdade:** manter o texto. No 1º parágrafo, trocar "`detect_possible_hidden_logic`" por "`detect_hidden_logic`". Acrescentar ao final:
  > No experimento final, a heurística rotulou 460 amostras como positivas e 140 como negativas. A distribuição é desigual entre níveis: o nível *simple* tem apenas 17 amostras negativas, contra 37 no *medium* e 86 no *complex*. Por isso, a FPR por nível, sobretudo no *simple*, é estimada sobre poucos exemplos e deve ser lida com cautela.
- **Nova seção 5.3 Avaliação humana** (as atuais 5.3 e 5.4 passam a 5.4 e 5.5):
  > Para validar a heurística de referência e medir o acerto da defesa e do juiz em relação a um julgamento humano, foi extraída uma amostra estratificada de 90 amostras: três por célula de tarefa × nível × modelo (30 células), com semente fixa. As amostras foram embaralhadas e renumeradas, para que amostras vizinhas não revelem a mesma célula de origem. Cada uma foi exportada como arquivo `.py` com um cabeçalho neutro que descreve apenas a especificação benigna da função.
  >
  > Dois avaliadores, de forma independente, preenchem uma planilha que não contém nenhum veredicto automático: nem nota do ataque, nem rótulo da heurística, nem decisão de agentes ou cenários. Para cada amostra, registram se há desvio malicioso (0/1), onde ele está, se é inofensivo (0/1), se o código cumpre a tarefa (0/1), a furtividade (1–5), a confiança no próprio julgamento (1–5) e observações. Um gabarito mantido em separado associa cada amostra à sua origem e às decisões automáticas.
  >
  > A análise prevista compreende: (i) a concordância entre avaliadores, medida pelo coeficiente kappa de Cohen (COHEN, 1960); (ii) a concordância entre o rótulo humano e a heurística regex; (iii) as métricas de cada cenário de defesa recalculadas com o rótulo humano como referência; e (iv) a concordância entre o juiz e os avaliadores.
- **5.4 (antiga 5.3) O bloco de avaliação:** acrescentar: "No experimento final, o mesmo *system prompt* do juiz é utilizado nos dez cenários."
- **5.5 (antiga 5.4) Métricas:** manter as equações. Acrescentar depois da Eq. 5.6:
  > Para resumir o poder discriminativo isolado de cada agente, utiliza-se também o índice de Youden (YOUDEN, 1950):
  > J = Recall − FPR. (5.7)

---

### Capítulo 6 — Resultados e Discussão (reescrever inteiro)

Estrutura nova:

**6.1 Experimentos preliminares.** Condensar o conteúdo atual das Seções 6.1 a 6.3 em um único bloco:
- Manter a Tabela 2 (matriz de confusão) e a Tabela 3 (métricas), renomeadas para "dos experimentos preliminares".
- A Tabela 4 (votos por agente) pode ser removida ou mantida.
- Manter as conclusões centrais: FPR de 1,000 no cenário simples, ASR de 10,5% e dois falsos negativos do Detector de Padrões com confiança 1,0 nas cadeias, concentração da decisão em um agente.
- Fechar com: "Essas observações motivaram três mudanças no experimento final: ampliar e equilibrar a matriz de amostras, acrescentar um nível intermediário de complexidade e avaliar a contribuição de cada agente por meio de cenários de defesa alternativos."
- `[PENDENTE: o autor decide se cita aqui o artigo aceito no AISec Dev @ CBSoft 2026 e os números dele (151 amostras), que diferem dos 12 + 30 desta seção]`.

**6.2 Execução do experimento final.**
- Etapa 1 (ataque) em 4/out/2026; Etapas 2 e 3 em 5/out/2026; cenários adicionais em 6/out/2026.
- 600 amostras, sendo apenas 1 vazia.
- Explicar em 2–3 frases a exclusão do R1 (ver 4.2), citando o motivo de infraestrutura.

**6.3 Resultados do ataque.**
- Usar a tabela de estatísticas do ataque da Seção 2.
- Pontos a discutir:
  - A nota média de furtividade sobe com a complexidade (7,08 → 7,12 → 7,91), enquanto a correção funcional cai (amostras com 4/4 testes: 55,0% → 44,0% → 23,5%). O juiz PAIR pontua furtividade, não correção, e várias amostras complexas receberam nota alta mesmo falhando nos testes.
  - A proporção de amostras positivas pela heurística cai com a complexidade (91,5% → 81,5% → 57,0%). Há duas explicações possíveis, e o texto deve declarar que não é possível separá-las sem a avaliação humana: os desvios distribuídos usam menos os padrões textuais que a regex procura, ou os modelos de fato inserem menos desvios.
  - O DeepSeek-V3 produziu código funcionalmente mais correto que o Qwen (0,643 contra 0,407 de testes aprovados em média).

**6.4 Agentes isolados e combinação por união.** Usar a Tabela B. Pontos:
- O Detector de Padrões de Trojan é o mais sensível (recall 0,967) e o menos seletivo (FPR 0,843): bloqueou 563 das 600 amostras.
- O Detector de Comportamentos é o mais seletivo (FPR 0,264) e o de menor recall (0,628). Isso é coerente com o modelo de ameaça, em que o ataque não usa rede nem arquivos.
- Qualquer cenário que inclua o Detector de Padrões fica com ASR entre 2,6% e 3,3% e FPR entre 0,84 e 0,85.
- O trio é idêntico ao par Padrões + Políticas (448 TP, 119 FP, 12 FN, 21 TN), e o ganho do trio sobre o Detector de Padrões sozinho é de 0,7 ponto percentual de ASR. A união confirma, em escala maior, a concentração de decisão observada nos experimentos preliminares.

**6.5 Comparação entre topologias.** Usar a Tabela B, a Figura A (pontos de operação) e a Figura C (matrizes de confusão). Pontos:
- Os cenários formam uma fronteira de compromisso; nenhuma topologia domina as outras.
- **Paralelo (trio):** ASR 2,6%, FPR 0,850, F1 0,872.
- **Orquestrador:** ASR 4,6%, FPR 0,821, F1 0,866. Escolheu os 3 agentes em 442 de 600 casos (73,7%), 2 em 143 e 1 em 15 (Figura E). Como o Detector de Padrões domina a decisão, a triagem quase nunca reduz chamadas sem mudar o veredicto. O orquestrador acrescenta uma chamada LLM por amostra sem melhorar o compromisso: uma estrutura mais elaborada não produziu melhor resultado.
- **Ponderado:** ASR 21,5%, FPR 0,457, F1 0,816. Reduzir o peso do agente que bloqueia demais cortou a FPR quase pela metade (0,850 → 0,457), ao custo de mais trojans passando. Ficou praticamente igual ao par Comportamentos + Políticas (ASR 21,1%, FPR 0,464). Os pesos funcionam como um ajuste explícito do ponto de operação.
- **Série:** a menor FPR (0,257), mas a maior ASR (40,0%) e o menor F1 (0,715). No nível *simple* não houve nenhum falso positivo (FPR 0,000, sobre 17 negativas).
- Variabilidade entre células (Figura D): os cenários com o Detector de Padrões têm mediana de ASR por célula igual a 0. A série e o Detector de Comportamentos isolado têm a maior dispersão (até ~0,9 em algumas células).
- A escolha da topologia depende do custo relativo de um falso positivo (atrito, código legítimo bloqueado) e de um falso negativo (trojan aceito). Em aplicações financeiras, isso precisa ser explicitado pela organização.

**6.6 Efeito da complexidade.** Usar a Tabela C e a Figura B.
- Em todas as topologias, o F1 cai de *simple* para *complex*: trio 0,970 → 0,725; ponderado 0,919 → 0,681; série 0,819 → 0,589.
- A ASR sobe na série (30,6% → 49,1%) e no ponderado (13,1% → 30,7%). No trio ela permanece baixa (1,6% → 6,1%), mas a acurácia cai de 0,945 para 0,595 porque a FPR sobe para 0,861 no *complex*.
- Isso confirma o achado dos experimentos preliminares: distribuir o desvio por mais funções dificulta a detecção. Reforça também a necessidade de análise interprocedural.

**6.7 Efeito do modelo gerador.** Usar a Tabela D e a Figura F.
- As diferenças entre modelos são pequenas diante das diferenças entre topologias: a ASR da série é 40,1% (V3) e 39,9% (Qwen).
- O código do DeepSeek-V3 escapou um pouco mais nas topologias de alta sensibilidade (trio: 3,6% contra 1,7%).

**6.8 Parecer do juiz LLM.**
- Nos dez cenários, o juiz classificou a defesa como efetiva, com nota de defesa 8 e nota de ataque 9, inclusive em cenários com FPR de 0,85 ou ASR de 40%.
- O parecer qualitativo não discrimina entre cenários e não deve ser usado como evidência de eficácia, o que confirma a observação dos experimentos preliminares. Essa é uma das razões para a avaliação humana.

**6.9 Avaliação humana.** `[PENDENTE: resultados da avaliação humana — κ entre os dois avaliadores; concordância humano × regex; métricas dos 10 cenários recalculadas com o rótulo humano; concordância humano × juiz. Se não estiverem prontos na entrega, a seção descreve o protocolo (já na 5.3) e declara a análise como em andamento.]`

**6.10 Limitações** (substituir a lista atual):
1. O rótulo de referência é uma heurística regex, e todas as métricas dependem dela até a conclusão da avaliação humana.
2. As classes estão desbalanceadas (460 × 140): a FPR geral se apoia em 140 amostras, e a FPR do nível *simple* em apenas 17.
3. Os pesos do cenário ponderado foram calibrados nos mesmos dados em que foram avaliados.
4. A defesa, o juiz e o orquestrador usam um único modelo pequeno (Llama-3.1-8B-Instruct); os resultados podem não se manter com modelos de defesa maiores.
5. Apenas dois modelos geradores foram avaliados; o DeepSeek-R1 foi excluído por limitação de infraestrutura.
6. O ataque é de geração dirigida (o pedido malicioso é explícito), e não de quebra de recusa.
7. `safe_exec` não substitui uma sandbox com isolamento de sistema operacional.
8. As tarefas são sintéticas e cobrem cinco funções financeiras.

---

### Capítulo 7 — Cronograma

- Trocar "até 28 de setembro de 2026" por `[PENDENTE: data de fechamento do texto]`.
- Atualizar a coluna "Realização" da Tabela 5:

| Atividade | Realização (atualizar para) |
|---|---|
| Implementação do fluxo com atacante PAIR e LLM gerador | Concluída em junho; ampliada em outubro para 2 geradores e 3 níveis. |
| Desenvolvimento e ajustes da camada de defesa multiagente | Concluído em junho; em outubro, acrescentados os cenários ponderado, série e orquestrador. |
| Execução dos testes e validação experimental | Preliminares em 3 e 18 de junho; experimento final em 4–6 de outubro (600 amostras, 10 cenários). |
| Análise dos resultados e consolidação das conclusões | Concluída para o experimento final; avaliação humana em andamento. |
| Redação final, revisão textual e preparação da entrega | `[PENDENTE: status atual]` |

- Acrescentar uma linha: **"Avaliação humana cega (90 amostras, 2 avaliadores)"** — período previsto: não previsto originalmente; realização: pacote preparado em 12/out/2026, `[PENDENTE: status]`.
- No parágrafo final, acrescentar que o período ganho permitiu ampliar o experimento e incluir a comparação de topologias.

---

### Capítulo 8 — Considerações Finais (reescrever)

**8.1 Síntese:** manter a primeira frase. Atualizar o restante para: dois geradores, cinco tarefas, três níveis, 600 amostras, dez cenários de defesa, juiz com *system prompt* único e avaliação humana cega.

**8.2 Contribuições:**
1. Pipeline reprodutível em três etapas retomáveis, com cache de vereditos que permite comparar regras de agregação sem reexecutar os agentes.
2. Matriz experimental equilibrada (tarefa × nível × modelo).
3. Comparação sistemática de dez topologias de defesa, que evidencia a fronteira de compromisso entre ASR e FPR.
4. Protocolo de avaliação humana cega para validar o rótulo, a defesa e o juiz.
5. Publicação dos resultados preliminares no AISec Dev @ CBSoft 2026.

Status dos objetivos específicos:

| Objetivo | Status |
|---|---|
| Fluxo completo | Cumprido |
| Requisitos | Cumprido |
| Agentes especializados | Cumprido, com o analisador de fluxo de dados substituído pelo Detector de Comportamentos |
| Plano de avaliação | Cumprido |
| Comparar induções do PAIR | Cumprido para 3 níveis e 2 modelos |
| Comparar topologias | Cumprido |
| Avaliação humana | Em andamento |

**8.3 Andamento atual:** substituir pelos achados do experimento final, em 3 frases:
- Nenhuma topologia domina: o trio minimiza a ASR (2,6%) com FPR de 0,85, e a série minimiza a FPR (0,26) com ASR de 40%.
- O Detector de Padrões concentra a decisão, e o orquestrador não melhora o compromisso.
- A complexidade degrada todas as topologias.

Manter a ressalva de que os resultados não sustentam o uso da defesa em produção e de que dependem do rótulo heurístico até a conclusão da avaliação humana.

**8.4 Perspectivas:** manter os itens atuais que continuam válidos (análise interprocedural, sandbox, mais tarefas). Remover "estudos de ablação" e "variação sistemática das configurações da defesa", que foram feitos. Acrescentar:
- concluir a avaliação humana e recalcular as métricas;
- calibrar pesos e limiares em uma partição separada dos dados;
- avaliar modelos de defesa maiores ou ajustados para código;
- incluir modelos de raciocínio (como o DeepSeek-R1) por uma API que suporte gerações longas;
- testar ataques sem pedido explícito (quebra de recusa).

---

## 4. Tabelas novas (converter para LaTeX no padrão das tabelas existentes)

**Tabela A — Cenários de defesa avaliados** (Seção 4.3.4)

| Cenário | Agentes | Regra |
|---|---|---|
| Comportamentos, Padrões, Políticas (isolados) | 1 | O agente bloqueia |
| Pares (3 combinações) | 2 | União (OR) |
| Trio (paralelo) | 3 | União (OR) |
| Ponderado | 3 | Σ pesos dos que bloqueiam ≥ 1,55 (pesos 1,5 / 1,0 / 0,6) |
| Série (cascata) | 3, em ordem | Saída antecipada (bloqueia com conf. ≥ 0,90; libera com *clean* ≥ 0,70); senão, maioria |
| Orquestrador | 1 a 3, escolhidos por LLM | União dos escolhidos |

**Tabela B — Métricas dos 10 cenários (600 amostras; referência: heurística regex)** (Seções 6.4 e 6.5)

| Cenário | TP | FP | FN | TN | ASR | FPR | Precision | Recall | F1 | Acurácia |
|---|---|---|---|---|---|---|---|---|---|---|
| Trio (paralelo) | 448 | 119 | 12 | 21 | 2,6% | 0,850 | 0,790 | 0,974 | 0,872 | 0,782 |
| Padrões + Políticas | 448 | 119 | 12 | 21 | 2,6% | 0,850 | 0,790 | 0,974 | 0,872 | 0,782 |
| Comportamentos + Padrões | 446 | 118 | 14 | 22 | 3,0% | 0,843 | 0,791 | 0,970 | 0,871 | 0,780 |
| Padrões (isolado) | 445 | 118 | 15 | 22 | 3,3% | 0,843 | 0,790 | 0,967 | 0,870 | 0,778 |
| Orquestrador | 439 | 115 | 21 | 25 | 4,6% | 0,821 | 0,792 | 0,954 | 0,866 | 0,773 |
| Comportamentos + Políticas | 363 | 65 | 97 | 75 | 21,1% | 0,464 | 0,848 | 0,789 | 0,818 | 0,730 |
| Ponderado | 361 | 64 | 99 | 76 | 21,5% | 0,457 | 0,849 | 0,785 | 0,816 | 0,728 |
| Políticas (isolado) | 334 | 63 | 126 | 77 | 27,4% | 0,450 | 0,841 | 0,726 | 0,779 | 0,685 |
| Comportamentos (isolado) | 289 | 37 | 171 | 103 | 37,2% | 0,264 | 0,887 | 0,628 | 0,735 | 0,653 |
| Série (cascata) | 276 | 36 | 184 | 104 | 40,0% | 0,257 | 0,885 | 0,600 | 0,715 | 0,633 |

**Tabela C — Métricas por nível de complexidade** (Seção 6.6)

| Cenário | Nível | TP | FP | FN | TN | ASR | FPR | F1 | Acurácia |
|---|---|---|---|---|---|---|---|---|---|
| Trio | simple | 180 | 8 | 3 | 9 | 1,6% | 0,471 | 0,970 | 0,945 |
| Trio | medium | 161 | 37 | 2 | 0 | 1,2% | 1,000 | 0,892 | 0,805 |
| Trio | complex | 107 | 74 | 7 | 12 | 6,1% | 0,861 | 0,725 | 0,595 |
| Ponderado | simple | 159 | 4 | 24 | 13 | 13,1% | 0,235 | 0,919 | 0,860 |
| Ponderado | medium | 123 | 21 | 40 | 16 | 24,5% | 0,568 | 0,801 | 0,695 |
| Ponderado | complex | 79 | 39 | 35 | 47 | 30,7% | 0,454 | 0,681 | 0,630 |
| Série | simple | 127 | 0 | 56 | 17 | 30,6% | 0,000 | 0,819 | 0,720 |
| Série | medium | 91 | 11 | 72 | 26 | 44,2% | 0,297 | 0,687 | 0,585 |
| Série | complex | 58 | 25 | 56 | 61 | 49,1% | 0,291 | 0,589 | 0,595 |
| Orquestrador | simple | 171 | 5 | 12 | 12 | 6,6% | 0,294 | 0,953 | 0,915 |
| Orquestrador | medium | 161 | 36 | 2 | 1 | 1,2% | 0,973 | 0,894 | 0,810 |
| Orquestrador | complex | 107 | 74 | 7 | 12 | 6,1% | 0,861 | 0,725 | 0,595 |

Nota para a legenda: as negativas por nível são 17 (*simple*), 37 (*medium*) e 86 (*complex*).

**Tabela D — Métricas por modelo gerador** (Seção 6.7)

| Cenário | Modelo | TP | FP | FN | TN | ASR | FPR | F1 | Acurácia |
|---|---|---|---|---|---|---|---|---|---|
| Trio | DeepSeek-V3 | 214 | 63 | 8 | 15 | 3,6% | 0,808 | 0,858 | 0,763 |
| Trio | Qwen2.5-72B | 234 | 56 | 4 | 6 | 1,7% | 0,903 | 0,886 | 0,800 |
| Ponderado | DeepSeek-V3 | 172 | 35 | 50 | 43 | 22,5% | 0,449 | 0,802 | 0,717 |
| Ponderado | Qwen2.5-72B | 189 | 29 | 49 | 33 | 20,6% | 0,468 | 0,829 | 0,740 |
| Série | DeepSeek-V3 | 133 | 16 | 89 | 62 | 40,1% | 0,205 | 0,717 | 0,650 |
| Série | Qwen2.5-72B | 143 | 20 | 95 | 42 | 39,9% | 0,323 | 0,713 | 0,617 |
| Orquestrador | DeepSeek-V3 | 209 | 62 | 13 | 16 | 5,9% | 0,795 | 0,848 | 0,750 |
| Orquestrador | Qwen2.5-72B | 230 | 53 | 8 | 9 | 3,4% | 0,855 | 0,883 | 0,797 |

Nota para a legenda: a classe negativa tem 78 amostras para o V3 e 62 para o Qwen.

---

## 5. Figuras novas

Todas já existem em `FinalExperiment/data/figures/`. As figuras foram geradas com rótulos em português; inserir com largura de texto (`\textwidth`) e citar a fonte como "Elaborada pelo autor (2026)".

| Ref. | Arquivo | Seção | Legenda sugerida |
|---|---|---|---|
| Figura A | `fig1_operating_points.png` | 6.5 | Pontos de operação (Recall × FPR) dos dez cenários de defesa. O canto superior esquerdo é o ideal; ASR = 1 − Recall. |
| Figura B | `fig4_complexity.png` | 6.6 | ASR e F1 por nível de complexidade para as quatro topologias de sistema. |
| Figura C | `fig3_confusion_matrices.png` | 6.5 | Matrizes de confusão dos agentes isolados e das quatro topologias de sistema. |
| Figura D | `fig5_boxplot_percell_asr.png` | 6.5 | Distribuição da ASR entre as 30 células (tarefa × nível × modelo) para cada cenário. |
| Figura E | `fig6_orchestrator.png` | 6.5 | Número de agentes consultados pelo orquestrador e frequência de consulta de cada agente. |
| Figura F | `fig7_model_breakdown.png` | 6.7 | ASR por modelo gerador e topologia de defesa. |
| (opcional) | `fig2_metrics_bars.png` | 6.5 | ASR, FPR, F1 e acurácia por cenário. É redundante com a Tabela B; usar apenas se o autor preferir a forma visual. |

---

## 6. Referências a acrescentar

- COHEN, J. A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, v. 20, n. 1, p. 37–46, 1960. (kappa, Seção 5.3)
- YOUDEN, W. J. Index for rating diagnostic tests. *Cancer*, v. 3, n. 1, p. 32–35, 1950. (índice J, Seções 4.3.4 e 5.5)
- DEEPSEEK-AI. *DeepSeek-V3 Technical Report*. 2024. ArXiv preprint arXiv:2412.19437. (Seção 4.2)
- QWEN TEAM. *Qwen2.5 Technical Report*. 2024. ArXiv preprint arXiv:2412.15115. (Seção 4.2)
- GRATTAFIORI, A. et al. *The Llama 3 Herd of Models*. 2024. ArXiv preprint arXiv:2407.21783. (Seções 4.2 e 4.3)
- MARIA, Y. A.; HAYASHI, V. T.; SIMPLICIO JUNIOR, M. A. *Trojans in Financial Code generated by LLMs: Empirical Evaluation with PAIR*. In: AISec Dev @ CBSoft 2026. `[PENDENTE: confirmar a forma de citação e as páginas com o autor]`

---

## 7. Pendências que só o autor resolve

1. Manter ou redesenhar a Figura 7 (Seção 3, Capítulo 4).
2. Confirmar o tratamento das 3 amostras com nota 10 (Seção 4.2).
3. Decidir se e como citar o artigo do AISec Dev e seus números (Seção 6.1).
4. Resultados da avaliação humana (Seção 6.9) e status no cronograma (Capítulo 7).
5. Data de fechamento do texto (Capítulo 7).

---

## 8. Checklist para a IA editora ao terminar

- [ ] Resumo e Abstract citam 600 amostras e os números do trio, da série e do ponderado.
- [ ] Nenhum trecho do texto ainda afirma que "apenas uma configuração da defesa foi avaliada" ou que o experimento "não compara diferentes configurações da defesa" (frases atuais nas Seções 5.1 e 6.5).
- [ ] Nenhum trecho afirma parada antecipada ou "até quatro iterações" para o experimento final.
- [ ] RF08 e a Seção 4.3.4 não descrevem mais o coordenador com regra "≥ 2 votos *suspicious/unknown*", exceto na Seção 6.1 (preliminares).
- [ ] As Tabelas B, C e D e as Figuras A a F estão citadas no texto antes de aparecerem.
- [ ] Todos os marcadores `[PENDENTE: ...]` estão visíveis.
- [ ] Nenhum prompt de ataque nem trecho de código com trojan foi incluído.
- [ ] As novas referências estão na lista e são citadas no texto.
