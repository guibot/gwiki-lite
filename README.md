# gwiki-lite

Versão sem servidor do [gwiki](https://github.com/guibot/gwiki): um único
ficheiro HTML, autossuficiente, que funciona como wiki editável ou tutorial
passo a passo — sem instalar nada, sem build, sem backend.

## Porquê

O gwiki original precisa de servidor. Este é para quando isso é a mais:
notas de curso, um tutorial para partilhar, documentação de um projeto
pequeno — abre-se o ficheiro no browser (`file://`) e já está.

## Como usar

1. Copia `gwiki_template.html` para o teu projeto (podes renomear para
   `index.html`).
2. Abre-o num browser. Na primeira vez, escolhe o modo:
   - **Wiki Básica** — blocos e sessões de texto, com notas por atividade.
   - **Tutorial** — passos numerados, cada um com imagem + legenda.
3. Clica no 🔒 para desbloquear e editar diretamente na página.
4. Clica outra vez (🔓 → 🔒) para gravar — o browser descarrega um
   `index.html` atualizado. Substitui o ficheiro antigo por esse.

Não há servidor nem base de dados: todo o estado (conteúdo, modo escolhido,
tema de cor, notas, larguras das sidebars) fica guardado dentro do próprio
HTML. Gravar = descarregar o ficheiro e substituir o anterior.

## Funcionalidades

- Escolha de modo na primeira abertura (fica fixa depois de gravares)
- Índice lateral gerado automaticamente a partir do conteúdo
- Edição direta na página (lock/unlock)
- Modo Básica: notas por atividade, num painel lateral
- Modo Tutorial: passos com imagem + legenda, numerados automaticamente
- 4 temas de cor (verde/azul/laranja/cinza)
- Sidebars redimensionáveis e colapsáveis
- Zero dependências externas, zero build, zero servidor

## Ficheiros

- `gwiki_template.html` — o template principal (usar este)
- `template.md` — documentação da estrutura interna do HTML, para quem for
  editar o conteúdo diretamente no código (ou pedir ao Claude Code para o
  fazer)

## Relação com o gwiki

Este projeto é uma derivação do [gwiki](https://github.com/guibot/gwiki),
pensada para casos em que não vale a pena montar servidor. Não é um
substituto — é uma versão leve para uso pontual ou offline.
