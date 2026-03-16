# AutoBot Pro — Estado Partilhado (Gemini ↔ Claude)

> Ficheiro de comunicação assíncrona entre Gemini CLI e Claude Code.
> Qualquer agente deve ler este ficheiro no início de cada sessão e atualizar a sua secção ao terminar trabalho relevante.

---

## Estado Atual do Projeto

**Última atualização:** 2026-03-15 — Claw (Orquestrador)

### Demos Conpletas ✅
| Demo | Estado | Testes | Notas |
|------|--------|--------|-------|
| 01-instagram-autoresponder | ✅ Completo | 18/18 ✅ | rules, simulator, dashboard |
| 02-appointment-reminder | ✅ Completo | 12/12 ✅ | models, scheduler, dashboard |
| 03-price-monitor | ✅ Completo | 12/12 ✅ | models, scraper, dashboard |

### Fase Atual: Melhorias Pós-PASSO 6 ✅ / A aguardar Demo 04
**Responsável:** Claude Code (implementação) / Gemini CLI (decisão Demo 04)

### Testes
| Suite | Testes | Estado |
|-------|--------|--------|
| shared/tests | 14 | ✅ |
| demo01 | 18 | ✅ |
| demo02 | 12 | ✅ |
| demo03 | 12 | ✅ |
| **Total** | **56** | **✅** |

---

## Fila de Trabalho para Gemini

_Tarefas de arquitetura/estratégia para o Gemini CLI:_

- [ ] Revisar estrutura do PASSO 5 quando Claude terminar
- [ ] Validar estratégia de portfolio.md (foco no mercado PT)
- [ ] Sugerir melhorias no github-profile-readme.md
- [ ] **Decidir arquitectura Demo 04** — opções:
  - **(A) Email Automator** — envia emails personalizados com base em triggers (novo cliente, carrinho abandonado); usa smtplib + mock SMTP; porta 8004
  - **(B) Lead Generator Bot** — formulário web que captura leads e notifica por Telegram; simples, muito útil para PMEs PT
  - **(C) outra sugestão**
  - Critério: sem APIs pagas, modo demo 100% funcional sem credenciais, útil para pequenos negócios em Portugal

---

## Fila de Trabalho para Claude

_Tarefas de implementação para o Claude Code — ORDENADAS:_

### PRIORIDADE ALTA (PASSO 5 — Documentação)

1. [x] **Criar `docs/portfolio.md`** ✅ (2026-03-15)
   - One-pager profissional do serviço
   - Descrição de cada automação
   - Benefícios concretos (percentagens, tempo poupado)
   - Tabela de preços
   - Processo de trabalho (4 passos)
   - FAQ

2. [x] **Criar `docs/pricing.md`** ✅ (2026-03-15)
   - Pacotes (Basic, Pro, Enterprise)
   - O que cada pacote inclui
   - Opções de manutenção mensal
   - Descontos para primeiro cliente

3. [x] **Atualizar `README.md` principal** ✅ (2026-03-15)
   - Badges shields.io (Python 3.11+, FastAPI, Docker, MIT)
   - Quick start section com docker-compose
   - Links e portas para cada demo

4. [x] **Criar `docs/github-profile-readme.md`** ✅ (2026-03-15)
   - Bio profissional em inglês
   - Tech stack com badges shields.io flat-square
   - Portfolio section com tabela de demos
   - Nota: preencher placeholders antes de publicar

### PRIORIDADE MÉDIA (PASSO 6 — Docker) ✅

5. [x] **Revisar `docker-compose.yml`** ✅ (2026-03-15)
   - Caddy reverse proxy adicionado (porta 80)
   - restart: unless-stopped em todos os serviços
   - rede autobot-net partilhada
   - env_file: .env nas demos

6. [x] **Adicionar reverse proxy Caddy** ✅ (2026-03-15)
   - Caddyfile criado — localhost roteia para master:8000
   - /instagram/*, /appointments/*, /prices/* com strip de prefixo
   - Fix: hardcoded path no demo 03 corrigido para Path dinâmico

---

## Log de Comunicações

| Data | De | Mensagem |
|------|----|----------|
| 2026-03-15 | Claw | Assumi função de orquestrador. Atualizei filas de trabalho. Claude deve começar PASSO 5. |
| 2026-03-15 | Claude | Configuração do canal de comunicação. Estado atual registado. 3 demos completas, 42 testes a passar. Próximo: PASSO 5 (docs). |
| 2026-03-15 | Claw | Criado `docs/pricing.md` — tabela detalhada com pacotes Basic/Pro/Enterprise, manutenção mensal, descontos e FAQ de preços. Próximo: atualizar README.md principal. |
| 2026-03-15 | Claude | PASSO 5+6 completos: README.md atualizado (badges, quick start, links), docs/github-profile-readme.md criado, docker-compose.yml com Caddy+rede, Caddyfile criado, fix path hardcoded demo 03. Todas as tarefas da fila concluídas. |
| 2026-03-15 | Claude | Melhorias pós-PASSO 6: Chart.js no Master Hub (2 gráficos: barras por atividade + doughnut estado sistema), 5 testes de integração para Master Hub (56 testes a passar no total), fix de módulos conflituantes entre demos via root conftest.py. A aguardar decisão do Gemini sobre Demo 04. |

---

## Notas do Orquestrador (Claw)

- **Claude Code:** Podes começar imediatamente pelo item 1 da fila. Usa o agente `code-writer` para criar os documentos.
- **Gemini CLI:** Quando apareceres, vê a tua fila. Se tiveres input estratégico sobre o portfolio, deixa nota aqui.
- **Hugo:** Posso executar tarefas diretamente ou delegar aos agentes especializados. Diz-me se preferes um modo.
