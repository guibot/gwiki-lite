# gwiki_template.html — mini-wiki/tutorial offline, sem servidor

## O que é isto

`gwiki_template.html` é uma página HTML **única e autossuficiente** (sem
servidor, sem build, sem dependências externas) que funciona como pequeno
wiki ou tutorial passo a passo, estruturado em **Blocos** e **Sessões**, com:

- Escolha de **modo** na primeira abertura: **Básica** (texto + notas por
  atividade) ou **Tutorial** (passos com imagem + legenda)
- Sidebar esquerda com índice automático (gerado a partir do conteúdo)
- Modo de edição com lock/unlock (🔒/🔓)
- Painel de notas à direita, por atividade (modo Básica)
- Passos com imagem+legenda, numerados automaticamente (modo Tutorial)
- 4 temas de cor (verde/azul/laranja/cinza), escolhidos junto ao 🔒
- Sidebars redimensionáveis e a esquerda colapsável
- Tema escuro, fonte mono para UI e sans para texto

Abre-se a fazer duplo-clique no ficheiro (`file://`), não precisa de internet
nem de servidor. Basta um browser moderno (Chrome, Edge, Firefox, Safari).

## Escolha de modo (primeira abertura)

Ao abrir o ficheiro pela primeira vez (sem `mode-basic`/`mode-tutorial` na
classe do `<body>`), aparece uma página de escolha em vez do layout normal —
"Wiki Básica" ou "Tutorial". Ao clicar:

- Adiciona-se a classe `mode-basic` ou `mode-tutorial` ao `<body>`.
- Removem-se do DOM os elementos de exemplo do outro modo
  (`[data-mode="basic"]` / `[data-mode="tutorial"]`).
- A escolha só fica **permanente** quando o ficheiro for gravado (🔒 → 🔓 → 🔒,
  ou "💾 Guardar no ficheiro"). Sem gravar, se a página for recarregada, a
  pergunta volta a aparecer.

Não há popup nem `confirm()` para isto — é uma página inteira, sem servidor
nem `localStorage`, seguindo a mesma filosofia do resto do ficheiro (ver
secção de persistência abaixo).

## Estrutura de dados (onde fica o conteúdo)

Todo o conteúdo visível vive dentro de:

```html
<main class="main" id="main">
  ... aqui dentro ...
</main>
```

Cada **Bloco** é um `<section class="doc-section">` com um `id` único.
Cada **Sessão** é um `<div class="sub-section">` dentro de um bloco, também
com `id` único. A sidebar é **construída automaticamente por JavaScript** a
partir destes elementos — nunca se edita a `<ul id="navList">` à mão.

### Esqueleto mínimo — modo Básica (Bloco com uma Sessão)

```html
<section id="bloco-x" class="doc-section">
  <div class="section-controls">
    <button class="ctrl-btn add-session-btn" type="button">+ Sessão</button>
    <button class="ctrl-btn danger del-block-btn" type="button">🗑 Bloco</button>
  </div>
  <h1 contenteditable="false">Título do Bloco</h1>
  <p contenteditable="false">Parágrafo introdutório opcional do bloco.</p>

  <div id="sessao-x-1" class="sub-section">
    <div class="section-controls">
      <button class="ctrl-btn danger del-session-btn" type="button">🗑 Sessão</button>
    </div>
    <h2 contenteditable="false">Sessão 1 · duração - Título da sessão</h2>

    <p contenteditable="false"><strong>15 min · Nome da atividade</strong> Texto descritivo da atividade.</p>

    <ul>
      <li contenteditable="false">Ponto de apoio opcional.</li>
      <li contenteditable="false">Outro ponto.</li>
    </ul>

    <p contenteditable="false"><strong>Materiais e recursos sugeridos</strong> Lista de materiais.</p>
  </div>
</section>
```

### Esqueleto mínimo — modo Tutorial (Sessão com um Passo)

```html
<div id="sessao-y-1" class="sub-section">
  <div class="section-controls">
    <button class="ctrl-btn danger del-session-btn" type="button">🗑 Sessão</button>
  </div>
  <h2 contenteditable="false">Sessão 1 · Título</h2>

  <div class="step-block">
    <div class="section-controls step-controls">
      <button class="ctrl-btn add-step-btn" type="button">+ Passo</button>
      <button class="ctrl-btn danger del-step-btn" type="button">🗑 Passo</button>
    </div>
    <p contenteditable="false"><strong>Passo 01</strong> <em>legenda…</em></p>
    <img src="screenshots/nome-do-ficheiro.png" alt="Passo 01"
         style="max-width:100%;border-radius:8px;border:1px solid var(--border);margin:4px 0 24px;display:block">
  </div>

  <div class="step-end-wrap">
    <button class="ctrl-btn add-step-end-btn" type="button">+ Passo (no fim da sessão)</button>
  </div>
</div>
```

A imagem tem de estar previamente copiada para uma pasta `screenshots/` ao
lado do HTML — o botão "+ Passo" só lê o **nome** do ficheiro escolhido, não
copia o ficheiro em si. A numeração (`Passo 01`, `Passo 02`…) e o `alt` da
imagem são recalculados automaticamente a cada adição/remoção
(`renumberSteps()`).

### Regras importantes ao adicionar/editar conteúdo à mão (via código)

1. **IDs únicos em todo o documento.** Nunca repetir um `id` (nem entre
   blocos, nem entre sessões). Usar kebab-case descritivo (`bloco-cafe`,
   `sessao-metodos-extracao`) ou um sufixo aleatório se gerado
   automaticamente.
