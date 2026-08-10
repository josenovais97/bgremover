"""
European Portuguese (pt-PT) catalogue.

Data only — the lookup helpers live in ``remover.translations``, which registers
this module in ``CATALOGUES``. Every catalogue module exposes the same four
names, so adding a language is a new file here plus one line there.

``UI``      — template copy, resolved by the ``{% t %}`` tag.
``JS_UI``   — runtime messages shipped to the browser for ``CBG.t()``.
``USE_CASES`` — translated fields merged over the English use-case landings.
``FAQS``    — (question, answer) pairs keyed by the English question.

Any string without an entry falls back to English, so partial coverage degrades
gracefully rather than breaking a page.
"""

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
    "What are you removing the background from?": "De que está a remover o fundo?",

    # --- hub -> landing cluster links (partials/related_landings.html) -------
    "Looking for something more specific?": "Procura algo mais específico?",
    "Compress PNG": "Comprimir PNG",
    "Compress JPEG": "Comprimir JPEG",
    "Compress WEBP": "Comprimir WEBP",
    "Compress Video": "Comprimir vídeo",
    "Under 1MB": "Abaixo de 1 MB",
    "Under 500KB": "Abaixo de 500 KB",
    "Under 100KB": "Abaixo de 100 KB",
    "For email": "Para email",
    "For websites": "Para sites",
    "For Discord": "Para o Discord",
    "Private image tools": "Ferramentas de imagem privadas",
    "Remove background without uploading": "Remover fundo sem carregar",
    "Offline image editor": "Editor de imagem offline",
    "Open HEIC on Windows": "Abrir HEIC no Windows",
    "iPhone photos to JPG": "Fotos do iPhone para JPG",
    "Extract text from image": "Extrair texto de imagem",
    "remove.bg alternative": "alternativa ao remove.bg",
    "vs TinyPNG": "vs TinyPNG",
    "vs Canva": "vs Canva",
    "vs Adobe Express": "vs Adobe Express",
    "vs Photoroom": "vs Photoroom",
    "vs CloudConvert": "vs CloudConvert",

    # --- /photo-filters/ DEEP -----------------------------------------------
    "Using filters and adjustments well": "Usar bem os filtros e os ajustes",
    "Adjustments versus looks": "Ajustes versus estilos",
    "Two different things get called filters. Adjustments — exposure, contrast, saturation, temperature — are corrections that move an image towards what it should have looked like. Looks are stylistic presets that move it somewhere deliberately different.":
        "Chamam-se filtros a duas coisas diferentes. Os ajustes — exposição, contraste, saturação, temperatura — são correções que movem uma imagem na direção do que ela devia ter parecido. Os estilos são predefinições estéticas que a movem deliberadamente para outro lugar.",
    "The order matters. Correct first, then style. A preset applied to an underexposed, colour-cast photo bakes those problems in and makes them harder to fix, because the preset has already redistributed the tones you needed to work with.":
        "A ordem importa. Corrija primeiro, estilize depois. Uma predefinição aplicada a uma foto subexposta e com desvio de cor cristaliza esses problemas e torna-os mais difíceis de corrigir, porque a predefinição já redistribuiu os tons com que precisava de trabalhar.",
    "What each slider actually does": "O que cada cursor faz de facto",
    "Knowing the mechanism makes the results predictable:":
        "Conhecer o mecanismo torna os resultados previsíveis:",
    "Exposure shifts every tone up or down together, and clips highlights or shadows once they hit the ends of the range.":
        "A exposição desloca todos os tons para cima ou para baixo em conjunto, e corta as luzes ou as sombras quando estas atingem os extremos da escala.",
    "Contrast pushes tones away from the middle — brights brighter, darks darker — which also increases apparent saturation as a side effect.":
        "O contraste afasta os tons do meio — os claros mais claros, os escuros mais escuros — o que também aumenta a saturação aparente como efeito secundário.",
    "Saturation scales all colour intensity uniformly, so already-vivid colours clip first. Vibrance boosts the muted ones more than the vivid ones, which is why it is gentler on skin.":
        "A saturação escala uniformemente toda a intensidade de cor, pelo que as cores já vivas são as primeiras a cortar. A vibração reforça mais as apagadas do que as vivas, e é por isso que é mais suave na pele.",
    "Temperature and tint correct colour casts along the blue–orange and green–magenta axes respectively.":
        "A temperatura e a tonalidade corrigem desvios de cor ao longo dos eixos azul–laranja e verde–magenta, respetivamente.",
    "Sharpening increases contrast at edges. It adds no detail, and overdone it produces bright halos along high-contrast boundaries.":
        "A nitidez aumenta o contraste nas arestas. Não acrescenta detalhe, e em excesso produz halos claros ao longo das fronteiras de alto contraste.",
    "Where over-editing shows first": "Onde a edição excessiva se nota primeiro",
    "Skin tones and skies are the two places that give away a heavy hand. Skin turns orange with too much saturation or warmth and grey-green with too much correction the other way; the eye is extremely well calibrated for this and forgiving of almost nothing.":
        "Os tons de pele e os céus são os dois sítios que denunciam mão pesada. A pele fica laranja com saturação ou calor em excesso e verde-acinzentada com correção em excesso no sentido inverso; o olho está extremamente bem calibrado para isto e não perdoa quase nada.",
    "Skies band. A gradient pushed hard runs out of intermediate values, and the smooth transition becomes visible steps — made worse by any subsequent lossy compression, which handles gradients badly to begin with.":
        "Os céus criam faixas. Um gradiente forçado esgota os valores intermédios, e a transição suave torna-se em degraus visíveis — agravados por qualquer compressão com perdas posterior, que já lida mal com gradientes.",
    "Edit non-destructively where you can": "Edite de forma não destrutiva onde puder",
    "Every adjustment discards information: pushed highlights clip, crushed shadows merge, and neither comes back by moving the slider the other way. Doing it repeatedly on a saved JPEG compounds the loss with compression damage.":
        "Cada ajuste descarta informação: as luzes forçadas cortam, as sombras esmagadas fundem-se, e nenhuma das duas volta ao mover o cursor no sentido inverso. Fazê-lo repetidamente num JPEG gravado soma essa perda aos danos de compressão.",
    "Work from the highest-quality original each time rather than re-editing an export, and keep that original untouched. If you are producing several versions of one image, generate each from the master instead of editing one into the next.":
        "Trabalhe sempre a partir do original de maior qualidade em vez de reeditar uma exportação, e mantenha esse original intacto. Se está a produzir várias versões de uma imagem, gere cada uma a partir do original em vez de editar uma para dentro da seguinte.",

    # --- /remove-object/ DEEP -----------------------------------------------
    "How content-aware fill decides what goes in the hole":
        "Como o preenchimento com reconhecimento de conteúdo decide o que vai no buraco",
    "The fill is borrowed, not imagined": "O preenchimento é emprestado, não imaginado",
    "Erasing an object leaves a hole, and the fill is assembled from the pixels around it — colour, texture and gradient sampled from the boundary and propagated inward, coarse structure first and fine detail after.":
        "Apagar um objeto deixa um buraco, e o preenchimento é montado a partir dos pixels em volta — cor, textura e gradiente amostrados na fronteira e propagados para dentro, primeiro a estrutura grosseira e depois o detalhe fino.",
    "This is why the surroundings decide the result far more than the object does. A person standing against open sky disappears completely, because the algorithm has an enormous amount of consistent sky to borrow from. The same person in front of a bookshelf leaves a smear, because there is no way to infer which book was behind them.":
        "É por isto que o que está em volta decide o resultado muito mais do que o próprio objeto. Uma pessoa contra céu aberto desaparece por completo, porque o algoritmo tem uma enorme quantidade de céu consistente de onde tirar. A mesma pessoa à frente de uma estante deixa uma mancha, porque não há forma de inferir que livro estava por trás dela.",
    "Brush generously, but not too generously": "Pinte com generosidade, mas não em excesso",
    "Under-brushing is the most common mistake. Leaving a rim of the object's edge pixels means those colours get treated as legitimate surroundings and propagated into the fill, producing a ghost in roughly the object's shape.":
        "Pintar de menos é o erro mais comum. Deixar um aro dos pixels da borda do objeto faz com que essas cores sejam tratadas como envolvente legítima e propagadas para o preenchimento, produzindo um fantasma aproximadamente com a forma do objeto.",
    "Cover the object plus a small margin, including its shadow and any reflection — a removed object whose shadow remains reads as obviously wrong. But an unnecessarily huge selection forces the algorithm to invent more area than it has evidence for, so the fill turns mushy. Slightly larger than the object is the target.":
        "Cubra o objeto mais uma pequena margem, incluindo a sua sombra e qualquer reflexo — um objeto removido cuja sombra permanece lê-se como obviamente errado. Mas uma seleção desnecessariamente enorme obriga o algoritmo a inventar mais área do que aquela para a qual tem indícios, e o preenchimento fica pastoso. Ligeiramente maior do que o objeto é o alvo.",
    "Several small passes beat one large one": "Várias passagens pequenas vencem uma grande",
    "A big object over varied background is better removed in stages. Erase a portion, let the fill settle, then erase the next — each pass has more plausible surroundings to work from than one enormous selection would.":
        "Um objeto grande sobre um fundo variado remove-se melhor por fases. Apague uma parte, deixe o preenchimento assentar, depois apague a seguinte — cada passagem tem envolvente mais plausível de onde partir do que uma única seleção enorme teria.",
    "It also lets you stop when it looks right rather than committing to a single result, and to work along a boundary — the edge of a wall, a horizon — instead of across it, which is where fills most visibly break down.":
        "Permite também parar quando está bom em vez de se comprometer com um único resultado, e trabalhar ao longo de uma fronteira — o limite de uma parede, um horizonte — em vez de a atravessar, que é onde os preenchimentos falham de forma mais visível.",
    "Where this approach runs out": "Onde esta abordagem se esgota",
    "Straight lines that pass behind the object rarely reconnect convincingly: tiles, window frames, floorboards and railings all show a kink. Repeating patterns can drift out of phase. And anything that would require knowing what was genuinely hidden — a face behind a hand, text behind a sign — cannot be recovered by any amount of borrowing.":
        "As linhas retas que passam por trás do objeto raramente voltam a ligar-se de forma convincente: azulejos, caixilhos de janela, tábuas de soalho e gradeamentos mostram todos um desvio. Os padrões repetidos podem sair de fase. E qualquer coisa que exigisse saber o que estava genuinamente escondido — um rosto atrás de uma mão, texto atrás de um sinal — não pode ser recuperada por muito que se empreste.",
    "When the fill fails, cropping the object out of the frame is often the better edit, and an honest one.":
        "Quando o preenchimento falha, recortar o objeto para fora do enquadramento é muitas vezes a melhor edição, e uma edição honesta.",

    # --- /svg-to-png/ DEEP --------------------------------------------------
    "Rasterising vector art without losing the edges": "Rasterizar arte vetorial sem perder as arestas",
    "Why exports from other tools come out soft":
        "Porque é que as exportações de outras ferramentas saem suaves",
    "An SVG has a nominal size in its width, height or viewBox attributes, and many converters rasterise at that size and then scale the resulting bitmap to whatever you asked for. The vector is only consulted once, at the small size, and everything after that is a bitmap being stretched.":
        "Um SVG tem um tamanho nominal nos atributos width, height ou viewBox, e muitos conversores rasterizam nesse tamanho e depois escalam o bitmap resultante para o que pediu. O vetor só é consultado uma vez, no tamanho pequeno, e tudo o que vem depois é um bitmap a ser esticado.",
    "Rendering at the target size instead means the curves are evaluated at the resolution you actually want, so a 4x export contains four times the real detail rather than four times the pixels. The difference is most obvious on diagonal edges and small text, which is where stretched bitmaps go to pieces.":
        "Renderizar diretamente no tamanho de destino significa que as curvas são avaliadas na resolução que realmente quer, pelo que uma exportação a 4× contém quatro vezes o detalhe real e não quatro vezes os pixels. A diferença é mais evidente nas arestas diagonais e no texto pequeno, que é onde os bitmaps esticados se desfazem.",
    "Fonts are the usual surprise": "As fontes são a surpresa habitual",
    "SVG text is not shapes — it is characters plus a font name, resolved at render time. If the file names a font that is not available where it is rasterised, a fallback is substituted and the text reflows: different widths, different line breaks, sometimes overlapping other elements.":
        "O texto num SVG não são formas — são caracteres mais um nome de fonte, resolvidos no momento da renderização. Se o ficheiro nomeia uma fonte que não está disponível onde é rasterizado, é substituída por uma alternativa e o texto reflui: larguras diferentes, quebras de linha diferentes, às vezes sobrepondo-se a outros elementos.",
    "The fix belongs in the SVG rather than in the converter. Converting text to outlines in your vector editor before export makes the file self-contained and immune to this, at the cost of no longer being editable as text. For a logo destined for export that is almost always the right trade.":
        "A correção pertence ao SVG e não ao conversor. Converter o texto em contornos no seu editor vetorial antes de exportar torna o ficheiro autossuficiente e imune a isto, ao custo de deixar de ser editável como texto. Para um logótipo destinado a exportação, é quase sempre a troca certa.",
    "External references do not travel": "As referências externas não viajam",
    "An SVG can reference images by URL rather than embedding them, and can pull in webfonts and stylesheets the same way. Rasterised in isolation, those references produce blank rectangles and fallback type, because nothing is fetched.":
        "Um SVG pode referenciar imagens por URL em vez de as incorporar, e pode ir buscar webfonts e folhas de estilo da mesma forma. Rasterizado isoladamente, essas referências produzem retângulos vazios e tipos de letra alternativos, porque nada é transferido.",
    "Embedding raster content as a data URI inside the SVG makes it self-contained. It grows the file, but the file then renders identically everywhere, which is the entire point of handing someone a vector.":
        "Incorporar conteúdo raster como data URI dentro do SVG torna-o autossuficiente. Aumenta o ficheiro, mas o ficheiro passa a renderizar de forma idêntica em qualquer lugar, que é precisamente o objetivo de entregar um vetor a alguém.",
    "Transparency and what JPG does to it": "A transparência e o que o JPG lhe faz",
    "PNG output keeps the alpha channel, so an icon exported at any size drops onto any background cleanly. That is normally what you want from vector art.":
        "A saída em PNG mantém o canal alfa, pelo que um ícone exportado em qualquer tamanho assenta sobre qualquer fundo de forma limpa. É normalmente isso que se quer de arte vetorial.",
    "Exporting the same artwork as JPG flattens transparency onto white, and the result is a white box wherever the artwork was transparent. If the destination cannot take PNG, fill the background with the colour it will actually sit on rather than accepting the default.":
        "Exportar a mesma arte em JPG achata a transparência contra branco, e o resultado é uma caixa branca onde a arte era transparente. Se o destino não aceitar PNG, preencha o fundo com a cor sobre a qual vai realmente assentar em vez de aceitar a predefinição.",

    # --- /image-to-text/ DEEP -----------------------------------------------
    "Getting a clean read out of an image": "Obter uma leitura limpa a partir de uma imagem",
    "Why the same document reads twice differently": "Porque é que o mesmo documento se lê de duas maneiras",
    "Recognition begins by deciding, pixel by pixel, what is ink and what is paper. That decision is made from local contrast, so anything that changes brightness across the page changes the answer — a shadow from your hand, a window on one side, the curve of a book's spine.":
        "O reconhecimento começa por decidir, pixel a pixel, o que é tinta e o que é papel. Essa decisão é tomada a partir do contraste local, pelo que tudo o que altera o brilho ao longo da página altera a resposta — a sombra da sua mão, uma janela de um lado, a curvatura da lombada de um livro.",
    "It is why a photo that looks perfectly legible to you can return nonsense from one half of the page and near-perfect text from the other. The half that failed was thresholded to solid black or solid white before any character was examined.":
        "É por isso que uma foto que lhe parece perfeitamente legível pode devolver disparates de metade da página e texto quase perfeito da outra. A metade que falhou foi convertida para preto sólido ou branco sólido antes de qualquer caractere ser examinado.",
    "The resolution floor": "O mínimo de resolução",
    "Accuracy is governed by how many pixels tall a lowercase letter is, not by the megapixels of the image. Around 20-30 pixels is comfortable. Below about 10, the shapes that distinguish similar characters — the gap in an 'e', the join on an 'a' — simply are not present in the data, and no amount of processing recovers them.":
        "A precisão é governada pela altura em pixels de uma letra minúscula, não pelos megapixels da imagem. Cerca de 20-30 pixels é confortável. Abaixo de uns 10, as formas que distinguem caracteres semelhantes — a abertura de um «e», a ligação de um «a» — simplesmente não estão nos dados, e nenhum processamento as recupera.",
    "The practical consequence is that zooming in before you capture beats every post-processing step. A screenshot of a zoomed page outperforms a full-page screenshot scaled up afterwards, because one has the pixels and the other is inventing them.":
        "A consequência prática é que aproximar antes de captar vence qualquer passo de pós-processamento. Uma captura de uma página ampliada supera uma captura da página inteira aumentada depois, porque uma tem os pixels e a outra está a inventá-los.",
    "Choosing the language actually matters": "Escolher o idioma importa de facto",
    "The engine resolves ambiguous shapes against a model of the language you selected, so the wrong selection does not merely fail to help — it produces confident, wrong, real words. Portuguese text read as English comes back as English-looking nonsense, and accented characters tend to vanish because the model has no expectation of them.":
        "O motor resolve formas ambíguas contra um modelo do idioma que selecionou, pelo que a escolha errada não se limita a não ajudar — produz palavras reais, erradas e seguras de si. Texto português lido como inglês volta como disparate de aspeto inglês, e os caracteres acentuados tendem a desaparecer porque o modelo não os espera.",
    "If a document mixes languages, pick the dominant one rather than loading several. Multiple packs dilute each model and usually cost more accuracy than the mixed content does.":
        "Se um documento mistura idiomas, escolha o dominante em vez de carregar vários. Vários pacotes diluem cada modelo e normalmente custam mais precisão do que o próprio conteúdo misturado.",
    "What to fix before recognising": "O que corrigir antes de reconhecer",
    "Almost every improvement is upstream of the recognition step.":
        "Quase todas as melhorias estão a montante do passo de reconhecimento.",
    "Crop to the text block, so layout analysis has nothing else to interpret.":
        "Recorte até ao bloco de texto, para a análise de layout não ter mais nada para interpretar.",
    "Straighten the page — small skew is corrected automatically, large skew defeats line detection.":
        "Endireite a página — uma pequena inclinação é corrigida automaticamente, uma grande derrota a deteção de linhas.",
    "Even out the lighting before raising contrast; contrast on an uneven image amplifies the problem.":
        "Uniformize a iluminação antes de aumentar o contraste; contraste numa imagem irregular amplifica o problema.",
    "Do not sharpen heavily — the haloes it creates get read as ink and merge adjacent characters.":
        "Não aplique nitidez em excesso — os halos que cria são lidos como tinta e fundem caracteres vizinhos.",

    # --- /pdf-to-image/ DEEP ------------------------------------------------
    "Turning PDF pages into usable images": "Transformar páginas de PDF em imagens utilizáveis",
    "Rendering versus extracting": "Renderizar versus extrair",
    "There are two different operations people call 'PDF to image'. Extracting pulls out photographs that were embedded in the file, at whatever resolution they were embedded. Rendering draws the page — text, vectors, images and all — into a new bitmap at a size you choose.":
        "Há duas operações diferentes a que as pessoas chamam «PDF para imagem». Extrair retira as fotografias que foram incorporadas no ficheiro, na resolução em que foram incorporadas. Renderizar desenha a página — texto, vetores, imagens, tudo — num novo bitmap com o tamanho que escolher.",
    "This tool renders. That is what you want for anything containing text or diagrams, because the characters are drawn from their vector outlines at the output size and stay crisp. Extraction would give you only the photos and none of the layout.":
        "Esta ferramenta renderiza. É isso que quer para qualquer coisa com texto ou diagramas, porque os caracteres são desenhados a partir dos seus contornos vetoriais no tamanho de saída e ficam nítidos. A extração daria-lhe apenas as fotos e nada do layout.",
    "Choosing a scale that is worth the megabytes": "Escolher uma escala que justifique os megabytes",
    "A PDF page has a nominal size in points, and rendering at 1x produces roughly 72 pixels per inch — fine for a thumbnail and too soft to read comfortably. 2x lands near 150 DPI, which is the sensible default for screen reading and the point where body text becomes properly legible.":
        "Uma página de PDF tem um tamanho nominal em pontos, e renderizar a 1× produz cerca de 72 pixels por polegada — suficiente para uma miniatura e demasiado suave para ler com conforto. 2× fica perto de 150 DPI, que é a predefinição sensata para leitura em ecrã e o ponto em que o texto corrido se torna bem legível.",
    "4x approaches 300 DPI and is worth it only when the result will be printed or when you intend to run recognition over the output. The file size scales with the square of the factor, so a 4x render of a twenty-page document is a genuinely large download for output most people will view at a quarter of that size.":
        "4× aproxima-se dos 300 DPI e só vale a pena quando o resultado vai ser impresso ou quando pretende correr reconhecimento sobre o resultado. O tamanho do ficheiro escala com o quadrado do fator, pelo que uma renderização a 4× de um documento de vinte páginas é um download genuinamente grande para um resultado que a maioria das pessoas vai ver a um quarto desse tamanho.",
    "Why a scanned PDF behaves differently": "Porque é que um PDF digitalizado se comporta de outra forma",
    "A PDF produced by a scanner has no text in it at all — each page is one large photograph. Rendering such a page above the resolution of the original scan cannot add detail; it enlarges the scan and inflates the file.":
        "Um PDF produzido por um scanner não tem texto nenhum — cada página é uma grande fotografia. Renderizar uma página assim acima da resolução da digitalização original não pode acrescentar detalhe; amplia a digitalização e inflaciona o ficheiro.",
    "You can usually tell which kind you have by trying to select text in a PDF viewer. If nothing highlights, the page is an image, the useful export is JPG rather than PNG, and the natural next step is text recognition rather than a higher scale factor.":
        "Normalmente descobre que tipo tem tentando selecionar texto num leitor de PDF. Se nada ficar realçado, a página é uma imagem, a exportação útil é JPG e não PNG, e o passo natural seguinte é o reconhecimento de texto e não um fator de escala maior.",
    "PNG or JPG for the pages": "PNG ou JPG para as páginas",
    "Pages that are mostly text, tables or line diagrams should be PNG: the content is hard edges on flat white, which is exactly where lossless compression is small and where JPEG's ringing artefacts show up around every character.":
        "As páginas que são sobretudo texto, tabelas ou diagramas de linhas devem ser PNG: o conteúdo são arestas duras sobre branco liso, que é exatamente onde a compressão sem perdas ocupa pouco e onde os artefactos de anel do JPEG aparecem em volta de cada caractere.",
    "Pages that are mostly photographs should be JPG, where PNG would be several times larger for no visible gain. A mixed document is usually better off as PNG, because damaged text is more noticeable than a slightly larger file.":
        "As páginas que são sobretudo fotografias devem ser JPG, onde o PNG seria várias vezes maior sem ganho visível. Um documento misto costuma ficar melhor em PNG, porque texto estragado nota-se mais do que um ficheiro ligeiramente maior.",

    # --- /heic-to-jpg/ DEEP -------------------------------------------------
    "Converting iPhone photos without wasting quality": "Converter fotos do iPhone sem desperdiçar qualidade",
    "What you give up in the conversion": "O que perde na conversão",
    "HEIC stores 10 bits per colour channel; JPEG stores 8. That difference is invisible in most photographs and shows up as faint banding in large smooth gradients — a clear sky at dusk is the classic case. It cannot be recovered afterwards.":
        "O HEIC guarda 10 bits por canal de cor; o JPEG guarda 8. Essa diferença é invisível na maioria das fotografias e aparece como leves faixas em grandes gradientes suaves — um céu limpo ao crepúsculo é o caso clássico. Não pode ser recuperada depois.",
    "The container also carries things a flat image format has nowhere to put: Live Photo motion, the depth map that portrait blur relies on, and the edit history that makes Revert possible on the phone. Converting produces a finished picture and discards the rest.":
        "O contentor transporta também coisas que um formato de imagem plano não tem onde guardar: o movimento das Live Photos, o mapa de profundidade de que o desfoque de retrato depende, e o histórico de edições que torna possível o Reverter no telemóvel. Converter produz uma imagem acabada e descarta o resto.",
    "Convert once, from the original": "Converta uma vez, a partir do original",
    "JPEG is lossy, so every encode discards a little more. Converting an already-converted file compounds that for no reason. Go back to the HEIC each time rather than re-exporting a JPG you made earlier.":
        "O JPEG tem perdas, portanto cada codificação descarta um pouco mais. Converter um ficheiro já convertido agrava isso sem razão. Volte ao HEIC de cada vez, em vez de reexportar um JPG que já tinha feito.",
    "Keep the originals until you have checked the output. Deleting the HEIC masters is the only irreversible step in this process, and it is the one people do first.":
        "Guarde os originais até ter verificado o resultado. Apagar os HEIC originais é o único passo irreversível deste processo, e é o que as pessoas fazem primeiro.",
    "JPG or PNG out": "Sair em JPG ou PNG",
    "Pick JPG when the destination is an upload form, an email or long-term storage — the size saving is the entire reason the format exists and the quality cost at a high setting is not visible.":
        "Escolha JPG quando o destino é um formulário de carregamento, um email ou armazenamento a longo prazo — a poupança de tamanho é a razão de existir do formato e o custo em qualidade numa definição alta não é visível.",
    "Pick PNG when the photo is going into further editing. It is lossless, so the conversion adds no generational damage, at the cost of a file several times larger than the HEIC you started with.":
        "Escolha PNG quando a foto vai ser editada mais. É sem perdas, logo a conversão não acrescenta dano de geração, ao custo de um ficheiro várias vezes maior do que o HEIC de onde partiu.",
    "Order of operations for a camera roll": "Ordem das operações para um rolo de fotos",
    "A holiday folder is the real case, and a few habits keep it clean.":
        "Uma pasta de férias é o caso real, e alguns hábitos mantêm-na limpa.",
    "Convert the whole batch in one pass so the generational loss happens once.":
        "Converta o lote todo numa só passagem, para a perda de geração acontecer uma vez.",
    "Convert first and compress second, as separate decisions — a converter that silently shrinks to hit a size target has chosen quality for you.":
        "Converta primeiro e comprima depois, como decisões separadas — um conversor que encolhe em silêncio para cumprir um tamanho já escolheu a qualidade por você.",
    "Strip metadata at the same time if the photos are going somewhere public; every file is being rewritten anyway.":
        "Remova os metadados ao mesmo tempo se as fotos vão para um lugar público; todos os ficheiros estão a ser reescritos de qualquer forma.",
    "Check a few outputs before deleting anything.":
        "Verifique alguns resultados antes de apagar o que for.",

    # --- /upscale/ DEEP -----------------------------------------------------
    "What enlarging an image can and cannot do": "O que ampliar uma imagem pode e não pode fazer",
    "Resampling is interpolation, not invention": "A reamostragem é interpolação, não invenção",
    "Enlarging computes new pixels from the ones around them. A good filter — Lanczos, here — weights a neighbourhood of source pixels to estimate each new one, which keeps edges clean where a naive method would produce stair-stepping or blur.":
        "Ampliar calcula novos pixels a partir dos que estão em volta. Um bom filtro — aqui, Lanczos — pondera uma vizinhança de pixels de origem para estimar cada novo pixel, o que mantém as arestas limpas onde um método ingénuo produziria serrilhado ou desfoque.",
    "What it cannot do is add detail that was never captured. If a face occupies forty pixels in the original, no filter recovers the eyelashes, because that information does not exist in the file. Enlargement makes an image bigger and, done well, keeps it looking deliberate rather than stretched.":
        "O que não pode fazer é acrescentar detalhe que nunca foi captado. Se um rosto ocupa quarenta pixels no original, nenhum filtro recupera as pestanas, porque essa informação não existe no ficheiro. A ampliação torna uma imagem maior e, bem feita, mantém-na com um aspeto intencional em vez de esticado.",
    "Why this is not an AI upscaler, on purpose": "Porque isto não é um ampliador com IA, de propósito",
    "Model-based super-resolution genuinely can hallucinate plausible detail, and on the right image it is impressive. In a browser tab it is also slow enough to lock the page for tens of seconds on a large photo, and memory-hungry enough to crash a phone.":
        "A super-resolução baseada em modelos consegue de facto alucinar detalhe plausível, e na imagem certa é impressionante. Num separador de navegador é também lenta o suficiente para bloquear a página durante dezenas de segundos numa foto grande, e voraz de memória o suficiente para fazer um telemóvel abortar.",
    "There is a second, less discussed cost: an AI upscaler invents detail, and invented detail is wrong detail. On a document, a licence plate or a face, that is a liability rather than a feature. A resampled enlargement is honest about what it knows.":
        "Há um segundo custo, menos discutido: um ampliador com IA inventa detalhe, e detalhe inventado é detalhe errado. Num documento, numa matrícula ou num rosto, isso é um risco e não uma vantagem. Uma ampliação por reamostragem é honesta sobre o que sabe.",
    "Sharpening after, not before": "Nitidez depois, não antes",
    "Enlargement softens edges slightly no matter how good the filter is, so a gentle unsharp pass afterwards restores the appearance of crispness. Applied before enlargement, the same sharpening gets magnified along with everything else and turns into visible haloes.":
        "A ampliação suaviza ligeiramente as arestas, por muito bom que seja o filtro, pelo que uma leve passagem de nitidez a seguir devolve a aparência de definição. Aplicada antes da ampliação, essa mesma nitidez é aumentada com tudo o resto e transforma-se em halos visíveis.",
    "Overdoing it is the common mistake. Sharpening amplifies noise and JPEG artefacts as readily as detail, so an already-compressed source will show its blocking pattern long before it looks sharp.":
        "Exagerar é o erro comum. A nitidez amplifica o ruído e os artefactos JPEG com a mesma facilidade com que amplifica o detalhe, pelo que uma origem já comprimida mostra o seu padrão de blocos muito antes de parecer nítida.",
    "When enlargement is the wrong answer": "Quando a ampliação é a resposta errada",
    "If you need a larger image for print and have access to the original file, go back to it. A camera original or a vector source beats any enlargement of a downscaled copy, and the difference is not subtle.":
        "Se precisa de uma imagem maior para impressão e tem acesso ao ficheiro original, volte a ele. Um original de câmara ou uma fonte vetorial vence qualquer ampliação de uma cópia reduzida, e a diferença não é subtil.",
    "Logos and icons: find the SVG and rasterise it instead — infinitely better than any enlargement.":
        "Logótipos e ícones: encontre o SVG e rasterize-o — infinitamente melhor do que qualquer ampliação.",
    "Screenshots of text: retake at a higher zoom rather than enlarging.":
        "Capturas de ecrã de texto: refaça a captura com mais zoom em vez de ampliar.",
    "Heavily compressed images: compress artefacts enlarge too, and sharpening makes them worse.":
        "Imagens muito comprimidas: os artefactos de compressão também ampliam, e a nitidez piora-os.",
    "Print: 2x from a good original is usually plenty; 4x from a thumbnail will not rescue it.":
        "Impressão: 2× a partir de um bom original costuma ser suficiente; 4× a partir de uma miniatura não a salva.",

    # --- /resize-image/ DEEP ------------------------------------------------
    "Resizing well": "Redimensionar bem",
    "Down is safe, up is not": "Reduzir é seguro, ampliar não",
    "Making an image smaller derives every output pixel from real measured data, so it is the safe direction. It can even improve apparent quality, since averaging groups of pixels reduces noise — a high-ISO photo often looks cleaner at half size.":
        "Tornar uma imagem mais pequena deriva cada pixel de saída de dados realmente medidos, pelo que é a direção segura. Pode até melhorar a qualidade aparente, já que fazer a média de grupos de pixels reduz o ruído — uma foto com ISO alto costuma parecer mais limpa a metade do tamanho.",
    "Enlarging is a different problem. The detail was never captured, so it has to be invented: classical resampling does it softly, producing a bigger but blurrier image. Around 2× is the practical ceiling for anything that must look natural.":
        "Ampliar é um problema diferente. O detalhe nunca foi captado, portanto tem de ser inventado: a reamostragem clássica fá-lo de forma suave, produzindo uma imagem maior mas mais desfocada. Cerca de 2× é o limite prático para algo que tenha de parecer natural.",
    "Keep the aspect ratio": "Mantenha a proporção",
    "Changing width and height by different amounts stretches the image, and people are extremely good at spotting it — a face a few percent too wide looks wrong even to someone who cannot say why.":
        "Alterar a largura e a altura em proporções diferentes distorce a imagem, e as pessoas são extremamente boas a detetá-lo — um rosto poucos por cento demasiado largo parece errado até a quem não sabe explicar porquê.",
    "When a destination demands an exact ratio your original does not have, crop to that ratio first and then resize, rather than stretching to fit. You lose some framing and keep the proportions.":
        "Quando um destino exige uma proporção exata que o seu original não tem, recorte primeiro para essa proporção e só depois redimensione, em vez de esticar para caber. Perde algum enquadramento e mantém as proporções.",
    "Resize before compressing, not after": "Redimensione antes de comprimir, não depois",
    "File size is driven far more by pixel count than by the quality setting, so reducing dimensions to what will actually be displayed usually clears an upload limit on its own.":
        "O tamanho do ficheiro depende muito mais do número de pixels do que da definição de qualidade, pelo que reduzir as dimensões ao que vai realmente ser mostrado normalmente cumpre um limite de carregamento por si só.",
    "The common mistake is to keep full dimensions and push quality down until the file fits, which produces a large, artefact-ridden image where a smaller clean one would have looked better and weighed less.":
        "O erro comum é manter as dimensões totais e baixar a qualidade até o ficheiro caber, o que produz uma imagem grande e cheia de artefactos onde uma mais pequena e limpa teria ficado melhor e pesado menos.",
    "Sharpening comes last": "A nitidez vem no fim",
    "Downscaling softens an image slightly — that is inherent to averaging pixels together — so a light sharpen afterwards is normal and appropriate.":
        "Reduzir a escala suaviza ligeiramente a imagem — é inerente a fazer a média dos pixels — pelo que uma leve aplicação de nitidez a seguir é normal e apropriada.",
    "Doing it in the other order does not work: sharpening before you downscale amplifies noise and edge detail that the resize is about to average away, and can leave visible halos around high-contrast edges.":
        "Fazê-lo na ordem inversa não funciona: aplicar nitidez antes de reduzir amplifica ruído e detalhe de arestas que o redimensionamento está prestes a diluir, e pode deixar halos visíveis em volta de arestas de alto contraste.",

    # --- /exif-remover/ DEEP ------------------------------------------------
    "What the file says about you after you send it": "O que o ficheiro diz sobre você depois de o enviar",
    "The fields that actually matter": "Os campos que realmente importam",
    "Cameras and phones write a block of metadata into every photo. Most of it is harmless — exposure, focal length, orientation. Three fields are not: GPS coordinates, the timestamp, and the device identifier.":
        "As câmaras e os telemóveis escrevem um bloco de metadados em cada foto. A maior parte é inofensiva — exposição, distância focal, orientação. Três campos não são: as coordenadas GPS, a data e hora, e o identificador do dispositivo.",
    "The coordinates are precise enough to identify a building, and a photo taken indoors is usually taken at home. A set of photos shared over months carries a movement history nobody intended to publish, which is the part people underestimate.":
        "As coordenadas são precisas o suficiente para identificar um edifício, e uma foto tirada dentro de casa é normalmente tirada em casa. Um conjunto de fotos partilhadas ao longo de meses transporta um histórico de deslocações que ninguém quis publicar, e é essa a parte que as pessoas subestimam.",
    "Which platforms strip it, and why that is not a plan":
        "Que plataformas os removem, e porque isso não é um plano",
    "Large social networks generally strip metadata on upload, partly for privacy and partly because they re-encode everything anyway. That protects the public copy and nothing else.":
        "As grandes redes sociais geralmente removem os metadados no carregamento, em parte por privacidade e em parte porque recodificam tudo de qualquer forma. Isso protege a cópia pública e mais nada.",
    "The file you emailed, put in a shared folder, sent over a chat app that preserves originals, or attached to a marketplace listing keeps every field. Stripping before sending is the only approach that does not depend on each destination's current behaviour.":
        "O ficheiro que enviou por email, pôs numa pasta partilhada, mandou por uma aplicação de mensagens que preserva os originais, ou anexou a um anúncio, mantém todos os campos. Remover antes de enviar é a única abordagem que não depende do comportamento atual de cada destino.",
    "Why stripping costs no quality on a JPEG": "Porque remover não custa qualidade num JPEG",
    "A JPEG is a sequence of marker segments, and metadata lives in its own segments alongside the compressed image data. Removing them is a matter of dropping those segments and rewriting the file — the pixels are never decoded, so there is no re-encode and no generational loss.":
        "Um JPEG é uma sequência de segmentos marcados, e os metadados vivem nos seus próprios segmentos ao lado dos dados de imagem comprimidos. Removê-los é uma questão de descartar esses segmentos e reescrever o ficheiro — os pixels nunca são descodificados, logo não há recodificação nem perda de geração.",
    "This is worth knowing because the alternative people reach for — opening the photo in an editor and re-saving it — does re-encode, and loses a little quality every time.":
        "Vale a pena saber isto porque a alternativa a que as pessoas recorrem — abrir a foto num editor e gravá-la de novo — recodifica de facto, e perde um pouco de qualidade cada vez.",
    "What metadata will not tell you": "O que os metadados não lhe dizem",
    "Absent metadata is not evidence of anything. Screenshots never had any, messaging apps remove it, and any re-save can drop it, so a photo with no EXIF is unremarkable rather than suspicious.":
        "A ausência de metadados não é prova de nada. As capturas de ecrã nunca os tiveram, as aplicações de mensagens removem-nos, e qualquer nova gravação os pode eliminar, pelo que uma foto sem EXIF é banal e não suspeita.",
    "Equally, present metadata is not proof: every field is editable. It is a convenience for organising your own photos and a privacy risk when sharing, and it is not a chain of custody.":
        "Da mesma forma, a presença de metadados não é prova: todos os campos são editáveis. São uma conveniência para organizar as suas próprias fotos e um risco de privacidade ao partilhar, e não uma cadeia de custódia.",

    # --- /compress/ DEEP ----------------------------------------------------
    "Compressing without visible damage": "Comprimir sem estragos visíveis",
    "Resize before you compress": "Redimensione antes de comprimir",
    "This is the single most useful thing to know about hitting a size limit, and most people do it in the wrong order. File size scales roughly with pixel count, so halving an image's width and height cuts it to about a quarter — before the quality slider is touched at all.":
        "Esta é a coisa mais útil que se pode saber sobre cumprir um limite de tamanho, e a maioria das pessoas fá-lo na ordem errada. O tamanho do ficheiro escala aproximadamente com o número de pixels, portanto reduzir a metade a largura e a altura de uma imagem corta-a para cerca de um quarto — antes de sequer tocar no cursor de qualidade.",
    "A 4000-pixel-wide photo dropped to 1600 pixels will usually clear an upload limit on its own, with no perceptible loss, because nothing displaying it needed 4000 pixels. A 1600-pixel image at quality 85 looks better and weighs less than a 4000-pixel image at quality 40.":
        "Uma foto de 4000 pixels de largura reduzida a 1600 normalmente cumpre um limite de carregamento por si só, sem perda perceptível, porque nada que a mostre precisava de 4000 pixels. Uma imagem de 1600 pixels com qualidade 85 fica melhor e pesa menos do que uma de 4000 pixels com qualidade 40.",
    "Where the quality scale actually bites": "Onde a escala de qualidade realmente pesa",
    "The 0–100 quality number is badly non-linear, and knowing its shape saves a lot of guessing:":
        "O número de qualidade de 0–100 é fortemente não linear, e conhecer a sua forma evita muitas adivinhas:",
    "100 to 90: no visible difference on most photographs, but a large file. Wasteful for the web.":
        "100 a 90: nenhuma diferença visível na maioria das fotografias, mas um ficheiro grande. Desperdício para a web.",
    "90 to 80: still visually indistinguishable, at roughly half the size. Where most images should sit.":
        "90 a 80: continua visualmente indistinguível, com cerca de metade do tamanho. É onde a maioria das imagens deve ficar.",
    "80 to 70: slight softening in fine texture. Fine for thumbnails and secondary images.":
        "80 a 70: ligeira perda de nitidez na textura fina. Serve para miniaturas e imagens secundárias.",
    "70 to 60: artefacts appear in skies, skin tones and around sharp edges.":
        "70 a 60: aparecem artefactos nos céus, nos tons de pele e em volta das arestas nítidas.",
    "Below 60: obvious blockiness and haloing. Only when size dominates everything.":
        "Abaixo de 60: blocos e halos evidentes. Só quando o tamanho domina tudo o resto.",
    "Content changes the answer": "O conteúdo muda a resposta",
    "Those bands assume photographs. Busy texture — foliage, gravel, fabric — hides compression artefacts well and can go lower than you would expect.":
        "Estas faixas pressupõem fotografias. Textura carregada — folhagem, gravilha, tecido — esconde bem os artefactos de compressão e pode descer mais do que se esperaria.",
    "Smooth gradients are the opposite. A clear sky or a studio backdrop has no texture to mask the boundaries between compression blocks, so banding appears early. Screenshots, illustrations and anything with text are the worst case and often should not be lossy at all; if they must be, start at 90 rather than 80.":
        "Os gradientes suaves são o oposto. Um céu limpo ou um fundo de estúdio não tem textura para mascarar as fronteiras entre os blocos de compressão, pelo que as faixas aparecem cedo. Capturas de ecrã, ilustrações e tudo o que tenha texto são o pior caso e muitas vezes não deviam sequer usar compressão com perdas; se tiverem de usar, comece em 90 em vez de 80.",
    "Never compress twice": "Nunca comprima duas vezes",
    "Each lossy save re-quantises data that already carries artefacts from the previous save, and the damage accumulates permanently. Ten saves at quality 90 produce a visibly worse image than one save at quality 60.":
        "Cada gravação com perdas volta a quantizar dados que já trazem artefactos da gravação anterior, e o dano acumula-se de forma permanente. Dez gravações com qualidade 90 produzem uma imagem visivelmente pior do que uma única gravação com qualidade 60.",
    "Keep a lossless master and export to a compressed format once, at the end. If you need to send an image to someone who will edit it further, send the master.":
        "Guarde um original sem perdas e exporte para um formato comprimido uma só vez, no fim. Se precisar de enviar uma imagem a alguém que a vá editar mais, envie o original.",

    # --- /convert/ DEEP -----------------------------------------------------
    "Choosing the right format": "Escolher o formato certo",
    "What conversion does and does not cost you": "O que a conversão lhe custa e o que não custa",
    "Converting to a lossless format — PNG, or WebP in lossless mode — preserves your pixels exactly. Converting to a lossy format (JPG, lossy WebP, AVIF) discards data permanently, in exchange for a much smaller file.":
        "Converter para um formato sem perdas — PNG, ou WebP em modo lossless — preserva os seus pixels exatamente. Converter para um formato com perdas (JPG, WebP com perdas, AVIF) descarta dados de forma permanente, em troca de um ficheiro muito mais pequeno.",
    "The case worth avoiding is converting between two lossy formats. A JPG turned into a lossy WebP has been through two rounds of quantisation, and the second round treats the first round's artefacts as real detail worth preserving. Always convert from the highest-quality copy you have, not from a file that has already been compressed.":
        "O caso a evitar é converter entre dois formatos com perdas. Um JPG transformado em WebP com perdas passou por duas rondas de quantização, e a segunda ronda trata os artefactos da primeira como detalhe real que vale a pena preservar. Converta sempre a partir da cópia de maior qualidade que tem, não de um ficheiro que já foi comprimido.",
    "Which target format to pick": "Que formato de destino escolher",
    "The answer depends almost entirely on where the file is going:":
        "A resposta depende quase inteiramente do destino do ficheiro:",
    "For your own website: WebP. Typically 25–35% smaller than JPG at the same visual quality, supported by every current browser.":
        "Para o seu próprio site: WebP. Tipicamente 25–35% mais pequeno que o JPG com a mesma qualidade visual, suportado por todos os navegadores atuais.",
    "For sending to someone else: JPG. It is the most compatible image format in existence and never gets rejected.":
        "Para enviar a outra pessoa: JPG. É o formato de imagem mais compatível que existe e nunca é rejeitado.",
    "For anything with a transparent background: PNG as a master, lossy WebP for the web. JPG cannot store transparency at all.":
        "Para qualquer coisa com fundo transparente: PNG como original, WebP com perdas para a web. O JPG não consegue guardar transparência de forma alguma.",
    "For screenshots and images containing text: PNG or lossless WebP — sharp edges are the worst case for lossy compression.":
        "Para capturas de ecrã e imagens com texto: PNG ou WebP sem perdas — as arestas nítidas são o pior caso para a compressão com perdas.",
    "For large hero images where bandwidth matters: AVIF, which compresses hardest but encodes slowly.":
        "Para imagens grandes de destaque onde a largura de banda importa: AVIF, que comprime mais mas codifica devagar.",
    "The transparency trap": "A armadilha da transparência",
    "Converting a transparent PNG to JPG is the most common conversion mistake, because JPEG has no alpha channel and no way to represent one. The transparency has to be resolved against something, and the software picks — usually white, sometimes black.":
        "Converter um PNG transparente para JPG é o erro de conversão mais comum, porque o JPEG não tem canal alfa nem forma de o representar. A transparência tem de ser resolvida contra alguma coisa, e o software escolhe — normalmente branco, às vezes preto.",
    "Nothing is broken and nothing can be recovered afterwards; the alpha channel was discarded at export. If your cut-out came back with a white background, this is why. Re-export from the original as PNG or WebP.":
        "Nada está avariado e nada pode ser recuperado depois; o canal alfa foi descartado na exportação. Se o seu recorte apareceu com fundo branco, é por isto. Volte a exportar a partir do original em PNG ou WebP.",
    "Why this runs on your device": "Porque é que isto corre no seu dispositivo",
    "Conversion happens in your browser using the same canvas and codec support the browser already ships for displaying images. Nothing is uploaded, which means no file size ceiling imposed by a server, no queue, and no per-image cost — so batch conversion is just a matter of waiting.":
        "A conversão acontece no seu navegador usando o mesmo canvas e o mesmo suporte de codecs que o navegador já traz para mostrar imagens. Nada é carregado, o que significa nenhum limite de tamanho imposto por um servidor, nenhuma fila e nenhum custo por imagem — logo converter em lote é apenas uma questão de esperar.",
    "It also means the tool works on files you would not want to hand to a service: scanned documents, identity paperwork, medical images, unreleased work.":
        "Significa também que a ferramenta funciona com ficheiros que não quereria entregar a um serviço: documentos digitalizados, papelada de identificação, imagens médicas, trabalho ainda não divulgado.",

    # --- /crop/ DEEP (the long-form block) ----------------------------------
    "Cropping with intent": "Recortar com intenção",
    "Cropping is free, enlarging is not": "Recortar é grátis, ampliar não",
    "Cropping discards pixels, which costs you nothing in quality — the pixels that remain are the original measured data. What it costs is resolution, and that only matters if the result ends up smaller than where it is going.":
        "Recortar descarta pixels, o que não custa nada em qualidade — os pixels que ficam são os dados originais medidos. O que custa é resolução, e isso só importa se o resultado acabar mais pequeno do que o destino onde vai ser usado.",
    "A 4000-pixel photo cropped to a quarter of its area is still 2000 pixels wide, which is more than enough for almost any screen use. Crop confidently; the mistake is enlarging afterwards to compensate, which invents detail that was never captured.":
        "Uma foto de 4000 pixels recortada a um quarto da sua área continua a ter 2000 pixels de largura, o que é mais do que suficiente para quase qualquer utilização em ecrã. Recorte com confiança; o erro é ampliar depois para compensar, o que inventa detalhe que nunca foi captado.",
    "The ratios worth knowing": "As proporções que vale a pena saber",
    "Most crops are made to fit a destination, and there are only a handful that matter:":
        "A maioria dos recortes é feita para caber num destino, e só um punhado de proporções importa:",
    "1:1 square — profile pictures, and the universally safe social format.":
        "1:1 quadrado — fotos de perfil, e o formato social seguro em qualquer sítio.",
    "4:5 vertical — the tallest ratio most feeds display uncropped, so it occupies the most screen space.":
        "4:5 vertical — a proporção mais alta que a maioria dos feeds mostra sem recortar, pelo que ocupa mais espaço no ecrã.",
    "9:16 — stories, reels and TikTok, full phone screen.":
        "9:16 — stories, reels e TikTok, ecrã de telemóvel inteiro.",
    "16:9 — YouTube, link previews and most horizontal video.":
        "16:9 — YouTube, pré-visualizações de links e a maioria do vídeo horizontal.",
    "3:2 and 4:3 — the native ratios of most cameras and phones, and the right choice for print.":
        "3:2 e 4:3 — as proporções nativas da maioria das câmaras e telemóveis, e a escolha certa para impressão.",
    "Circles are a crop plus transparency": "Os círculos são um recorte mais transparência",
    "A circular crop is not really a crop — an image file is always rectangular. What it produces is a square image whose corners are transparent, which is why the export format matters.":
        "Um recorte circular não é bem um recorte — um ficheiro de imagem é sempre retangular. O que produz é uma imagem quadrada com os cantos transparentes, e é por isso que o formato de exportação importa.",
    "Save a circular crop as PNG or WebP and the corners stay transparent over any background. Save it as JPG and the corners become solid white or black, giving you a circle in a box. This catches people out constantly with avatars.":
        "Guarde um recorte circular em PNG ou WebP e os cantos ficam transparentes sobre qualquer fundo. Guarde-o em JPG e os cantos passam a branco ou preto sólido, dando-lhe um círculo dentro de uma caixa. Isto engana as pessoas constantemente nos avatares.",
    "Composition, briefly": "Composição, em resumo",
    "Two habits improve most crops. Leave space in the direction a subject faces or moves, so the frame does not feel cramped against their gaze. And avoid cropping a person at a joint — the wrist, elbow, knee or ankle — because it reads as an amputation rather than a frame edge; crop mid-limb instead.":
        "Dois hábitos melhoram a maioria dos recortes. Deixe espaço na direção para onde o motivo olha ou se move, para o enquadramento não parecer apertado contra o seu olhar. E evite recortar uma pessoa numa articulação — pulso, cotovelo, joelho ou tornozelo — porque se lê como uma amputação e não como o limite do enquadramento; recorte a meio do membro.",
    "For anything going into a circular avatar slot, compose inside the inscribed circle. Everything in the corners of your square will be discarded by the platform.":
        "Para qualquer coisa destinada a um avatar circular, componha dentro do círculo inscrito. Tudo o que estiver nos cantos do seu quadrado vai ser descartado pela plataforma.",

    # --- /crop/ -------------------------------------------------------------
    "Free Image Crop Tool — Circle, Square & Custom Ratio":
        "Recortar Imagens Grátis — Círculo, Quadrado e Proporção Personalizada",
    "Free Image Crop Tool — Circle, Square, Custom Ratio & Rotate":
        "Recortar Imagens Grátis — Círculo, Quadrado, Proporção Personalizada e Rodar",
    "Crop images free in your browser — square, circle, rounded, 4:5, 16:9, 9:16 or any custom ratio, with rotate, flip and zoom. Nothing leaves your device.":
        "Recorte imagens grátis no seu navegador — quadrado, círculo, cantos arredondados, 4:5, 16:9, 9:16 ou qualquer proporção personalizada, com rodar, espelhar e zoom. Nada sai do seu dispositivo.",
    "Crops locally — nothing is uploaded": "Recorta localmente — nada é carregado",
    "Crop an": "Recortar uma",
    "Square, circle, rounded or any custom ratio — with rotate, flip, zoom and drag. No background removal needed. Export a transparent PNG or a JPG, 100% in your browser.":
        "Quadrado, círculo, cantos arredondados ou qualquer proporção personalizada — com rodar, espelhar, zoom e arrastar. Sem precisar de remover o fundo. Exporte um PNG transparente ou um JPG, 100% no seu navegador.",
    "Drop a photo to crop": "Largue uma foto para recortar",
    "or click to browse — JPG, PNG or WEBP · pick several to crop a batch":
        "ou clique para procurar — JPG, PNG ou WEBP · escolha várias para recortar em lote",
    "Drag the photo to reposition · scroll or use the slider to zoom":
        "Arraste a foto para reposicionar · use a roda ou o cursor para o zoom",
    "Shape": "Forma",
    "Rectangle": "Retângulo",
    "Rounded": "Arredondado",
    "Circle": "Círculo",
    "Ratio": "Proporção",
    "Custom": "Personalizada",
    "ratio": "proporção",
    "Rotate & flip": "Rodar e espelhar",
    "Left": "Esquerda",
    "Right": "Direita",
    "Flip H": "Espelhar H",
    "Flip V": "Espelhar V",
    "Straighten": "Endireitar",
    "Export as": "Exportar como",
    "Next-gen, smallest files (Chromium)": "Nova geração, ficheiros mais pequenos (Chromium)",
    "PNG keeps transparent corners on rounded/circle crops.":
        "O PNG mantém os cantos transparentes nos recortes arredondados e circulares.",
    "Download crop": "Descarregar recorte",
    "Crop any image, right in your browser": "Recorte qualquer imagem, no seu próprio navegador",
    "Circle & rounded": "Círculo e arredondado",
    "Perfect avatars with transparent corners, saved as PNG.":
        "Avatares perfeitos com cantos transparentes, guardados em PNG.",
    "Any ratio": "Qualquer proporção",
    "1:1, 4:5, 16:9, 9:16 or your own custom width : height.":
        "1:1, 4:5, 16:9, 9:16 ou a sua própria largura : altura.",
    "Private": "Privado",
    "No upload and no background removal — the crop runs on your device.":
        "Sem carregamento e sem remoção de fundo — o recorte corre no seu dispositivo.",
    "Upload a photo, pick a shape and ratio, rotate or flip, then drag and zoom to frame it. Download a full-resolution crop as a transparent PNG or a JPG — nothing ever leaves your browser.":
        "Escolha uma foto, defina a forma e a proporção, rode ou espelhe, depois arraste e faça zoom para enquadrar. Descarregue o recorte em resolução total como PNG transparente ou JPG — nada sai do seu navegador.",
    "Each of these has its own guide, with the sizes and rules that apply to it.":
        "Cada um destes tem o seu guia, com os tamanhos e as regras que se lhe aplicam.",
    "Or read the": "Ou leia os",
    "guides": "guias",
    "— explanations of how image formats, compression, metadata and cut-outs actually work.":
        "— explicações de como funcionam realmente os formatos de imagem, a compressão, os metadados e os recortes.",
    "Instagram": "Instagram",
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
        "Remover Objetos de Fotografias — Grátis e no Navegador",
    "Erase unwanted objects, people or blemishes from a photo: brush over them and a content-aware fill blends them away. Free, and nothing is uploaded.":
        "Apague objetos, pessoas ou imperfeições de uma fotografia: pinte por cima e um preenchimento inteligente funde-os com o fundo. Grátis e sem nada carregado.",
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
    "Enlarge images 2× or 4× with high-quality Lanczos resampling and detail sharpening — free and instant, right in your browser. No upload, no sign-up.":
        "Amplie imagens 2× ou 4× com reamostragem Lanczos de alta qualidade e reforço de detalhe — grátis e instantâneo, no navegador. Sem carregamentos, sem registo.",
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
    "Convert iPhone HEIC photos to JPG, PNG or WEBP for free — in your browser, so your photos are never uploaded. Batch convert, download as a ZIP.":
        "Converta fotos HEIC do iPhone para JPG, PNG ou WEBP gratuitamente — no seu navegador, sem as fotos serem carregadas. Converta em lote, descarregue em ZIP.",
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
        "PDF para Imagens — Páginas de PDF em PNG ou JPG, Grátis",
    "Turn every page of a PDF into a sharp PNG or JPG, free and in your browser — the PDF is never uploaded. Download single pages or all as a ZIP.":
        "Transforme cada página de um PDF numa imagem PNG ou JPG nítida, grátis e no seu navegador — o PDF nunca é carregado. Descarregue páginas ou tudo em ZIP.",
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
        "Imagem para Texto (OCR) — Copie Texto de uma Foto, Grátis",
    "Extract and copy text from any photo or screenshot with on-device OCR — free, in your browser, nothing uploaded. No sign-up, no limits.":
        "Extraia e copie texto de qualquer foto ou captura de ecrã com OCR no dispositivo — grátis, no navegador, sem nada carregado. Sem registo, sem limites.",
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
        "Conversor SVG para PNG — Nítido em Qualquer Tamanho, Grátis",
    "Convert SVG to PNG at 1×, 2×, 4× or any exact width — rendered from the vector so edges stay pixel-sharp. Free, in your browser, nothing uploaded.":
        "Converta SVG para PNG a 1×, 2×, 4× ou numa largura exata — gerado do vetor para os contornos ficarem nítidos. Grátis, no navegador, sem nada carregado.",
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
        "Filtros e Ajustes de Fotografia — Editor Online Grátis",
    "Apply one-tap looks and fine-tune brightness, contrast, saturation, warmth, vignette and grain — free, in your browser, nothing uploaded.":
        "Aplique estilos de um toque e afine brilho, contraste, saturação, calor, vinheta e grão — grátis, no seu navegador, sem nada carregado.",
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
    # Stat-strip labels under each number (see the hero badge in index.html).
    "this week": "esta semana",
    "all time": "desde sempre",
    # --- How it works: what actually runs on the device ---
    "Three steps — with no server anywhere in them.":
        "Três passos — sem qualquer servidor pelo meio.",
    "What actually runs on your device": "O que corre mesmo no seu dispositivo",
    "The cut-out comes from IS-Net, a segmentation model that runs through ONNX Runtime Web "
    "inside this browser tab. Your browser downloads the model once, then keeps it — so the "
    "second image is instant, and the tool keeps working with no connection at all.":
        "O recorte vem do IS-Net, um modelo de segmentação que corre através do ONNX Runtime Web "
        "dentro deste separador. O seu navegador transfere o modelo uma vez e guarda-o — por isso "
        "a segunda imagem é instantânea e a ferramenta continua a funcionar sem qualquer ligação.",
    "Where your browser exposes WebGPU, the model runs on your graphics card and off the main "
    "thread, which is why the page stays responsive while it works. Everywhere else it falls "
    "back to WebAssembly with SIMD and multiple threads on the CPU. Browsers that allow "
    "cross-origin isolation get the full-precision weights; the rest get a smaller quantised "
    "build of the same model.":
        "Quando o navegador disponibiliza WebGPU, o modelo corre na placa gráfica e fora da "
        "thread principal, e é por isso que a página continua a responder enquanto trabalha. Nos "
        "restantes casos recorre a WebAssembly com SIMD e várias threads no CPU. Os navegadores "
        "que permitem isolamento de origem recebem os pesos em precisão total; os outros recebem "
        "uma versão quantizada, mais pequena, do mesmo modelo.",
    "What that means for your device: the first run is a real download and needs some memory, "
    "so it takes a few seconds on a recent laptop or phone and can take up to a minute on an "
    "older one. Every run after that is fast. If your browser can't run the model at all, the "
    "page says so plainly instead of hanging — and the editing tools that don't need AI (crop, "
    "convert, compress, resize) keep working regardless.":
        "O que isso significa para o seu dispositivo: a primeira utilização é mesmo uma "
        "transferência e precisa de alguma memória, por isso demora alguns segundos num portátil "
        "ou telemóvel recente e pode demorar até um minuto num mais antigo. Todas as seguintes "
        "são rápidas. Se o seu navegador não conseguir mesmo correr o modelo, a página diz-lho "
        "claramente em vez de ficar bloqueada — e as ferramentas que não precisam de IA (recortar, "
        "converter, comprimir, redimensionar) continuam a funcionar.",
    "None of this involves an upload: there is no queue to wait in, no per-image limit to hit, "
    "and no copy of your photo on a server to trust anyone with.":
        "Nada disto envolve um carregamento: não há fila de espera, não há limite por imagem e não "
        "há nenhuma cópia da sua fotografia num servidor que tenha de confiar a alguém.",
    "Check it yourself:": "Confirme você mesmo:",
    "once you have made a single cut-out, turn off your Wi-Fi and reload this page. Every tool "
    "keeps working — the background remover included — because the page, the tools and the model "
    "are already on your device. Nothing else you have tried this in will survive that test.":
        "depois de fazer um único recorte, desligue o Wi-Fi e recarregue esta página. Todas as "
        "ferramentas continuam a funcionar — incluindo a remoção de fundo — porque a página, as "
        "ferramentas e o modelo já estão no seu dispositivo. Mais nenhum serviço onde tenha "
        "experimentado isto sobrevive a esse teste.",
    # --- Why is it free? ---
    "Why is it free?": "Porque é gratuito?",
    "The usual catch is that you are the product. Here is the actual arrangement.":
        "Normalmente, a armadilha é que o produto é você. Aqui fica o acordo real.",
    "Your device does the work": "O trabalho é feito pelo seu dispositivo",
    "Cloud removers rent GPUs by the second and bill you per image. Nothing here runs on a "
    "server, so there is no per-image cost to pass on — and no reason to cap you at five free "
    "photos.":
        "Os serviços na nuvem alugam GPUs ao segundo e cobram por imagem. Aqui nada corre num "
        "servidor, por isso não há custo por imagem para lhe passar — nem motivo para o limitar a "
        "cinco fotografias grátis.",
    "There is nothing to sell": "Não há nada para vender",
    "Your images never leave the browser, so we could not train on them, sell them or leak them "
    "even if we wanted to. There is no account, so there is no profile to build either.":
        "As suas imagens nunca saem do navegador, por isso não poderíamos treinar com elas, "
        "vendê-las ou deixá-las escapar mesmo que quiséssemos. Não há conta, por isso também não "
        "há perfil para construir.",
    "What keeps it running": "O que o mantém no ar",
    "A domain and some cheap hosting — that is the whole bill. Ads on the written guides help "
    "cover it, the tool pages stay ad-free, and a coffee from anyone who finds this useful "
    "covers the rest.":
        "Um domínio e alojamento barato — a conta é essa. Os anúncios nos guias escritos ajudam a "
        "pagá-la, as páginas das ferramentas ficam sem anúncios, e um café de quem achar isto útil "
        "cobre o resto.",
    "No trial, no credit card, no watermark, no “pro” tier holding the good export hostage.":
        "Sem período experimental, sem cartão de crédito, sem marca de água e sem versão “pro” a "
        "reter a exportação boa como refém.",
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
    "Free Background Remover — No Upload, No Signup, No Watermark":
        "Removedor de Fundo Grátis — Sem Upload, Sem Registo, Sem Marca de Água",
    "Remove image backgrounds free and unlimited — your photo never leaves your device. No upload, no sign-up, no watermark, full resolution.":
        "Remova fundos de imagens grátis e sem limites — a sua foto nunca sai do seu dispositivo. Sem upload, sem registo, sem marca de água, resolução total.",
    "Free Background Remover": "Removedor de Fundo Grátis",
    "No Upload Required": "Sem Upload Necessário",
    "Remove image backgrounds automatically in seconds. 100% free, unlimited and private — your images never leave your device.":
        "Remova fundos de imagens automaticamente em segundos. 100% gratuito, ilimitado e privado — as suas imagens nunca saem do seu dispositivo.",
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
    # --- Resizer + EXIF remover (tool pages translated in 1.11) ---
    'Free Image Resizer — Resize Photos by Pixels or Percentage':
        'Redimensionar Imagens Grátis — Por Píxeis ou Percentagem',
    'Resize any image to exact pixels or a percentage, free and in your browser. Lock the aspect ratio, pick a preset, and export JPG, PNG or WEBP.':
        'Redimensione qualquer imagem para píxeis exatos ou uma percentagem, grátis e no seu navegador. Bloqueie a proporção, escolha uma predefinição e exporte JPG, PNG ou WEBP.',
    'Free Image Resizer — Exact Pixels, Private':
        'Redimensionar Imagens Grátis — Píxeis Exatos, Privado',
    'Made locally — nothing is uploaded': 'Feito localmente — nada é carregado',
    'Resizer': 'Redimensionador',
    'Resize any photo to exact': 'Redimensione qualquer fotografia para',
    'pixels': 'píxeis exatos',
    'or a': 'ou uma',
    'percentage': 'percentagem',
    '— aspect ratio locked so nothing stretches. Free, full quality and 100% private.':
        '— com a proporção bloqueada para nada ficar esticado. Grátis, com qualidade total e 100% privado.',
    'or click to browse — JPG, PNG or WEBP · pick several to resize a batch':
        'ou clique para procurar — JPG, PNG ou WEBP · escolha várias para redimensionar um lote',
    'Width': 'Largura',
    'Height': 'Altura',
    'Lock aspect ratio': 'Bloquear proporção',
    'Fit within': 'Caber em',
    'Same': 'Igual',
    'New': 'Nova',
    'Resize in three steps': 'Redimensionar em três passos',
    "Any JPG, PNG or WEBP — it's read straight in your browser.":
        'Qualquer JPG, PNG ou WEBP — é lido diretamente no seu navegador.',
    'Set the size': 'Defina o tamanho',
    'Type exact pixels, pick a percentage, or fit within a preset. Aspect ratio stays locked.':
        'Escreva os píxeis exatos, escolha uma percentagem ou caiba numa predefinição. A proporção mantém-se bloqueada.',
    'Export JPG, PNG or WEBP at the new size — free, no watermark.':
        'Exporte JPG, PNG ou WEBP no novo tamanho — grátis e sem marca de água.',
    'Free EXIF Remover — View & Remove Photo Metadata (GPS)':
        'Removedor de EXIF Grátis — Ver e Remover Metadados (GPS)',
    'See and remove the hidden metadata in your photos — GPS location, camera, date and more. Strips EXIF losslessly, in your browser, nothing uploaded.':
        'Veja e remova os metadados escondidos nas suas fotografias — localização GPS, câmara, data e mais. Remove EXIF sem perdas, no seu navegador, sem carregar nada.',
    'EXIF Remover — Strip Photo Metadata & GPS, Free & Private':
        'Removedor de EXIF — Apague Metadados e GPS, Grátis e Privado',
    'Read locally — nothing is uploaded': 'Lido localmente — nada é carregado',
    'EXIF & Metadata': 'EXIF e Metadados',
    'Remover': 'Removedor',
    'See the hidden data in your photos —': 'Veja os dados escondidos nas suas fotografias —',
    'GPS location': 'localização GPS',
    ', camera, date — and strip it out before you share. Lossless, free and 100% private.':
        ', câmara, data — e apague-os antes de partilhar. Sem perdas, grátis e 100% privado.',
    'or click to browse — JPG photos carry the most hidden data · pick several to clean a batch':
        'ou clique para procurar — as fotografias JPG são as que escondem mais dados · escolha várias para limpar um lote',
    'No photo handy?': 'Não tem nenhuma fotografia à mão?',
    'Try a sample photo': 'Experimente uma fotografia de exemplo',
    '— a real JPEG with GPS and camera data inside.':
        '— um JPEG real com dados de GPS e da câmara lá dentro.',
    'Location data found': 'Foram encontrados dados de localização',
    'All metadata': 'Todos os metadados',
    'Download clean copy': 'Descarregar cópia limpa',
    'New photo': 'Nova fotografia',
    "What's hiding in your photos": 'O que se esconde nas suas fotografias',
    'Phones tag photos with the exact coordinates they were taken — often your home. Strip it before posting.':
        'Os telemóveis marcam as fotografias com as coordenadas exatas onde foram tiradas — muitas vezes a sua casa. Apague-as antes de publicar.',
    'Date & device': 'Data e dispositivo',
    'The exact timestamp, camera and even the software used are all embedded in the file.':
        'A hora exata, a câmara e até o software usado estão todos embutidos no ficheiro.',
    'Lossless & private': 'Sem perdas e privado',
    'JPEGs are cleaned losslessly with zero quality loss, and nothing ever leaves your device.':
        'Os JPEG são limpos sem qualquer perda de qualidade, e nada sai do seu dispositivo.',
    'Why this one runs on your device': 'Porque é que esta ferramenta corre no seu dispositivo',
    "You can check this yourself: open your browser's network panel, run the tool, and watch it stay silent. Or turn off your Wi-Fi — the tool keeps working.":
        'Pode confirmar por si: abra o painel de rede do navegador, use a ferramenta e veja que fica em silêncio. Ou desligue o Wi-Fi — a ferramenta continua a funcionar.',
    "Resize your": "Redimensionar as suas",
    "Photos": "Fotografias",
    "Remove EXIF &": "Remover EXIF e",
    "Metadata": "Metadados",
    # --- Converter + compressor (translated in 1.11) ---
    'Free Image Converter — PNG, JPG & WEBP in Your Browser':
        'Conversor de Imagens Grátis — PNG, JPG e WEBP no Navegador',
    'Convert images between PNG, JPG and WEBP for free. Auto-detects the input format and converts locally in your browser — no uploads, batch supported.':
        'Converta imagens entre PNG, JPG e WEBP gratuitamente. Deteta o formato de origem e converte localmente no seu navegador — sem carregamentos e com lotes.',
    'Free Image Format Converter — Private & Instant':
        'Conversor de Formatos Grátis — Privado e Instantâneo',
    'Convert locally — nothing is uploaded': 'Convertido localmente — nada é carregado',
    'Convert Images to': 'Converta Imagens para',
    'Any Format': 'Qualquer Formato',
    'Drop any image — we detect its format automatically. Pick a target format and download instantly. Batch supported, full quality, 100% private.':
        'Largue qualquer imagem — detetamos o formato automaticamente. Escolha o formato de destino e descarregue de imediato. Com lotes, qualidade total e 100% privado.',
    'Detects PNG, JPG, WEBP, GIF, BMP & more · Converts to PNG, JPG, WEBP or AVIF':
        'Deteta PNG, JPG, WEBP, GIF, BMP e mais · Converte para PNG, JPG, WEBP ou AVIF',
    'Convert to': 'Converter para',
    'Supported output formats': 'Formatos de saída suportados',
    'Converting…': 'A converter…',
    'Compress Images Free — Shrink JPG, PNG & WEBP In-Browser':
        'Comprimir Imagens Grátis — Reduza JPG, PNG e WEBP no Navegador',
    'Compress and shrink images for free — reduce JPG, PNG and WEBP file size with a quality slider or a target size. In your browser, batch supported.':
        'Comprima e reduza imagens gratuitamente — diminua o tamanho de JPG, PNG e WEBP com um cursor de qualidade ou um tamanho alvo. No seu navegador e com lotes.',
    'Free Image Compressor — Shrink Images Privately & Instantly':
        'Compressor de Imagens Grátis — Reduza de Forma Privada e Instantânea',
    'Compress Images to a': 'Comprima Imagens para um',
    'Smaller Size': 'Tamanho Menor',
    'Drop an image and shrink its file size — set a quality level or a target size like':
        'Largue uma imagem e reduza o tamanho do ficheiro — defina um nível de qualidade ou um tamanho alvo como',
    'under 200 KB': 'menos de 200 KB',
    '. Batch supported, full control, 100% private.':
        '. Com lotes, controlo total e 100% privado.',
    'Shrinks JPG, PNG & WEBP · Choose a quality or a target file size':
        'Reduz JPG, PNG e WEBP · Escolha uma qualidade ou um tamanho alvo',
    'Quality': 'Qualidade',
    'Target size': 'Tamanho alvo',
    'Max dimension': 'Dimensão máxima',
    'How to compress an image': 'Como comprimir uma imagem',
    'Drop your images': 'Largue as suas imagens',
    'Add one or many — JPG, PNG or WEBP. Everything stays on your device.':
        'Adicione uma ou várias — JPG, PNG ou WEBP. Tudo fica no seu dispositivo.',
    'Pick quality or size': 'Escolha qualidade ou tamanho',
    'Slide the quality, or set a target like “under 200 KB” and we hit it automatically.':
        'Ajuste a qualidade, ou defina um alvo como “menos de 200 KB” e nós chegamos lá automaticamente.',
    'Grab the smaller file, or download them all as a ZIP. No watermark, no sign-up.':
        'Leve o ficheiro mais pequeno, ou descarregue tudo num ZIP. Sem marca de água e sem registo.',
    'Compressing…': 'A comprimir…',
}


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
    "No file chosen": "Nenhum ficheiro escolhido",
    "That is not a .docx file": "Esse não é um ficheiro .docx",
    "That file could not be read as a Word document": "Não foi possível ler esse ficheiro como documento do Word",
    "This is an old .doc file. Open it in Word and save as .docx first.":
        "Este é um ficheiro .doc antigo. Abra-o no Word e guarde primeiro como .docx.",
    "{n} row": "{n} linha",
    "{n} rows": "{n} linhas",
    "{n} column": "{n} coluna",
    "{n} columns": "{n} colunas",
    "{n} file": "{n} ficheiro",
    "{n} files": "{n} ficheiros",
    "{n} word": "{n} palavra",
    "Drop a CSV file": "Largue um ficheiro CSV",
    "Drop an Excel file": "Largue um ficheiro Excel",
    "or click to browse — .csv or .tsv": "ou clique para procurar — .csv ou .tsv",
    "or click to browse — .xlsx": "ou clique para procurar — .xlsx",
    "Download .xlsx": "Descarregar .xlsx",
    "Download .csv": "Descarregar .csv",
    "Could not read that CSV file": "Não foi possível ler esse ficheiro CSV",
    "Could not read that Excel file": "Não foi possível ler esse ficheiro Excel",
    "That file has no rows": "Esse ficheiro não tem linhas",
    "Preview shows the first rows and columns only — the whole file is converted.":
        "A pré-visualização mostra apenas as primeiras linhas e colunas — o ficheiro é convertido por inteiro.",
    "Conversion failed": "A conversão falhou",
    "Excel file ready": "Ficheiro Excel pronto",
    "CSV ready — import it in Google Sheets with File → Import":
        "CSV pronto — importe-o no Google Sheets em Ficheiro → Importar",
    "Drop your PDFs": "Largue os seus PDFs",
    "Drop a PDF to split": "Largue um PDF para dividir",
    "or click to browse — add as many as you like":
        "ou clique para procurar — adicione quantos quiser",
    "or click to browse — one file": "ou clique para procurar — um ficheiro",
    "Merge into one PDF": "Juntar num só PDF",
    "Split into separate PDFs": "Dividir em PDFs separados",
    "Could not read {name} — it may be password-protected":
        "Não foi possível ler {name} — pode estar protegido por palavra-passe",
    "Leave empty to get every page as its own PDF.":
        "Deixe vazio para obter cada página como um PDF próprio.",
    "Not a valid range: ": "Intervalo inválido: ",
    "Add at least two PDFs to merge": "Adicione pelo menos dois PDFs para juntar",
    "Merged PDF ready": "PDF juntado pronto",
    "No pages selected": "Nenhuma página selecionada",
    "Split PDF ready": "PDF dividido pronto",
    "Remove": "Remover",
    "This PDF has no text — it is probably a scan. Try the Image to Text tool.":
        "Este PDF não tem texto — é provavelmente uma digitalização. Experimente a ferramenta Imagem para Texto.",
    "Word document ready": "Documento Word pronto",
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
    "Added to pack": "Adicionado ao pacote",
    "Pack downloaded": "Pacote transferido",
    "Background removed": "Fundo removido",
    # Live status on the result card while a cut-out is being made.
    "Removing background…": "A remover o fundo…",
    "Downloading AI model… {pct}%": "A descarregar o modelo de IA… {pct}%",
    # --- Model status badge (app.js ModelStatus) ---
    "Loading the AI": "A carregar a IA",
    "one-time": "uma única vez",
    "AI ready — GPU-accelerated, runs 100% on your device":
        "IA pronta — acelerada por GPU, corre 100% no seu dispositivo",
    "AI ready — runs 100% on your device": "IA pronta — corre 100% no seu dispositivo",
    "first image may take a little longer here":
        "a primeira imagem pode demorar um pouco mais aqui",
    "Could not preload the AI here — it will try again when you add an image":
        "Não foi possível pré-carregar a IA aqui — tentará de novo quando adicionar uma imagem",
    # --- Support nudge (kit.js showSupport) ---
    "Everything here stays free. If it saved you some time, a coffee helps keep it that way.":
        "Aqui tudo continua gratuito. Se lhe poupou tempo, um café ajuda a que assim continue.",
    "Buy me a coffee": "Pague-me um café",
    "Dismiss": "Dispensar",
    # Shown on cards waiting their turn in the batch queue, with a rough ETA
    # measured from how fast this device actually works.
    "Next up": "A seguir",
    "#{n} in line": "{n}.º na fila",
    "about {n}s": "cerca de {n}s",
    "about {m}m": "cerca de {m}min",
    "about {m}m {s}s": "cerca de {m}min {s}s",
    "GPU acceleration failed — reload the page to switch to CPU mode":
        "A aceleração por GPU falhou — recarregue a página para mudar para o modo CPU",
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
    # --- Share sheet (kit.js) ---
    "Share": "Partilhar",
    "Ready to share:": "Pronto a partilhar:",
    # Rides along as the caption where the target app accepts one, so it is the
    # one piece of copy here that a stranger reads. Kept to a plain statement of
    # where the image came from — anything more is a caption the user did not
    # write, on a message they did.
    "Made with clearbg.pt": "Feito com clearbg.pt",
    "Could not open the share sheet": "Não foi possível abrir a partilha",
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
    # --- PWA install offer ---
    'Install ClearBG to keep these tools one tap away — they work offline too.':
        'Instale o ClearBG para ter estas ferramentas a um toque — funcionam também offline.',
    'Install': 'Instalar',
}


