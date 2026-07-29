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
    "Beautify Shot": "Embelezar Captura",
    "Frame a screenshot on a pretty backdrop": "Emoldure uma captura de ecrã num fundo bonito",
    "Screenshot Beautifier": "Embelezador de Capturas",
    # Command palette (Ctrl+K)
    "Search tools": "Pesquisar ferramentas",
    "Search tools…": "Pesquisar ferramentas…",
    "No tools found": "Nenhuma ferramenta encontrada",
    "Recent": "Recente",
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
    # New tools (1.10)
    "Remove Object": "Remover Objeto",
    "Brush over anything and erase it from the photo": "Pinte sobre qualquer coisa e apague-a da foto",
    "Filters": "Filtros",
    "One-tap looks plus fine adjustment sliders": "Estilos de um toque e ajustes finos",
    "Upscale": "Ampliar",
    "Enlarge 2× or 4× with clean, sharp edges": "Amplie 2× ou 4× com contornos nítidos",
    "HEIC to JPG": "HEIC para JPG",
    "Open iPhone HEIC photos anywhere as JPG": "Abra fotos HEIC do iPhone em qualquer lado como JPG",
    "PDF to Images": "PDF para Imagens",
    "Save every PDF page as a sharp image": "Guarde cada página do PDF como imagem nítida",
    "Image to Text": "Imagem para Texto",
    "Copy the text out of any photo or screenshot": "Copie o texto de qualquer foto ou captura",
    "SVG to PNG": "SVG para PNG",
    "Rasterise vector art at any size, pixel-sharp": "Converta vetores em qualquer tamanho, sem perda",
    # --- New tool pages: og:title (social share cards) ------------------------
    "Remove Objects from Photos — Free & Private":
        "Remover Objetos de Fotografias — Grátis e Privado",
    "Free Image Upscaler — Enlarge 2× / 4× Privately":
        "Ampliador de Imagens Grátis — Amplie 2× / 4× em Privado",
    "HEIC to JPG — Free Private Converter":
        "HEIC para JPG — Conversor Grátis e Privado",
    "PDF to Images — Free & Private Converter":
        "PDF para Imagens — Conversor Grátis e Privado",
    "Image to Text — Free Private OCR":
        "Imagem para Texto — OCR Grátis e Privado",
    "SVG to PNG — Free & Sharp at Any Size":
        "SVG para PNG — Grátis e Nítido em Qualquer Tamanho",
    "Photo Filters — Free Private Editor":
        "Filtros de Fotografia — Editor Grátis e Privado",
    # --- New tool pages: shared body copy -------------------------------------
    "Drop a photo": "Largue uma fotografia",
    "Drop an image": "Largue uma imagem",
    "or click to browse — JPG, PNG or WEBP": "ou clique para procurar — JPG, PNG ou WEBP",
    "Select a photo": "Selecionar uma fotografia",
    "Select an image": "Selecionar uma imagem",
    "Select photos": "Selecionar fotografias",
    "New photo": "Nova fotografia",
    "New image": "Nova imagem",
    "Output format": "Formato de saída",
    "Frequently asked questions": "Perguntas frequentes",
    # --- Remove Object page ---
    "Erased locally — nothing is uploaded": "Apagado localmente — nada é carregado",
    "Remove Objects from Photos — Free, Private & In Your Browser":
        "Remover Objetos de Fotografias — Grátis, Privado e no Navegador",
    "Erase unwanted objects, people or blemishes from a photo: brush over them and a content-aware fill blends them away. Free, no watermark, and nothing is uploaded — it all runs in your browser.":
        "Apague objetos, pessoas ou imperfeições de uma fotografia: pinte por cima e um preenchimento inteligente funde-os com o fundo. Grátis, sem marca de água e sem nada carregado — corre tudo no seu navegador.",
    "Remove Objects from Photos": "Remova Objetos de Fotografias",
    "Remove": "Remova",
    "Objects": "Objetos",
    "from Photos": "de Fotografias",
    "Brush over the thing you want gone — a stranger, a sign, a blemish — and a":
        "Pinte sobre o que quer remover — um estranho, um sinal, uma imperfeição — e um",
    "content-aware fill": "preenchimento inteligente",
    "blends it away. Free, private and instant.":
        "funde-o com o fundo. Grátis, privado e instantâneo.",
    "Works best on even backgrounds — sky, grass, walls, sand":
        "Funciona melhor em fundos uniformes — céu, relva, paredes, areia",
    "Brush over the object, then press": "Pinte sobre o objeto e carregue em",
    "Repeat in smaller passes for tricky areas.": "Repita em passagens mais pequenas nas zonas difíceis.",
    "Clear brush": "Limpar pincel",
    "Erase selection": "Apagar seleção",
    "Erasing…": "A apagar…",
    "Erase an object in three steps": "Apague um objeto em três passos",
    "Any JPG, PNG or WEBP — it's read straight in your browser, never uploaded.":
        "Qualquer JPG, PNG ou WEBP — é lido diretamente no navegador, nunca carregado.",
    "Brush the object": "Pinte o objeto",
    "Paint over the thing you want gone and press Erase — the fill blends the area away.":
        "Pinte sobre o que quer remover e carregue em Apagar — o preenchimento funde a área com o fundo.",
    "Export full resolution as PNG or JPG — free and watermark-free.":
        "Exporte em resolução total como PNG ou JPG — grátis e sem marca de água.",
    "Object removed": "Objeto removido",
    "Drag the handle — the stranger is brushed out, on-device":
        "Arraste o cursor — o estranho é apagado, no seu dispositivo",
    "Your photo — brush over the object you want to remove":
        "A sua foto — pinte sobre o objeto que quer remover",
    "Brushing the mask requires a mouse, trackpad or touchscreen. The Erase, Undo and Download buttons are keyboard-accessible.":
        "Pintar a máscara requer rato, trackpad ou ecrã tátil. Os botões Apagar, Anular e Descarregar são acessíveis por teclado.",
    # --- Upscale page ---
    "Enlarged locally — nothing is uploaded": "Ampliado localmente — nada é carregado",
    "Upscale an Image 2× or 4× — Free, Sharp & In Your Browser":
        "Ampliar uma Imagem 2× ou 4× — Grátis, Nítido e no Navegador",
    "Enlarge images 2× or 4× with high-quality Lanczos resampling and detail sharpening — free and instant, right in your browser. No upload, no watermark, no sign-up.":
        "Amplie imagens 2× ou 4× com reamostragem Lanczos de alta qualidade e reforço de detalhe — grátis e instantâneo, no seu navegador. Sem carregamentos, sem marca de água, sem registo.",
    "Upscale an Image": "Amplie uma Imagem",
    "2× or 4×": "2× ou 4×",
    "High-quality": "Reamostragem",
    "Lanczos resampling": "Lanczos de alta qualidade",
    "with a gentle sharpening pass — edges stay clean instead of going soft or blocky. Instant, free and 100% private.":
        "com um reforço subtil de nitidez — os contornos ficam limpos em vez de esborratados. Instantâneo, grátis e 100% privado.",
    "Great for logos, small photos and web images headed for print":
        "Ideal para logótipos, fotos pequenas e imagens da web destinadas a impressão",
    "Scale": "Escala",
    "Sharpen": "Nitidez",
    "Upscaling…": "A ampliar…",
    "Upscale an image in three steps": "Amplie uma imagem em três passos",
    "Pick 2× or 4×": "Escolha 2× ou 4×",
    "Lanczos resampling enlarges cleanly, and the sharpen slider brings detail forward.":
        "A reamostragem Lanczos amplia de forma limpa e o controlo de nitidez realça o detalhe.",
    "Export as lossless PNG or a high-quality JPG — no watermark, no limits.":
        "Exporte como PNG sem perdas ou JPG de alta qualidade — sem marca de água, sem limites.",
    "Plain stretch": "Esticado simples",
    "Lanczos + sharpen": "Lanczos + nitidez",
    "The same small image, stretched vs resampled — drag to compare":
        "A mesma imagem pequena, esticada vs reamostrada — arraste para comparar",
    # --- HEIC page ---
    "Converted locally — nothing is uploaded": "Convertido localmente — nada é carregado",
    "HEIC to JPG Converter — Free, Private & In Your Browser":
        "Conversor de HEIC para JPG — Grátis, Privado e no Navegador",
    "Convert iPhone HEIC photos to JPG, PNG or WEBP for free — right in your browser, so your photos are never uploaded. Batch convert and download as a ZIP. No watermark, no sign-up.":
        "Converta fotos HEIC do iPhone para JPG, PNG ou WEBP gratuitamente — no seu navegador, sem as fotos serem carregadas. Converta em lote e descarregue em ZIP. Sem marca de água, sem registo.",
    "Convert HEIC to": "Converta HEIC para",
    "iPhone photos that won't open on Windows, Android or the web? Drop them here and get":
        "Fotos do iPhone que não abrem no Windows, no Android ou na web? Largue-as aqui e receba",
    "JPG, PNG or WEBP": "JPG, PNG ou WEBP",
    "back — free, private and in your browser.":
        "de volta — grátis, privado e no seu navegador.",
    "Drop your HEIC photos": "Largue as suas fotos HEIC",
    "or click to browse — .heic and .heif, single or batch":
        "ou clique para procurar — .heic e .heif, uma ou em lote",
    "The decoder loads once (~1 MB) and is cached — photos never leave your device":
        "O descodificador carrega uma vez (~1 MB) e fica em cache — as fotos nunca saem do seu dispositivo",
    "Same photo, a format everything opens — converted on your device":
        "A mesma foto, num formato que tudo abre — convertida no seu dispositivo",
    "Convert HEIC in three steps": "Converta HEIC em três passos",
    "Drop your photos": "Largue as suas fotografias",
    "Straight from an iPhone, AirDrop or a folder — .heic and .heif both work.":
        "Diretamente do iPhone, por AirDrop ou de uma pasta — .heic e .heif funcionam.",
    "Pick a format": "Escolha um formato",
    "JPG opens everywhere; PNG is lossless; WEBP is smallest for the web.":
        "JPG abre em todo o lado; PNG é sem perdas; WEBP é o mais pequeno para a web.",
    "Grab photos one by one or all together as a ZIP — full resolution, no watermark.":
        "Descarregue as fotos uma a uma ou todas juntas em ZIP — resolução total, sem marca de água.",
    # --- PDF to images page ---
    "Rendered locally — nothing is uploaded": "Processado localmente — nada é carregado",
    "PDF to Images — Convert PDF Pages to PNG or JPG, Free":
        "PDF para Imagens — Converta Páginas de PDF em PNG ou JPG, Grátis",
    "Turn every page of a PDF into a sharp PNG or JPG image, free and in your browser — the PDF is never uploaded. Download single pages or all pages as a ZIP. No watermark, no limits.":
        "Transforme cada página de um PDF numa imagem PNG ou JPG nítida, grátis e no seu navegador — o PDF nunca é carregado. Descarregue páginas individuais ou todas em ZIP. Sem marca de água, sem limites.",
    "PDF to": "PDF para",
    "Images": "Imagens",
    "Every page of your PDF as a sharp": "Cada página do seu PDF como um",
    "PNG or JPG": "PNG ou JPG nítido",
    "— rendered from the vector source, so text stays crisp. Free, private, no page limits.":
        "— gerado a partir da fonte vetorial, para o texto ficar nítido. Grátis, privado, sem limite de páginas.",
    "Drop a PDF": "Largue um PDF",
    "or click to browse — contracts, scans, slides, forms":
        "ou clique para procurar — contratos, digitalizações, slides, formulários",
    "Select a PDF": "Selecionar um PDF",
    "Your document is parsed on your device — it never leaves the browser":
        "O documento é lido no seu dispositivo — nunca sai do navegador",
    "Resolution": "Resolução",
    "One PDF in, every page out as its own sharp image":
        "Entra um PDF, sai cada página como uma imagem nítida",
    "PDF to images in three steps": "PDF para imagens em três passos",
    "It's parsed right in your browser — private documents stay private.":
        "É lido diretamente no navegador — documentos privados continuam privados.",
    "Pick quality": "Escolha a qualidade",
    "2× is sharp for screens; 4× is print quality. Pages render from the vector source.":
        "2× é nítido para ecrã; 4× é qualidade de impressão. As páginas são geradas da fonte vetorial.",
    "Save the pages you need, or every page at once as a ZIP.":
        "Guarde as páginas de que precisa, ou todas de uma vez em ZIP.",
    "New PDF": "Novo PDF",
    # --- OCR page ---
    "Recognised locally — nothing is uploaded": "Reconhecido localmente — nada é carregado",
    "Image to Text (OCR) — Copy Text from a Photo, Free & Private":
        "Imagem para Texto (OCR) — Copie Texto de uma Foto, Grátis e Privado",
    "Extract and copy text from any photo or screenshot with on-device OCR — free, in your browser, nothing uploaded. Supports English and Portuguese. No watermark, no sign-up, no limits.":
        "Extraia e copie texto de qualquer foto ou captura de ecrã com OCR no dispositivo — grátis, no navegador, sem nada carregado. Suporta português e inglês. Sem marca de água, sem registo, sem limites.",
    "Copy Text out of": "Copie o Texto de",
    "Any Image": "Qualquer Imagem",
    "Screenshots, photos of documents, whiteboards — the OCR engine reads them":
        "Capturas de ecrã, fotos de documentos, quadros — o motor de OCR lê-os",
    "on your device": "no seu dispositivo",
    "and hands you editable text. Free and private.":
        "e devolve-lhe texto editável. Grátis e privado.",
    "Drop an image with text": "Largue uma imagem com texto",
    "or click to browse, or paste a screenshot — JPG, PNG or WEBP":
        "ou clique para procurar, ou cole uma captura — JPG, PNG ou WEBP",
    "The OCR engine loads once and is cached — screenshots never leave your device":
        "O motor de OCR carrega uma vez e fica em cache — as capturas nunca saem do seu dispositivo",
    "A photo of text in, editable text out — recognised on your device":
        "Entra uma foto com texto, sai texto editável — reconhecido no seu dispositivo",
    "Text recognition progress": "Progresso do reconhecimento de texto",
    "Read again": "Ler novamente",
    "Recognised text": "Texto reconhecido",
    "Copy text": "Copiar texto",
    "Save .txt": "Guardar .txt",
    "Image to text in three steps": "Imagem para texto em três passos",
    "A screenshot, a photo of a page, a whiteboard — paste works too.":
        "Uma captura de ecrã, a foto de uma página, um quadro — colar também funciona.",
    "On-device OCR reads it": "O OCR lê no dispositivo",
    "The Tesseract engine runs in your browser via WebAssembly — nothing is uploaded.":
        "O motor Tesseract corre no navegador via WebAssembly — nada é carregado.",
    "Copy or save": "Copie ou guarde",
    "Fix anything in the editable box, then copy it or save it as a .txt file.":
        "Corrija o que precisar na caixa editável e depois copie ou guarde como ficheiro .txt.",
    # --- SVG page ---
    "Rasterised locally — nothing is uploaded": "Convertido localmente — nada é carregado",
    "SVG to PNG Converter — Pixel-Sharp at Any Size, Free":
        "Conversor de SVG para PNG — Nítido em Qualquer Tamanho, Grátis",
    "Convert SVG to PNG at 1×, 2×, 4× or any exact width — rendered from the vector so edges stay pixel-sharp. Free, in your browser, transparent background kept, nothing uploaded.":
        "Converta SVG para PNG a 1×, 2×, 4× ou numa largura exata — gerado do vetor para os contornos ficarem nítidos. Grátis, no navegador, com transparência mantida e sem nada carregado.",
    "SVG to": "SVG para",
    "Rendered from the": "Gerado a partir da",
    "vector source": "fonte vetorial",
    "at the exact size you pick — so a 4× export has 4× the real detail, not stretched pixels. Transparency preserved.":
        "no tamanho exato que escolher — uma exportação a 4× tem 4× o detalhe real, não píxeis esticados. Transparência preservada.",
    "Drop an SVG": "Largue um SVG",
    "or click to browse — logos, icons, illustrations":
        "ou clique para procurar — logótipos, ícones, ilustrações",
    "Select an SVG": "Selecionar um SVG",
    "Or an exact width (px)": "Ou uma largura exata (px)",
    "New SVG": "Novo SVG",
    "Stretched bitmap": "Bitmap esticado",
    "Rendered from vector": "Gerado do vetor",
    "The same logo at 4× — a stretched export vs a vector render":
        "O mesmo logótipo a 4× — exportação esticada vs geração vetorial",
    "SVG to PNG in three steps": "SVG para PNG em três passos",
    "It's read and rendered right in your browser — never uploaded.":
        "É lido e processado diretamente no navegador — nunca carregado.",
    "Pick a size": "Escolha um tamanho",
    "1×, 2×, 4× or an exact pixel width — the vector renders sharp at any of them.":
        "1×, 2×, 4× ou uma largura exata em píxeis — o vetor fica nítido em qualquer uma.",
    "PNG keeps transparency; JPG fills white. Free and watermark-free.":
        "PNG mantém a transparência; JPG preenche a branco. Grátis e sem marca de água.",
    # --- Photo filters page ---
    "Edited locally — nothing is uploaded": "Editado localmente — nada é carregado",
    "Photo Filters & Adjustments — Free Online Editor, No Upload":
        "Filtros e Ajustes de Fotografia — Editor Online Grátis, Sem Carregamentos",
    "Apply one-tap looks and fine-tune brightness, contrast, saturation, warmth, vignette and grain — free, in your browser, full-resolution export with no watermark and nothing uploaded.":
        "Aplique estilos de um toque e afine brilho, contraste, saturação, calor, vinheta e grão — grátis, no navegador, com exportação em resolução total, sem marca de água e sem nada carregado.",
    "Photo Filters &": "Filtros e",
    "Adjustments": "Ajustes",
    "Ten one-tap": "Dez",
    "looks": "estilos de um toque",
    "plus real sliders — brightness, contrast, saturation, warmth, vignette, grain. Full-resolution export, free and private.":
        "e controlos reais — brilho, contraste, saturação, calor, vinheta, grão. Exportação em resolução total, grátis e privada.",
    "Looks": "Estilos",
    "Brightness": "Brilho",
    "Contrast": "Contraste",
    "Saturation": "Saturação",
    "Warmth": "Calor",
    "Vignette": "Vinheta",
    "Grain": "Grão",
    "Hold to compare": "Segure para comparar",
    "Golden look": "Estilo dourado",
    "One tap, then fine-tune with the sliders — drag to compare":
        "Um toque e afine com os controlos — arraste para comparar",
    "Live preview of your photo with the current filter and adjustments":
        "Pré-visualização em direto da sua foto com o filtro e ajustes atuais",
    "Edit a photo in three steps": "Edite uma fotografia em três passos",
    "Tap a look, then fine-tune": "Toque num estilo e afine",
    "A look sets the starting point; every slider stays yours. Hold Compare to check.":
        "O estilo define o ponto de partida; os controlos continuam seus. Segure Comparar para verificar.",
    "Your exact settings re-applied at full resolution — JPG, PNG or WEBP.":
        "As suas definições exatas reaplicadas em resolução total — JPG, PNG ou WEBP.",
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
    "Photo Filters": "Filtros de Fotografia",
    "Image Upscaler": "Ampliador de Imagens",
    "Video to GIF": "Vídeo para GIF",
    "Video Converter": "Conversor de Vídeo",
    "Base64 Image": "Imagem Base64",
    "Colour Palette": "Paleta de Cores",
    "Photo Collage": "Colagem de Fotos",
    "Border & Polaroid": "Moldura e Polaroid",
    "Coming from another tool?": "Vem de outra ferramenta?",
    "See how we compare to remove.bg": "Veja como nos comparamos ao remove.bg",
    "images processed": "imagens processadas",
    "Tools": "Ferramentas",
    "Use cases": "Casos de uso",
    # The footer heading is translated but the guide titles under it are not — the
    # articles themselves are English-only, and a Portuguese label over English
    # content is the mismatch the hreflang gate exists to prevent.
    "Guides": "Guias",
    "All guides": "Todos os guias",
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
    "Redo": "Refazer",
    "Reset": "Repor",
    "Show original": "Mostrar original",
    "ghosts the photo underneath so you can see what to paint back.":
        "mostra a foto por baixo, esbatida, para ver o que pode repor.",
    "size,": "tamanho,",
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
    "Please choose a video file": "Escolha um ficheiro de vídeo",
    "This video format can't be read in your browser — try an MP4 or WebM.": "O seu navegador não consegue ler este formato de vídeo — experimente um MP4 ou WebM.",
    "Could not convert the video": "Não foi possível converter o vídeo",
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
    # Live status on the result card while a cut-out is being made.
    "Removing background…": "A remover o fundo…",
    "Downloading AI model… {pct}%": "A descarregar o modelo de IA… {pct}%",
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
    # --- Compressor quality compare ---
    "Original": "Original",
    # --- Base64 / palette / collage / border ---
    "That is not a valid image data URI": "Isso não é um URI de dados de imagem válido",
    "Click to copy": "Clique para copiar",
    "Copied {value}": "{value} copiado",
    "Palette copied as CSS": "Paleta copiada como CSS",
    "Palette copied as {kind}": "Paleta copiada como {kind}",
    "Remove": "Remover",
    "{n} photo": "{n} fotografia",
    "{n} photos": "{n} fotografias",
    # --- Cross-tool chaining (kit.js) ---
    "Keep editing this image:": "Continue a editar esta imagem:",
    "— keep going:": "— continue:",
    "Carried over from {tool}": "Trazido de {tool}",
    # --- Remove object ---
    "Brush over the object first": "Pinte primeiro sobre o objeto",
    "Object erased — download or keep brushing": "Objeto apagado — descarregue ou continue a pintar",
    "Erase failed": "Não foi possível apagar",
    # --- Upscale ---
    "capped": "limitado",
    "Upscaled to {w}×{h}": "Ampliado para {w}×{h}",
    "Could not upscale that image": "Não foi possível ampliar essa imagem",
    # --- HEIC ---
    "Those are not HEIC files — drop .heic photos": "Esses ficheiros não são HEIC — largue fotos .heic",
    "Converting…": "A converter…",
    "Could not convert {name}": "Não foi possível converter {name}",
    "Converted {n} photo": "{n} fotografia convertida",
    "Converted {n} photos": "{n} fotografias convertidas",
    # --- PDF to images ---
    "That is not a PDF file": "Isso não é um ficheiro PDF",
    "Reading PDF…": "A ler o PDF…",
    "Could not read that PDF": "Não foi possível ler esse PDF",
    "{n} page": "{n} página",
    "{n} pages": "{n} páginas",
    "Page": "Página",
    "Page {n} failed": "A página {n} falhou",
    # --- OCR ---
    "Reading…": "A ler…",
    "No text found in that image": "Nenhum texto encontrado nessa imagem",
    "{n} words": "{n} palavras",
    "Could not read the text": "Não foi possível ler o texto",
    # --- SVG to PNG ---
    "That is not an SVG file": "Isso não é um ficheiro SVG",
    "Could not render that SVG": "Não foi possível processar esse SVG",
    # --- Filters / upscale batch ---
    "Exported {n} photo": "{n} fotografia exportada",
    "Exported {n} photos": "{n} fotografias exportadas",
    # --- Video frame grab ---
    "Could not capture that frame": "Não foi possível capturar esse fotograma",
    "Frame captured — pick a tool below to edit it":
        "Fotograma capturado — escolha abaixo uma ferramenta para o editar",
    # --- Compressor zero-savings hint ---
    "already optimized: try WEBP or AVIF, or lower the quality":
        "já otimizada: experimente WEBP ou AVIF, ou reduza a qualidade",
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