2. **`contenteditable="false"` em todos os `<h1>`, `<h2>` e `<p>` dentro de
   `#main`.** O JavaScript liga/desliga isto para `true` quando o utilizador
   desbloqueia a página (🔓). Não é obrigatório à mão, mas é a convenção
   usada em todo o ficheiro.
3. **Atividades (modo Básica) = parágrafos que começam com `<strong>`.**
   Qualquer `<p>` cujo primeiro filho seja `<strong>texto</strong>` é
   automaticamente:
   - Estilizado como um "badge" em destaque (a etiqueta com o tempo/título).
   - Clicável em modo de leitura, abrindo o painel de notas à direita.

   Padrão a seguir: `<p><strong>15 min · Nome da atividade</strong> resto do texto…</p>`
4. **`section-controls` é obrigatório** em cada `.doc-section` (com botões
   `+ Sessão` e `🗑 Bloco`), em cada `.sub-section` (com botão `🗑 Sessão`) e
   em cada `.step-block` (com `step-controls`: `+ Passo` / `🗑 Passo`). Sem
   isto, os botões de edição não aparecem — mas o JavaScript também os
   injeta automaticamente ao carregar (`decorateAll()`), por isso não é
   crítico esquecê-los para blocos/sessões (passos têm de vir já com os
   botões, não são reconstruídos automaticamente).
5. **`data-mode="basic"` / `data-mode="tutorial"`** só se usa nos blocos de
   exemplo mostrados **antes** da escolha de modo. Depois de o modo estar
   escolhido (classe no `<body>`), conteúdo novo não precisa deste atributo.
6. **Não editar `<ul id="navList">` nem o `<script>`.** A sidebar e toda a
   lógica (lock, notas, passos, tema, resize, guardar) são geradas/
   controladas por JavaScript já incluído no ficheiro. Editar isso
   manualmente pode partir a página.
7. **Título e subtítulo do documento** (topo da sidebar) estão em:
   ```html
   <h1 id="docTitle" contenteditable="false">Offline Wiki</h1>
   <div class="meta" id="docSubtitle" contenteditable="false">Edita e adiciona conteúdo</div>
   ```
   Podem ser editados à mão diretamente no HTML, ou pela própria UI depois
   de desbloquear.

## Como funciona a edição (para quem vai usar a página, não só editar o código)

- **Escolha de modo (primeira vez):** página de boas-vindas com dois
  cartões — "Wiki Básica" e "Tutorial". Escolhida uma vez, fica fixa (ver
  secção acima).
- **🔒 / 🔓 (canto superior da sidebar):** desbloqueia a página para edição
  direta no browser (clicar em qualquer título/parágrafo e escrever). Ao
  clicar de novo para bloquear, a página **descarrega automaticamente um
  `index.html` atualizado** — é preciso substituir o ficheiro na pasta do
  projeto manualmente. Não há servidor, por isso não há outra forma de
  gravar.
- **Bolinhas de tema** (aparecem só desbloqueado, logo abaixo do 🔒):
  verde/azul/laranja/cinza — mudam a cor de destaque em todo o documento.
- **+ Novo Bloco** (só visível desbloqueado, fundo da sidebar): cria um
  bloco novo vazio.
- **+ Sessão / 🗑 Bloco / 🗑 Sessão**: aparecem por cima de cada
  bloco/sessão quando desbloqueado. No modo Tutorial, "+ Sessão" já cria a
  sessão com um passo incluído.
- **+ Passo / 🗑 Passo / + Passo (no fim da sessão)** (só no modo Tutorial,
  desbloqueado): pede um ficheiro de imagem (já deve estar em
  `screenshots/`) e insere um novo passo antes/depois.
- **Clicar numa atividade (parágrafo com badge) em modo bloqueado, modo
  Básica:** abre o painel de notas à direita. O botão **💾 Guardar no
  ficheiro** dentro desse painel descarrega o ficheiro com a nota incluída,
  sem precisar de mexer no lock.
- **Barra lateral esquerda:** `⟨` esconde-a, um botão `☰` fixo reaparece
  para a mostrar de novo. Arrastar a borda direita da sidebar (ou esquerda
  do painel de notas) para redimensionar.

## Persistência — não há localStorage

**Tudo** (conteúdo, modo escolhido, tema de cor, notas, largura das
sidebars, estado colapsado) vive dentro do próprio ficheiro HTML (atributos
`style`/`data-*`, classes, texto). Não existe nenhuma base de dados nem
`localStorage` — o único "guardar" real é descarregar o ficheiro atualizado
e substituir o original em disco. Se a página for recarregada sem gravar
antes, as alterações feitas nessa sessão do browser perdem-se — incluindo a
escolha de modo, se ainda não tiver sido gravada.

## Quando o Claude Code for pedido para adicionar conteúdo a este ficheiro

1. Ler o ficheiro `.html` de destino primeiro.
2. Confirmar o modo já escolhido (classe `mode-basic`/`mode-tutorial` no
   `<body>`) para saber que esqueleto usar (Básica vs. Tutorial).
3. Localizar `<main class="main" id="main">` e inserir novos blocos/sessões
   seguindo exatamente o esqueleto correspondente acima (ids únicos,
   `contenteditable="false"`, `section-controls`, parágrafos de atividade
   com `<strong>` no início, ou `step-block`/`step-end-wrap` no Tutorial).
4. Não tocar no `<style>` nem no `<script>`, exceto se for pedido
   explicitamente para mudar aparência/comportamento.
5. Não é preciso editar a sidebar (`<ul id="navList">`) — é reconstruída
   automaticamente no arranque a partir do conteúdo de `#main`.
6. Validar o HTML resultante (por exemplo, correndo `node --check` sobre o
   conteúdo do `<script>` extraído) antes de dar como terminado, para
   garantir que nenhuma edição partiu a sintaxe.