# --- Landing-page (use-case) copy, fully translated --------------------------
# Keyed by slug; only the translated fields are stored and merged over the
# English source in localize_use_case().
USE_CASES = {
    "product-photos": {
        "nav": "Fotos de produtos",
        "title": "Remover Fundo de Fotos de Produtos — Grátis e Instantâneo",
        "description": "Crie fotos de produtos limpas, em branco ou transparentes, para a sua loja online. Grátis e ilimitado — a IA corre no seu navegador, nada é carregado.",
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
            {"icon": "fa-swatchbook", "title": "Qualquer cor de fundo", "text": "Combine com uma paleta de marca ou um fundo de estúdio liso, e exporte em PNG, JPG ou WEBP."},
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
        "description": "Transforme uma foto ou digitalização da sua assinatura manuscrita num PNG transparente para documentos e contratos. Grátis — corre no seu navegador.",
        "h1": "Crie uma Assinatura Transparente",
        "tagline": "Transforme uma digitalização ou foto da sua assinatura manuscrita num PNG transparente e limpo para contratos e documentos.",
        "intro": [
            "Assine uma folha de papel em branco, fotografe ou digitalize, e largue-a aqui. A IA remove o fundo de papel e deixa apenas a tinta como um PNG transparente que pode colocar em qualquer PDF ou documento.",
            "Como todo o processo corre no seu navegador, a sua assinatura — uma informação sensível — nunca é carregada para um servidor.",
        ],
        "benefits": [
            {"icon": "fa-stamp", "title": "Pronto para documentos", "text": "Obtenha tinta transparente que pode colocar diretamente em PDFs, contratos e cartas."},
            {"icon": "fa-shield-halved", "title": "Mantido privado", "text": "A sua assinatura nunca sai do seu dispositivo — nada é enviado para lado nenhum."},
            {"icon": "fa-wand-magic-sparkles", "title": "Isolamento limpo", "text": "Separa a tinta da textura do papel e das sombras, com um pincel para refinar o resultado."},
        ],
    },
    "car-photos": {
        "nav": "Fotos de carros",
        "title": "Remover Fundo de Fotos de Carros — Grátis e Instantâneo",
        "description": "Remova o fundo de fotos de carros para anúncios de stands e marketplaces. Coloque qualquer veículo sobre branco ou transparente — grátis, no navegador.",
        "h1": "Remova Fundos de Fotos de Carros",
        "tagline": "Dê a cada veículo uma foto de anúncio limpa e consistente para o seu stand ou marketplace — grátis, ilimitado e processado no seu dispositivo.",
        "intro": [
            "Os anúncios de carros vendem mais depressa quando cada veículo surge sobre um fundo limpo e consistente em vez de um stand desarrumado. Esta ferramenta corta o fundo das suas fotos de carros em segundos.",
            "Como a IA corre localmente no seu navegador, pode processar todo o stock sem carregar uma única foto, sem limites de API e sem pagar por imagem.",
        ],
        "benefits": [
            {"icon": "fa-square-full", "title": "Limpo como um showroom", "text": "Troque um stand desarrumado por um fundo de estúdio impecável que mantém o foco no carro."},
            {"icon": "fa-layer-group", "title": "Lotes inteiros", "text": "Coloque dezenas de fotos de uma vez e descarregue-as juntas num ZIP."},
            {"icon": "fa-clock", "title": "Instantâneo e grátis", "text": "Sem custo por foto e sem marca de água — resolução total sempre."},
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
            {"icon": "fa-store", "title": "Vendável em segundos", "text": "Recortes limpos de tops, vestidos e sapatos que ficam bem em qualquer grelha de loja."},
            {"icon": "fa-bookmark", "title": "Anúncios consistentes", "text": "Dê a cada peça o mesmo fundo limpo para uma montra profissional."},
            {"icon": "fa-shield-halved", "title": "Privado por design", "text": "As suas fotos nunca saem do seu dispositivo — nada é carregado para um servidor."},
        ],
    },
    "pet-photos": {
        "nav": "Fotos de animais",
        "title": "Remover Fundo de Fotos de Animais — Grátis e Privado",
        "description": "Recorte o seu cão, gato ou qualquer animal de uma foto grátis. Crie PNGs transparentes para autocolantes, impressões e memes — no seu navegador.",
        "h1": "Remova o Fundo de Fotos de Animais",
        "tagline": "Recorte o seu cão, gato ou amigo peludo para autocolantes, impressões, canecas e memes — grátis, ilimitado e tudo no seu navegador.",
        "intro": [
            "Quer o seu animal numa caneca, num autocolante ou numa impressão personalizada? Carregue uma foto e a IA separa o seu cão ou gato do fundo — lidando com pelo e bigodes — para obter um PNG transparente e limpo.",
            "Tudo acontece no seu dispositivo, por isso pode experimentar quantas fotos quiser — sem carregamentos, sem limites e sem marca de água.",
        ],
        "benefits": [
            {"icon": "fa-brush", "title": "Ótimo com pelo", "text": "Preparado para lidar com contornos suaves, pelo e bigodes para um recorte natural."},
            {"icon": "fa-wand-magic-sparkles", "title": "Refine à mão", "text": "Limpe fundo restante ou restaure detalhes finos com o pincel de contorno integrado."},
            {"icon": "fa-note-sticky", "title": "Pronto para impressão e autocolantes", "text": "PNGs transparentes em resolução total para canecas, autocolantes, impressões e memes."},
        ],
    },
    "youtube-thumbnail": {
        "nav": "Miniaturas de YouTube",
        "title": "Remover Fundo para Miniaturas de YouTube — Grátis e Ilimitado",
        "description": "Recorte-se para uma miniatura de YouTube — grátis, ilimitado e em resolução total. Sem registo, sem marca de água, sem carregamentos: a IA corre no seu navegador.",
        "h1": "Remova Fundos para Miniaturas de YouTube",
        "tagline": "Recorte-se a si ou ao seu assunto de forma limpa e coloque sobre um fundo forte para miniaturas que geram cliques — grátis e ilimitado.",
        "intro": [
            "As melhores miniaturas colocam um recorte nítido de uma pessoa ou produto sobre um fundo impactante. Carregue a sua foto e a IA remove o fundo em segundos, dando-lhe um PNG transparente para compor no seu editor de miniaturas.",
            "Corre inteiramente no seu navegador em resolução total, para os criadores produzirem miniaturas rapidamente — sem carregamentos, sem subscrições e sem marca de água.",
        ],
        "benefits": [
            {"icon": "fa-camera", "title": "Feito para criadores", "text": "Recortes limpos de si ou do seu assunto para se destacarem sobre qualquer fundo de miniatura."},
            {"icon": "fa-clock", "title": "Rápido", "text": "Remove o fundo em segundos para publicar a miniatura e carregar em publicar."},
            {"icon": "fa-crop-simple", "title": "Qualidade total", "text": "PNGs transparentes em resolução total, sem marca de água, prontos para qualquer editor."},
        ],
    },
    "ebay": {
        "nav": "Anúncios eBay",
        "title": "Remover Fundo de Fotos eBay — Grátis e Instantâneo",
        "description": "Dê aos seus anúncios eBay fundos brancos ou transparentes gratuitamente. Faça os artigos parecerem profissionais — ilimitado, no seu navegador.",
        "h1": "Remova Fundos de Fotos eBay",
        "tagline": "Transforme fotos de telemóvel desarrumadas em fotos de anúncio eBay limpas e profissionais — grátis, ilimitado e processado no seu dispositivo.",
        "intro": [
            "Anúncios com fotos limpas e consistentes ganham mais cliques e vendem mais depressa. Largue uma foto do seu artigo e a IA remove o fundo desarrumado, para colocar branco puro — o aspeto em que os compradores confiam.",
            "Como a IA corre localmente no seu navegador, pode preparar um inventário inteiro sem carregar uma única foto, sem limites de API e sem pagar por imagem.",
        ],
        "benefits": [
            {"icon": "fa-bookmark", "title": "Venda mais depressa", "text": "Fundos brancos limpos tornam os artigos profissionais e criam confiança no comprador."},
            {"icon": "fa-layer-group", "title": "Inventário em lote", "text": "Coloque dezenas de artigos de uma vez e descarregue-os juntos num ZIP."},
            {"icon": "fa-circle-check", "title": "Grátis e ilimitado", "text": "Sem custo por foto e sem marca de água — resolução total sempre."},
        ],
    },
    "discord-pfp": {
        "nav": "Avatares Discord",
        "title": "Removedor de Fundo para Foto de Perfil de Discord — Grátis",
        "description": "Crie uma foto de perfil de Discord limpa removendo o fundo da sua foto ou avatar. PNGs transparentes grátis para qualquer cor — no seu navegador.",
        "h1": "Remova o Fundo da Sua Foto de Perfil de Discord",
        "tagline": "Recorte-se a si ou à sua personagem de forma limpa para um avatar de Discord nítido — grátis, ilimitado e tudo no seu navegador.",
        "intro": [
            "Uma foto de perfil limpa destaca a sua presença no Discord. Carregue uma foto, selfie ou arte e a IA isola o assunto, para o manter transparente ou colocar qualquer cor sólida ou gradiente antes de recortar em círculo.",
            "Tudo acontece no seu dispositivo, por isso pode experimentar quantos estilos quiser — sem carregamentos, sem limites e sem marca de água.",
        ],
        "benefits": [
            {"icon": "fa-user", "title": "Avatares nítidos", "text": "Recortes limpos que se leem bem mesmo no tamanho pequeno de avatar do Discord."},
            {"icon": "fa-swatchbook", "title": "Qualquer cor ou gradiente", "text": "Coloque o seu recorte sobre uma cor sólida, gradiente ou fundo desfocado, e recorte em círculo."},
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
            {"icon": "fa-wand-magic-sparkles", "title": "Sem chroma key", "text": "Obtenha um recorte limpo de qualquer foto — sem chroma key nem estúdio."},
            {"icon": "fa-images", "title": "Painéis e emotes", "text": "PNGs transparentes prontos para overlays, painéis, horários e arte de emotes."},
            {"icon": "fa-crop-simple", "title": "Qualidade total", "text": "Exportações em resolução total, sem marca de água, para qualquer ferramenta de layout de streaming."},
        ],
    },
}


