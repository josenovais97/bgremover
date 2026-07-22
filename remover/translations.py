"""
Lightweight in-code translation catalogue (European Portuguese, pt-PT).

Django's gettext workflow needs the ``gettext`` binaries (msgfmt/xgettext) to
compile ``.mo`` files, which aren't guaranteed on the build host. Instead we keep
translations here as plain Python dicts and resolve them via the ``{% t %}``
template tag (see ``remover/templatetags/i18n_extras.py``) and the helpers below.
Any string without a Portuguese entry falls back to English, so partial coverage
degrades gracefully.

Language is activated by Django's LocaleMiddleware from the ``/pt/`` URL prefix
(config/urls.py), so ``get_language()`` returns ``"pt"`` on Portuguese pages.
"""
from django.utils.translation import get_language


def _is_pt(lang=None):
    lang = lang or get_language() or "en"
    return lang.startswith("pt")


# --- UI strings (keyed by their English source text) -------------------------
UI = {
    # Header / tool nav
    "Remove BG": "Remover Fundo",
    "Convert": "Converter",
    "Compress": "Comprimir",
    "Crop": "Recortar",
    "Stickers": "Autocolantes",
    "Meme": "Meme",
    "Passport": "Passaporte",
    "eCommerce": "eCommerce",
    "Blur": "Desfocar",
    "Portrait": "Retrato",
    "Resize": "Redimensionar",
    "Text Behind": "Texto Atrás",
    "Redact": "Ocultar",
    "QR Code": "Código QR",
    # "Instagram" and "EXIF" are left alone — both are proper nouns in Portuguese.
    "Favicon": "Favicon",
    "Image to PDF": "Imagem para PDF",
    "Combine photos or scans into one PDF": "Junte fotos ou digitalizações num só PDF",
    "More": "Mais",
    "nothing uploaded": "nada carregado",
    "or try it with a sample photo": "ou experimente com uma foto de exemplo",
    "No photo? Try a sample": "Sem foto? Experimente um exemplo",
    "All tools": "Todas as ferramentas",
    "Remove & Edit": "Remover e Editar",
    "Convert & Optimize": "Converter e Otimizar",
    "Create & Share": "Criar e Partilhar",
    "Photos": "Fotos",
    "Skip to content": "Saltar para o conteúdo",
    # Related-tools cross-link block (foot of every tool page)
    "More free, private tools": "Mais ferramentas grátis e privadas",
    "Same story everywhere — runs in your browser, nothing uploaded.":
        "A mesma história em todo o lado — corre no seu navegador, sem nada carregado.",
    "Export here and keep editing there — your image carries over, with no re-upload.":
        "Exporte aqui e continue a editar ali — a sua imagem acompanha-o, sem novo carregamento.",
    "Finish in one, carry straight on to the next — no re-uploading.":
        "Termine numa e siga logo para a seguinte — sem voltar a carregar.",
    # Homepage tool grid — heading, intro, and one blurb per TOOL_NAV entry
    "One toolkit for every image job": "Um conjunto de ferramentas para cada tarefa",
    "Every tool runs the same way the background remover does — on your device, free, with nothing uploaded.":
        "Todas as ferramentas funcionam como o removedor de fundo — no seu dispositivo, grátis, sem nada carregado.",
    "Cut out any subject into a transparent PNG": "Recorte qualquer objeto para um PNG transparente",
    "Swap between PNG, JPG, WEBP and AVIF": "Alterne entre PNG, JPG, WEBP e AVIF",
    "Shrink file size without visible quality loss": "Reduza o tamanho sem perda visível de qualidade",
    "Scale to exact pixel dimensions": "Redimensione para medidas exatas em píxeis",
    "Crop and fit for feed, story or reel": "Recorte e ajuste para feed, story ou reel",
    "Trim to a shape or a fixed ratio": "Corte para uma forma ou proporção fixa",
    "Add a die-cut outline for chat stickers": "Adicione contorno para autocolantes de chat",
    "Tuck text behind your subject": "Coloque texto atrás do seu objeto",
    "Stamp text or a logo across an image": "Aplique texto ou um logótipo sobre a imagem",
    "Turn a set of frames into an animation": "Transforme um conjunto de imagens numa animação",
    "Classic top and bottom caption text": "Legendas clássicas em cima e em baixo",
    "Official sizes for any country": "Medidas oficiais para qualquer país",
    "Clean white product shots that pass review": "Fotos de produto em fundo branco aprovadas",
    "Portrait-mode depth on any photo": "Efeito retrato em qualquer fotografia",
    "Blur out faces, plates and private details": "Desfoque rostos, matrículas e dados privados",
    "Every icon size a site or app needs": "Todos os tamanhos de ícone para site ou app",
    "Generate a scannable code from a link": "Gere um código legível a partir de um link",
    "Strip GPS and camera data from photos": "Remova dados de GPS e da câmara das fotos",
    # Footer
    "Background Remover": "Removedor de Fundo",
    "Image Converter": "Conversor de Imagens",
    "Image Compressor": "Compressor de Imagens",
    "Meme Maker": "Criador de Memes",
    "Instagram Editor": "Editor de Instagram",
    "Crop Image": "Recortar Imagem",
    "Sticker Maker": "Criador de Autocolantes",
    "Text Behind Image": "Texto Atrás da Imagem",
    "Watermark": "Marca de Água",
    "GIF Maker": "Criador de GIF",
    "Passport Photo": "Foto de Passaporte",
    "Product Photos": "Fotos de Produtos",
    "Background Blur": "Desfoque de Fundo",
    "Blur & Redact": "Desfocar e Ocultar",
    "Favicon Generator": "Gerador de Favicon",
    "QR Code Generator": "Gerador de Código QR",
    "EXIF Remover": "Removedor de EXIF",
    "Coming from another tool?": "Vem de outra ferramenta?",
    "See how we compare to remove.bg": "Veja como nos comparamos ao remove.bg",
    "images processed": "imagens processadas",
    "Tools": "Ferramentas",
    "Use cases": "Casos de uso",
    "Company": "Empresa",
    "About": "Sobre",
    "Privacy Policy": "Política de Privacidade",
    "Terms of Use": "Termos de Utilização",
    "Contact": "Contacto",
    "Your images never leave your device — processing happens 100% in your browser.":
        "As suas imagens nunca saem do seu dispositivo — o processamento acontece 100% no seu navegador.",
    "This tool is free — if it saved you time, you can support it:":
        "Esta ferramenta é gratuita — se lhe poupou tempo, pode apoiá-la:",
    "Buy me a coffee": "Pague-me um café",
    "Free, private, and unlimited.": "Gratuito, privado e ilimitado.",
    "Language": "Idioma",
    # Home page
    "Private & free — runs in your browser": "Privado e gratuito — corre no seu navegador",
    "Remove Image Backgrounds": "Remova Fundos de Imagens",
    "Automatically & Free": "Automaticamente e Grátis",
    "Drop an image and get a clean, transparent PNG in seconds. No sign-up, no watermarks, no quality loss — the AI runs entirely on your device.":
        "Largue uma imagem e obtenha um PNG transparente e nítido em segundos. Sem registo, sem marcas de água, sem perda de qualidade — a IA corre inteiramente no seu dispositivo.",
    "Drag & drop your images": "Arraste e largue as suas imagens",
    "or click to browse — you can select multiple files": "ou clique para procurar — pode selecionar vários ficheiros",
    "Select images": "Selecionar imagens",
    "Supports JPG, PNG & WEBP · Full resolution preserved": "Suporta JPG, PNG e WEBP · Resolução total preservada",
    "Your images never leave your device": "As suas imagens nunca saem do seu dispositivo",
    "How it works": "Como funciona",
    "Frequently asked questions": "Perguntas frequentes",
    # Shared landing-page strings
    "Why use it": "Porquê usar",
    "Ready to try it?": "Pronto para experimentar?",
    "It's free, unlimited, and completely private.": "É gratuito, ilimitado e totalmente privado.",
    "Remove a background now": "Remover um fundo agora",
    "Open the free tool": "Abrir a ferramenta gratuita",
    "Three steps, right in your browser. No account, no uploads.":
        "Três passos, no seu navegador. Sem conta, sem carregamentos.",
    "1. Add your image": "1. Adicione a sua imagem",
    "Drag & drop, browse, or paste — batch upload works too.":
        "Arraste e largue, procure ou cole — também funciona em lote.",
    "2. AI removes the background": "2. A IA remove o fundo",
    "Runs on your device in seconds — nothing is uploaded.":
        "Corre no seu dispositivo em segundos — nada é carregado.",
    "3. Download": "3. Descarregue",
    "Transparent PNG, or pick a background color. Full quality.":
        "PNG transparente, ou escolha uma cor de fundo. Qualidade total.",
    # --- Home page: how-it-works steps ---
    "Add": "Adicione",
    "an image — drag, browse or paste": "uma imagem — arraste, procure ou cole",
    "AI removes": "A IA remove",
    "the background on your device": "o fundo no seu dispositivo",
    "a transparent PNG, full quality": "um PNG transparente, com qualidade total",
    # --- Remover workspace ---
    "Your results": "Os seus resultados",
    "processed": "processadas",
    "avg": "média",
    "saved": "guardou",
    "images total": "imagens no total",
    "Download all (ZIP)": "Descarregar tudo (ZIP)",
    "Add more": "Adicionar mais",
    "Clear": "Limpar",
    "Recent this session": "Recentes nesta sessão",
    "Clear history": "Limpar histórico",
    # --- Result card ---
    "Before": "Antes",
    "After": "Depois",
    "Original": "Original",
    "Result": "Resultado",
    "Removing background…": "A remover o fundo…",
    "Something went wrong.": "Algo correu mal.",
    "Try again": "Tentar novamente",
    "Background": "Fundo",
    "Size & format": "Tamanho e formato",
    "Effects": "Efeitos",
    "Fill style": "Estilo de preenchimento",
    "Gradient": "Gradiente",
    "Blur photo": "Desfocar foto",
    "Image": "Imagem",
    "Use your own photo": "Use a sua própria foto",
    "Photo backgrounds": "Fundos fotográficos",
    "Format": "Formato",
    "Export size": "Tamanho de exportação",
    "Profile": "Perfil",
    "Story": "Story",
    "Sticker effects": "Efeitos de autocolante",
    "Outline": "Contorno",
    "Drop shadow": "Sombra",
    "Padding": "Margem",
    "Trim transparent edges": "Cortar margens transparentes",
    "Crop the export down to the subject, removing empty transparent margins":
        "Corta a exportação até ao motivo, removendo margens transparentes vazias",
    "Apply these options to all images": "Aplicar estas opções a todas as imagens",
    "Refine": "Refinar",
    "Style & export": "Estilo e exportação",
    "Copy result": "Copiar resultado",
    "Side-by-side": "Lado a lado",
    "Continue in": "Continuar em",
    "Sticker": "Autocolante",
    "Remove": "Remover",
    "Download": "Descarregar",
    # --- Refine editor ---
    "Refine edges": "Refinar contornos",
    "Cancel": "Cancelar",
    "Apply": "Aplicar",
    "Tool": "Ferramenta",
    "Restore": "Restaurar",
    "Erase": "Apagar",
    "Move": "Mover",
    "Brush size": "Tamanho do pincel",
    "Smooth edges": "Suavizar contornos",
    "Zoom": "Zoom",
    "Undo": "Anular",
    "Reset": "Repor",
    "paints back the original;": "repõe o original;",
    "wipes leftover background.": "apaga o fundo que sobrou.",
    "Scroll to zoom, or use the": "Faça scroll para ampliar, ou use a ferramenta",
    "tool / hold": "/ mantenha",
    "to pan.": "para deslocar.",
    "Shortcuts:": "Atalhos:",
    "size.": "tamanho.",
    # --- Crop dialog ---
    "Crop image": "Recortar imagem",
    "Remove crop": "Remover recorte",
    "Source": "Origem",
    "Cut-out": "Recorte",
    "keeps the background.": "mantém o fundo.",
    "uses the removed-background result.": "usa o resultado com o fundo removido.",
    "Shape": "Forma",
    "Circle": "Círculo",
    "Square": "Quadrado",
    "Round": "Arredondado",
    "Custom ratio": "Proporção personalizada",
    "Orientation": "Orientação",
    "Rotate": "Rodar",
    "Flip": "Espelhar",
    "Pick a shape or a": "Escolha uma forma ou uma",
    "custom ratio": "proporção personalizada",
    "then": "depois",
    "drag": "arraste",
    "to reposition and": "para reposicionar e",
    "scroll": "faça scroll",
    "to zoom. Rotate and flip from the buttons above.":
        "para ampliar. Rode e espelhe com os botões acima.",
    # --- Shortcuts modal ---
    "Keyboard shortcuts": "Atalhos de teclado",
    "Paste image from clipboard": "Colar imagem da área de transferência",
    "Open file picker": "Abrir seletor de ficheiros",
    "Download all as ZIP": "Descarregar tudo em ZIP",
    "Toggle dark mode": "Alternar modo escuro",
    "Close dialogs": "Fechar caixas de diálogo",
    "Remove a background": "Remover um fundo",
    # --- Quick background presets (remover) ---
    "Quick presets": "Predefinições rápidas",
    "Transparent": "Transparente",
    "White": "Branco",
    "Studio": "Estúdio",
    # --- Batch bar (resize / watermark / EXIF) ---
    "images queued": "imagens em fila",
    "Download all as ZIP (%d)": "Descarregar tudo em ZIP (%d)",
}