# --- FAQ translations for the translated tool pages ---------------------------
# Keyed by the English question (the seo_content source of truth); each value is
# the (question, answer) pair in Portuguese. localize_faqs() swaps them in on
# /pt/ pages — for both the visible accordion and the FAQPage JSON-LD, which
# render from the same list.
FAQS_PT = {
    # Remove object
    "How do I remove an object from a photo?":
        ("Como removo um objeto de uma fotografia?",
         "Largue uma fotografia, pinte sobre o objeto que quer remover e carregue em Apagar. A ferramenta preenche a área pintada a partir dos píxeis à volta — tudo no seu navegador, em segundos."),
    "Does it use AI? How good is the result?":
        ("Usa IA? Qual é a qualidade do resultado?",
         "Usa um preenchimento inteligente e rápido que funde as cores e a textura envolventes na área apagada. Brilha em céus, paredes, relva, areia e outros fundos uniformes; fundos muito detalhados podem pedir uma segunda passagem mais pequena."),
    "Is my photo uploaded anywhere?":
        ("A minha fotografia é carregada para algum lado?",
         "Não. Todo o preenchimento corre no seu dispositivo — a fotografia nunca sai do navegador, que é exatamente o que quer ao editar imagens pessoais."),
    "Can I remove people from photos?":
        ("Posso remover pessoas das fotografias?",
         "Sim — pinte sobre a pessoa e apague. Os resultados são melhores quando a pessoa está sobre um fundo relativamente uniforme, como céu, mar, relva ou uma parede."),
    "Is it free, and is there a watermark?":
        ("É grátis? Tem marca de água?",
         "Completamente grátis e ilimitado, sem marca de água e sem registo — como todas as ferramentas ClearBG."),
    # Upscale
    "How does the upscaler enlarge my image?":
        ("Como é que o ampliador aumenta a minha imagem?",
         "Reamostra a imagem a 2× ou 4× com um filtro Lanczos de alta qualidade e aplica depois um reforço subtil de nitidez — a mesma abordagem do software profissional de fotografia. Corre instantaneamente no navegador."),
    "Is this AI super-resolution?":
        ("Isto é super-resolução por IA?",
         "Não — e é deliberado. Os modelos de ampliação por IA no navegador são lentos e podem bloquear o separador em fotos grandes. Esta ferramenta troca um pouco dessa magia por resultados instantâneos e fiáveis em qualquer tamanho, sem nada carregado."),
    "What sizes can I upscale to?":
        ("Até que tamanhos posso ampliar?",
         "O dobro ou o quádruplo do original, até um limite de segurança de 8000 píxeis no lado maior, para o navegador nunca ficar sem memória. As exportações são PNG (sem perdas) ou JPG."),
    "Will an upscaled photo look better than the original?":
        ("Uma foto ampliada fica melhor do que o original?",
         "Ampliar não inventa detalhe que nunca foi captado, mas uma ampliação bem reamostrada e levemente nítida fica muito melhor do que um simples esticar — os contornos mantêm-se limpos em vez de ficarem esborratados."),
    "Is it private and free?":
        ("É privado e grátis?",
         "Sim. A reamostragem corre inteiramente no seu dispositivo — nada é carregado — e é grátis, ilimitada e sem marca de água."),
    # HEIC
    "Why can't I open my iPhone's HEIC photos?":
        ("Porque não consigo abrir as fotos HEIC do meu iPhone?",
         "Os iPhones guardam fotos em HEIC por predefinição. Reduz os ficheiros para metade, mas o Windows, o Android e a maioria dos sites não o abrem — por isso a foto funciona no telemóvel e em mais lado nenhum. Converter para JPG resolve isso de imediato."),
    "How do I convert HEIC to JPG for free?":
        ("Como converto HEIC para JPG gratuitamente?",
         "Largue aqui os seus ficheiros .heic e descarregue-os como JPG (ou PNG / WEBP). A conversão acontece no navegador — sem software para instalar, sem carregamentos, sem marca de água, sem limites."),
    "Are my photos uploaded to a server?":
        ("As minhas fotos são carregadas para um servidor?",
         "Não. O descodificador HEIC corre no seu dispositivo, por isso as fotos nunca saem do navegador. E isso importa — fotos pessoais não deviam passar pelo servidor de terceiros só para mudar de formato."),
    "Does converting HEIC lose quality?":
        ("Converter HEIC perde qualidade?",
         "A foto é descodificada em resolução total e recodificada em alta qualidade. O JPG tem perdas por natureza, mas neste nível a diferença não é visível; escolha PNG para uma exportação sem perdas."),
    "Can I convert many HEIC photos at once?":
        ("Posso converter muitas fotos HEIC de uma vez?",
         "Sim — largue um lote inteiro e descarregue-as individualmente ou todas juntas em ZIP."),
    # PDF to images
    "How do I turn a PDF into images?":
        ("Como transformo um PDF em imagens?",
         "Largue aqui um PDF e cada página é gerada como imagem de alta resolução no seu navegador. Descarregue páginas individuais em PNG ou JPG, ou todas de uma vez em ZIP."),
    "Is my PDF uploaded anywhere?":
        ("O meu PDF é carregado para algum lado?",
         "Não. O PDF é lido e processado inteiramente no seu dispositivo — importante, porque os PDFs são muitas vezes contratos, documentos, extratos e outros ficheiros privados."),
    "What resolution are the exported images?":
        ("Qual é a resolução das imagens exportadas?",
         "As páginas são geradas ao dobro do tamanho nominal (cerca de 150 DPI) por predefinição, e pode aumentar para qualidade de impressão. O texto fica nítido porque a página é gerada da fonte vetorial, não esticada de uma pré-visualização."),
    "Can I extract just one page?":
        ("Posso extrair só uma página?",
         "Sim — cada página tem o seu próprio botão de descarregar, por isso pode guardar exatamente as páginas de que precisa, ou todas em ZIP."),
    # Shared by the PDF-to-images and photo-filters pages, so the answer stays
    # generic enough to be true on both.
    "Is it free, with no watermark?":
        ("É grátis, sem marca de água?",
         "Completamente grátis, ilimitado e sem marca de água — sem registo, sem limites e sem versão de teste."),
    # OCR
    "How do I copy text out of an image?":
        ("Como copio o texto de uma imagem?",
         "Largue uma foto ou captura de ecrã e o reconhecedor de texto lê-a no seu navegador. O texto reconhecido aparece numa caixa editável — copie-o todo com um clique."),
    "Is my image uploaded for the text recognition?":
        ("A imagem é carregada para o reconhecimento de texto?",
         "Não. O motor de OCR (Tesseract, o mesmo motor open-source de muitos digitalizadores) corre no seu dispositivo via WebAssembly. As capturas de ecrã contêm muitas vezes conversas e documentos privados — aqui nunca saem do navegador."),
    "Which languages does it recognise?":
        ("Que idiomas reconhece?",
         "Português e inglês estão incluídos, entre outros, e o motor descarrega o pacote do idioma escolhido na primeira utilização — depois fica em cache e funciona offline."),
    "How accurate is it?":
        ("Qual é a precisão?",
         "Muito boa em capturas de ecrã limpas e documentos impressos; fotos difíceis (ângulos, manuscrito, pouca luz) reduzem a precisão. Imagens nítidas, de frente e com bom contraste reconhecem melhor."),
    "Is it free and unlimited?":
        ("É grátis e ilimitado?",
         "Sim — grátis, ilimitado, sem marca de água, sem registo. Reconheça as imagens que quiser."),
    # SVG to PNG
    "How do I convert an SVG to PNG?":
        ("Como converto um SVG para PNG?",
         "Largue aqui um ficheiro .svg, escolha um tamanho (1×, 2×, 4× ou uma largura exata em píxeis) e descarregue um PNG nítido. O navegador converte o vetor diretamente, por isso os contornos ficam perfeitos em qualquer escala."),
    "Why does my SVG export blurry from other tools?":
        ("Porque é que o meu SVG sai desfocado noutras ferramentas?",
         "Porque convertem no tamanho nominal do SVG e depois esticam o bitmap. Esta ferramenta gera o vetor no tamanho exato que escolher, por isso uma exportação a 4× tem 4× o detalhe real."),
    "Does it keep transparency?":
        ("Mantém a transparência?",
         "Sim — as exportações PNG mantêm o fundo totalmente transparente por predefinição, ou pode preenchê-lo com qualquer cor. A exportação JPG preenche a branco automaticamente."),
    "Is my SVG uploaded?":
        ("O meu SVG é carregado?",
         "Não. O ficheiro é lido e processado inteiramente no seu navegador — nada é enviado para um servidor."),
    "What about fonts and embedded images inside the SVG?":
        ("E as fontes e imagens incorporadas no SVG?",
         "SVGs que incorporam as suas imagens e usam fontes de sistema comuns são gerados exatamente. Um SVG que referencia ficheiros externos ou webfonts pode ser gerado com fontes de substituição, porque o navegador o processa isoladamente."),
    # Photo filters
    "What can I adjust in this photo editor?":
        ("O que posso ajustar neste editor de fotografia?",
         "Estilos de um toque (vivo, quente, dramático, película, preto e branco e mais) e controlos manuais de brilho, contraste, saturação, calor, vinheta e grão. Segure o botão Comparar a qualquer momento para verificar contra o original."),
    "Are the filters applied to the full-quality photo?":
        ("Os filtros são aplicados à foto em qualidade total?",
         "Sim. A pré-visualização é reduzida por velocidade, mas a exportação reaplica as suas definições exatas ao original em resolução total — sem perda de qualidade além do formato escolhido."),
    "Is my photo uploaded to apply filters?":
        ("A minha foto é carregada para aplicar os filtros?",
         "Não. Cada ajuste é desenhado num canvas no seu dispositivo — a foto nunca sai do navegador."),
    "Can I fine-tune a preset look?":
        ("Posso afinar um estilo predefinido?",
         "Sim — toque num estilo e ajuste qualquer controlo por cima. O estilo define um ponto de partida; os controlos continuam sempre seus."),
}


def localize_faqs(faqs, lang=None):
    """Return `faqs` with Portuguese Q&A swapped in on /pt/ pages.

    Keys are the English question text; a question without a translation stays
    English (graceful degradation, like everything else in this module).
    """
    if not _is_pt(lang):
        return faqs
    out = []
    for f in faqs:
        tr = FAQS_PT.get(f["q"])
        out.append({"q": tr[0], "a": tr[1]} if tr else f)
    return out