# --- FAQ translations for the translated tool pages ---------------------------
# Keyed by the English question (the seo_content source of truth); each value is
# the (question, answer) pair in Portuguese. localize_faqs() swaps them in on
# /pt/ pages — for both the visible accordion and the FAQPage JSON-LD, which
# render from the same list.
FAQS = {
    # --- /crop/ -------------------------------------------------------------
    "Is this image cropper free and private?":
        ("Este recortador de imagens é grátis e privado?",
         "Sim — é completamente gratuito, sem marca de água nem registo, e o recorte acontece inteiramente no seu navegador, pelo que a sua foto nunca é carregada."),
    "How do I crop an image to a circle?":
        ("Como recorto uma imagem num círculo?",
         "Escolha a forma circular e a ferramenta aplica uma máscara à sua foto num círculo perfeito, com os cantos transparentes. Exporte em PNG para manter a transparência — em JPG os cantos ficam brancos, porque o formato JPG não suporta transparência."),
    "Can I crop to a specific aspect ratio?":
        ("Posso recortar numa proporção específica?",
         "Sim. Escolha uma proporção pré-definida como 1:1, 4:5, 16:9 ou 9:16, ou introduza a sua própria largura:altura. A caixa de recorte fica fixa nessa proporção enquanto arrasta e faz zoom, para que o enquadramento nunca a desrespeite."),
    "Does cropping reduce the image resolution?":
        ("O recorte reduz a resolução da imagem?",
         "Nunca há ampliação. O ficheiro é exportado na resolução nativa da região recortada, pelo que mantém todos os pixels dentro do recorte com a qualidade original."),
    "Can I rotate or flip while cropping?":
        ("Posso rodar ou espelhar durante o recorte?",
         "Sim — rode em passos de 90° e espelhe na horizontal ou na vertical antes de exportar, para que uma foto tirada de lado saia na orientação correta."),
    "What format should I export a cropped image as?":
        ("Em que formato devo exportar uma imagem recortada?",
         "Use PNG em recortes circulares ou arredondados, para preservar os cantos transparentes. Use JPG para um ficheiro mais pequeno quando não precisa de transparência, ou AVIF para os ficheiros menores em navegadores Chromium."),

    # Home — trust questions ("what's the catch", the tech, the device)
    "What's the catch — how can it be free and unlimited?":
        ("Qual é a armadilha — como pode ser gratuito e ilimitado?",
         "A parte cara é feita pelo seu dispositivo. As ferramentas na nuvem alugam GPUs ao segundo e cobram por imagem, por isso têm de o limitar; aqui o modelo corre no seu navegador, logo uma imagem extra não custa nada a ninguém. A conta toda é um domínio e alojamento barato, pagos pelos anúncios nos guias escritos (as páginas das ferramentas ficam sem anúncios) e por um café ocasional. Não há conta, período experimental nem venda adicional, porque não há nada para vender."),
    "Which AI model does it use, and where does it run?":
        ("Que modelo de IA usa e onde corre?",
         "IS-Net, um modelo de segmentação, através do ONNX Runtime Web dentro do separador do seu navegador. Quando há WebGPU, corre na placa gráfica e fora da thread principal; caso contrário usa WebAssembly com SIMD e várias threads no CPU. Os navegadores com isolamento de origem recebem os pesos em precisão total, os outros uma versão quantizada mais pequena. O modelo é transferido uma vez e fica em cache, por isso as utilizações seguintes funcionam offline."),
    "What does my device need, and why is the first image slow?":
        ("De que precisa o meu dispositivo e porque é que a primeira imagem é lenta?",
         "De qualquer navegador moderno num dispositivo com alguma memória livre. A primeira utilização transfere o modelo uma vez — é essa a espera que nota — e tudo o resto é rápido porque fica em cache. Um portátil ou telemóvel recente demora alguns segundos por imagem; um dispositivo mais antigo pode demorar até um minuto e usa o modelo mais pequeno. Se o seu navegador não conseguir correr o modelo, a página avisa-o em vez de ficar bloqueada, e as ferramentas que não precisam de IA (recortar, converter, comprimir, redimensionar) continuam a funcionar."),
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
         "Estão disponíveis português, inglês, espanhol, francês e alemão, e o motor descarrega o pacote do idioma escolhido na primeira utilização — depois fica em cache e funciona offline."),
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
    # --- Resizer + EXIF remover ---
    'Is this image resizer free?':
        ('Este redimensionador de imagens é gratuito?',
         'Sim — gratuito, ilimitado, sem marca de água e sem registo. Redimensione quantas imagens quiser.'),
    'Will resizing reduce quality?':
        ('Redimensionar reduz a qualidade?',
         'Tornar uma imagem mais pequena mantém-na nítida. Aumentar para além do tamanho original pode ficar suave, porque não há detalhe extra para acrescentar — os melhores resultados vêm de reduzir.'),
    'Can I keep the aspect ratio?':
        ('Posso manter a proporção?',
         'Sim. Bloqueie a proporção e alterar a largura atualiza a altura automaticamente, para a imagem nunca ficar esticada; desbloqueie para definir dimensões exatas.'),
    'Is my image uploaded?':
        ('A minha imagem é carregada?',
         'Não — o redimensionamento acontece inteiramente no seu navegador, por isso as suas imagens nunca saem do seu dispositivo.'),
    'What is EXIF / photo metadata?':
        ('O que são EXIF / metadados de fotografia?',
         'Dados escondidos que a sua câmara ou telemóvel guarda dentro de uma fotografia — localização GPS, a data e hora exatas e o modelo do dispositivo. Viajam com o ficheiro quando o partilha.'),
    'Is removing it private?':
        ('A remoção é privada?',
         'Sim — a fotografia é lida e limpa inteiramente no seu navegador e nunca é carregada, por isso até fotografias privadas com geoetiqueta ficam no seu dispositivo.'),
    'Does removing metadata reduce quality?':
        ('Remover os metadados reduz a qualidade?',
         'Não. Nos JPEG os metadados são removidos sem perdas — os dados da imagem ficam intactos, por isso não há qualquer perda de qualidade.'),
    'Why remove location data before sharing?':
        ('Porquê remover os dados de localização antes de partilhar?',
         'As fotografias com geoetiqueta revelam exatamente onde foram tiradas — muitas vezes a sua casa. Apagar a etiqueta GPS antes de publicar protege a sua privacidade.'),
    # --- Converter + compressor ---
    'Will converting reduce my image quality?':
        ('Converter reduz a qualidade da imagem?',
         'Converter para um formato sem perdas como PNG mantém todos os píxeis intactos. Converter para um formato com perdas (JPG, WEBP ou AVIF) volta a codificar a imagem, por isso pode haver uma pequena alteração de qualidade, mas mantém a resolução original completa — nada é reduzido.'),
    'Does converting to PNG add transparency to a JPG?':
        ('Converter para PNG acrescenta transparência a um JPG?',
         'Não. Converter um JPG para PNG muda o contentor, mas não pode inventar uma transparência que não existia no original — um JPG tem fundo sólido. Para tornar um fundo transparente precisa do nosso removedor de fundos, que recorta primeiro o assunto.'),
    'Are my images uploaded to a server?':
        ('As minhas imagens são carregadas para um servidor?',
         'Não. A conversão corre inteiramente no seu navegador através da API de canvas, por isso as suas imagens nunca saem do dispositivo. Não há limites de carregamento nem custo por ficheiro.'),
    'Can I convert several images at once?':
        ('Posso converter várias imagens de uma vez?',
         'Sim. Largue um lote de imagens, escolha o formato de saída e descarregue-as juntas — todas processadas localmente, uma a seguir à outra.'),
    'How does image compression reduce file size?':
        ('Como é que a compressão reduz o tamanho do ficheiro?',
         'A compressão volta a codificar a imagem com uma qualidade mais baixa e, nas fotografias, descarta detalhe fino que o olho quase não nota. Esta ferramenta deixa-o trocar um pouco de qualidade por um ficheiro muito menor, e mostra o tamanho antes e depois para encontrar o ponto certo.'),
    'Will compressing make my image look bad?':
        ('Comprimir vai estragar o aspeto da imagem?',
         'Não se escolher um nível de qualidade sensato. Entre 70% e 85% a maioria das fotografias fica igual ao original enquanto o ficheiro encolhe 60% a 80%. Pode pré-visualizar o resultado e ajustar o cursor antes de descarregar.'),
    "What's the best format to compress to?":
        ('Qual é o melhor formato para comprimir?',
         'Para fotografias, WEBP ou AVIF costumam dar o ficheiro mais pequeno com a mesma qualidade visual, seguidos do JPG. Para gráficos com cores planas ou transparência, PNG ou WEBP são melhores. A ferramenta permite comparar formatos para escolher o menor que seja aceitável.'),
    'Can I compress an image to a specific size, like under 1MB?':
        ('Posso comprimir uma imagem para um tamanho exato, como menos de 1 MB?',
         'Sim — baixe o cursor de qualidade até o tamanho estimado ficar abaixo do seu alvo (por exemplo 1 MB, 500 KB ou 100 KB para um limite de email ou de carregamento). O tamanho é atualizado ao vivo à medida que ajusta.'),
    'Are my images uploaded when I compress them?':
        ('As minhas imagens são carregadas quando as comprimo?',
         'Não. Toda a compressão acontece localmente no seu navegador, por isso as suas imagens nunca são carregadas, guardadas nem vistas por ninguém. Funciona offline depois de a página carregar.'),
    'Does compressing remove EXIF and location data?':
        ('Comprimir remove os dados EXIF e de localização?',
         'Voltar a codificar uma imagem costuma remover a maior parte dos metadados embutidos, incluindo dados da câmara e coordenadas GPS. Se quer remover metadados mantendo a qualidade total, use antes o nosso removedor de EXIF.'),
    'Which image formats can I convert between?':
        ('Entre que formatos de imagem posso converter?',
         'Pode converter entre PNG, JPG, WEBP e AVIF em qualquer direção — por exemplo PNG para JPG, JPG para WEBP ou WEBP para PNG. Carregue um desses formatos e exporte qualquer um dos outros.'),
    "What's the difference between PNG, JPG, WEBP and AVIF?":
        ('Qual é a diferença entre PNG, JPG, WEBP e AVIF?',
         'O PNG é sem perdas e suporta transparência, o que o torna ideal para logótipos, ícones e capturas de ecrã. O JPG é um formato pequeno e com perdas, melhor para fotografias, mas não tem transparência. WEBP e AVIF são formatos modernos que juntam ficheiros pequenos com suporte de transparência — o AVIF costuma ser o mais pequeno e o WEBP tem o suporte mais alargado.'),
}