def t(text, lang=None):
    """Translate a UI string, falling back to the English source."""
    if _is_pt(lang):
        return UI.get(text, text)
    return text


# --- Runtime (JavaScript) strings --------------------------------------------
# Messages the tools raise while you use them. These live apart from UI because
# they are shipped to the browser as JSON (see js_catalogue below) rather than
# rendered by {% t %} — sending the whole UI catalogue would mean paying for the
# marketing copy on every tool page.
#
# `{name}`-style placeholders are filled in by CBG.t(key, vars). Keep them in
# both languages; a missing placeholder silently drops the value.
#
# Singular/plural pairs are two separate keys picked by CBG.plural(n, …),
# because Portuguese and English do not always agree on which counts are plural.
JS_UI = {
    # --- Input / file handling ---
    "Please choose an image": "Escolha uma imagem",
    "Please choose image files": "Escolha ficheiros de imagem",
    "Couldn't open that image": "Não foi possível abrir essa imagem",
    "Could not read that image": "Não foi possível ler essa imagem",
    "Could not load that image": "Não foi possível carregar essa imagem",
    "Could not read {name}": "Não foi possível ler {name}",
    "{name}: too large (max {max})": "{name}: demasiado grande (máx. {max})",
    "{name}: unsupported format (use JPG, PNG or WEBP)":
        "{name}: formato não suportado (use JPG, PNG ou WEBP)",
    "Couldn't load the sample": "Não foi possível carregar o exemplo",
    "Couldn't load that logo": "Não foi possível carregar esse logótipo",
    "Cleared all images": "Todas as imagens foram removidas",
    "History cleared": "Histórico limpo",
    "Add at least 2 photos": "Adicione pelo menos 2 fotografias",
    "Add more images to apply options to all":
        "Adicione mais imagens para aplicar as opções a todas",
    # --- Export ---
    "Export failed": "A exportação falhou",
    "Building ZIP…": "A criar o ZIP…",
    "Could not build the ZIP": "Não foi possível criar o ZIP",
    "Could not build the GIF": "Não foi possível criar o GIF",
    "Could not build the PDF": "Não foi possível criar o PDF",
    "Building your icon pack…": "A criar o seu pacote de ícones…",
    "Could not build the icon pack": "Não foi possível criar o pacote de ícones",
    "Icon pack downloaded": "Pacote de ícones descarregado",
    "Could not prepare the download": "Não foi possível preparar a transferência",
    "WebP not supported here — downloading PNG instead":
        "WebP não é suportado aqui — a descarregar PNG",
    "Building carousel ZIP…": "A criar o ZIP do carrossel…",
    "Carousel export failed": "A exportação do carrossel falhou",
    "Saved a {n}-tile carousel — post the tiles in order":
        "Carrossel de {n} imagens guardado — publique-as por ordem",
    "Saved crop {w}×{h}": "Recorte {w}×{h} guardado",
    "Saved {w}×{h} for Instagram": "Guardado {w}×{h} para Instagram",
    "Photo is larger than a 6×4 print": "A fotografia é maior do que uma impressão 6×4",
    # --- Clipboard ---
    "Copied to clipboard": "Copiado para a área de transferência",
    "Meme copied to clipboard": "Meme copiado para a área de transferência",
    "HTML copied to clipboard": "HTML copiado para a área de transferência",
    "Copy failed": "Não foi possível copiar",
    "Clipboard not supported in this browser":
        "A área de transferência não é suportada neste navegador",
    "Copy not supported here — use Download":
        "Cópia não suportada aqui — use Descarregar",
    # --- Background removal ---
    "Background removal failed": "A remoção do fundo falhou",
    "Background removed": "Fundo removido",
    "Background removed — add your outline & text":
        "Fundo removido — adicione o contorno e o texto",
    "Background removed — position the head inside the guides":
        "Fundo removido — posicione a cabeça dentro das guias",
    "Could not cut out the subject": "Não foi possível recortar o assunto",
    "Could not find the subject": "Não foi possível encontrar o assunto",
    "Portrait blur applied — adjust the strength":
        "Desfoque de retrato aplicado — ajuste a intensidade",
    # --- Editing ---
    "Crop applied": "Recorte aplicado",
    "Edits applied": "Alterações aplicadas",
    "Could not open the image to crop": "Não foi possível abrir a imagem para recortar",
    "Could not render the crop preview":
        "Não foi possível gerar a pré-visualização do recorte",
    "Type your text and drag it behind the subject":
        "Escreva o seu texto e arraste-o para trás do assunto",
    'Saved look "{name}"': 'Estilo "{name}" guardado',
    # --- Redaction ---
    "Face detection is not available in this browser":
        "A deteção de rostos não está disponível neste navegador",
    "No faces found — draw over them by hand":
        "Nenhum rosto encontrado — desenhe sobre eles manualmente",
    "{n} face hidden — adjust or add more by hand":
        "{n} rosto ocultado — ajuste ou adicione mais manualmente",
    "{n} faces hidden — adjust or add more by hand":
        "{n} rostos ocultados — ajuste ou adicione mais manualmente",
    # --- Batch ---
    "Applied to {n} other image": "Aplicado a mais {n} imagem",
    "Applied to {n} other images": "Aplicado a mais {n} imagens",
    "Ready — {n} photo. Pick a marketplace and download.":
        "Pronto — {n} fotografia. Escolha um marketplace e descarregue.",
    "Ready — {n} photos. Pick a marketplace and download.":
        "Pronto — {n} fotografias. Escolha um marketplace e descarregue.",
    # --- Errors ---
    "Error: {message}": "Erro: {message}",
    "Failed: {detail}": "Falhou: {detail}",
    # --- Cross-tool chaining (kit.js) ---
    "Keep editing this image:": "Continue a editar esta imagem:",
    "— keep going:": "— continue:",
    "Carried over from {tool}": "Trazido de {tool}",
}


def js_catalogue(lang=None):
    """The runtime string catalogue for the browser, or {} on English pages.

    Empty for English on purpose: CBG.t() returns its key unchanged when a
    string is missing, and the keys ARE the English text, so an English page
    needs no payload at all.
    """
    return JS_UI if _is_pt(lang) else {}


# --- Landing-page (use-case) copy, fully translated --------------------------
# Keyed by slug; only the translated fields are stored and merged over the
# English source in localize_use_case().
USE_CASES_PT = {
    "product-photos": {
        "nav": "Fotos de produtos",
        "title": "Remover Fundo de Fotos de Produtos — Grátis e Instantâneo",
        "description": "Crie fotos de produtos limpas, em branco ou transparentes, para a sua loja online. Grátis, privado e ilimitado — a IA corre no seu navegador, por isso nada é carregado.",
        "h1": "Remova Fundos de Fotos de Produtos",
        "tagline": "Dê à sua loja um aspeto consistente e profissional com recortes limpos — grátis, ilimitado e processado inteiramente no seu dispositivo.",
        "intro": [
            "Marketplaces como Amazon, eBay, Etsy e Shopify convertem melhor quando cada produto surge sobre um fundo limpo e consistente. Esta ferramenta remove o fundo das suas fotos de produto em segundos, para exportar um PNG transparente ou colocar um fundo branco puro.",
            "Como a IA corre localmente no seu navegador, pode processar um catálogo inteiro sem carregar uma única imagem, sem limites de API e sem pagar por foto.",
        ],
        "benefits": [
            {"icon": "fa-store", "title": "Pronto para marketplaces", "text": "Exporte sobre branco puro para anúncios ao estilo Amazon, ou PNGs transparentes para compor em qualquer lado."},
            {"icon": "fa-layer-group", "title": "Processe o catálogo em lote", "text": "Coloque dezenas de fotos de produtos de uma vez e descarregue-as juntas num ZIP."},
            {"icon": "fa-crop-simple", "title": "Resolução total", "text": "Mantém a qualidade original — sem redução de tamanho e sem marca de água nas suas imagens."},
        ],
    },
    "profile-picture": {
        "nav": "Fotos de perfil",
        "title": "Removedor de Fundo para Foto de Perfil — Grátis e Privado",
        "description": "Remova o fundo da sua foto de perfil ou retrato para o LinkedIn, um CV ou redes sociais. 100% grátis e privado — as imagens nunca saem do seu navegador.",
        "h1": "Remova o Fundo da Sua Foto de Perfil",
        "tagline": "Retratos e avatares perfeitos para LinkedIn, CVs e perfis sociais — troque por qualquer cor, tudo no seu navegador.",
        "intro": [
            "Um retrato limpo faz o seu LinkedIn, CV ou perfil social parecer profissional. Carregue a sua foto e a IA isola-o do fundo, para o manter transparente ou colocar uma cor sólida de marca.",
            "Tudo acontece no seu dispositivo — a sua foto nunca é carregada, o que mantém uma imagem pessoal totalmente privada.",
        ],
        "benefits": [
            {"icon": "fa-user", "title": "Recortes favorecedores", "text": "Preparado para lidar com cabelo e contornos suaves, com um pincel de refinamento para os retoques finais."},
            {"icon": "fa-palette", "title": "Qualquer cor de fundo", "text": "Combine com uma paleta de marca ou um fundo de estúdio liso, e exporte em PNG, JPG ou WEBP."},
            {"icon": "fa-shield-halved", "title": "Privado por design", "text": "O seu rosto nunca sai do navegador — nada é enviado para um servidor."},
        ],
    },
    "logo": {
        "nav": "Logótipos",
        "title": "Remover Fundo de um Logótipo — Obtenha um PNG Transparente",
        "description": "Transforme um logótipo com fundo sólido num PNG transparente e limpo. Grátis, ilimitado e processado de forma privada no seu navegador — sem registo.",
        "h1": "Torne o Fundo do Seu Logótipo Transparente",
        "tagline": "Transforme um logótipo plano num PNG transparente que pode colocar sobre qualquer cor, slide ou site — grátis e instantâneo.",
        "intro": [
            "Tem um logótipo preso num quadrado branco ou colorido? Esta ferramenta remove esse fundo e dá-lhe um PNG transparente que assenta de forma limpa em qualquer site, documento ou apresentação.",
            "Corre tudo no seu navegador em resolução total, por isso os seus recursos de marca permanecem nítidos e nunca são carregados para lado nenhum.",
        ],
        "benefits": [
            {"icon": "fa-vector-square", "title": "Transparência limpa", "text": "Remove fundos sólidos para o seu logótipo assentar sobre qualquer cor sem halo."},
            {"icon": "fa-brush", "title": "Refine os contornos", "text": "Limpe pixéis restantes ou restaure detalhes finos com o pincel de contorno integrado."},
            {"icon": "fa-crop-simple", "title": "Exportação em qualidade total", "text": "Descarregue um PNG sem perdas e em resolução total — nunca com marca de água."},
        ],
    },
    "signature": {
        "nav": "Assinaturas",
        "title": "Remover Fundo de uma Assinatura — PNG Transparente",
        "description": "Transforme uma foto ou digitalização da sua assinatura manuscrita num PNG transparente e limpo para documentos e contratos. Grátis e privado — corre no seu navegador.",
        "h1": "Crie uma Assinatura Transparente",
        "tagline": "Transforme uma digitalização ou foto da sua assinatura manuscrita num PNG transparente e limpo para contratos e documentos.",
        "intro": [
            "Assine uma folha de papel em branco, fotografe ou digitalize, e largue-a aqui. A IA remove o fundo de papel e deixa apenas a tinta como um PNG transparente que pode colocar em qualquer PDF ou documento.",
            "Como todo o processo corre no seu navegador, a sua assinatura — uma informação sensível — nunca é carregada para um servidor.",
        ],
        "benefits": [
            {"icon": "fa-file-signature", "title": "Pronto para documentos", "text": "Obtenha tinta transparente que pode colocar diretamente em PDFs, contratos e cartas."},
            {"icon": "fa-shield-halved", "title": "Mantido privado", "text": "A sua assinatura nunca sai do seu dispositivo — nada é enviado para lado nenhum."},
            {"icon": "fa-wand-magic-sparkles", "title": "Isolamento limpo", "text": "Separa a tinta da textura do papel e das sombras, com um pincel para refinar o resultado."},
        ],
    },
    "car-photos": {
        "nav": "Fotos de carros",
        "title": "Remover Fundo de Fotos de Carros — Grátis e Instantâneo",
        "description": "Remova o fundo de fotos de carros para anúncios de stands e marketplaces. Coloque qualquer veículo sobre um fundo branco ou transparente — grátis, privado, no seu navegador.",
        "h1": "Remova Fundos de Fotos de Carros",
        "tagline": "Dê a cada veículo uma foto de anúncio limpa e consistente para o seu stand ou marketplace — grátis, ilimitado e processado no seu dispositivo.",
        "intro": [
            "Os anúncios de carros vendem mais depressa quando cada veículo surge sobre um fundo limpo e consistente em vez de um stand desarrumado. Esta ferramenta corta o fundo das suas fotos de carros em segundos.",
            "Como a IA corre localmente no seu navegador, pode processar todo o stock sem carregar uma única foto, sem limites de API e sem pagar por imagem.",
        ],
        "benefits": [
            {"icon": "fa-car", "title": "Limpo como um showroom", "text": "Troque um stand desarrumado por um fundo de estúdio impecável que mantém o foco no carro."},
            {"icon": "fa-layer-group", "title": "Lotes inteiros", "text": "Coloque dezenas de fotos de uma vez e descarregue-as juntas num ZIP."},
            {"icon": "fa-bolt", "title": "Instantâneo e grátis", "text": "Sem custo por foto e sem marca de água — resolução total sempre."},
        ],
    },
    "clothing": {
        "nav": "Roupa e moda",
        "title": "Remover Fundo de Fotos de Roupa — Grátis para Revendedores",
        "description": "Remova o fundo de fotos de roupa e moda para Vinted, Depop, Poshmark ou a sua loja. PNGs limpos em branco ou transparentes — grátis, privado, no seu navegador.",
        "h1": "Remova o Fundo de Fotos de Roupa",
        "tagline": "Transforme fotos de telemóvel de roupa em fotos de produto limpas e vendáveis para Vinted, Depop, Poshmark ou a sua loja — grátis e ilimitado.",
        "intro": [
            "A moda em segunda mão e de boutique vende mais depressa quando cada peça parece consistente e profissional. Carregue a foto de uma peça e a IA isola-a do seu tapete, cabide ou parede.",
            "Corre tudo no seu navegador em resolução total, por isso pode preparar um guarda-roupa inteiro de anúncios de forma privada — sem carregamentos, sem taxas por foto.",
        ],
        "benefits": [
            {"icon": "fa-shirt", "title": "Vendável em segundos", "text": "Recortes limpos de tops, vestidos e sapatos que ficam bem em qualquer grelha de loja."},
            {"icon": "fa-tags", "title": "Anúncios consistentes", "text": "Dê a cada peça o mesmo fundo limpo para uma montra profissional."},
            {"icon": "fa-shield-halved", "title": "Privado por design", "text": "As suas fotos nunca saem do seu dispositivo — nada é carregado para um servidor."},
        ],
    },
    "pet-photos": {
        "nav": "Fotos de animais",
        "title": "Remover Fundo de Fotos de Animais — Grátis e Privado",
        "description": "Recorte o seu cão, gato ou qualquer animal de uma foto grátis. Crie PNGs transparentes para autocolantes, impressões e memes — privado e no seu navegador, nada é carregado.",
        "h1": "Remova o Fundo de Fotos de Animais",
        "tagline": "Recorte o seu cão, gato ou amigo peludo para autocolantes, impressões, canecas e memes — grátis, ilimitado e tudo no seu navegador.",
        "intro": [
            "Quer o seu animal numa caneca, num autocolante ou numa impressão personalizada? Carregue uma foto e a IA separa o seu cão ou gato do fundo — lidando com pelo e bigodes — para obter um PNG transparente e limpo.",
            "Tudo acontece no seu dispositivo, por isso pode experimentar quantas fotos quiser — sem carregamentos, sem limites e sem marca de água.",
        ],
        "benefits": [
            {"icon": "fa-paw", "title": "Ótimo com pelo", "text": "Preparado para lidar com contornos suaves, pelo e bigodes para um recorte natural."},
            {"icon": "fa-wand-magic-sparkles", "title": "Refine à mão", "text": "Limpe fundo restante ou restaure detalhes finos com o pincel de contorno integrado."},
            {"icon": "fa-heart", "title": "Pronto para impressão e autocolantes", "text": "PNGs transparentes em resolução total para canecas, autocolantes, impressões e memes."},
        ],
    },
    "youtube-thumbnail": {
        "nav": "Miniaturas de YouTube",
        "title": "Remover Fundo para Miniaturas de YouTube — Grátis",
        "description": "Recorte-se de uma foto para uma miniatura de YouTube apelativa. PNGs transparentes grátis para colocar sobre qualquer fundo — privado, no seu navegador, nada é carregado.",
        "h1": "Remova Fundos para Miniaturas de YouTube",
        "tagline": "Recorte-se a si ou ao seu assunto de forma limpa e coloque sobre um fundo forte para miniaturas que geram cliques — grátis e ilimitado.",
        "intro": [
            "As melhores miniaturas colocam um recorte nítido de uma pessoa ou produto sobre um fundo impactante. Carregue a sua foto e a IA remove o fundo em segundos, dando-lhe um PNG transparente para compor no seu editor de miniaturas.",
            "Corre inteiramente no seu navegador em resolução total, para os criadores produzirem miniaturas rapidamente — sem carregamentos, sem subscrições e sem marca de água.",
        ],
        "benefits": [
            {"icon": "fa-clapperboard", "title": "Feito para criadores", "text": "Recortes limpos de si ou do seu assunto para se destacarem sobre qualquer fundo de miniatura."},
            {"icon": "fa-bolt", "title": "Rápido", "text": "Remove o fundo em segundos para publicar a miniatura e carregar em publicar."},
            {"icon": "fa-crop-simple", "title": "Qualidade total", "text": "PNGs transparentes em resolução total, sem marca de água, prontos para qualquer editor."},
        ],
    },
    "ebay": {
        "nav": "Anúncios eBay",
        "title": "Remover Fundo de Fotos eBay — Grátis e Instantâneo",
        "description": "Dê aos seus anúncios eBay fundos brancos ou transparentes gratuitamente. Faça os artigos parecerem profissionais e vender mais depressa — privado, ilimitado e no seu navegador.",
        "h1": "Remova Fundos de Fotos eBay",
        "tagline": "Transforme fotos de telemóvel desarrumadas em fotos de anúncio eBay limpas e profissionais — grátis, ilimitado e processado no seu dispositivo.",
        "intro": [
            "Anúncios com fotos limpas e consistentes ganham mais cliques e vendem mais depressa. Largue uma foto do seu artigo e a IA remove o fundo desarrumado, para colocar branco puro — o aspeto em que os compradores confiam.",
            "Como a IA corre localmente no seu navegador, pode preparar um inventário inteiro sem carregar uma única foto, sem limites de API e sem pagar por imagem.",
        ],
        "benefits": [
            {"icon": "fa-tag", "title": "Venda mais depressa", "text": "Fundos brancos limpos tornam os artigos profissionais e criam confiança no comprador."},
            {"icon": "fa-layer-group", "title": "Inventário em lote", "text": "Coloque dezenas de artigos de uma vez e descarregue-os juntos num ZIP."},
            {"icon": "fa-bolt", "title": "Grátis e ilimitado", "text": "Sem custo por foto e sem marca de água — resolução total sempre."},
        ],
    },
    "discord-pfp": {
        "nav": "Avatares Discord",
        "title": "Removedor de Fundo para Foto de Perfil de Discord — Grátis",
        "description": "Crie uma foto de perfil de Discord limpa removendo o fundo da sua foto ou avatar. PNGs transparentes grátis para colocar sobre qualquer cor — privado, no seu navegador, nada é carregado.",
        "h1": "Remova o Fundo da Sua Foto de Perfil de Discord",
        "tagline": "Recorte-se a si ou à sua personagem de forma limpa para um avatar de Discord nítido — grátis, ilimitado e tudo no seu navegador.",
        "intro": [
            "Uma foto de perfil limpa destaca a sua presença no Discord. Carregue uma foto, selfie ou arte e a IA isola o assunto, para o manter transparente ou colocar qualquer cor sólida ou gradiente antes de recortar em círculo.",
            "Tudo acontece no seu dispositivo, por isso pode experimentar quantos estilos quiser — sem carregamentos, sem limites e sem marca de água.",
        ],
        "benefits": [
            {"icon": "fa-circle-user", "title": "Avatares nítidos", "text": "Recortes limpos que se leem bem mesmo no tamanho pequeno de avatar do Discord."},
            {"icon": "fa-palette", "title": "Qualquer cor ou gradiente", "text": "Coloque o seu recorte sobre uma cor sólida, gradiente ou fundo desfocado, e recorte em círculo."},
            {"icon": "fa-shield-halved", "title": "Privado por design", "text": "A sua foto nunca sai do navegador — nada é carregado para um servidor."},
        ],
    },
    "twitch": {
        "nav": "Twitch e streaming",
        "title": "Remover Fundo para Twitch e Streaming — Sem Chroma Key",
        "description": "Recorte-se de uma foto para painéis, overlays e emotes de Twitch — sem chroma key. PNGs transparentes grátis, privados e no seu navegador, nada é carregado.",
        "h1": "Remova Fundos para Twitch e Streaming",
        "tagline": "Crie recortes limpos para painéis, overlays e emotes sem chroma key — grátis, ilimitado e processado no seu dispositivo.",
        "intro": [
            "Uma boa imagem de canal começa com recursos limpos. Carregue uma foto e a IA remove o fundo para obter um PNG transparente para os seus painéis de Twitch, overlays, gráficos de horário ou emotes — sem chroma key nem máscaras manuais.",
            "Corre tudo no seu navegador em resolução total, por isso pode criar um conjunto inteiro de gráficos de marca de forma privada — sem carregamentos, sem taxas por imagem, sem marca de água.",
        ],
        "benefits": [
            {"icon": "fa-tower-broadcast", "title": "Sem chroma key", "text": "Obtenha um recorte limpo de qualquer foto — sem chroma key nem estúdio."},
            {"icon": "fa-icons", "title": "Painéis e emotes", "text": "PNGs transparentes prontos para overlays, painéis, horários e arte de emotes."},
            {"icon": "fa-crop-simple", "title": "Qualidade total", "text": "Exportações em resolução total, sem marca de água, para qualquer ferramenta de layout de streaming."},
        ],
    },
}


def localize_use_case(case, lang=None):
    """Return the use-case dict with Portuguese fields merged in (or unchanged)."""
    if not _is_pt(lang):
        return case
    tr = USE_CASES_PT.get(case["slug"])
    return {**case, **tr} if tr else case
