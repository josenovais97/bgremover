"""
Spanish (es) catalogue.

Data only — the lookup helpers live in ``remover.translations``, which registers
this module in ``CATALOGUES``. Every catalogue module exposes the same four
names, so adding a language is a new file here plus one line there.

``UI``      — template copy, resolved by the ``{% t %}`` tag.
``JS_UI``   — runtime messages shipped to the browser for ``CBG.t()``.
``USE_CASES`` — translated fields merged over the English use-case landings.
``FAQS``    — (question, answer) pairs keyed by the English question.

Neutral (pan-regional) Spanish: "ordenador"/"computadora" and vosotros forms are
avoided, and the polite second person is "tu" throughout — the site talks to one
person doing one job, and "usted" reads as a bank rather than a tool. Any string
without an entry falls back to English, so partial coverage degrades gracefully.
"""

# --- UI strings (keyed by their English source text) -------------------------
UI = {
    # Header / tool nav
    "Remove BG": "Quitar Fondo",
    "Convert": "Convertir",
    "Compress": "Comprimir",
    "Crop": "Recortar",
    "Stickers": "Stickers",
    "Meme": "Meme",
    "Passport": "Pasaporte",
    "eCommerce": "eCommerce",
    "Blur": "Desenfocar",
    "Portrait": "Retrato",
    "Resize": "Redimensionar",
    "Text Behind": "Texto Detrás",
    "Redact": "Ocultar",
    "QR Code": "Código QR",
    # "Instagram" and "EXIF" are left alone — both are proper nouns in Spanish.
    "Favicon": "Favicon",
    "Beautify Shot": "Embellecer Captura",
    "Frame a screenshot on a pretty backdrop": "Enmarca una captura sobre un fondo bonito",
    "Screenshot Beautifier": "Embellecedor de Capturas",
    # Command palette (Ctrl+K)
    "Search tools": "Buscar herramientas",
    "Search tools…": "Buscar herramientas…",
    "No tools found": "No se encontraron herramientas",
    "Recent": "Reciente",
    "Image to PDF": "Imagen a PDF",
    "Combine photos or scans into one PDF": "Une fotos o escaneos en un solo PDF",
    "More": "Más",
    "nothing uploaded": "nada se sube",
    "or try it with a sample photo": "o pruébalo con una foto de ejemplo",
    "No photo? Try a sample": "¿No tienes foto? Prueba un ejemplo",
    "All tools": "Todas las herramientas",
    "Remove & Edit": "Quitar y Editar",
    "Convert & Optimize": "Convertir y Optimizar",
    "Create & Share": "Crear y Compartir",
    "Photos": "Fotos",
    "Skip to content": "Saltar al contenido",
    # Related-tools cross-link block (foot of every tool page)
    "More free, private tools": "Más herramientas gratis y privadas",
    "Same story everywhere — runs in your browser, nothing uploaded.":
        "La misma historia en todas — funcionan en tu navegador, sin subir nada.",
    "Export here and keep editing there — your image carries over, with no re-upload.":
        "Exporta aquí y sigue editando allí — tu imagen te acompaña, sin volver a subirla.",
    "Finish in one, carry straight on to the next — no re-uploading.":
        "Termina en una y pasa directo a la siguiente — sin volver a subir nada.",
    # Homepage tool grid — heading, intro, and one blurb per TOOL_NAV entry
    "One toolkit for every image job": "Un kit para cada tarea con imágenes",
    "Every tool runs the same way the background remover does — on your device, free, with nothing uploaded.":
        "Todas las herramientas funcionan igual que el quitafondos — en tu dispositivo, gratis y sin subir nada.",
    "Cut out any subject into a transparent PNG": "Recorta cualquier sujeto en un PNG transparente",
    "What are you removing the background from?": "¿A qué le vas a quitar el fondo?",

    # --- hub -> landing cluster links (partials/related_landings.html) -------
    "Looking for something more specific?": "¿Buscas algo más concreto?",
    "Compress PNG": "Comprimir PNG",
    "Compress JPEG": "Comprimir JPEG",
    "Compress WEBP": "Comprimir WEBP",
    "Compress Video": "Comprimir vídeo",
    "Under 1MB": "Menos de 1 MB",
    "Under 500KB": "Menos de 500 KB",
    "Under 100KB": "Menos de 100 KB",
    "For email": "Para correo",
    "For websites": "Para webs",
    "For Discord": "Para Discord",
    "Private image tools": "Herramientas de imagen privadas",
    "Remove background without uploading": "Quitar el fondo sin subir nada",
    "Offline image editor": "Editor de imágenes sin conexión",
    "Open HEIC on Windows": "Abrir HEIC en Windows",
    "iPhone photos to JPG": "Fotos del iPhone a JPG",
    "Extract text from image": "Extraer texto de una imagen",
    "remove.bg alternative": "alternativa a remove.bg",
    "vs TinyPNG": "vs TinyPNG",
    "vs Canva": "vs Canva",
    "vs Adobe Express": "vs Adobe Express",
    "vs Photoroom": "vs Photoroom",
    "vs CloudConvert": "vs CloudConvert",

    # --- /photo-filters/ DEEP -----------------------------------------------
    "Using filters and adjustments well": "Usar bien los filtros y los ajustes",
    "Adjustments versus looks": "Ajustes frente a estilos",
    "Two different things get called filters. Adjustments — exposure, contrast, saturation, temperature — are corrections that move an image towards what it should have looked like. Looks are stylistic presets that move it somewhere deliberately different.":
        "Se llaman filtros a dos cosas distintas. Los ajustes — exposición, contraste, saturación, temperatura — son correcciones que mueven una imagen hacia lo que debería haber parecido. Los estilos son preajustes estéticos que la llevan deliberadamente a otro sitio.",
    "The order matters. Correct first, then style. A preset applied to an underexposed, colour-cast photo bakes those problems in and makes them harder to fix, because the preset has already redistributed the tones you needed to work with.":
        "El orden importa. Corrige primero, estiliza después. Un preajuste aplicado a una foto subexpuesta y con desviación de color fija esos problemas y los vuelve más difíciles de arreglar, porque el preajuste ya ha redistribuido los tonos con los que necesitabas trabajar.",
    "What each slider actually does": "Qué hace realmente cada control",
    "Knowing the mechanism makes the results predictable:":
        "Conocer el mecanismo hace que los resultados sean predecibles:",
    "Exposure shifts every tone up or down together, and clips highlights or shadows once they hit the ends of the range.":
        "La exposición desplaza todos los tonos hacia arriba o hacia abajo a la vez, y recorta las luces o las sombras cuando llegan a los extremos del rango.",
    "Contrast pushes tones away from the middle — brights brighter, darks darker — which also increases apparent saturation as a side effect.":
        "El contraste aleja los tonos del centro — los claros más claros, los oscuros más oscuros — lo que además aumenta la saturación aparente como efecto secundario.",
    "Saturation scales all colour intensity uniformly, so already-vivid colours clip first. Vibrance boosts the muted ones more than the vivid ones, which is why it is gentler on skin.":
        "La saturación escala uniformemente toda la intensidad de color, así que los colores ya vivos son los primeros en recortarse. La intensidad realza más los apagados que los vivos, y por eso es más suave con la piel.",
    "Temperature and tint correct colour casts along the blue–orange and green–magenta axes respectively.":
        "La temperatura y el matiz corrigen desviaciones de color a lo largo de los ejes azul–naranja y verde–magenta, respectivamente.",
    "Sharpening increases contrast at edges. It adds no detail, and overdone it produces bright halos along high-contrast boundaries.":
        "El enfoque aumenta el contraste en los bordes. No añade detalle, y en exceso produce halos claros a lo largo de los límites de alto contraste.",
    "Where over-editing shows first": "Dónde se nota primero la edición excesiva",
    "Skin tones and skies are the two places that give away a heavy hand. Skin turns orange with too much saturation or warmth and grey-green with too much correction the other way; the eye is extremely well calibrated for this and forgiving of almost nothing.":
        "Los tonos de piel y los cielos son los dos sitios que delatan una mano pesada. La piel se vuelve naranja con demasiada saturación o calidez y verde grisácea con demasiada corrección en sentido contrario; el ojo está extremadamente bien calibrado para esto y no perdona casi nada.",
    "Skies band. A gradient pushed hard runs out of intermediate values, and the smooth transition becomes visible steps — made worse by any subsequent lossy compression, which handles gradients badly to begin with.":
        "Los cielos se bandean. Un degradado forzado se queda sin valores intermedios, y la transición suave se convierte en escalones visibles — agravados por cualquier compresión con pérdida posterior, que ya maneja mal los degradados.",
    "Edit non-destructively where you can": "Edita de forma no destructiva cuando puedas",
    "Every adjustment discards information: pushed highlights clip, crushed shadows merge, and neither comes back by moving the slider the other way. Doing it repeatedly on a saved JPEG compounds the loss with compression damage.":
        "Cada ajuste descarta información: las luces forzadas se recortan, las sombras aplastadas se fusionan, y ninguna vuelve moviendo el control en sentido contrario. Hacerlo repetidamente sobre un JPEG guardado suma esa pérdida al daño de compresión.",
    "Work from the highest-quality original each time rather than re-editing an export, and keep that original untouched. If you are producing several versions of one image, generate each from the master instead of editing one into the next.":
        "Trabaja siempre desde el original de mayor calidad en vez de reeditar una exportación, y mantén ese original intacto. Si estás produciendo varias versiones de una imagen, genera cada una desde el original en vez de editar una dentro de la siguiente.",

    # --- /remove-object/ DEEP -----------------------------------------------
    "How content-aware fill decides what goes in the hole":
        "Cómo decide el relleno según contenido qué va en el hueco",
    "The fill is borrowed, not imagined": "El relleno es prestado, no imaginado",
    "Erasing an object leaves a hole, and the fill is assembled from the pixels around it — colour, texture and gradient sampled from the boundary and propagated inward, coarse structure first and fine detail after.":
        "Borrar un objeto deja un hueco, y el relleno se monta a partir de los píxeles de alrededor — color, textura y degradado muestreados en el límite y propagados hacia dentro, primero la estructura gruesa y después el detalle fino.",
    "This is why the surroundings decide the result far more than the object does. A person standing against open sky disappears completely, because the algorithm has an enormous amount of consistent sky to borrow from. The same person in front of a bookshelf leaves a smear, because there is no way to infer which book was behind them.":
        "Por eso el entorno decide el resultado mucho más que el propio objeto. Una persona contra cielo abierto desaparece por completo, porque el algoritmo tiene una cantidad enorme de cielo consistente de donde tomar. La misma persona delante de una estantería deja un borrón, porque no hay manera de inferir qué libro había detrás.",
    "Brush generously, but not too generously": "Pinta con generosidad, pero sin exagerar",
    "Under-brushing is the most common mistake. Leaving a rim of the object's edge pixels means those colours get treated as legitimate surroundings and propagated into the fill, producing a ghost in roughly the object's shape.":
        "Pintar de menos es el error más común. Dejar un borde de los píxeles del contorno del objeto hace que esos colores se traten como entorno legítimo y se propaguen al relleno, produciendo un fantasma con aproximadamente la forma del objeto.",
    "Cover the object plus a small margin, including its shadow and any reflection — a removed object whose shadow remains reads as obviously wrong. But an unnecessarily huge selection forces the algorithm to invent more area than it has evidence for, so the fill turns mushy. Slightly larger than the object is the target.":
        "Cubre el objeto más un pequeño margen, incluida su sombra y cualquier reflejo — un objeto eliminado cuya sombra permanece se lee como obviamente erróneo. Pero una selección innecesariamente enorme obliga al algoritmo a inventar más área de la que tiene evidencia, y el relleno queda pastoso. Un poco más grande que el objeto es el objetivo.",
    "Several small passes beat one large one": "Varias pasadas pequeñas superan a una grande",
    "A big object over varied background is better removed in stages. Erase a portion, let the fill settle, then erase the next — each pass has more plausible surroundings to work from than one enormous selection would.":
        "Un objeto grande sobre un fondo variado se elimina mejor por etapas. Borra una parte, deja que el relleno se asiente, luego borra la siguiente — cada pasada tiene un entorno más plausible del que partir que una única selección enorme.",
    "It also lets you stop when it looks right rather than committing to a single result, and to work along a boundary — the edge of a wall, a horizon — instead of across it, which is where fills most visibly break down.":
        "También te permite parar cuando queda bien en vez de comprometerte con un único resultado, y trabajar a lo largo de un límite — el borde de una pared, un horizonte — en vez de cruzarlo, que es donde los rellenos fallan de forma más visible.",
    "Where this approach runs out": "Dónde se agota este enfoque",
    "Straight lines that pass behind the object rarely reconnect convincingly: tiles, window frames, floorboards and railings all show a kink. Repeating patterns can drift out of phase. And anything that would require knowing what was genuinely hidden — a face behind a hand, text behind a sign — cannot be recovered by any amount of borrowing.":
        "Las líneas rectas que pasan por detrás del objeto rara vez se reconectan de forma convincente: azulejos, marcos de ventana, tablas del suelo y barandillas muestran todos un desvío. Los patrones repetidos pueden desfasarse. Y cualquier cosa que exigiera saber qué estaba realmente oculto — una cara detrás de una mano, texto detrás de un cartel — no puede recuperarse por mucho que se tome prestado.",
    "When the fill fails, cropping the object out of the frame is often the better edit, and an honest one.":
        "Cuando el relleno falla, recortar el objeto fuera del encuadre suele ser la mejor edición, y una edición honesta.",

    # --- /svg-to-png/ DEEP --------------------------------------------------
    "Rasterising vector art without losing the edges": "Rasterizar arte vectorial sin perder los bordes",
    "Why exports from other tools come out soft":
        "Por qué las exportaciones de otras herramientas salen suaves",
    "An SVG has a nominal size in its width, height or viewBox attributes, and many converters rasterise at that size and then scale the resulting bitmap to whatever you asked for. The vector is only consulted once, at the small size, and everything after that is a bitmap being stretched.":
        "Un SVG tiene un tamaño nominal en sus atributos width, height o viewBox, y muchos conversores rasterizan a ese tamaño y luego escalan el bitmap resultante a lo que pediste. El vector solo se consulta una vez, en el tamaño pequeño, y todo lo que viene después es un bitmap estirado.",
    "Rendering at the target size instead means the curves are evaluated at the resolution you actually want, so a 4x export contains four times the real detail rather than four times the pixels. The difference is most obvious on diagonal edges and small text, which is where stretched bitmaps go to pieces.":
        "Renderizar directamente al tamaño de destino significa que las curvas se evalúan a la resolución que realmente quieres, así que una exportación a 4× contiene cuatro veces el detalle real y no cuatro veces los píxeles. La diferencia es más evidente en los bordes diagonales y el texto pequeño, que es donde los bitmaps estirados se deshacen.",
    "Fonts are the usual surprise": "Las tipografías son la sorpresa habitual",
    "SVG text is not shapes — it is characters plus a font name, resolved at render time. If the file names a font that is not available where it is rasterised, a fallback is substituted and the text reflows: different widths, different line breaks, sometimes overlapping other elements.":
        "El texto de un SVG no son formas — son caracteres más un nombre de tipografía, resueltos en el momento de renderizar. Si el archivo nombra una tipografía que no está disponible donde se rasteriza, se sustituye por una alternativa y el texto refluye: anchos distintos, saltos de línea distintos, a veces solapando otros elementos.",
    "The fix belongs in the SVG rather than in the converter. Converting text to outlines in your vector editor before export makes the file self-contained and immune to this, at the cost of no longer being editable as text. For a logo destined for export that is almost always the right trade.":
        "El arreglo corresponde al SVG y no al conversor. Convertir el texto en contornos en tu editor vectorial antes de exportar hace el archivo autosuficiente e inmune a esto, a costa de dejar de ser editable como texto. Para un logotipo destinado a exportación, casi siempre es el intercambio correcto.",
    "External references do not travel": "Las referencias externas no viajan",
    "An SVG can reference images by URL rather than embedding them, and can pull in webfonts and stylesheets the same way. Rasterised in isolation, those references produce blank rectangles and fallback type, because nothing is fetched.":
        "Un SVG puede referenciar imágenes por URL en vez de incrustarlas, y puede traer webfonts y hojas de estilo del mismo modo. Rasterizado en aislamiento, esas referencias producen rectángulos vacíos y tipografías alternativas, porque no se descarga nada.",
    "Embedding raster content as a data URI inside the SVG makes it self-contained. It grows the file, but the file then renders identically everywhere, which is the entire point of handing someone a vector.":
        "Incrustar contenido ráster como data URI dentro del SVG lo hace autosuficiente. Aumenta el archivo, pero entonces el archivo se renderiza igual en todas partes, que es precisamente el sentido de entregarle un vector a alguien.",
    "Transparency and what JPG does to it": "La transparencia y lo que el JPG le hace",
    "PNG output keeps the alpha channel, so an icon exported at any size drops onto any background cleanly. That is normally what you want from vector art.":
        "La salida en PNG conserva el canal alfa, así que un icono exportado a cualquier tamaño encaja limpiamente sobre cualquier fondo. Eso es normalmente lo que quieres del arte vectorial.",
    "Exporting the same artwork as JPG flattens transparency onto white, and the result is a white box wherever the artwork was transparent. If the destination cannot take PNG, fill the background with the colour it will actually sit on rather than accepting the default.":
        "Exportar la misma obra en JPG aplana la transparencia sobre blanco, y el resultado es una caja blanca donde el arte era transparente. Si el destino no acepta PNG, rellena el fondo con el color sobre el que realmente va a asentarse en vez de aceptar el valor por defecto.",

    # --- /image-to-text/ DEEP -----------------------------------------------
    "Getting a clean read out of an image": "Conseguir una lectura limpia de una imagen",
    "Why the same document reads twice differently": "Por qué el mismo documento se lee de dos maneras",
    "Recognition begins by deciding, pixel by pixel, what is ink and what is paper. That decision is made from local contrast, so anything that changes brightness across the page changes the answer — a shadow from your hand, a window on one side, the curve of a book's spine.":
        "El reconocimiento empieza decidiendo, píxel a píxel, qué es tinta y qué es papel. Esa decisión se toma a partir del contraste local, así que todo lo que cambie el brillo a lo largo de la página cambia la respuesta — la sombra de tu mano, una ventana a un lado, la curvatura del lomo de un libro.",
    "It is why a photo that looks perfectly legible to you can return nonsense from one half of the page and near-perfect text from the other. The half that failed was thresholded to solid black or solid white before any character was examined.":
        "Por eso una foto que a ti te parece perfectamente legible puede devolver disparates de una mitad de la página y texto casi perfecto de la otra. La mitad que falló se convirtió a negro sólido o blanco sólido antes de examinar un solo carácter.",
    "The resolution floor": "El mínimo de resolución",
    "Accuracy is governed by how many pixels tall a lowercase letter is, not by the megapixels of the image. Around 20-30 pixels is comfortable. Below about 10, the shapes that distinguish similar characters — the gap in an 'e', the join on an 'a' — simply are not present in the data, and no amount of processing recovers them.":
        "La precisión la gobierna la altura en píxeles de una letra minúscula, no los megapíxeles de la imagen. Unos 20-30 píxeles resulta cómodo. Por debajo de unos 10, las formas que distinguen caracteres parecidos — la abertura de una «e», la unión de una «a» — simplemente no están en los datos, y ningún procesamiento las recupera.",
    "The practical consequence is that zooming in before you capture beats every post-processing step. A screenshot of a zoomed page outperforms a full-page screenshot scaled up afterwards, because one has the pixels and the other is inventing them.":
        "La consecuencia práctica es que acercarse antes de capturar supera cualquier paso de posprocesado. Una captura de una página ampliada supera a una captura de la página completa escalada después, porque una tiene los píxeles y la otra los está inventando.",
    "Choosing the language actually matters": "Elegir el idioma importa de verdad",
    "The engine resolves ambiguous shapes against a model of the language you selected, so the wrong selection does not merely fail to help — it produces confident, wrong, real words. Portuguese text read as English comes back as English-looking nonsense, and accented characters tend to vanish because the model has no expectation of them.":
        "El motor resuelve las formas ambiguas contra un modelo del idioma que seleccionaste, así que una elección equivocada no se limita a no ayudar — produce palabras reales, erróneas y seguras de sí. Un texto en portugués leído como inglés vuelve como disparates con aspecto inglés, y los caracteres acentuados tienden a desaparecer porque el modelo no los espera.",
    "If a document mixes languages, pick the dominant one rather than loading several. Multiple packs dilute each model and usually cost more accuracy than the mixed content does.":
        "Si un documento mezcla idiomas, elige el dominante en vez de cargar varios. Varios paquetes diluyen cada modelo y normalmente cuestan más precisión que el propio contenido mezclado.",
    "What to fix before recognising": "Qué corregir antes de reconocer",
    "Almost every improvement is upstream of the recognition step.":
        "Casi todas las mejoras están antes del paso de reconocimiento.",
    "Crop to the text block, so layout analysis has nothing else to interpret.":
        "Recorta hasta el bloque de texto, para que el análisis de diseño no tenga nada más que interpretar.",
    "Straighten the page — small skew is corrected automatically, large skew defeats line detection.":
        "Endereza la página — una inclinación pequeña se corrige automáticamente, una grande derrota la detección de líneas.",
    "Even out the lighting before raising contrast; contrast on an uneven image amplifies the problem.":
        "Uniforma la iluminación antes de subir el contraste; el contraste en una imagen irregular amplifica el problema.",
    "Do not sharpen heavily — the haloes it creates get read as ink and merge adjacent characters.":
        "No enfoques en exceso — los halos que crea se leen como tinta y fusionan caracteres contiguos.",

    # --- /pdf-to-image/ DEEP ------------------------------------------------
    "Turning PDF pages into usable images": "Convertir páginas de PDF en imágenes utilizables",
    "Rendering versus extracting": "Renderizar frente a extraer",
    "There are two different operations people call 'PDF to image'. Extracting pulls out photographs that were embedded in the file, at whatever resolution they were embedded. Rendering draws the page — text, vectors, images and all — into a new bitmap at a size you choose.":
        "Hay dos operaciones distintas a las que la gente llama «PDF a imagen». Extraer saca las fotografías que se incrustaron en el archivo, a la resolución con la que se incrustaron. Renderizar dibuja la página — texto, vectores, imágenes, todo — en un nuevo bitmap del tamaño que elijas.",
    "This tool renders. That is what you want for anything containing text or diagrams, because the characters are drawn from their vector outlines at the output size and stay crisp. Extraction would give you only the photos and none of the layout.":
        "Esta herramienta renderiza. Es lo que quieres para cualquier cosa con texto o diagramas, porque los caracteres se dibujan desde sus contornos vectoriales al tamaño de salida y quedan nítidos. La extracción te daría solo las fotos y nada del diseño.",
    "Choosing a scale that is worth the megabytes": "Elegir una escala que justifique los megabytes",
    "A PDF page has a nominal size in points, and rendering at 1x produces roughly 72 pixels per inch — fine for a thumbnail and too soft to read comfortably. 2x lands near 150 DPI, which is the sensible default for screen reading and the point where body text becomes properly legible.":
        "Una página de PDF tiene un tamaño nominal en puntos, y renderizar a 1× produce unos 72 píxeles por pulgada — suficiente para una miniatura y demasiado suave para leer con comodidad. 2× queda cerca de 150 DPI, que es el valor por defecto sensato para leer en pantalla y el punto en que el texto corrido se vuelve bien legible.",
    "4x approaches 300 DPI and is worth it only when the result will be printed or when you intend to run recognition over the output. The file size scales with the square of the factor, so a 4x render of a twenty-page document is a genuinely large download for output most people will view at a quarter of that size.":
        "4× se acerca a los 300 DPI y solo vale la pena cuando el resultado se va a imprimir o cuando piensas pasarle reconocimiento de texto. El tamaño del archivo escala con el cuadrado del factor, así que renderizar a 4× un documento de veinte páginas es una descarga realmente grande para un resultado que la mayoría verá a una cuarta parte de ese tamaño.",
    "Why a scanned PDF behaves differently": "Por qué un PDF escaneado se comporta de otra forma",
    "A PDF produced by a scanner has no text in it at all — each page is one large photograph. Rendering such a page above the resolution of the original scan cannot add detail; it enlarges the scan and inflates the file.":
        "Un PDF producido por un escáner no tiene texto alguno — cada página es una gran fotografía. Renderizar una página así por encima de la resolución del escaneo original no puede añadir detalle; amplía el escaneo e infla el archivo.",
    "You can usually tell which kind you have by trying to select text in a PDF viewer. If nothing highlights, the page is an image, the useful export is JPG rather than PNG, and the natural next step is text recognition rather than a higher scale factor.":
        "Normalmente puedes saber qué tipo tienes intentando seleccionar texto en un lector de PDF. Si no se resalta nada, la página es una imagen, la exportación útil es JPG y no PNG, y el paso natural siguiente es el reconocimiento de texto y no un factor de escala mayor.",
    "PNG or JPG for the pages": "PNG o JPG para las páginas",
    "Pages that are mostly text, tables or line diagrams should be PNG: the content is hard edges on flat white, which is exactly where lossless compression is small and where JPEG's ringing artefacts show up around every character.":
        "Las páginas que son sobre todo texto, tablas o diagramas de líneas deben ser PNG: el contenido son bordes duros sobre blanco liso, que es exactamente donde la compresión sin pérdida ocupa poco y donde los artefactos de anillo del JPEG aparecen alrededor de cada carácter.",
    "Pages that are mostly photographs should be JPG, where PNG would be several times larger for no visible gain. A mixed document is usually better off as PNG, because damaged text is more noticeable than a slightly larger file.":
        "Las páginas que son sobre todo fotografías deben ser JPG, donde el PNG sería varias veces mayor sin ganancia visible. Un documento mixto suele quedar mejor en PNG, porque el texto dañado se nota más que un archivo algo más grande.",

    # --- /heic-to-jpg/ DEEP -------------------------------------------------
    "Converting iPhone photos without wasting quality": "Convertir fotos del iPhone sin desperdiciar calidad",
    "What you give up in the conversion": "Lo que pierdes en la conversión",
    "HEIC stores 10 bits per colour channel; JPEG stores 8. That difference is invisible in most photographs and shows up as faint banding in large smooth gradients — a clear sky at dusk is the classic case. It cannot be recovered afterwards.":
        "El HEIC guarda 10 bits por canal de color; el JPEG guarda 8. Esa diferencia es invisible en la mayoría de las fotografías y aparece como un leve bandeado en grandes degradados suaves — un cielo despejado al atardecer es el caso clásico. No se puede recuperar después.",
    "The container also carries things a flat image format has nowhere to put: Live Photo motion, the depth map that portrait blur relies on, and the edit history that makes Revert possible on the phone. Converting produces a finished picture and discards the rest.":
        "El contenedor también lleva cosas que un formato de imagen plano no tiene dónde guardar: el movimiento de las Live Photos, el mapa de profundidad del que depende el desenfoque de retrato, y el historial de edición que hace posible el Revertir en el móvil. Convertir produce una imagen terminada y descarta el resto.",
    "Convert once, from the original": "Convierte una vez, desde el original",
    "JPEG is lossy, so every encode discards a little more. Converting an already-converted file compounds that for no reason. Go back to the HEIC each time rather than re-exporting a JPG you made earlier.":
        "El JPEG tiene pérdida, así que cada codificación descarta un poco más. Convertir un archivo ya convertido agrava eso sin motivo. Vuelve al HEIC cada vez, en lugar de reexportar un JPG que ya habías hecho.",
    "Keep the originals until you have checked the output. Deleting the HEIC masters is the only irreversible step in this process, and it is the one people do first.":
        "Conserva los originales hasta haber revisado el resultado. Borrar los HEIC originales es el único paso irreversible de este proceso, y es el que la gente hace primero.",
    "JPG or PNG out": "Salir en JPG o PNG",
    "Pick JPG when the destination is an upload form, an email or long-term storage — the size saving is the entire reason the format exists and the quality cost at a high setting is not visible.":
        "Elige JPG cuando el destino es un formulario de subida, un correo o almacenamiento a largo plazo — el ahorro de tamaño es la razón de existir del formato y el coste en calidad con un ajuste alto no se ve.",
    "Pick PNG when the photo is going into further editing. It is lossless, so the conversion adds no generational damage, at the cost of a file several times larger than the HEIC you started with.":
        "Elige PNG cuando la foto va a seguir editándose. Es sin pérdida, así que la conversión no añade daño generacional, a cambio de un archivo varias veces mayor que el HEIC del que partiste.",
    "Order of operations for a camera roll": "Orden de operaciones para un carrete",
    "A holiday folder is the real case, and a few habits keep it clean.":
        "Una carpeta de vacaciones es el caso real, y unos pocos hábitos la mantienen limpia.",
    "Convert the whole batch in one pass so the generational loss happens once.":
        "Convierte todo el lote en una sola pasada, para que la pérdida generacional ocurra una vez.",
    "Convert first and compress second, as separate decisions — a converter that silently shrinks to hit a size target has chosen quality for you.":
        "Convierte primero y comprime después, como decisiones separadas — un conversor que encoge en silencio para cumplir un tamaño ya ha elegido la calidad por ti.",
    "Strip metadata at the same time if the photos are going somewhere public; every file is being rewritten anyway.":
        "Elimina los metadatos al mismo tiempo si las fotos van a un sitio público; todos los archivos se están reescribiendo de todos modos.",
    "Check a few outputs before deleting anything.":
        "Revisa algunos resultados antes de borrar nada.",

    # --- /upscale/ DEEP -----------------------------------------------------
    "What enlarging an image can and cannot do": "Lo que ampliar una imagen puede y no puede hacer",
    "Resampling is interpolation, not invention": "El remuestreo es interpolación, no invención",
    "Enlarging computes new pixels from the ones around them. A good filter — Lanczos, here — weights a neighbourhood of source pixels to estimate each new one, which keeps edges clean where a naive method would produce stair-stepping or blur.":
        "Ampliar calcula nuevos píxeles a partir de los que están alrededor. Un buen filtro — aquí, Lanczos — pondera un vecindario de píxeles de origen para estimar cada píxel nuevo, lo que mantiene los bordes limpios donde un método ingenuo produciría escalonado o desenfoque.",
    "What it cannot do is add detail that was never captured. If a face occupies forty pixels in the original, no filter recovers the eyelashes, because that information does not exist in the file. Enlargement makes an image bigger and, done well, keeps it looking deliberate rather than stretched.":
        "Lo que no puede hacer es añadir detalle que nunca se capturó. Si una cara ocupa cuarenta píxeles en el original, ningún filtro recupera las pestañas, porque esa información no existe en el archivo. La ampliación hace la imagen más grande y, bien hecha, la mantiene con aspecto intencionado en vez de estirado.",
    "Why this is not an AI upscaler, on purpose": "Por qué esto no es un ampliador con IA, a propósito",
    "Model-based super-resolution genuinely can hallucinate plausible detail, and on the right image it is impressive. In a browser tab it is also slow enough to lock the page for tens of seconds on a large photo, and memory-hungry enough to crash a phone.":
        "La superresolución basada en modelos puede realmente alucinar detalle plausible, y en la imagen adecuada resulta impresionante. En una pestaña del navegador es también lo bastante lenta para bloquear la página durante decenas de segundos en una foto grande, y lo bastante ávida de memoria para tumbar un móvil.",
    "There is a second, less discussed cost: an AI upscaler invents detail, and invented detail is wrong detail. On a document, a licence plate or a face, that is a liability rather than a feature. A resampled enlargement is honest about what it knows.":
        "Hay un segundo coste, menos comentado: un ampliador con IA inventa detalle, y el detalle inventado es detalle equivocado. En un documento, una matrícula o una cara, eso es un riesgo y no una ventaja. Una ampliación por remuestreo es honesta sobre lo que sabe.",
    "Sharpening after, not before": "Enfocar después, no antes",
    "Enlargement softens edges slightly no matter how good the filter is, so a gentle unsharp pass afterwards restores the appearance of crispness. Applied before enlargement, the same sharpening gets magnified along with everything else and turns into visible haloes.":
        "La ampliación suaviza ligeramente los bordes por bueno que sea el filtro, así que una pasada suave de enfoque después devuelve la apariencia de nitidez. Aplicado antes de ampliar, ese mismo enfoque se magnifica junto con todo lo demás y se convierte en halos visibles.",
    "Overdoing it is the common mistake. Sharpening amplifies noise and JPEG artefacts as readily as detail, so an already-compressed source will show its blocking pattern long before it looks sharp.":
        "Pasarse es el error común. El enfoque amplifica el ruido y los artefactos JPEG con la misma facilidad que el detalle, así que un origen ya comprimido mostrará su patrón de bloques mucho antes de parecer nítido.",
    "When enlargement is the wrong answer": "Cuándo la ampliación es la respuesta equivocada",
    "If you need a larger image for print and have access to the original file, go back to it. A camera original or a vector source beats any enlargement of a downscaled copy, and the difference is not subtle.":
        "Si necesitas una imagen más grande para imprimir y tienes acceso al archivo original, vuelve a él. Un original de cámara o una fuente vectorial supera cualquier ampliación de una copia reducida, y la diferencia no es sutil.",
    "Logos and icons: find the SVG and rasterise it instead — infinitely better than any enlargement.":
        "Logotipos e iconos: busca el SVG y rasterízalo — infinitamente mejor que cualquier ampliación.",
    "Screenshots of text: retake at a higher zoom rather than enlarging.":
        "Capturas de pantalla de texto: vuelve a capturar con más zoom en vez de ampliar.",
    "Heavily compressed images: compress artefacts enlarge too, and sharpening makes them worse.":
        "Imágenes muy comprimidas: los artefactos de compresión también se amplían, y el enfoque los empeora.",
    "Print: 2x from a good original is usually plenty; 4x from a thumbnail will not rescue it.":
        "Impresión: 2× desde un buen original suele bastar; 4× desde una miniatura no la salva.",

    # --- /resize-image/ DEEP ------------------------------------------------
    "Resizing well": "Redimensionar bien",
    "Down is safe, up is not": "Reducir es seguro, ampliar no",
    "Making an image smaller derives every output pixel from real measured data, so it is the safe direction. It can even improve apparent quality, since averaging groups of pixels reduces noise — a high-ISO photo often looks cleaner at half size.":
        "Hacer una imagen más pequeña deriva cada píxel de salida de datos realmente medidos, así que es la dirección segura. Incluso puede mejorar la calidad aparente, ya que promediar grupos de píxeles reduce el ruido — una foto con ISO alto suele verse más limpia a la mitad de tamaño.",
    "Enlarging is a different problem. The detail was never captured, so it has to be invented: classical resampling does it softly, producing a bigger but blurrier image. Around 2× is the practical ceiling for anything that must look natural.":
        "Ampliar es un problema distinto. El detalle nunca se capturó, así que hay que inventarlo: el remuestreo clásico lo hace de forma suave, produciendo una imagen más grande pero más borrosa. Unas 2× es el techo práctico para algo que deba parecer natural.",
    "Keep the aspect ratio": "Mantén la proporción",
    "Changing width and height by different amounts stretches the image, and people are extremely good at spotting it — a face a few percent too wide looks wrong even to someone who cannot say why.":
        "Cambiar el ancho y el alto en proporciones distintas deforma la imagen, y la gente es extremadamente buena detectándolo — una cara un pequeño porcentaje demasiado ancha se ve mal incluso para quien no sabe explicar por qué.",
    "When a destination demands an exact ratio your original does not have, crop to that ratio first and then resize, rather than stretching to fit. You lose some framing and keep the proportions.":
        "Cuando un destino exige una proporción exacta que tu original no tiene, recorta primero a esa proporción y luego redimensiona, en vez de estirar para encajar. Pierdes algo de encuadre y conservas las proporciones.",
    "Resize before compressing, not after": "Redimensiona antes de comprimir, no después",
    "File size is driven far more by pixel count than by the quality setting, so reducing dimensions to what will actually be displayed usually clears an upload limit on its own.":
        "El tamaño del archivo depende mucho más del número de píxeles que del ajuste de calidad, así que reducir las dimensiones a lo que realmente se va a mostrar suele cumplir un límite de subida por sí solo.",
    "The common mistake is to keep full dimensions and push quality down until the file fits, which produces a large, artefact-ridden image where a smaller clean one would have looked better and weighed less.":
        "El error común es mantener las dimensiones completas y bajar la calidad hasta que el archivo entre, lo que produce una imagen grande y llena de artefactos donde una más pequeña y limpia se habría visto mejor y habría pesado menos.",
    "Sharpening comes last": "El enfoque va al final",
    "Downscaling softens an image slightly — that is inherent to averaging pixels together — so a light sharpen afterwards is normal and appropriate.":
        "Reducir la escala suaviza ligeramente la imagen — es inherente a promediar píxeles — así que un enfoque ligero después es normal y apropiado.",
    "Doing it in the other order does not work: sharpening before you downscale amplifies noise and edge detail that the resize is about to average away, and can leave visible halos around high-contrast edges.":
        "Hacerlo en el orden inverso no funciona: enfocar antes de reducir amplifica ruido y detalle de bordes que el redimensionado está a punto de promediar, y puede dejar halos visibles alrededor de los bordes de alto contraste.",

    # --- /exif-remover/ DEEP ------------------------------------------------
    "What the file says about you after you send it": "Lo que el archivo dice de ti después de enviarlo",
    "The fields that actually matter": "Los campos que de verdad importan",
    "Cameras and phones write a block of metadata into every photo. Most of it is harmless — exposure, focal length, orientation. Three fields are not: GPS coordinates, the timestamp, and the device identifier.":
        "Las cámaras y los móviles escriben un bloque de metadatos en cada foto. La mayoría es inofensiva — exposición, distancia focal, orientación. Tres campos no lo son: las coordenadas GPS, la fecha y hora, y el identificador del dispositivo.",
    "The coordinates are precise enough to identify a building, and a photo taken indoors is usually taken at home. A set of photos shared over months carries a movement history nobody intended to publish, which is the part people underestimate.":
        "Las coordenadas son lo bastante precisas para identificar un edificio, y una foto tomada en interior suele estar tomada en casa. Un conjunto de fotos compartidas a lo largo de meses arrastra un historial de desplazamientos que nadie pretendía publicar, y esa es la parte que la gente subestima.",
    "Which platforms strip it, and why that is not a plan":
        "Qué plataformas los eliminan, y por qué eso no es un plan",
    "Large social networks generally strip metadata on upload, partly for privacy and partly because they re-encode everything anyway. That protects the public copy and nothing else.":
        "Las grandes redes sociales suelen eliminar los metadatos al subir, en parte por privacidad y en parte porque recodifican todo de todos modos. Eso protege la copia pública y nada más.",
    "The file you emailed, put in a shared folder, sent over a chat app that preserves originals, or attached to a marketplace listing keeps every field. Stripping before sending is the only approach that does not depend on each destination's current behaviour.":
        "El archivo que enviaste por correo, pusiste en una carpeta compartida, mandaste por una app de mensajería que conserva los originales, o adjuntaste a un anuncio, conserva todos los campos. Eliminarlos antes de enviar es el único enfoque que no depende del comportamiento actual de cada destino.",
    "Why stripping costs no quality on a JPEG": "Por qué eliminarlos no cuesta calidad en un JPEG",
    "A JPEG is a sequence of marker segments, and metadata lives in its own segments alongside the compressed image data. Removing them is a matter of dropping those segments and rewriting the file — the pixels are never decoded, so there is no re-encode and no generational loss.":
        "Un JPEG es una secuencia de segmentos marcados, y los metadatos viven en sus propios segmentos junto a los datos de imagen comprimidos. Eliminarlos es cuestión de descartar esos segmentos y reescribir el archivo — los píxeles nunca se decodifican, así que no hay recodificación ni pérdida generacional.",
    "This is worth knowing because the alternative people reach for — opening the photo in an editor and re-saving it — does re-encode, and loses a little quality every time.":
        "Conviene saberlo porque la alternativa a la que recurre la gente — abrir la foto en un editor y volver a guardarla — sí recodifica, y pierde un poco de calidad cada vez.",
    "What metadata will not tell you": "Lo que los metadatos no te dicen",
    "Absent metadata is not evidence of anything. Screenshots never had any, messaging apps remove it, and any re-save can drop it, so a photo with no EXIF is unremarkable rather than suspicious.":
        "La ausencia de metadatos no es prueba de nada. Las capturas de pantalla nunca los tuvieron, las apps de mensajería los eliminan, y cualquier nuevo guardado puede quitarlos, así que una foto sin EXIF es corriente y no sospechosa.",
    "Equally, present metadata is not proof: every field is editable. It is a convenience for organising your own photos and a privacy risk when sharing, and it is not a chain of custody.":
        "Igualmente, su presencia no es prueba: todos los campos son editables. Son una comodidad para organizar tus propias fotos y un riesgo de privacidad al compartir, y no una cadena de custodia.",

    # --- /compress/ DEEP ----------------------------------------------------
    "Compressing without visible damage": "Comprimir sin daños visibles",
    "Resize before you compress": "Redimensiona antes de comprimir",
    "This is the single most useful thing to know about hitting a size limit, and most people do it in the wrong order. File size scales roughly with pixel count, so halving an image's width and height cuts it to about a quarter — before the quality slider is touched at all.":
        "Esto es lo más útil que se puede saber para cumplir un límite de tamaño, y la mayoría lo hace en el orden equivocado. El tamaño del archivo escala aproximadamente con el número de píxeles, así que reducir a la mitad el ancho y el alto de una imagen la recorta a una cuarta parte — antes de tocar siquiera el control de calidad.",
    "A 4000-pixel-wide photo dropped to 1600 pixels will usually clear an upload limit on its own, with no perceptible loss, because nothing displaying it needed 4000 pixels. A 1600-pixel image at quality 85 looks better and weighs less than a 4000-pixel image at quality 40.":
        "Una foto de 4000 píxeles de ancho reducida a 1600 normalmente cumple un límite de subida por sí sola, sin pérdida perceptible, porque nada que la muestre necesitaba 4000 píxeles. Una imagen de 1600 píxeles con calidad 85 se ve mejor y pesa menos que una de 4000 píxeles con calidad 40.",
    "Where the quality scale actually bites": "Dónde pesa de verdad la escala de calidad",
    "The 0–100 quality number is badly non-linear, and knowing its shape saves a lot of guessing:":
        "El número de calidad de 0–100 es muy poco lineal, y conocer su forma ahorra muchas conjeturas:",
    "100 to 90: no visible difference on most photographs, but a large file. Wasteful for the web.":
        "100 a 90: ninguna diferencia visible en la mayoría de las fotografías, pero un archivo grande. Un desperdicio para la web.",
    "90 to 80: still visually indistinguishable, at roughly half the size. Where most images should sit.":
        "90 a 80: sigue siendo visualmente indistinguible, con aproximadamente la mitad del tamaño. Donde debería estar la mayoría de las imágenes.",
    "80 to 70: slight softening in fine texture. Fine for thumbnails and secondary images.":
        "80 a 70: ligera pérdida de nitidez en la textura fina. Vale para miniaturas e imágenes secundarias.",
    "70 to 60: artefacts appear in skies, skin tones and around sharp edges.":
        "70 a 60: aparecen artefactos en cielos, tonos de piel y alrededor de los bordes nítidos.",
    "Below 60: obvious blockiness and haloing. Only when size dominates everything.":
        "Por debajo de 60: bloques y halos evidentes. Solo cuando el tamaño domina todo lo demás.",
    "Content changes the answer": "El contenido cambia la respuesta",
    "Those bands assume photographs. Busy texture — foliage, gravel, fabric — hides compression artefacts well and can go lower than you would expect.":
        "Estos rangos suponen fotografías. La textura cargada — follaje, grava, tela — oculta bien los artefactos de compresión y puede bajar más de lo que esperarías.",
    "Smooth gradients are the opposite. A clear sky or a studio backdrop has no texture to mask the boundaries between compression blocks, so banding appears early. Screenshots, illustrations and anything with text are the worst case and often should not be lossy at all; if they must be, start at 90 rather than 80.":
        "Los degradados suaves son lo contrario. Un cielo despejado o un fondo de estudio no tiene textura que enmascare los límites entre los bloques de compresión, así que el bandeado aparece pronto. Las capturas de pantalla, las ilustraciones y todo lo que lleve texto son el peor caso y a menudo no deberían usar compresión con pérdida en absoluto; si deben, empieza en 90 y no en 80.",
    "Never compress twice": "Nunca comprimas dos veces",
    "Each lossy save re-quantises data that already carries artefacts from the previous save, and the damage accumulates permanently. Ten saves at quality 90 produce a visibly worse image than one save at quality 60.":
        "Cada guardado con pérdida vuelve a cuantizar datos que ya arrastran artefactos del guardado anterior, y el daño se acumula de forma permanente. Diez guardados con calidad 90 producen una imagen visiblemente peor que un solo guardado con calidad 60.",
    "Keep a lossless master and export to a compressed format once, at the end. If you need to send an image to someone who will edit it further, send the master.":
        "Guarda un original sin pérdida y exporta a un formato comprimido una sola vez, al final. Si necesitas enviar una imagen a alguien que la va a seguir editando, envía el original.",

    # --- /convert/ DEEP -----------------------------------------------------
    "Choosing the right format": "Elegir el formato correcto",
    "What conversion does and does not cost you": "Lo que la conversión te cuesta y lo que no",
    "Converting to a lossless format — PNG, or WebP in lossless mode — preserves your pixels exactly. Converting to a lossy format (JPG, lossy WebP, AVIF) discards data permanently, in exchange for a much smaller file.":
        "Convertir a un formato sin pérdida — PNG, o WebP en modo lossless — preserva tus píxeles exactamente. Convertir a un formato con pérdida (JPG, WebP con pérdida, AVIF) descarta datos de forma permanente, a cambio de un archivo mucho más pequeño.",
    "The case worth avoiding is converting between two lossy formats. A JPG turned into a lossy WebP has been through two rounds of quantisation, and the second round treats the first round's artefacts as real detail worth preserving. Always convert from the highest-quality copy you have, not from a file that has already been compressed.":
        "El caso que conviene evitar es convertir entre dos formatos con pérdida. Un JPG convertido en WebP con pérdida ha pasado por dos rondas de cuantización, y la segunda trata los artefactos de la primera como detalle real que merece preservarse. Convierte siempre desde la copia de mayor calidad que tengas, no desde un archivo ya comprimido.",
    "Which target format to pick": "Qué formato de destino elegir",
    "The answer depends almost entirely on where the file is going:":
        "La respuesta depende casi por completo del destino del archivo:",
    "For your own website: WebP. Typically 25–35% smaller than JPG at the same visual quality, supported by every current browser.":
        "Para tu propia web: WebP. Normalmente un 25–35% más pequeño que el JPG con la misma calidad visual, compatible con todos los navegadores actuales.",
    "For sending to someone else: JPG. It is the most compatible image format in existence and never gets rejected.":
        "Para enviar a otra persona: JPG. Es el formato de imagen más compatible que existe y nunca se rechaza.",
    "For anything with a transparent background: PNG as a master, lossy WebP for the web. JPG cannot store transparency at all.":
        "Para cualquier cosa con fondo transparente: PNG como original, WebP con pérdida para la web. El JPG no puede guardar transparencia en absoluto.",
    "For screenshots and images containing text: PNG or lossless WebP — sharp edges are the worst case for lossy compression.":
        "Para capturas de pantalla e imágenes con texto: PNG o WebP sin pérdida — los bordes nítidos son el peor caso para la compresión con pérdida.",
    "For large hero images where bandwidth matters: AVIF, which compresses hardest but encodes slowly.":
        "Para imágenes grandes destacadas donde importa el ancho de banda: AVIF, que comprime más pero codifica despacio.",
    "The transparency trap": "La trampa de la transparencia",
    "Converting a transparent PNG to JPG is the most common conversion mistake, because JPEG has no alpha channel and no way to represent one. The transparency has to be resolved against something, and the software picks — usually white, sometimes black.":
        "Convertir un PNG transparente a JPG es el error de conversión más común, porque el JPEG no tiene canal alfa ni forma de representarlo. La transparencia debe resolverse contra algo, y el software elige — normalmente blanco, a veces negro.",
    "Nothing is broken and nothing can be recovered afterwards; the alpha channel was discarded at export. If your cut-out came back with a white background, this is why. Re-export from the original as PNG or WebP.":
        "Nada está roto y nada puede recuperarse después; el canal alfa se descartó al exportar. Si tu recorte salió con fondo blanco, es por esto. Vuelve a exportar desde el original en PNG o WebP.",
    "Why this runs on your device": "Por qué esto se ejecuta en tu dispositivo",
    "Conversion happens in your browser using the same canvas and codec support the browser already ships for displaying images. Nothing is uploaded, which means no file size ceiling imposed by a server, no queue, and no per-image cost — so batch conversion is just a matter of waiting.":
        "La conversión ocurre en tu navegador usando el mismo canvas y el mismo soporte de códecs que el navegador ya incluye para mostrar imágenes. No se sube nada, lo que significa ningún límite de tamaño impuesto por un servidor, ninguna cola y ningún coste por imagen — así que convertir en lote es solo cuestión de esperar.",
    "It also means the tool works on files you would not want to hand to a service: scanned documents, identity paperwork, medical images, unreleased work.":
        "También significa que la herramienta funciona con archivos que no querrías entregar a un servicio: documentos escaneados, papeleo de identidad, imágenes médicas, trabajo sin publicar.",

    # --- /crop/ DEEP (the long-form block) ----------------------------------
    "Cropping with intent": "Recortar con intención",
    "Cropping is free, enlarging is not": "Recortar es gratis, ampliar no",
    "Cropping discards pixels, which costs you nothing in quality — the pixels that remain are the original measured data. What it costs is resolution, and that only matters if the result ends up smaller than where it is going.":
        "Recortar descarta píxeles, lo que no cuesta nada en calidad — los píxeles que quedan son los datos originales medidos. Lo que cuesta es resolución, y eso solo importa si el resultado acaba siendo más pequeño que el destino donde va.",
    "A 4000-pixel photo cropped to a quarter of its area is still 2000 pixels wide, which is more than enough for almost any screen use. Crop confidently; the mistake is enlarging afterwards to compensate, which invents detail that was never captured.":
        "Una foto de 4000 píxeles recortada a una cuarta parte de su área sigue teniendo 2000 píxeles de ancho, más que suficiente para casi cualquier uso en pantalla. Recorta con confianza; el error es ampliar después para compensar, lo que inventa detalle que nunca se capturó.",
    "The ratios worth knowing": "Las proporciones que conviene conocer",
    "Most crops are made to fit a destination, and there are only a handful that matter:":
        "La mayoría de los recortes se hacen para encajar en un destino, y solo un puñado de proporciones importa:",
    "1:1 square — profile pictures, and the universally safe social format.":
        "1:1 cuadrado — fotos de perfil, y el formato social seguro en cualquier sitio.",
    "4:5 vertical — the tallest ratio most feeds display uncropped, so it occupies the most screen space.":
        "4:5 vertical — la proporción más alta que la mayoría de los feeds muestra sin recortar, por lo que ocupa más espacio en pantalla.",
    "9:16 — stories, reels and TikTok, full phone screen.":
        "9:16 — stories, reels y TikTok, pantalla completa del móvil.",
    "16:9 — YouTube, link previews and most horizontal video.":
        "16:9 — YouTube, vistas previas de enlaces y la mayoría del vídeo horizontal.",
    "3:2 and 4:3 — the native ratios of most cameras and phones, and the right choice for print.":
        "3:2 y 4:3 — las proporciones nativas de la mayoría de cámaras y móviles, y la elección correcta para imprimir.",
    "Circles are a crop plus transparency": "Los círculos son un recorte más transparencia",
    "A circular crop is not really a crop — an image file is always rectangular. What it produces is a square image whose corners are transparent, which is why the export format matters.":
        "Un recorte circular no es realmente un recorte — un archivo de imagen siempre es rectangular. Lo que produce es una imagen cuadrada con las esquinas transparentes, y por eso importa el formato de exportación.",
    "Save a circular crop as PNG or WebP and the corners stay transparent over any background. Save it as JPG and the corners become solid white or black, giving you a circle in a box. This catches people out constantly with avatars.":
        "Guarda un recorte circular en PNG o WebP y las esquinas quedan transparentes sobre cualquier fondo. Guárdalo en JPG y las esquinas pasan a blanco o negro sólido, dándote un círculo dentro de una caja. Esto pilla a la gente constantemente con los avatares.",
    "Composition, briefly": "Composición, en resumen",
    "Two habits improve most crops. Leave space in the direction a subject faces or moves, so the frame does not feel cramped against their gaze. And avoid cropping a person at a joint — the wrist, elbow, knee or ankle — because it reads as an amputation rather than a frame edge; crop mid-limb instead.":
        "Dos hábitos mejoran la mayoría de los recortes. Deja espacio en la dirección hacia la que el sujeto mira o se mueve, para que el encuadre no parezca apretado contra su mirada. Y evita recortar a una persona en una articulación — muñeca, codo, rodilla o tobillo — porque se lee como una amputación y no como el borde del encuadre; recorta a media extremidad.",
    "For anything going into a circular avatar slot, compose inside the inscribed circle. Everything in the corners of your square will be discarded by the platform.":
        "Para cualquier cosa destinada a un avatar circular, compón dentro del círculo inscrito. Todo lo que esté en las esquinas de tu cuadrado será descartado por la plataforma.",

    # --- /crop/ -------------------------------------------------------------
    "Free Image Crop Tool — Circle, Square & Custom Ratio":
        "Recortar Imágenes Gratis — Círculo, Cuadrado y Proporción Personalizada",
    "Free Image Crop Tool — Circle, Square, Custom Ratio & Rotate":
        "Recortar Imágenes Gratis — Círculo, Cuadrado, Proporción Personalizada y Rotar",
    "Crop images free in your browser — square, circle, rounded, 4:5, 16:9, 9:16 or any custom ratio, with rotate, flip and zoom. Nothing leaves your device.":
        "Recorta imágenes gratis en tu navegador — cuadrado, círculo, esquinas redondeadas, 4:5, 16:9, 9:16 o cualquier proporción personalizada, con rotar, voltear y zoom. Nada sale de tu dispositivo.",
    "Crops locally — nothing is uploaded": "Recorta en local — no se sube nada",
    "Crop an": "Recortar una",
    "Square, circle, rounded or any custom ratio — with rotate, flip, zoom and drag. No background removal needed. Export a transparent PNG or a JPG, 100% in your browser.":
        "Cuadrado, círculo, esquinas redondeadas o cualquier proporción personalizada — con rotar, voltear, zoom y arrastrar. Sin necesidad de quitar el fondo. Exporta un PNG transparente o un JPG, 100% en tu navegador.",
    "Drop a photo to crop": "Suelta una foto para recortar",
    "or click to browse — JPG, PNG or WEBP · pick several to crop a batch":
        "o haz clic para buscar — JPG, PNG o WEBP · elige varias para recortar en lote",
    "Drag the photo to reposition · scroll or use the slider to zoom":
        "Arrastra la foto para recolocarla · usa la rueda o el control para el zoom",
    "Shape": "Forma",
    "Rectangle": "Rectángulo",
    "Rounded": "Redondeado",
    "Circle": "Círculo",
    "Ratio": "Proporción",
    "Custom": "Personalizada",
    "ratio": "proporción",
    "Rotate & flip": "Rotar y voltear",
    "Left": "Izquierda",
    "Right": "Derecha",
    "Flip H": "Voltear H",
    "Flip V": "Voltear V",
    "Straighten": "Enderezar",
    "Export as": "Exportar como",
    "Next-gen, smallest files (Chromium)": "Nueva generación, archivos más pequeños (Chromium)",
    "PNG keeps transparent corners on rounded/circle crops.":
        "El PNG conserva las esquinas transparentes en recortes redondeados y circulares.",
    "Download crop": "Descargar recorte",
    "Crop any image, right in your browser": "Recorta cualquier imagen, en tu propio navegador",
    "Circle & rounded": "Círculo y redondeado",
    "Perfect avatars with transparent corners, saved as PNG.":
        "Avatares perfectos con esquinas transparentes, guardados en PNG.",
    "Any ratio": "Cualquier proporción",
    "1:1, 4:5, 16:9, 9:16 or your own custom width : height.":
        "1:1, 4:5, 16:9, 9:16 o tu propio ancho : alto.",
    "Private": "Privado",
    "No upload and no background removal — the crop runs on your device.":
        "Sin subidas y sin quitar el fondo — el recorte se ejecuta en tu dispositivo.",
    "Upload a photo, pick a shape and ratio, rotate or flip, then drag and zoom to frame it. Download a full-resolution crop as a transparent PNG or a JPG — nothing ever leaves your browser.":
        "Elige una foto, define la forma y la proporción, rota o voltea, luego arrastra y haz zoom para encuadrar. Descarga el recorte a resolución completa como PNG transparente o JPG — nada sale de tu navegador.",
    "Each of these has its own guide, with the sizes and rules that apply to it.":
        "Cada uno tiene su propia guía, con los tamaños y las reglas que le corresponden.",
    "Or read the": "O lee las",
    "guides": "guías",
    "— explanations of how image formats, compression, metadata and cut-outs actually work.":
        "— explicaciones de cómo funcionan realmente los formatos de imagen, la compresión, los metadatos y los recortes.",
    "Instagram": "Instagram",
    "Swap between PNG, JPG, WEBP and AVIF": "Cambia entre PNG, JPG, WEBP y AVIF",
    "Shrink file size without visible quality loss": "Reduce el peso sin pérdida visible de calidad",
    "Scale to exact pixel dimensions": "Ajusta a medidas exactas en píxeles",
    "Crop and fit for feed, story or reel": "Recorta y ajusta para feed, story o reel",
    "Trim to a shape or a fixed ratio": "Corta a una forma o proporción fija",
    "Add a die-cut outline for chat stickers": "Añade un contorno troquelado para stickers de chat",
    "Tuck text behind your subject": "Coloca texto detrás de tu sujeto",
    "Stamp text or a logo across an image": "Aplica texto o un logo sobre la imagen",
    "Turn a set of frames into an animation": "Convierte un conjunto de fotogramas en una animación",
    "Classic top and bottom caption text": "Los clásicos textos arriba y abajo",
    "Official sizes for any country": "Medidas oficiales para cualquier país",
    "Clean white product shots that pass review": "Fotos de producto en blanco que pasan revisión",
    "Portrait-mode depth on any photo": "Efecto retrato en cualquier foto",
    "Blur out faces, plates and private details": "Difumina caras, matrículas y datos privados",
    "Every icon size a site or app needs": "Todos los tamaños de icono para una web o app",
    "Generate a scannable code from a link": "Genera un código escaneable desde un enlace",
    "Strip GPS and camera data from photos": "Elimina datos de GPS y cámara de las fotos",
    # New tools (1.10)
    "Remove Object": "Quitar Objeto",
    "Brush over anything and erase it from the photo": "Pinta sobre lo que sea y bórralo de la foto",
    "Filters": "Filtros",
    "One-tap looks plus fine adjustment sliders": "Estilos de un toque más ajustes finos",
    "Upscale": "Ampliar",
    "Enlarge 2× or 4× with clean, sharp edges": "Amplía 2× o 4× con bordes limpios y nítidos",
    "HEIC to JPG": "HEIC a JPG",
    "Open iPhone HEIC photos anywhere as JPG": "Abre fotos HEIC del iPhone en cualquier sitio como JPG",
    "PDF to Images": "PDF a Imágenes",
    "Save every PDF page as a sharp image": "Guarda cada página del PDF como imagen nítida",
    "Image to Text": "Imagen a Texto",
    "Copy the text out of any photo or screenshot": "Copia el texto de cualquier foto o captura",
    "SVG to PNG": "SVG a PNG",
    "Rasterise vector art at any size, pixel-sharp": "Rasteriza vectores a cualquier tamaño, nítidos",
    # --- New tool pages: og:title (social share cards) ------------------------
    "Remove Objects from Photos — Free & Private":
        "Quitar Objetos de Fotos — Gratis y Privado",
    "Free Image Upscaler — Enlarge 2× / 4× Privately":
        "Ampliador de Imágenes Gratis — Amplía 2× / 4× en Privado",
    "HEIC to JPG — Free Private Converter":
        "HEIC a JPG — Conversor Gratis y Privado",
    "PDF to Images — Free & Private Converter":
        "PDF a Imágenes — Conversor Gratis y Privado",
    "Image to Text — Free Private OCR":
        "Imagen a Texto — OCR Gratis y Privado",
    "SVG to PNG — Free & Sharp at Any Size":
        "SVG a PNG — Gratis y Nítido a Cualquier Tamaño",
    "Photo Filters — Free Private Editor":
        "Filtros de Fotos — Editor Gratis y Privado",
    # --- New tool pages: shared body copy -------------------------------------
    "Drop a photo": "Suelta una foto",
    "Drop an image": "Suelta una imagen",
    "or click to browse — JPG, PNG or WEBP": "o haz clic para buscar — JPG, PNG o WEBP",
    "Select a photo": "Seleccionar una foto",
    "Select an image": "Seleccionar una imagen",
    "Select photos": "Seleccionar fotos",
    "New photo": "Nueva foto",
    "New image": "Nueva imagen",
    "Output format": "Formato de salida",
    "Frequently asked questions": "Preguntas frecuentes",
    # --- Remove Object page ---
    "Erased locally — nothing is uploaded": "Borrado en local — no se sube nada",
    "Remove Objects from Photos — Free, Private & In Your Browser":
        "Quitar Objetos de Fotos — Gratis, Privado y en Tu Navegador",
    "Erase unwanted objects, people or blemishes from a photo: brush over them and a content-aware fill blends them away. Free, and nothing is uploaded.":
        "Borra objetos, personas o imperfecciones de una foto: pinta encima y un relleno inteligente los funde con el fondo. Gratis y sin subir nada.",
    "Remove Objects from Photos": "Quita Objetos de Tus Fotos",
    "Remove": "Quita",
    "Objects": "Objetos",
    "from Photos": "de Tus Fotos",
    "Brush over the thing you want gone — a stranger, a sign, a blemish — and a":
        "Pinta sobre lo que quieres que desaparezca — un desconocido, un cartel, una imperfección — y un",
    "content-aware fill": "relleno inteligente",
    "blends it away. Free, private and instant.":
        "lo funde con el fondo. Gratis, privado e instantáneo.",
    "Works best on even backgrounds — sky, grass, walls, sand":
        "Funciona mejor en fondos uniformes — cielo, césped, paredes, arena",
    "Brush over the object, then press": "Pinta sobre el objeto y pulsa",
    "Repeat in smaller passes for tricky areas.": "Repite en pasadas más pequeñas en las zonas difíciles.",
    "Clear brush": "Limpiar pincel",
    "Erase selection": "Borrar selección",
    "Erasing…": "Borrando…",
    "Erase an object in three steps": "Borra un objeto en tres pasos",
    "Any JPG, PNG or WEBP — it's read straight in your browser, never uploaded.":
        "Cualquier JPG, PNG o WEBP — se lee directamente en tu navegador, nunca se sube.",
    "Brush the object": "Pinta el objeto",
    "Paint over the thing you want gone and press Erase — the fill blends the area away.":
        "Pinta sobre lo que quieres quitar y pulsa Borrar — el relleno funde la zona con el fondo.",
    "Export full resolution as PNG or JPG — free and watermark-free.":
        "Exporta a resolución completa en PNG o JPG — gratis y sin marca de agua.",
    "Object removed": "Objeto eliminado",
    "Drag the handle — the stranger is brushed out, on-device":
        "Arrastra el control — el desconocido desaparece, en tu dispositivo",
    "Your photo — brush over the object you want to remove":
        "Tu foto — pinta sobre el objeto que quieres quitar",
    "Brushing the mask requires a mouse, trackpad or touchscreen. The Erase, Undo and Download buttons are keyboard-accessible.":
        "Pintar la máscara requiere ratón, trackpad o pantalla táctil. Los botones Borrar, Deshacer y Descargar son accesibles por teclado.",
    # --- Upscale page ---
    "Enlarged locally — nothing is uploaded": "Ampliado en local — no se sube nada",
    "Upscale an Image 2× or 4× — Free, Sharp & In Your Browser":
        "Ampliar una Imagen 2× o 4× — Gratis, Nítido y en Tu Navegador",
    "Enlarge images 2× or 4× with high-quality Lanczos resampling and detail sharpening — free and instant, right in your browser. No upload, no sign-up.":
        "Amplía imágenes 2× o 4× con remuestreo Lanczos de alta calidad y realce de detalle — gratis e instantáneo, en tu navegador. Sin subidas ni registro.",
    "Upscale an Image": "Amplía una Imagen",
    "2× or 4×": "2× o 4×",
    "High-quality": "Remuestreo Lanczos",
    "Lanczos resampling": "de alta calidad",
    "with a gentle sharpening pass — edges stay clean instead of going soft or blocky. Instant, free and 100% private.":
        "con un realce suave de nitidez — los bordes quedan limpios en vez de borrosos o pixelados. Instantáneo, gratis y 100% privado.",
    "Great for logos, small photos and web images headed for print":
        "Ideal para logos, fotos pequeñas e imágenes web destinadas a impresión",
    "Scale": "Escala",
    "Sharpen": "Nitidez",
    "Upscaling…": "Ampliando…",
    "Upscale an image in three steps": "Amplía una imagen en tres pasos",
    "Pick 2× or 4×": "Elige 2× o 4×",
    "Lanczos resampling enlarges cleanly, and the sharpen slider brings detail forward.":
        "El remuestreo Lanczos amplía de forma limpia y el control de nitidez realza el detalle.",
    "Export as lossless PNG or a high-quality JPG — no watermark, no limits.":
        "Exporta como PNG sin pérdida o JPG de alta calidad — sin marca de agua ni límites.",
    "Plain stretch": "Estirado simple",
    "Lanczos + sharpen": "Lanczos + nitidez",
    "The same small image, stretched vs resampled — drag to compare":
        "La misma imagen pequeña, estirada vs remuestreada — arrastra para comparar",
    # --- HEIC page ---
    "Converted locally — nothing is uploaded": "Convertido en local — no se sube nada",
    "HEIC to JPG Converter — Free, Private & In Your Browser":
        "Conversor de HEIC a JPG — Gratis, Privado y en Tu Navegador",
    "Convert iPhone HEIC photos to JPG, PNG or WEBP for free — in your browser, so your photos are never uploaded. Batch convert, download as a ZIP.":
        "Convierte fotos HEIC del iPhone a JPG, PNG o WEBP gratis — en tu navegador, así tus fotos nunca se suben. Convierte en lote y descarga en ZIP.",
    "Convert HEIC to": "Convierte HEIC a",
    "iPhone photos that won't open on Windows, Android or the web? Drop them here and get":
        "¿Fotos del iPhone que no se abren en Windows, Android o la web? Suéltalas aquí y recibe",
    "JPG, PNG or WEBP": "JPG, PNG o WEBP",
    "back — free, private and in your browser.":
        "de vuelta — gratis, privado y en tu navegador.",
    "Drop your HEIC photos": "Suelta tus fotos HEIC",
    "or click to browse — .heic and .heif, single or batch":
        "o haz clic para buscar — .heic y .heif, una o en lote",
    "The decoder loads once (~1 MB) and is cached — photos never leave your device":
        "El decodificador se carga una vez (~1 MB) y queda en caché — tus fotos nunca salen del dispositivo",
    "Same photo, a format everything opens — converted on your device":
        "La misma foto, en un formato que todo abre — convertida en tu dispositivo",
    "Convert HEIC in three steps": "Convierte HEIC en tres pasos",
    "Drop your photos": "Suelta tus fotos",
    "Straight from an iPhone, AirDrop or a folder — .heic and .heif both work.":
        "Directo del iPhone, por AirDrop o desde una carpeta — .heic y .heif funcionan.",
    "Pick a format": "Elige un formato",
    "JPG opens everywhere; PNG is lossless; WEBP is smallest for the web.":
        "JPG se abre en todas partes; PNG es sin pérdida; WEBP es el más ligero para la web.",
    "Grab photos one by one or all together as a ZIP — full resolution, no watermark.":
        "Descarga las fotos una a una o todas juntas en ZIP — resolución completa, sin marca de agua.",
    # --- PDF to images page ---
    "Rendered locally — nothing is uploaded": "Procesado en local — no se sube nada",
    "PDF to Images — Convert PDF Pages to PNG or JPG, Free":
        "PDF a Imágenes — Convierte Páginas de PDF a PNG o JPG, Gratis",
    "Turn every page of a PDF into a sharp PNG or JPG, free and in your browser — the PDF is never uploaded. Download single pages or all as a ZIP.":
        "Convierte cada página de un PDF en un PNG o JPG nítido, gratis y en tu navegador — el PDF nunca se sube. Descarga páginas sueltas o todas en ZIP.",
    "PDF to": "PDF a",
    "Images": "Imágenes",
    "Every page of your PDF as a sharp": "Cada página de tu PDF como un",
    "PNG or JPG": "PNG o JPG nítido",
    "— rendered from the vector source, so text stays crisp. Free, private, no page limits.":
        "— renderizado desde el vector original, así el texto se mantiene definido. Gratis, privado y sin límite de páginas.",
    "Drop a PDF": "Suelta un PDF",
    "or click to browse — contracts, scans, slides, forms":
        "o haz clic para buscar — contratos, escaneos, diapositivas, formularios",
    "Select a PDF": "Seleccionar un PDF",
    "Your document is parsed on your device — it never leaves the browser":
        "Tu documento se procesa en tu dispositivo — nunca sale del navegador",
    "Resolution": "Resolución",
    "One PDF in, every page out as its own sharp image":
        "Entra un PDF, sale cada página como su propia imagen nítida",
    "PDF to images in three steps": "PDF a imágenes en tres pasos",
    "It's parsed right in your browser — private documents stay private.":
        "Se procesa en tu propio navegador — los documentos privados siguen siendo privados.",
    "Pick quality": "Elige la calidad",
    "2× is sharp for screens; 4× is print quality. Pages render from the vector source.":
        "2× es nítido para pantalla; 4× es calidad de impresión. Las páginas se renderizan desde el vector.",
    "Save the pages you need, or every page at once as a ZIP.":
        "Guarda las páginas que necesites, o todas de una vez en un ZIP.",
    "New PDF": "Nuevo PDF",
    # --- OCR page ---
    "Recognised locally — nothing is uploaded": "Reconocido en local — no se sube nada",
    "Image to Text (OCR) — Copy Text from a Photo, Free & Private":
        "Imagen a Texto (OCR) — Copia Texto de una Foto, Gratis y Privado",
    "Extract and copy text from any photo or screenshot with on-device OCR — free, in your browser, nothing uploaded. No sign-up, no limits.":
        "Extrae y copia el texto de cualquier foto o captura con OCR en tu dispositivo — gratis, en tu navegador y sin subir nada. Sin registro ni límites.",
    "Copy Text out of": "Copia el Texto de",
    "Any Image": "Cualquier Imagen",
    "Screenshots, photos of documents, whiteboards — the OCR engine reads them":
        "Capturas, fotos de documentos, pizarras — el motor de OCR las lee",
    "on your device": "en tu dispositivo",
    "and hands you editable text. Free and private.":
        "y te entrega texto editable. Gratis y privado.",
    "Drop an image with text": "Suelta una imagen con texto",
    "or click to browse, or paste a screenshot — JPG, PNG or WEBP":
        "o haz clic para buscar, o pega una captura — JPG, PNG o WEBP",
    "The OCR engine loads once and is cached — screenshots never leave your device":
        "El motor de OCR se carga una vez y queda en caché — tus capturas nunca salen del dispositivo",
    "A photo of text in, editable text out — recognised on your device":
        "Entra una foto con texto, sale texto editable — reconocido en tu dispositivo",
    "Text recognition progress": "Progreso del reconocimiento de texto",
    "Read again": "Leer de nuevo",
    "Recognised text": "Texto reconocido",
    "Copy text": "Copiar texto",
    "Save .txt": "Guardar .txt",
    "Image to text in three steps": "Imagen a texto en tres pasos",
    "A screenshot, a photo of a page, a whiteboard — paste works too.":
        "Una captura, la foto de una página, una pizarra — pegar también funciona.",
    "On-device OCR reads it": "El OCR lo lee en tu dispositivo",
    "The Tesseract engine runs in your browser via WebAssembly — nothing is uploaded.":
        "El motor Tesseract funciona en tu navegador con WebAssembly — no se sube nada.",
    "Copy or save": "Copia o guarda",
    "Fix anything in the editable box, then copy it or save it as a .txt file.":
        "Corrige lo que haga falta en el cuadro editable y cópialo o guárdalo como archivo .txt.",
    # --- SVG page ---
    "Rasterised locally — nothing is uploaded": "Rasterizado en local — no se sube nada",
    "SVG to PNG Converter — Pixel-Sharp at Any Size, Free":
        "Conversor de SVG a PNG — Nítido a Cualquier Tamaño, Gratis",
    "Convert SVG to PNG at 1×, 2×, 4× or any exact width — rendered from the vector so edges stay pixel-sharp. Free, in your browser, nothing uploaded.":
        "Convierte SVG a PNG a 1×, 2×, 4× o cualquier ancho exacto — renderizado desde el vector, así los bordes quedan nítidos. Gratis, en tu navegador y sin subir nada.",
    "SVG to": "SVG a",
    "Rendered from the": "Renderizado desde el",
    "vector source": "vector original",
    "at the exact size you pick — so a 4× export has 4× the real detail, not stretched pixels. Transparency preserved.":
        "al tamaño exacto que elijas — así una exportación 4× tiene 4× de detalle real, no píxeles estirados. La transparencia se mantiene.",
    "Drop an SVG": "Suelta un SVG",
    "or click to browse — logos, icons, illustrations":
        "o haz clic para buscar — logos, iconos, ilustraciones",
    "Select an SVG": "Seleccionar un SVG",
    "Or an exact width (px)": "O un ancho exacto (px)",
    "New SVG": "Nuevo SVG",
    "Stretched bitmap": "Mapa de bits estirado",
    "Rendered from vector": "Renderizado desde vector",
    "The same logo at 4× — a stretched export vs a vector render":
        "El mismo logo a 4× — una exportación estirada vs un render vectorial",
    "SVG to PNG in three steps": "SVG a PNG en tres pasos",
    "It's read and rendered right in your browser — never uploaded.":
        "Se lee y se renderiza en tu propio navegador — nunca se sube.",
    "Pick a size": "Elige un tamaño",
    "1×, 2×, 4× or an exact pixel width — the vector renders sharp at any of them.":
        "1×, 2×, 4× o un ancho exacto en píxeles — el vector se renderiza nítido en todos.",
    "PNG keeps transparency; JPG fills white. Free and watermark-free.":
        "PNG conserva la transparencia; JPG rellena en blanco. Gratis y sin marca de agua.",
    # --- Photo filters page ---
    "Edited locally — nothing is uploaded": "Editado en local — no se sube nada",
    "Photo Filters & Adjustments — Free Online Editor, No Upload":
        "Filtros y Ajustes de Fotos — Editor Online Gratis, Sin Subidas",
    "Apply one-tap looks and fine-tune brightness, contrast, saturation, warmth, vignette and grain — free, in your browser, nothing uploaded.":
        "Aplica estilos de un toque y ajusta brillo, contraste, saturación, calidez, viñeta y grano — gratis, en tu navegador y sin subir nada.",
    "Photo Filters &": "Filtros y",
    "Adjustments": "Ajustes de Fotos",
    "Ten one-tap": "Diez",
    "looks": "estilos de un toque",
    "plus real sliders — brightness, contrast, saturation, warmth, vignette, grain. Full-resolution export, free and private.":
        "más controles de verdad — brillo, contraste, saturación, calidez, viñeta y grano. Exportación a resolución completa, gratis y privada.",
    "Looks": "Estilos",
    "Brightness": "Brillo",
    "Contrast": "Contraste",
    "Saturation": "Saturación",
    "Warmth": "Calidez",
    "Vignette": "Viñeta",
    "Grain": "Grano",
    "Hold to compare": "Mantén para comparar",
    "Golden look": "Estilo dorado",
    "One tap, then fine-tune with the sliders — drag to compare":
        "Un toque y luego afina con los controles — arrastra para comparar",
    "Live preview of your photo with the current filter and adjustments":
        "Vista previa en vivo de tu foto con el filtro y los ajustes actuales",
    "Edit a photo in three steps": "Edita una foto en tres pasos",
    "Tap a look, then fine-tune": "Toca un estilo y luego afina",
    "A look sets the starting point; every slider stays yours. Hold Compare to check.":
        "El estilo marca el punto de partida; todos los controles siguen siendo tuyos. Mantén Comparar para verlo.",
    "Your exact settings re-applied at full resolution — JPG, PNG or WEBP.":
        "Tus ajustes exactos aplicados a resolución completa — JPG, PNG o WEBP.",
    # Footer
    "Background Remover": "Quitafondos de Imágenes",
    "Image Converter": "Conversor de Imágenes",
    "Image Compressor": "Compresor de Imágenes",
    "Meme Maker": "Creador de Memes",
    "Instagram Editor": "Editor para Instagram",
    "Crop Image": "Recortar Imagen",
    "Sticker Maker": "Creador de Stickers",
    "Text Behind Image": "Texto Detrás de la Imagen",
    "Watermark": "Marca de Agua",
    "GIF Maker": "Creador de GIF",
    "Passport Photo": "Foto de Pasaporte",
    "Product Photos": "Fotos de Producto",
    "Background Blur": "Desenfoque de Fondo",
    "Blur & Redact": "Desenfocar y Ocultar",
    "Favicon Generator": "Generador de Favicon",
    "QR Code Generator": "Generador de Códigos QR",
    "EXIF Remover": "Eliminador de EXIF",
    "Photo Filters": "Filtros de Fotos",
    "Image Upscaler": "Ampliador de Imágenes",
    "Video to GIF": "Vídeo a GIF",
    "Video Converter": "Conversor de Vídeo",
    "Base64 Image": "Imagen en Base64",
    "Colour Palette": "Paleta de Colores",
    "Photo Collage": "Collage de Fotos",
    "Border & Polaroid": "Marco y Polaroid",
    "Coming from another tool?": "¿Vienes de otra herramienta?",
    "See how we compare to remove.bg": "Mira cómo nos comparamos con remove.bg",
    "images processed": "imágenes procesadas",
    # Stat-strip labels under each number (see the hero badge in index.html).
    "this week": "esta semana",
    "all time": "en total",
    # --- How it works: what actually runs on the device ---
    "Three steps — with no server anywhere in them.": "Tres pasos — y ningún servidor en ninguno de ellos.",
    "What actually runs on your device": "Lo que realmente se ejecuta en tu dispositivo",
    "The cut-out comes from IS-Net, a segmentation model that runs through ONNX Runtime Web inside this browser tab. Your browser downloads the model once, then keeps it — so the second image is instant, and the tool keeps working with no connection at all.":
        "El recorte lo hace IS-Net, un modelo de segmentación que se ejecuta con ONNX Runtime Web dentro de esta misma pestaña. Tu navegador descarga el modelo una vez y lo guarda — por eso la segunda imagen es instantánea y la herramienta sigue funcionando sin conexión alguna.",
    "Where your browser exposes WebGPU, the model runs on your graphics card and off the main thread, which is why the page stays responsive while it works. Everywhere else it falls back to WebAssembly with SIMD and multiple threads on the CPU. Browsers that allow cross-origin isolation get the full-precision weights; the rest get a smaller quantised build of the same model.":
        "Cuando el navegador ofrece WebGPU, el modelo se ejecuta en tu tarjeta gráfica y fuera del hilo principal, y por eso la página sigue respondiendo mientras trabaja. En los demás casos recurre a WebAssembly con SIMD y varios hilos en la CPU. Los navegadores que permiten aislamiento de origen reciben los pesos en precisión completa; el resto recibe una versión cuantizada, más pequeña, del mismo modelo.",
    "What that means for your device: the first run is a real download and needs some memory, so it takes a few seconds on a recent laptop or phone and can take up to a minute on an older one. Every run after that is fast. If your browser can't run the model at all, the page says so plainly instead of hanging — and the editing tools that don't need AI (crop, convert, compress, resize) keep working regardless.":
        "Lo que eso significa para tu dispositivo: la primera vez es una descarga de verdad y necesita algo de memoria, así que tarda unos segundos en un portátil o móvil reciente y puede tardar hasta un minuto en uno más antiguo. Todas las veces siguientes son rápidas. Si tu navegador no puede ejecutar el modelo, la página te lo dice claramente en vez de quedarse colgada — y las herramientas de edición que no necesitan IA (recortar, convertir, comprimir, redimensionar) siguen funcionando igualmente.",
    "None of this involves an upload: there is no queue to wait in, no per-image limit to hit, and no copy of your photo on a server to trust anyone with.":
        "Nada de esto implica una subida: no hay cola de espera, no hay límite por imagen y no hay ninguna copia de tu foto en un servidor que tengas que confiar a nadie.",
    "Check it yourself:": "Compruébalo tú mismo:",
    "once you have made a single cut-out, turn off your Wi-Fi and reload this page. Every tool keeps working — the background remover included — because the page, the tools and the model are already on your device. Nothing else you have tried this in will survive that test.":
        "cuando hayas hecho un solo recorte, apaga el Wi-Fi y recarga esta página. Todas las herramientas siguen funcionando — el quitafondos incluido — porque la página, las herramientas y el modelo ya están en tu dispositivo. Ningún otro servicio que hayas probado supera esa prueba.",
    # --- Why is it free? ---
    "Why is it free?": "¿Por qué es gratis?",
    "The usual catch is that you are the product. Here is the actual arrangement.":
        "La trampa habitual es que el producto eres tú. Este es el acuerdo real.",
    "Your device does the work": "Tu dispositivo hace el trabajo",
    "Cloud removers rent GPUs by the second and bill you per image. Nothing here runs on a server, so there is no per-image cost to pass on — and no reason to cap you at five free photos.":
        "Los servicios en la nube alquilan GPUs por segundo y te cobran por imagen. Aquí nada se ejecuta en un servidor, así que no hay coste por imagen que repercutir — ni motivo para limitarte a cinco fotos gratis.",
    "There is nothing to sell": "No hay nada que vender",
    "Your images never leave the browser, so we could not train on them, sell them or leak them even if we wanted to. There is no account, so there is no profile to build either.":
        "Tus imágenes nunca salen del navegador, así que no podríamos entrenar con ellas, venderlas ni filtrarlas aunque quisiéramos. No hay cuenta, así que tampoco hay perfil que construir.",
    "What keeps it running": "Lo que lo mantiene en marcha",
    "A domain and some cheap hosting — that is the whole bill. Ads on the written guides help cover it, the tool pages stay ad-free, and a coffee from anyone who finds this useful covers the rest.":
        "Un dominio y alojamiento barato — esa es toda la factura. Los anuncios de las guías escritas ayudan a pagarla, las páginas de herramientas siguen sin anuncios, y un café de quien encuentre esto útil cubre el resto.",
    "No trial, no credit card, no watermark, no “pro” tier holding the good export hostage.":
        "Sin prueba gratuita, sin tarjeta, sin marca de agua y sin un plan «pro» que retenga la buena exportación.",
    "Tools": "Herramientas",
    "Use cases": "Casos de uso",
    # The footer heading is translated but the guide titles under it are not — the
    # articles themselves are English-only, and a Spanish label over English
    # content is the mismatch the hreflang gate exists to prevent.
    "Guides": "Guías",
    "All guides": "Todas las guías",
    "Company": "Empresa",
    "About": "Acerca de",
    "Privacy Policy": "Política de Privacidad",
    "Terms of Use": "Términos de Uso",
    "Contact": "Contacto",
    "Your images never leave your device — processing happens 100% in your browser.":
        "Tus imágenes nunca salen de tu dispositivo — todo el proceso ocurre 100% en tu navegador.",
    "This tool is free — if it saved you time, you can support it:":
        "Esta herramienta es gratis — si te ahorró tiempo, puedes apoyarla:",
    "Buy me a coffee": "Invítame a un café",
    "Free, private, and unlimited.": "Gratis, privado e ilimitado.",
    "Language": "Idioma",
    # Home page
    "Private & free — runs in your browser": "Privado y gratis — funciona en tu navegador",
    "Free Background Remover — No Upload, No Signup, No Watermark":
        "Eliminador de Fondos Gratis — Sin Subir Nada, Sin Registro, Sin Marca de Agua",
    "Remove image backgrounds free and unlimited — your photo never leaves your device. No upload, no sign-up, no watermark, full resolution.":
        "Quita el fondo de tus imágenes gratis y sin límites — tu foto nunca sale de tu dispositivo. Sin subir nada, sin registro, sin marca de agua, resolución completa.",
    "Free Background Remover": "Eliminador de Fondos Gratis",
    "No Upload Required": "Sin Subir Nada",
    "Remove image backgrounds automatically in seconds. 100% free, unlimited and private — your images never leave your device.":
        "Quita el fondo de tus imágenes automáticamente en segundos. 100% gratis, ilimitado y privado — tus imágenes nunca salen de tu dispositivo.",
    "Drag & drop your images": "Arrastra y suelta tus imágenes",
    "or click to browse — you can select multiple files":
        "o haz clic para buscar — puedes seleccionar varios archivos",
    "Select images": "Seleccionar imágenes",
    "Supports JPG, PNG & WEBP · Full resolution preserved":
        "Admite JPG, PNG y WEBP · Se conserva la resolución completa",
    "Your images never leave your device": "Tus imágenes nunca salen de tu dispositivo",
    "How it works": "Cómo funciona",
    # Shared landing-page strings
    "Why use it": "Por qué usarlo",
    "Ready to try it?": "¿Listo para probarlo?",
    "It's free, unlimited, and completely private.": "Es gratis, ilimitado y completamente privado.",
    "Remove a background now": "Quita un fondo ahora",
    "Open the free tool": "Abrir la herramienta gratuita",
    "Three steps, right in your browser. No account, no uploads.":
        "Tres pasos, en tu propio navegador. Sin cuenta y sin subidas.",
    "1. Add your image": "1. Añade tu imagen",
    "Drag & drop, browse, or paste — batch upload works too.":
        "Arrastra y suelta, busca o pega — también funciona por lotes.",
    "2. AI removes the background": "2. La IA quita el fondo",
    "Runs on your device in seconds — nothing is uploaded.":
        "Funciona en tu dispositivo en segundos — no se sube nada.",
    "3. Download": "3. Descarga",
    "Transparent PNG, or pick a background color. Full quality.":
        "PNG transparente, o elige un color de fondo. Calidad completa.",
    # --- Home page: how-it-works steps ---
    "Add": "Añade",
    "an image — drag, browse or paste": "una imagen — arrastra, busca o pega",
    "AI removes": "La IA quita",
    "the background on your device": "el fondo en tu dispositivo",
    "a transparent PNG, full quality": "un PNG transparente, con calidad completa",
    # --- Remover workspace ---
    "Your results": "Tus resultados",
    "processed": "procesadas",
    "avg": "media",
    "saved": "ahorrado",
    "images total": "imágenes en total",
    "Download all (ZIP)": "Descargar todo (ZIP)",
    "Add more": "Añadir más",
    "Clear": "Limpiar",
    "Recent this session": "Recientes de esta sesión",
    "Clear history": "Borrar historial",
    # --- Result card ---
    "Before": "Antes",
    "After": "Después",
    "Original": "Original",
    "Result": "Resultado",
    "Removing background…": "Quitando el fondo…",
    "Something went wrong.": "Algo salió mal.",
    "Try again": "Intentar de nuevo",
    "Background": "Fondo",
    "Size & format": "Tamaño y formato",
    "Effects": "Efectos",
    "Fill style": "Estilo de relleno",
    "Gradient": "Degradado",
    "Blur photo": "Desenfocar foto",
    "Image": "Imagen",
    "Use your own photo": "Usa tu propia foto",
    "Photo backgrounds": "Fondos fotográficos",
    "Format": "Formato",
    "Export size": "Tamaño de exportación",
    "Profile": "Perfil",
    "Story": "Story",
    "Sticker effects": "Efectos de sticker",
    "Outline": "Contorno",
    "Drop shadow": "Sombra",
    "Padding": "Margen",
    "Trim transparent edges": "Recortar bordes transparentes",
    "Crop the export down to the subject, removing empty transparent margins":
        "Recorta la exportación hasta el sujeto, eliminando los márgenes transparentes vacíos",
    "Apply these options to all images": "Aplicar estas opciones a todas las imágenes",
    "Refine": "Refinar",
    "Style & export": "Estilo y exportación",
    "Copy result": "Copiar resultado",
    "Side-by-side": "Lado a lado",
    "Continue in": "Continuar en",
    "Sticker": "Sticker",
    "Download": "Descargar",
    # --- Refine editor ---
    "Refine edges": "Refinar bordes",
    "Cancel": "Cancelar",
    "Apply": "Aplicar",
    "Tool": "Herramienta",
    "Restore": "Restaurar",
    "Erase": "Borrar",
    "Move": "Mover",
    "Brush size": "Tamaño del pincel",
    "Smooth edges": "Suavizar bordes",
    "Zoom": "Zoom",
    "Undo": "Deshacer",
    "Redo": "Rehacer",
    "Reset": "Restablecer",
    "Show original": "Ver original",
    "ghosts the photo underneath so you can see what to paint back.":
        "muestra la foto por debajo para que veas qué recuperar con el pincel.",
    "size,": "tamaño,",
    "paints back the original;": "recupera el original;",
    "wipes leftover background.": "borra el fondo que quede.",
    "Scroll to zoom, or use the": "Desplaza para hacer zoom, o usa la herramienta",
    "tool / hold": "/ mantén",
    "to pan.": "para desplazarte.",
    "Shortcuts:": "Atajos:",
    "size.": "tamaño.",
    # --- Crop dialog ---
    "Crop image": "Recortar imagen",
    "Remove crop": "Quitar recorte",
    "Source": "Origen",
    "Cut-out": "Recorte",
    "keeps the background.": "conserva el fondo.",
    "uses the removed-background result.": "usa el resultado sin fondo.",
    "Shape": "Forma",
    "Circle": "Círculo",
    "Square": "Cuadrado",
    "Round": "Redondeado",
    "Custom ratio": "Proporción personalizada",
    "Orientation": "Orientación",
    "Rotate": "Girar",
    "Flip": "Voltear",
    "Pick a shape or a": "Elige una forma o una",
    "custom ratio": "proporción personalizada",
    "then": "y luego",
    "drag": "arrastra",
    "to reposition and": "para recolocar y",
    "scroll": "desplaza",
    "to zoom. Rotate and flip from the buttons above.":
        "para hacer zoom. Gira y voltea con los botones de arriba.",
    # --- Shortcuts modal ---
    "Keyboard shortcuts": "Atajos de teclado",
    "Paste image from clipboard": "Pegar imagen del portapapeles",
    "Open file picker": "Abrir el selector de archivos",
    "Download all as ZIP": "Descargar todo en ZIP",
    "Toggle dark mode": "Cambiar modo oscuro",
    "Close dialogs": "Cerrar diálogos",
    "Remove a background": "Quitar un fondo",
    # --- Quick background presets (remover) ---
    "Quick presets": "Ajustes rápidos",
    "Transparent": "Transparente",
    "White": "Blanco",
    "Studio": "Estudio",
    # --- Batch bar (resize / watermark / EXIF) ---
    "images queued": "imágenes en cola",
    "Download all as ZIP (%d)": "Descargar todo en ZIP (%d)",
    # --- Resizer + EXIF remover (tool pages translated in 1.11) ---
    'Free Image Resizer — Resize Photos by Pixels or Percentage':
        'Redimensionar Imágenes Gratis — Por Píxeles o Porcentaje',
    'Resize any image to exact pixels or a percentage, free and in your browser. Lock the aspect ratio, pick a preset, and export JPG, PNG or WEBP.':
        'Redimensiona cualquier imagen a píxeles exactos o a un porcentaje, gratis y en tu navegador. Bloquea la proporción, elige un ajuste y exporta JPG, PNG o WEBP.',
    'Free Image Resizer — Exact Pixels, Private':
        'Redimensionar Imágenes Gratis — Píxeles Exactos, Privado',
    'Made locally — nothing is uploaded': 'Hecho localmente — no se sube nada',
    'Resizer': 'Redimensionador',
    'Resize any photo to exact': 'Redimensiona cualquier foto a',
    'pixels': 'píxeles exactos',
    'or a': 'o a un',
    'percentage': 'porcentaje',
    '— aspect ratio locked so nothing stretches. Free, full quality and 100% private.':
        '— con la proporción bloqueada para que nada se deforme. Gratis, con calidad completa y 100% privado.',
    'or click to browse — JPG, PNG or WEBP · pick several to resize a batch':
        'o haz clic para buscar — JPG, PNG o WEBP · elige varias para redimensionar un lote',
    'Width': 'Ancho',
    'Height': 'Alto',
    'Lock aspect ratio': 'Bloquear proporción',
    'Fit within': 'Ajustar a',
    'Same': 'Igual',
    'New': 'Nueva',
    'Resize in three steps': 'Redimensionar en tres pasos',
    "Any JPG, PNG or WEBP — it's read straight in your browser.":
        'Cualquier JPG, PNG o WEBP — se lee directamente en tu navegador.',
    'Set the size': 'Define el tamaño',
    'Type exact pixels, pick a percentage, or fit within a preset. Aspect ratio stays locked.':
        'Escribe los píxeles exactos, elige un porcentaje o ajústala a una medida. La proporción se mantiene bloqueada.',
    'Export JPG, PNG or WEBP at the new size — free, no watermark.':
        'Exporta JPG, PNG o WEBP en el nuevo tamaño — gratis y sin marca de agua.',
    'Free EXIF Remover — View & Remove Photo Metadata (GPS)':
        'Eliminar EXIF Gratis — Ver y Borrar Metadatos de Fotos (GPS)',
    'See and remove the hidden metadata in your photos — GPS location, camera, date and more. Strips EXIF losslessly, in your browser, nothing uploaded.':
        'Mira y borra los metadatos ocultos de tus fotos — ubicación GPS, cámara, fecha y más. Elimina el EXIF sin pérdidas, en tu navegador y sin subir nada.',
    'EXIF Remover — Strip Photo Metadata & GPS, Free & Private':
        'Eliminar EXIF — Borra Metadatos y GPS, Gratis y Privado',
    'Read locally — nothing is uploaded': 'Leído localmente — no se sube nada',
    'EXIF & Metadata': 'EXIF y Metadatos',
    'Remover': 'Eliminar',
    'See the hidden data in your photos —': 'Mira los datos ocultos de tus fotos —',
    'GPS location': 'ubicación GPS',
    ', camera, date — and strip it out before you share. Lossless, free and 100% private.':
        ', cámara, fecha — y bórralos antes de compartir. Sin pérdidas, gratis y 100% privado.',
    'or click to browse — JPG photos carry the most hidden data · pick several to clean a batch':
        'o haz clic para buscar — las fotos JPG son las que más datos ocultan · elige varias para limpiar un lote',
    'No photo handy?': '¿No tienes ninguna foto a mano?',
    'Try a sample photo': 'Prueba con una foto de ejemplo',
    '— a real JPEG with GPS and camera data inside.':
        '— un JPEG real con datos de GPS y de la cámara dentro.',
    'Location data found': 'Se encontraron datos de ubicación',
    'All metadata': 'Todos los metadatos',
    'Download clean copy': 'Descargar copia limpia',
    'New photo': 'Nueva foto',
    "What's hiding in your photos": 'Lo que se esconde en tus fotos',
    'Phones tag photos with the exact coordinates they were taken — often your home. Strip it before posting.':
        'Los móviles etiquetan las fotos con las coordenadas exactas donde se tomaron — a menudo tu casa. Bórralas antes de publicar.',
    'Date & device': 'Fecha y dispositivo',
    'The exact timestamp, camera and even the software used are all embedded in the file.':
        'La hora exacta, la cámara e incluso el software usado están incrustados en el archivo.',
    'Lossless & private': 'Sin pérdidas y privado',
    'JPEGs are cleaned losslessly with zero quality loss, and nothing ever leaves your device.':
        'Los JPEG se limpian sin ninguna pérdida de calidad, y nada sale de tu dispositivo.',
    'Why this one runs on your device': 'Por qué esta herramienta corre en tu dispositivo',
    "You can check this yourself: open your browser's network panel, run the tool, and watch it stay silent. Or turn off your Wi-Fi — the tool keeps working.":
        'Puedes comprobarlo tú: abre el panel de red del navegador, usa la herramienta y verás que no dice nada. O apaga el Wi-Fi — la herramienta sigue funcionando.',
    "Resize your": "Redimensiona tus",
    "Photos": "Fotos",
    "Remove EXIF &": "Elimina EXIF y",
    "Metadata": "Metadatos",
    # --- Converter + compressor (translated in 1.11) ---
    'Free Image Converter — PNG, JPG & WEBP in Your Browser':
        'Conversor de Imágenes Gratis — PNG, JPG y WEBP en tu Navegador',
    'Convert images between PNG, JPG and WEBP for free. Auto-detects the input format and converts locally in your browser — no uploads, batch supported.':
        'Convierte imágenes entre PNG, JPG y WEBP gratis. Detecta el formato de origen y convierte localmente en tu navegador — sin subidas y por lotes.',
    'Free Image Format Converter — Private & Instant':
        'Conversor de Formatos Gratis — Privado e Instantáneo',
    'Convert locally — nothing is uploaded': 'Convertido localmente — no se sube nada',
    'Convert Images to': 'Convierte Imágenes a',
    'Any Format': 'Cualquier Formato',
    'Drop any image — we detect its format automatically. Pick a target format and download instantly. Batch supported, full quality, 100% private.':
        'Suelta cualquier imagen — detectamos su formato automáticamente. Elige el formato de destino y descarga al instante. Por lotes, con calidad completa y 100% privado.',
    'Detects PNG, JPG, WEBP, GIF, BMP & more · Converts to PNG, JPG, WEBP or AVIF':
        'Detecta PNG, JPG, WEBP, GIF, BMP y más · Convierte a PNG, JPG, WEBP o AVIF',
    'Convert to': 'Convertir a',
    'Supported output formats': 'Formatos de salida admitidos',
    'Converting…': 'Convirtiendo…',
    'Compress Images Free — Shrink JPG, PNG & WEBP In-Browser':
        'Comprimir Imágenes Gratis — Reduce JPG, PNG y WEBP en el Navegador',
    'Compress and shrink images for free — reduce JPG, PNG and WEBP file size with a quality slider or a target size. In your browser, batch supported.':
        'Comprime y reduce imágenes gratis — baja el tamaño de JPG, PNG y WEBP con un control de calidad o un tamaño objetivo. En tu navegador y por lotes.',
    'Free Image Compressor — Shrink Images Privately & Instantly':
        'Compresor de Imágenes Gratis — Reduce de Forma Privada e Instantánea',
    'Compress Images to a': 'Comprime Imágenes a un',
    'Smaller Size': 'Tamaño Menor',
    'Drop an image and shrink its file size — set a quality level or a target size like':
        'Suelta una imagen y reduce su tamaño — fija un nivel de calidad o un tamaño objetivo como',
    'under 200 KB': 'menos de 200 KB',
    '. Batch supported, full control, 100% private.':
        '. Por lotes, con control total y 100% privado.',
    'Shrinks JPG, PNG & WEBP · Choose a quality or a target file size':
        'Reduce JPG, PNG y WEBP · Elige una calidad o un tamaño objetivo',
    'Quality': 'Calidad',
    'Target size': 'Tamaño objetivo',
    'Max dimension': 'Dimensión máxima',
    'How to compress an image': 'Cómo comprimir una imagen',
    'Drop your images': 'Suelta tus imágenes',
    'Add one or many — JPG, PNG or WEBP. Everything stays on your device.':
        'Añade una o varias — JPG, PNG o WEBP. Todo se queda en tu dispositivo.',
    'Pick quality or size': 'Elige calidad o tamaño',
    'Slide the quality, or set a target like “under 200 KB” and we hit it automatically.':
        'Mueve la calidad, o fija un objetivo como “menos de 200 KB” y lo alcanzamos automáticamente.',
    'Grab the smaller file, or download them all as a ZIP. No watermark, no sign-up.':
        'Llévate el archivo más pequeño, o descárgalos todos en un ZIP. Sin marca de agua y sin registro.',
    'Compressing…': 'Comprimiendo…',
}


# --- Runtime (JavaScript) strings --------------------------------------------
# Messages the tools raise while you use them. These live apart from UI because
# they are shipped to the browser as JSON (see translations.js_catalogue) rather
# than rendered by {% t %} — sending the whole UI catalogue would mean paying for
# the marketing copy on every tool page.
#
# `{name}`-style placeholders are filled in by CBG.t(key, vars). Keep them in
# every language; a missing placeholder silently drops the value, which
# JsTranslationTests fails the build over.
#
# Singular/plural pairs are two separate keys picked by CBG.plural(n, …),
# because Spanish and English do not always agree on which counts are plural.
JS_UI = {
    # --- Input / file handling ---
    "Please choose an image": "Elige una imagen",
    "Please choose image files": "Elige archivos de imagen",
    "Couldn't open that image": "No se pudo abrir esa imagen",
    "Could not read that image": "No se pudo leer esa imagen",
    "No file chosen": "Ningún archivo elegido",
    "That is not a .docx file": "Ese no es un archivo .docx",
    "That file could not be read as a Word document": "No se pudo leer ese archivo como documento de Word",
    "This is an old .doc file. Open it in Word and save as .docx first.":
        "Este es un archivo .doc antiguo. Ábrelo en Word y guárdalo primero como .docx.",
    "{n} row": "{n} fila",
    "{n} rows": "{n} filas",
    "{n} column": "{n} columna",
    "{n} columns": "{n} columnas",
    "{n} file": "{n} archivo",
    "{n} files": "{n} archivos",
    "{n} word": "{n} palabra",
    "Drop a CSV file": "Suelta un archivo CSV",
    "Drop an Excel file": "Suelta un archivo Excel",
    "or click to browse — .csv or .tsv": "o haz clic para buscar — .csv o .tsv",
    "or click to browse — .xlsx": "o haz clic para buscar — .xlsx",
    "Download .xlsx": "Descargar .xlsx",
    "Download .csv": "Descargar .csv",
    "Could not read that CSV file": "No se pudo leer ese archivo CSV",
    "Could not read that Excel file": "No se pudo leer ese archivo Excel",
    "That file has no rows": "Ese archivo no tiene filas",
    "Preview shows the first rows and columns only — the whole file is converted.":
        "La vista previa muestra solo las primeras filas y columnas — el archivo se convierte por completo.",
    "Conversion failed": "La conversión falló",
    "Excel file ready": "Archivo Excel listo",
    "CSV ready — import it in Google Sheets with File → Import":
        "CSV listo — impórtalo en Google Sheets con Archivo → Importar",
    "Drop your PDFs": "Suelta tus PDF",
    "Drop a PDF to split": "Suelta un PDF para dividir",
    "or click to browse — add as many as you like":
        "o haz clic para buscar — añade todos los que quieras",
    "or click to browse — one file": "o haz clic para buscar — un archivo",
    "Merge into one PDF": "Unir en un solo PDF",
    "Split into separate PDFs": "Dividir en PDF separados",
    "Could not read {name} — it may be password-protected":
        "No se pudo leer {name} — puede estar protegido con contraseña",
    "Leave empty to get every page as its own PDF.":
        "Déjalo vacío para obtener cada página como su propio PDF.",
    "Not a valid range: ": "Intervalo no válido: ",
    "Add at least two PDFs to merge": "Añade al menos dos PDF para unir",
    "Merged PDF ready": "PDF unido listo",
    "No pages selected": "Ninguna página seleccionada",
    "Split PDF ready": "PDF dividido listo",
    "Remove": "Quitar",
    "This PDF has no text — it is probably a scan. Try the Image to Text tool.":
        "Este PDF no tiene texto — probablemente sea un escaneo. Prueba la herramienta Imagen a Texto.",
    "Word document ready": "Documento de Word listo",
    "Could not load that image": "No se pudo cargar esa imagen",
    "Could not read {name}": "No se pudo leer {name}",
    "{name}: too large (max {max})": "{name}: demasiado grande (máx. {max})",
    "{name}: unsupported format (use JPG, PNG or WEBP)":
        "{name}: formato no admitido (usa JPG, PNG o WEBP)",
    "Couldn't load the sample": "No se pudo cargar el ejemplo",
    "Couldn't load that logo": "No se pudo cargar ese logo",
    "Cleared all images": "Se borraron todas las imágenes",
    "History cleared": "Historial borrado",
    "Add at least 2 photos": "Añade al menos 2 fotos",
    "Add more images to apply options to all":
        "Añade más imágenes para aplicar las opciones a todas",
    # --- Export ---
    "Export failed": "Falló la exportación",
    "Building ZIP…": "Creando el ZIP…",
    "Could not build the ZIP": "No se pudo crear el ZIP",
    "Could not build the GIF": "No se pudo crear el GIF",
    "Please choose a video file": "Elige un archivo de vídeo",
    "This video format can't be read in your browser — try an MP4 or WebM.":
        "Tu navegador no puede leer este formato de vídeo — prueba con MP4 o WebM.",
    "Could not convert the video": "No se pudo convertir el vídeo",
    "Could not build the PDF": "No se pudo crear el PDF",
    "Building your icon pack…": "Creando tu pack de iconos…",
    "Could not build the icon pack": "No se pudo crear el pack de iconos",
    "Icon pack downloaded": "Pack de iconos descargado",
    "Could not prepare the download": "No se pudo preparar la descarga",
    "WebP not supported here — downloading PNG instead":
        "WebP no es compatible aquí — se descarga PNG en su lugar",
    "Building carousel ZIP…": "Creando el ZIP del carrusel…",
    "Carousel export failed": "Falló la exportación del carrusel",
    "Saved a {n}-tile carousel — post the tiles in order":
        "Guardado un carrusel de {n} piezas — publícalas en orden",
    "Saved crop {w}×{h}": "Recorte guardado {w}×{h}",
    "Saved {w}×{h} for Instagram": "Guardado {w}×{h} para Instagram",
    "Photo is larger than a 6×4 print": "La foto es mayor que una copia de 15×10",
    # --- Clipboard ---
    "Copied to clipboard": "Copiado al portapapeles",
    "Meme copied to clipboard": "Meme copiado al portapapeles",
    "HTML copied to clipboard": "HTML copiado al portapapeles",
    "Copy failed": "No se pudo copiar",
    "Clipboard not supported in this browser":
        "Este navegador no admite el portapapeles",
    "Copy not supported here — use Download": "Copiar no funciona aquí — usa Descargar",
    # --- Background removal ---
    "Background removal failed": "No se pudo quitar el fondo",
    "Added to pack": "Añadido al paquete",
    "Pack downloaded": "Paquete descargado",
    "Background removed": "Fondo eliminado",
    # Live status on the result card while a cut-out is being made.
    "Removing background…": "Quitando el fondo…",
    "Downloading AI model… {pct}%": "Descargando el modelo de IA… {pct}%",
    # --- Model status badge (app.js ModelStatus) ---
    "Loading the AI": "Cargando la IA",
    "one-time": "una sola vez",
    "AI ready — GPU-accelerated, runs 100% on your device":
        "IA lista — acelerada por GPU, funciona 100% en tu dispositivo",
    "AI ready — runs 100% on your device": "IA lista — funciona 100% en tu dispositivo",
    "first image may take a little longer here":
        "aquí la primera imagen puede tardar un poco más",
    "Could not preload the AI here — it will try again when you add an image":
        "No se pudo precargar la IA — lo intentará de nuevo al añadir una imagen",
    # --- Support nudge (kit.js showSupport) ---
    "Everything here stays free. If it saved you some time, a coffee helps keep it that way.":
        "Todo esto seguirá siendo gratis. Si te ahorró tiempo, un café ayuda a que siga así.",
    "Buy me a coffee": "Invítame a un café",
    "Dismiss": "Cerrar",
    # Shown on cards waiting their turn in the batch queue, with a rough ETA
    # measured from how fast this device actually works.
    "Next up": "La siguiente",
    "#{n} in line": "#{n} en la cola",
    "about {n}s": "unos {n} s",
    "about {m}m": "unos {m} min",
    "about {m}m {s}s": "unos {m} min {s} s",
    "GPU acceleration failed — reload the page to switch to CPU mode":
        "Falló la aceleración por GPU — recarga la página para pasar a modo CPU",
    "Background removed — add your outline & text":
        "Fondo eliminado — añade tu contorno y texto",
    "Background removed — position the head inside the guides":
        "Fondo eliminado — coloca la cabeza dentro de las guías",
    "Could not cut out the subject": "No se pudo recortar el sujeto",
    "Could not find the subject": "No se encontró el sujeto",
    "Portrait blur applied — adjust the strength":
        "Desenfoque de retrato aplicado — ajusta la intensidad",
    # --- Editing ---
    "Crop applied": "Recorte aplicado",
    "Edits applied": "Cambios aplicados",
    "Could not open the image to crop": "No se pudo abrir la imagen para recortar",
    "Could not render the crop preview":
        "No se pudo generar la vista previa del recorte",
    "Type your text and drag it behind the subject":
        "Escribe tu texto y arrástralo detrás del sujeto",
    'Saved look "{name}"': 'Estilo "{name}" guardado',
    # --- Redaction ---
    "Face detection is not available in this browser":
        "La detección de caras no está disponible en este navegador",
    "No faces found — draw over them by hand":
        "No se encontraron caras — dibuja sobre ellas a mano",
    "{n} face hidden — adjust or add more by hand":
        "{n} cara oculta — ajústala o añade más a mano",
    "{n} faces hidden — adjust or add more by hand":
        "{n} caras ocultas — ajústalas o añade más a mano",
    # --- Batch ---
    "Applied to {n} other image": "Aplicado a {n} imagen más",
    "Applied to {n} other images": "Aplicado a {n} imágenes más",
    "Ready — {n} photo. Pick a marketplace and download.":
        "Lista — {n} foto. Elige un marketplace y descarga.",
    "Ready — {n} photos. Pick a marketplace and download.":
        "Listas — {n} fotos. Elige un marketplace y descarga.",
    # --- Errors ---
    "Error: {message}": "Error: {message}",
    "Failed: {detail}": "Falló: {detail}",
    # --- Compressor quality compare ---
    "Original": "Original",
    # --- Base64 / palette / collage / border ---
    "That is not a valid image data URI": "Ese no es un data URI de imagen válido",
    "Click to copy": "Haz clic para copiar",
    "Copied {value}": "Copiado {value}",
    "Palette copied as CSS": "Paleta copiada como CSS",
    "Palette copied as {kind}": "Paleta copiada como {kind}",
    "Remove": "Quitar",
    "{n} photo": "{n} foto",
    "{n} photos": "{n} fotos",
    # --- Cross-tool chaining (kit.js) ---
    "Keep editing this image:": "Sigue editando esta imagen:",
    "— keep going:": "— continúa:",
    "Carried over from {tool}": "Traída desde {tool}",
    # --- Share sheet (kit.js) ---
    "Share": "Compartir",
    "Ready to share:": "Lista para compartir:",
    # Rides along as the caption where the target app accepts one, so it is the
    # one piece of copy here that a stranger reads. Kept to a plain statement of
    # where the image came from — anything more is a caption the user did not
    # write, on a message they did.
    "Made with clearbg.pt": "Hecho con clearbg.pt",
    "Could not open the share sheet": "No se pudo abrir el menú de compartir",
    # --- Remove object ---
    "Brush over the object first": "Pinta primero sobre el objeto",
    "Object erased — download or keep brushing":
        "Objeto borrado — descarga o sigue pintando",
    "Erase failed": "No se pudo borrar",
    # --- Upscale ---
    "capped": "limitado",
    "Upscaled to {w}×{h}": "Ampliado a {w}×{h}",
    "Could not upscale that image": "No se pudo ampliar esa imagen",
    # --- HEIC ---
    "Those are not HEIC files — drop .heic photos":
        "Esos archivos no son HEIC — suelta fotos .heic",
    "Converting…": "Convirtiendo…",
    "Could not convert {name}": "No se pudo convertir {name}",
    "Converted {n} photo": "{n} foto convertida",
    "Converted {n} photos": "{n} fotos convertidas",
    # --- PDF to images ---
    "That is not a PDF file": "Ese archivo no es un PDF",
    "Reading PDF…": "Leyendo el PDF…",
    "Could not read that PDF": "No se pudo leer ese PDF",
    "{n} page": "{n} página",
    "{n} pages": "{n} páginas",
    "Page": "Página",
    "Page {n} failed": "Falló la página {n}",
    # --- OCR ---
    "Reading…": "Leyendo…",
    "No text found in that image": "No se encontró texto en esa imagen",
    "{n} words": "{n} palabras",
    "Could not read the text": "No se pudo leer el texto",
    # --- SVG to PNG ---
    "That is not an SVG file": "Ese archivo no es un SVG",
    "Could not render that SVG": "No se pudo renderizar ese SVG",
    # --- Filters / upscale batch ---
    "Exported {n} photo": "{n} foto exportada",
    "Exported {n} photos": "{n} fotos exportadas",
    # --- Video frame grab ---
    "Could not capture that frame": "No se pudo capturar ese fotograma",
    "Frame captured — pick a tool below to edit it":
        "Fotograma capturado — elige abajo una herramienta para editarlo",
    # --- Compressor zero-savings hint ---
    "already optimized: try WEBP or AVIF, or lower the quality":
        "ya optimizada: prueba WEBP o AVIF, o baja la calidad",
    # --- PWA install offer ---
    'Install ClearBG to keep these tools one tap away — they work offline too.':
        'Instala ClearBG para tener estas herramientas a un toque — también funcionan sin conexión.',
    'Install': 'Instalar',
}

# --- Use-case landings (keyed by slug) ---------------------------------------
# Merged shallowly over the English case in views.USE_CASES, so a key given here
# REPLACES its English counterpart outright — `benefits` has to repeat the icons
# rather than only the copy it changes.
USE_CASES = {
    "product-photos": {
        "nav": "Fotos de producto",
        "title": "Quitar el Fondo de Fotos de Producto — Gratis e Instantáneo",
        "description": "Crea fotos de producto limpias, en blanco o transparentes, para tu tienda online. Gratis e ilimitado — la IA corre en tu navegador y no se sube nada.",
        "h1": "Quita el Fondo de tus Fotos de Producto",
        "tagline": "Dale a tu tienda un aspecto uniforme y profesional con recortes limpios — gratis, ilimitado y procesado por completo en tu dispositivo.",
        "intro": [
            "Marketplaces como Amazon, eBay, Etsy y Shopify convierten mejor cuando cada producto aparece sobre un fondo limpio y uniforme. Esta herramienta quita el fondo de tus fotos de producto en segundos, para que exportes un PNG transparente o pongas un fondo blanco puro.",
            "Como la IA corre localmente en tu navegador, puedes procesar un catálogo entero sin subir una sola imagen, sin límites de API y sin pagar por foto.",
        ],
        "benefits": [
            {"icon": "fa-store", "title": "Listo para marketplaces", "text": "Exporta sobre blanco puro para anuncios estilo Amazon, o PNG transparentes para componer donde quieras."},
            {"icon": "fa-layer-group", "title": "Procesa el catálogo en lote", "text": "Suelta decenas de fotos de producto a la vez y descárgalas juntas en un ZIP."},
            {"icon": "fa-crop-simple", "title": "Resolución completa", "text": "Mantiene la calidad original — sin reducir el tamaño y sin marca de agua en tus imágenes."},
        ],
    },
    "profile-picture": {
        "nav": "Fotos de perfil",
        "title": "Quitar el Fondo de una Foto de Perfil — Gratis y Privado",
        "description": "Quita el fondo de tu foto de perfil o retrato para LinkedIn, un CV o redes sociales. 100% gratis y privado — las imágenes nunca salen de tu navegador.",
        "h1": "Quita el Fondo de tu Foto de Perfil",
        "tagline": "Retratos y avatares perfectos para LinkedIn, CV y perfiles sociales — cambia el fondo por cualquier color, todo en tu navegador.",
        "intro": [
            "Un retrato limpio hace que tu LinkedIn, tu CV o tu perfil social se vean cuidados. Sube tu foto y la IA te separa del fondo, para que lo dejes transparente o pongas un color sólido de marca.",
            "Todo ocurre en tu dispositivo — tu foto nunca se sube, lo que mantiene una imagen personal completamente privada.",
        ],
        "benefits": [
            {"icon": "fa-user", "title": "Recortes favorecedores", "text": "Preparada para el pelo y los bordes suaves, con un pincel de refinado para los últimos retoques."},
            {"icon": "fa-swatchbook", "title": "Cualquier color de fondo", "text": "Combina con una paleta de marca o un fondo de estudio liso, y exporta en PNG, JPG o WEBP."},
            {"icon": "fa-shield-halved", "title": "Privado por diseño", "text": "Tu cara nunca sale de tu navegador — no se envía nada a un servidor."},
        ],
    },
    "logo": {
        "nav": "Logotipos",
        "title": "Quitar el Fondo de un Logotipo — Consigue un PNG Transparente",
        "description": "Convierte un logotipo con fondo sólido en un PNG transparente y limpio. Gratis, ilimitado y procesado de forma privada en tu navegador — sin registro.",
        "h1": "Haz Transparente el Fondo de tu Logotipo",
        "tagline": "Convierte un logotipo plano en un PNG transparente que puedes poner sobre cualquier color, diapositiva o web — gratis e instantáneo.",
        "intro": [
            "¿Tienes un logotipo atrapado en un cuadrado blanco o de color? Esta herramienta quita ese fondo y te da un PNG transparente que encaja limpiamente en cualquier web, documento o presentación.",
            "Todo corre en tu navegador a resolución completa, así que tus recursos de marca siguen nítidos y nunca se suben a ninguna parte.",
        ],
        "benefits": [
            {"icon": "fa-vector-square", "title": "Transparencia limpia", "text": "Quita fondos sólidos para que tu logotipo se apoye sobre cualquier color sin halo."},
            {"icon": "fa-brush", "title": "Refina los bordes", "text": "Limpia los píxeles que sobran o recupera detalles finos con el pincel de bordes integrado."},
            {"icon": "fa-crop-simple", "title": "Exportación con calidad completa", "text": "Descarga un PNG sin pérdidas y a resolución completa — nunca con marca de agua."},
        ],
    },
    "signature": {
        "nav": "Firmas",
        "title": "Quitar el Fondo de una Firma — PNG Transparente",
        "description": "Convierte una foto o un escaneo de tu firma manuscrita en un PNG transparente para documentos y contratos. Gratis — corre en tu navegador.",
        "h1": "Crea una Firma Transparente",
        "tagline": "Convierte un escaneo o una foto de tu firma manuscrita en un PNG transparente y limpio para contratos y documentos.",
        "intro": [
            "Firma una hoja en blanco, fotografíala o escanéala y suéltala aquí. La IA quita el fondo de papel y deja solo la tinta como un PNG transparente que puedes colocar en cualquier PDF o documento.",
            "Como todo el proceso corre en tu navegador, tu firma — un dato sensible — nunca se sube a un servidor.",
        ],
        "benefits": [
            {"icon": "fa-stamp", "title": "Lista para documentos", "text": "Consigue tinta transparente que puedes colocar directamente en PDF, contratos y cartas."},
            {"icon": "fa-shield-halved", "title": "Se queda en privado", "text": "Tu firma nunca sale de tu dispositivo — no se envía nada a ninguna parte."},
            {"icon": "fa-wand-magic-sparkles", "title": "Aislado limpio", "text": "Separa la tinta de la textura del papel y de las sombras, con un pincel para refinar el resultado."},
        ],
    },
    "car-photos": {
        "nav": "Fotos de coches",
        "title": "Quitar el Fondo de Fotos de Coches — Gratis e Instantáneo",
        "description": "Quita el fondo de fotos de coches para anuncios de concesionarios y marketplaces. Pon cualquier vehículo sobre blanco o transparente — gratis, en tu navegador.",
        "h1": "Quita el Fondo de tus Fotos de Coches",
        "tagline": "Dale a cada vehículo una foto de anuncio limpia y uniforme para tu concesionario o tu marketplace — gratis, ilimitado y procesado en tu dispositivo.",
        "intro": [
            "Los anuncios de coches se venden más rápido cuando cada vehículo aparece sobre un fondo limpio y uniforme en lugar de un aparcamiento desordenado. Esta herramienta recorta el fondo de tus fotos de coches en segundos, para que pongas blanco puro o mantengas un PNG transparente para tu plantilla.",
            "Como la IA corre localmente en tu navegador, puedes procesar todo el stock sin subir una sola foto, sin límites de API y sin pagar por imagen.",
        ],
        "benefits": [
            {"icon": "fa-square-full", "title": "Limpio como un concesionario", "text": "Cambia un aparcamiento desordenado por un fondo de estudio impecable que mantiene el foco en el coche."},
            {"icon": "fa-layer-group", "title": "Lotes completos", "text": "Suelta decenas de fotos a la vez y descárgalas juntas en un ZIP."},
            {"icon": "fa-clock", "title": "Instantáneo y gratis", "text": "Sin coste por foto y sin marca de agua — resolución completa siempre."},
        ],
    },
    "clothing": {
        "nav": "Ropa y moda",
        "title": "Quitar el Fondo de Fotos de Ropa — Gratis para Revendedores",
        "description": "Quita el fondo de fotos de ropa y moda para Vinted, Depop, Poshmark o tu tienda. PNG limpios en blanco o transparentes — gratis y en tu navegador.",
        "h1": "Quita el Fondo de tus Fotos de Ropa",
        "tagline": "Convierte fotos de móvil de ropa en fotos de producto limpias y vendibles para Vinted, Depop, Poshmark o tu tienda — gratis e ilimitado.",
        "intro": [
            "La moda de segunda mano y de boutique se vende más rápido cuando cada prenda se ve uniforme y profesional. Sube la foto de una prenda y la IA la separa de tu alfombra, tu percha o tu pared, para que la pongas sobre blanco limpio o un fondo transparente.",
            "Todo corre en tu navegador a resolución completa, así que puedes preparar un armario entero de anuncios en privado — sin subidas y sin tarifas por foto.",
        ],
        "benefits": [
            {"icon": "fa-store", "title": "Vendible en segundos", "text": "Recortes limpios de tops, vestidos y zapatos que encajan en cualquier cuadrícula de tienda."},
            {"icon": "fa-bookmark", "title": "Anuncios uniformes", "text": "Dale a cada prenda el mismo fondo cuidado para que tu escaparate se vea profesional."},
            {"icon": "fa-shield-halved", "title": "Privado por diseño", "text": "Tus fotos nunca salen de tu dispositivo — no se sube nada a un servidor."},
        ],
    },
    "pet-photos": {
        "nav": "Fotos de mascotas",
        "title": "Quitar el Fondo de Fotos de Mascotas — Gratis y Privado",
        "description": "Recorta a tu perro, gato o cualquier mascota de una foto gratis. Crea PNG transparentes para pegatinas, impresiones y memes — en tu navegador.",
        "h1": "Quita el Fondo de tus Fotos de Mascotas",
        "tagline": "Recorta a tu perro, gato o amigo peludo para pegatinas, impresiones, tazas y memes — gratis, ilimitado y todo en tu navegador.",
        "intro": [
            "¿Quieres a tu mascota en una taza, una pegatina o una impresión personalizada? Sube una foto y la IA separa a tu perro o tu gato del fondo — con el pelo y los bigotes incluidos — y te da un PNG transparente y limpio.",
            "Todo ocurre en tu dispositivo, así que puedes probar con todas las fotos que quieras — sin subidas, sin límites y sin marca de agua.",
        ],
        "benefits": [
            {"icon": "fa-brush", "title": "Genial con el pelo", "text": "Preparada para bordes suaves, pelo y bigotes, para un recorte de aspecto natural."},
            {"icon": "fa-wand-magic-sparkles", "title": "Refina a mano", "text": "Limpia el fondo que sobra o recupera detalles finos con el pincel de bordes integrado."},
            {"icon": "fa-note-sticky", "title": "Lista para imprimir y pegar", "text": "PNG transparentes a resolución completa para tazas, pegatinas, impresiones y memes."},
        ],
    },
    "youtube-thumbnail": {
        "nav": "Miniaturas de YouTube",
        "title": "Quitar el Fondo para Miniaturas de YouTube — Gratis e Ilimitado",
        "description": "Recórtate para una miniatura de YouTube — gratis, ilimitado y en resolución completa. Sin registro, sin marca de agua y sin subir nada: la IA funciona en tu navegador.",
        "h1": "Quita el Fondo para Miniaturas de YouTube",
        "tagline": "Recórtate a ti o a tu sujeto con limpieza y ponlo sobre un fondo llamativo para miniaturas que se ganan el clic — gratis e ilimitado.",
        "intro": [
            "Las miniaturas que mejor funcionan ponen un recorte nítido de una persona o un producto sobre un fondo contundente. Sube tu foto y la IA quita el fondo en segundos, y te deja un PNG transparente para componer en tu editor de miniaturas.",
            "Corre entero en tu navegador a resolución completa, así que puedes sacar miniaturas rápido — sin subidas, sin suscripciones y sin marca de agua.",
        ],
        "benefits": [
            {"icon": "fa-camera", "title": "Hecho para creadores", "text": "Recortes limpios de ti o de tu sujeto para que destaquen sobre cualquier fondo de miniatura."},
            {"icon": "fa-clock", "title": "Resultados rápidos", "text": "Quita el fondo en segundos para que cierres la miniatura y le des a publicar."},
            {"icon": "fa-crop-simple", "title": "Calidad completa", "text": "PNG transparentes a resolución completa y sin marca de agua, listos para cualquier editor."},
        ],
    },
    "ebay": {
        "nav": "Anuncios de eBay",
        "title": "Quitar el Fondo de Fotos para eBay — Gratis e Instantáneo",
        "description": "Dale a tus anuncios de eBay fondos blancos o transparentes gratis. Haz que tus artículos se vean profesionales — privado, ilimitado y en tu navegador.",
        "h1": "Quita el Fondo de tus Fotos para eBay",
        "tagline": "Convierte fotos de móvil desordenadas en fotos de anuncio limpias y profesionales para eBay — gratis, ilimitado y procesado en tu dispositivo.",
        "intro": [
            "Los anuncios con fotos limpias y uniformes se llevan más clics y se venden más rápido. Suelta una foto de tu artículo y la IA quita el fondo desordenado, para que pongas blanco puro — el aspecto en el que confían los compradores — o mantengas un PNG transparente para tu plantilla.",
            "Como la IA corre localmente en tu navegador, puedes preparar un inventario entero sin subir una sola foto, sin límites de API y sin pagar por imagen.",
        ],
        "benefits": [
            {"icon": "fa-bookmark", "title": "Vende más rápido", "text": "Los fondos blancos y limpios hacen que los artículos se vean profesionales y generan confianza."},
            {"icon": "fa-layer-group", "title": "Procesa el inventario en lote", "text": "Suelta decenas de artículos a la vez y descárgalos juntos en un ZIP."},
            {"icon": "fa-circle-check", "title": "Gratis e ilimitado", "text": "Sin coste por foto y sin marca de agua — resolución completa siempre."},
        ],
    },
    "discord-pfp": {
        "nav": "Avatares de Discord",
        "title": "Quitar el Fondo de tu Foto de Perfil de Discord — Gratis",
        "description": "Crea un PFP de Discord limpio quitando el fondo de tu foto o avatar. PNG transparentes gratis para ponerlos sobre cualquier color — en tu navegador.",
        "h1": "Quita el Fondo de tu Foto de Perfil de Discord",
        "tagline": "Recórtate a ti o a tu personaje con limpieza para un avatar de Discord nítido — gratis, ilimitado y todo en tu navegador.",
        "intro": [
            "Una foto de perfil limpia hace que destaques en Discord. Sube una foto, un selfie o una ilustración y la IA aísla al sujeto, para que lo dejes transparente o pongas cualquier color sólido o degradado antes de recortarlo en círculo.",
            "Todo ocurre en tu dispositivo, así que puedes probar todos los estilos que quieras — sin subidas, sin límites y sin marca de agua.",
        ],
        "benefits": [
            {"icon": "fa-user", "title": "Avatares nítidos", "text": "Recortes limpios que se leen bien incluso en el tamaño pequeño de los avatares de Discord."},
            {"icon": "fa-swatchbook", "title": "Cualquier color o degradado", "text": "Pon tu recorte sobre un color sólido, un degradado o un fondo desenfocado, y recórtalo en círculo."},
            {"icon": "fa-shield-halved", "title": "Privado por diseño", "text": "Tu foto nunca sale de tu navegador — no se sube nada a un servidor."},
        ],
    },
    "twitch": {
        "nav": "Twitch y streaming",
        "title": "Quitar el Fondo para Twitch y Streaming — Sin Croma",
        "description": "Recórtate de una foto para paneles, overlays y emotes de Twitch — sin croma. PNG transparentes gratis, privados y en tu navegador.",
        "h1": "Quita el Fondo para Twitch y Streaming",
        "tagline": "Crea recortes limpios para paneles, overlays y emotes sin croma — gratis, ilimitado y procesado en tu dispositivo.",
        "intro": [
            "Una buena imagen de canal empieza con recursos limpios. Sube una foto y la IA quita el fondo para darte un PNG transparente para tus paneles de Twitch, overlays de directo, gráficos de horario o emotes — sin croma ni máscaras a mano.",
            "Todo corre en tu navegador a resolución completa, así que puedes montar un set entero de gráficos de marca en privado — sin subidas, sin tarifas por imagen y sin marca de agua.",
        ],
        "benefits": [
            {"icon": "fa-wand-magic-sparkles", "title": "Sin croma", "text": "Consigue un recorte limpio de cualquier foto — sin croma ni montaje de estudio."},
            {"icon": "fa-images", "title": "Paneles y emotes", "text": "PNG transparentes listos para overlays, paneles, horarios y arte de emotes."},
            {"icon": "fa-crop-simple", "title": "Calidad completa", "text": "Exportaciones a resolución completa y sin marca de agua para cualquier herramienta de diseño de directos."},
        ],
    },
}

# --- FAQs, keyed by the English question -------------------------------------
# Each value is a (question, answer) pair — the question is translated too, so
# the accordion and the FAQPage JSON-LD both speak Spanish.
FAQS = {
    # --- /crop/ -------------------------------------------------------------
    "Is this image cropper free and private?":
        ("¿Este recortador de imágenes es gratis y privado?",
         "Sí — es totalmente gratuito, sin marca de agua ni registro, y el recorte se hace por completo en tu navegador, así que tu foto nunca se sube."),
    "How do I crop an image to a circle?":
        ("¿Cómo recorto una imagen en círculo?",
         "Elige la forma circular y la herramienta enmascara tu foto en un círculo perfecto, con las esquinas transparentes. Expórtala en PNG para conservar la transparencia — en JPG las esquinas saldrán blancas, porque el formato JPG no admite transparencia."),
    "Can I crop to a specific aspect ratio?":
        ("¿Puedo recortar a una proporción concreta?",
         "Sí. Elige una proporción predefinida como 1:1, 4:5, 16:9 o 9:16, o introduce tu propio ancho:alto. La caja de recorte queda fijada a esa proporción mientras arrastras y haces zoom, de modo que el encuadre nunca la rompe."),
    "Does cropping reduce the image resolution?":
        ("¿El recorte reduce la resolución de la imagen?",
         "Nunca se amplía nada. El archivo se exporta a la resolución nativa de la región recortada, así que conservas todos los píxeles dentro del recorte con la calidad original."),
    "Can I rotate or flip while cropping?":
        ("¿Puedo rotar o voltear mientras recorto?",
         "Sí — rota en pasos de 90° y voltea en horizontal o en vertical antes de exportar, para que una foto tomada de lado salga bien orientada."),
    "What format should I export a cropped image as?":
        ("¿En qué formato debo exportar una imagen recortada?",
         "Usa PNG en recortes circulares o redondeados, para preservar las esquinas transparentes. Usa JPG para un archivo más pequeño cuando no necesites transparencia, o AVIF para los archivos más pequeños en navegadores Chromium."),

    # Home — trust questions ("what's the catch", the tech, the device)
    "What's the catch — how can it be free and unlimited?":
        ("¿Dónde está la trampa? ¿Cómo puede ser gratis e ilimitado?",
         "La parte cara la hace tu dispositivo. Las herramientas en la nube alquilan GPU por segundo y cobran por imagen, así que tienen que limitarte; aquí el modelo corre en tu navegador, así que una imagen más no le cuesta nada a nadie. Toda la factura es un dominio y un alojamiento barato, cubiertos por los anuncios de las guías escritas (las páginas de las herramientas se quedan sin anuncios) y algún café de vez en cuando. No hay cuenta, ni prueba, ni venta adicional, porque no hay nada que vender."),
    "Which AI model does it use, and where does it run?":
        ("¿Qué modelo de IA usa y dónde corre?",
         "IS-Net, un modelo de segmentación, a través de ONNX Runtime Web dentro de la pestaña de tu navegador. Donde hay WebGPU corre en tu tarjeta gráfica y fuera del hilo principal; si no, usa WebAssembly con SIMD e hilos en la CPU. Los navegadores con aislamiento de origen cruzado reciben los pesos con precisión completa, y el resto una versión cuantizada más pequeña. El modelo se descarga una vez y queda en caché, así que los usos siguientes funcionan sin conexión."),
    "What does my device need, and why is the first image slow?":
        ("¿Qué necesita mi dispositivo y por qué la primera imagen tarda?",
         "Cualquier navegador moderno en un dispositivo con algo de memoria libre. La primera vez se descarga el modelo — esa es la espera que notas — y todo lo demás va rápido porque queda en caché. Un portátil o un móvil reciente tarda unos segundos por imagen; un dispositivo más antiguo puede tardar hasta un minuto y usa el modelo más pequeño. Si tu navegador no puede correr el modelo, la página te avisa en vez de quedarse colgada, y las herramientas que no necesitan IA (recortar, convertir, comprimir, redimensionar) siguen funcionando."),
    # Remove object
    "How do I remove an object from a photo?":
        ("¿Cómo quito un objeto de una foto?",
         "Suelta una foto, pinta sobre el objeto que quieres quitar y pulsa Borrar. La herramienta rellena la zona pintada a partir de los píxeles de alrededor — todo en tu navegador, en segundos."),
    "Does it use AI? How good is the result?":
        ("¿Usa IA? ¿Qué tal es el resultado?",
         "Usa un relleno inteligente y rápido que funde los colores y la textura de alrededor en la zona borrada. Brilla en cielos, paredes, césped, arena y otros fondos uniformes; los fondos muy detallados o con patrones pueden pedir una segunda pasada más pequeña."),
    "Is my photo uploaded anywhere?":
        ("¿Se sube mi foto a algún sitio?",
         "No. Todo el relleno corre en tu dispositivo — la foto nunca sale de tu navegador, que es justo lo que quieres al editar imágenes personales."),
    "Can I remove people from photos?":
        ("¿Puedo quitar personas de las fotos?",
         "Sí — pinta sobre la persona y bórrala. El resultado es mejor cuando la persona está sobre un fondo relativamente uniforme, como el cielo, el mar, el césped o una pared."),
    "Is it free, and is there a watermark?":
        ("¿Es gratis? ¿Hay marca de agua?",
         "Totalmente gratis, ilimitado y sin marca de agua — como todas las herramientas de ClearBG. Sin cuenta, sin créditos y sin venta adicional en el botón de exportar."),
    # Upscaler
    "How does the upscaler enlarge my image?":
        ("¿Cómo amplía mi imagen el escalador?",
         "Remuestrea la imagen a 2× o 4× con un filtro Lanczos de alta calidad y después aplica una pasada suave de enfoque de detalle — el mismo método que usa el software fotográfico profesional para redimensionar. Corre al instante en tu navegador."),
    "Is this AI super-resolution?":
        ("¿Es superresolución con IA?",
         "No — y es a propósito. Los modelos de escalado con IA dentro del navegador son lentos y pueden bloquear la pestaña con fotos grandes. Esta herramienta cambia un poco de esa magia por resultados instantáneos y fiables a cualquier tamaño, sin subir nada."),
    "What sizes can I upscale to?":
        ("¿A qué tamaños puedo ampliar?",
         "Al doble o al cuádruple del original, hasta un límite de seguridad de 8000 píxeles en el lado más largo para que el navegador no se quede sin memoria. Las exportaciones son PNG (sin pérdidas) o JPG."),
    "Will an upscaled photo look better than the original?":
        ("¿Una foto ampliada se verá mejor que el original?",
         "Ampliar no puede inventar detalle que nunca se capturó, pero una ampliación bien remuestreada y ligeramente enfocada se ve muchísimo mejor que un estirado simple de un navegador o un editor — los bordes se mantienen limpios en vez de quedar borrosos o pixelados."),
    "Is it private and free?":
        ("¿Es privado y gratis?",
         "Sí. El remuestreo corre por completo en tu dispositivo — no se sube nada — y es gratis, ilimitado y sin marca de agua."),
    # HEIC converter
    "Why can't I open my iPhone's HEIC photos?":
        ("¿Por qué no puedo abrir las fotos HEIC de mi iPhone?",
         "Los iPhone guardan las fotos en HEIC (High Efficiency Image Container) por defecto. Reduce el tamaño de archivo a la mitad, pero Windows, Android y la mayoría de las webs no pueden abrirlo — por eso la foto funciona en tu móvil y en ningún otro sitio. Convertirla a JPG lo arregla al instante."),
    "How do I convert HEIC to JPG for free?":
        ("¿Cómo convierto HEIC a JPG gratis?",
         "Suelta aquí tus archivos .heic y descárgalos como JPG (o PNG / WEBP). La conversión ocurre en tu navegador — sin instalar nada, sin subidas, sin marca de agua y sin límite."),
    "Are my photos uploaded to a server?":
        ("¿Se suben mis fotos a un servidor?",
         "No. El decodificador HEIC corre en tu dispositivo, así que tus fotos nunca salen de tu navegador. Y eso importa — las fotos personales no deberían pasar por el servidor de nadie solo para cambiar de formato."),
    "Does converting HEIC lose quality?":
        ("¿Convertir HEIC pierde calidad?",
         "La foto se decodifica a resolución completa y se vuelve a codificar con alta calidad. JPG es ligeramente con pérdidas por naturaleza, pero con este ajuste la diferencia no se aprecia; elige PNG para una exportación sin pérdidas."),
    "Can I convert many HEIC photos at once?":
        ("¿Puedo convertir muchas fotos HEIC a la vez?",
         "Sí — suelta un lote entero y descárgalas una a una o todas juntas en un ZIP."),
    # PDF to images
    "How do I turn a PDF into images?":
        ("¿Cómo convierto un PDF en imágenes?",
         "Suelta aquí un PDF y cada página se renderiza como una imagen de alta resolución en tu propio navegador. Descarga páginas sueltas en PNG o JPG, o todas a la vez en un ZIP."),
    "Is my PDF uploaded anywhere?":
        ("¿Se sube mi PDF a algún sitio?",
         "No. El PDF se analiza y se renderiza por completo en tu dispositivo — algo importante, porque los PDF suelen ser contratos, documentos de identidad, extractos y otros papeles privados."),
    "What resolution are the exported images?":
        ("¿Con qué resolución se exportan las imágenes?",
         "Las páginas se renderizan al doble de su tamaño nominal (unos 150 PPP) por defecto, y puedes subirlo para obtener calidad de impresión. El texto se mantiene nítido porque la página se renderiza desde el origen vectorial, no estirando una vista previa."),
    "Can I extract just one page?":
        ("¿Puedo extraer solo una página?",
         "Sí — cada página tiene su propio botón de descarga, así que puedes guardar exactamente las páginas que necesitas, o todas en un ZIP."),
    "Is it free, with no watermark?":
        ("¿Es gratis y sin marca de agua?",
         "Totalmente gratis e ilimitado, sin marca de agua ni registro — exporta en PNG, JPG o WEBP."),
    # Image to text (OCR)
    "How do I copy text out of an image?":
        ("¿Cómo copio el texto de una imagen?",
         "Suelta una foto o una captura de pantalla y el reconocedor de texto la lee en tu propio navegador. El texto reconocido aparece en un cuadro editable — cópialo entero con un clic."),
    "Is my image uploaded for the text recognition?":
        ("¿Se sube mi imagen para reconocer el texto?",
         "No. El motor de OCR (Tesseract, el mismo motor de código abierto que usan muchos escáneres) corre en tu dispositivo mediante WebAssembly. Las capturas de pantalla suelen contener conversaciones y documentos privados — aquí nunca salen de tu navegador."),
    "Which languages does it recognise?":
        ("¿Qué idiomas reconoce?",
         "Están disponibles español, inglés, portugués, francés y alemán, y el motor descarga el paquete del idioma elegido la primera vez que lo usas — después queda en caché y funciona sin conexión."),
    "How accurate is it?":
        ("¿Es preciso?",
         "Muy bueno con capturas de pantalla limpias y documentos impresos; las fotos más difíciles (ángulos, escritura a mano, poca luz) reducen la precisión. Las imágenes nítidas, de frente y con buen contraste se reconocen mejor."),
    "Is it free and unlimited?":
        ("¿Es gratis e ilimitado?",
         "Sí — gratis, ilimitado, sin marca de agua y sin registro. Reconoce tantas imágenes como quieras."),
    # SVG to PNG
    "How do I convert an SVG to PNG?":
        ("¿Cómo convierto un SVG a PNG?",
         "Suelta aquí un archivo .svg, elige un tamaño (1×, 2×, 4× o un ancho exacto en píxeles) y descarga un PNG nítido. El navegador rasteriza el vector directamente, así que los bordes se mantienen perfectamente definidos a cualquier escala."),
    "Why does my SVG export blurry from other tools?":
        ("¿Por qué mi SVG se exporta borroso en otras herramientas?",
         "Porque rasterizan al tamaño nominal del SVG y luego estiran el mapa de bits. Esta herramienta renderiza el vector exactamente al tamaño de salida que elijas, así que una exportación a 4× tiene 4× de detalle real."),
    "Does it keep transparency?":
        ("¿Mantiene la transparencia?",
         "Sí — las exportaciones PNG mantienen un fondo totalmente transparente por defecto, o puedes rellenarlo con cualquier color. La exportación JPG lo rellena de blanco automáticamente."),
    "Is my SVG uploaded?":
        ("¿Se sube mi SVG?",
         "No. El archivo se lee y se renderiza por completo en tu navegador — no se envía nada a un servidor."),
    "What about fonts and embedded images inside the SVG?":
        ("¿Y las fuentes y las imágenes incrustadas dentro del SVG?",
         "Los SVG que incrustan sus imágenes y usan fuentes estándar del sistema se renderizan exactamente igual. Un SVG que hace referencia a archivos externos o a fuentes web puede renderizarse con fuentes alternativas, porque el navegador lo rasteriza de forma aislada."),
    # Photo filters
    "What can I adjust in this photo editor?":
        ("¿Qué puedo ajustar en este editor de fotos?",
         "Estilos de un toque (vivo, cálido, sombrío, película, blanco y negro y más) además de controles manuales de brillo, contraste, saturación, calidez, viñeta y grano. Mantén pulsado el botón de comparar en cualquier momento para verlo junto al original."),
    "Are the filters applied to the full-quality photo?":
        ("¿Los filtros se aplican a la foto con calidad completa?",
         "Sí. La vista previa se reduce por velocidad, pero la exportación vuelve a aplicar tus ajustes exactos al original a resolución completa — sin más pérdida de calidad que la del formato que elijas."),
    "Is my photo uploaded to apply filters?":
        ("¿Se sube mi foto para aplicar los filtros?",
         "No. Cada ajuste se dibuja en un lienzo en tu dispositivo — la foto nunca sale de tu navegador."),
    "Can I fine-tune a preset look?":
        ("¿Puedo ajustar un estilo predefinido?",
         "Sí — pulsa un estilo y luego mueve cualquier control encima. El estilo marca el punto de partida; los controles siempre los llevas tú."),
    # --- Resizer + EXIF remover ---
    'Is this image resizer free?':
        ('¿Este redimensionador de imágenes es gratis?',
         'Sí — gratis, ilimitado, sin marca de agua y sin registro. Redimensiona todas las imágenes que quieras.'),
    'Will resizing reduce quality?':
        ('¿Redimensionar reduce la calidad?',
         'Hacer una imagen más pequeña la mantiene nítida. Ampliarla más allá del tamaño original puede verse blanda, porque no hay detalle extra que añadir — los mejores resultados vienen de reducir.'),
    'Can I keep the aspect ratio?':
        ('¿Puedo mantener la proporción?',
         'Sí. Bloquea la proporción y al cambiar el ancho se actualiza el alto automáticamente, así la imagen nunca se deforma; desbloquéala para fijar dimensiones exactas.'),
    'Is my image uploaded?':
        ('¿Se sube mi imagen?',
         'No — el redimensionado ocurre por completo en tu navegador, así que tus imágenes nunca salen de tu dispositivo.'),
    'What is EXIF / photo metadata?':
        ('¿Qué son los EXIF o metadatos de una foto?',
         'Datos ocultos que tu cámara o tu móvil guarda dentro de la foto — ubicación GPS, la fecha y hora exactas y el modelo del dispositivo. Viajan con el archivo cuando lo compartes.'),
    'Is removing it private?':
        ('¿Borrarlos es privado?',
         'Sí — la foto se lee y se limpia por completo en tu navegador y nunca se sube, así que incluso las fotos privadas con geoetiqueta se quedan en tu dispositivo.'),
    'Does removing metadata reduce quality?':
        ('¿Borrar los metadatos reduce la calidad?',
         'No. En los JPEG los metadatos se eliminan sin pérdidas — los datos de la imagen quedan intactos, así que no hay ninguna pérdida de calidad.'),
    'Why remove location data before sharing?':
        ('¿Por qué borrar la ubicación antes de compartir?',
         'Las fotos con geoetiqueta revelan exactamente dónde se tomaron — a menudo tu casa. Borrar la etiqueta GPS antes de publicar protege tu privacidad.'),
    # --- Converter + compressor ---
    'Will converting reduce my image quality?':
        ('¿Convertir reduce la calidad de la imagen?',
         'Convertir a un formato sin pérdidas como PNG mantiene todos los píxeles intactos. Convertir a uno con pérdidas (JPG, WEBP o AVIF) vuelve a codificar la imagen, así que puede haber un pequeño cambio de calidad, pero conservas la resolución original completa — no se reduce nada.'),
    'Does converting to PNG add transparency to a JPG?':
        ('¿Convertir a PNG añade transparencia a un JPG?',
         'No. Convertir un JPG a PNG cambia el contenedor, pero no puede inventar una transparencia que no estaba en el original — un JPG tiene fondo sólido. Para hacer un fondo transparente necesitas nuestro quitador de fondos, que recorta primero el sujeto.'),
    'Are my images uploaded to a server?':
        ('¿Se suben mis imágenes a un servidor?',
         'No. La conversión corre por completo en tu navegador mediante la API de canvas, así que tus imágenes nunca salen del dispositivo. No hay límites de subida ni coste por archivo.'),
    'Can I convert several images at once?':
        ('¿Puedo convertir varias imágenes a la vez?',
         'Sí. Suelta un lote de imágenes, elige el formato de salida y descárgalas juntas — todas procesadas localmente, una tras otra.'),
    'How does image compression reduce file size?':
        ('¿Cómo reduce el tamaño la compresión de imágenes?',
         'La compresión vuelve a codificar la imagen con una calidad más baja y, en las fotos, descarta detalle fino que el ojo apenas nota. Esta herramienta te deja cambiar un poco de calidad por un archivo mucho más pequeño, y muestra el tamaño antes y después para encontrar el punto justo.'),
    'Will compressing make my image look bad?':
        ('¿Comprimir va a estropear la imagen?',
         'No si eliges un nivel de calidad sensato. Entre el 70% y el 85% la mayoría de las fotos se ven idénticas al original mientras el archivo encoge un 60-80%. Puedes previsualizar el resultado y ajustar el control antes de descargar.'),
    "What's the best format to compress to?":
        ('¿Cuál es el mejor formato para comprimir?',
         'Para fotografías, WEBP o AVIF suelen dar el archivo más pequeño con la misma calidad visual, seguidos de JPG. Para gráficos con colores planos o transparencia, PNG o WEBP son mejores. La herramienta permite comparar formatos para elegir el más pequeño que resulte aceptable.'),
    'Can I compress an image to a specific size, like under 1MB?':
        ('¿Puedo comprimir una imagen a un tamaño concreto, como menos de 1 MB?',
         'Sí — baja el control de calidad hasta que el tamaño estimado quede por debajo de tu objetivo (por ejemplo 1 MB, 500 KB o 100 KB para un límite de correo o de subida). El tamaño se actualiza en vivo mientras ajustas.'),
    'Are my images uploaded when I compress them?':
        ('¿Se suben mis imágenes al comprimirlas?',
         'No. Toda la compresión ocurre localmente en tu navegador, así que tus imágenes nunca se suben, se guardan ni las ve nadie. Funciona sin conexión una vez cargada la página.'),
    'Does compressing remove EXIF and location data?':
        ('¿Comprimir elimina los datos EXIF y de ubicación?',
         'Volver a codificar una imagen suele eliminar la mayoría de los metadatos incrustados, incluidos los datos de la cámara y las coordenadas GPS. Si quieres borrar metadatos manteniendo la calidad completa, usa mejor nuestro eliminador de EXIF.'),
    'Which image formats can I convert between?':
        ('¿Entre qué formatos de imagen puedo convertir?',
         'Puedes convertir entre PNG, JPG, WEBP y AVIF en cualquier dirección — por ejemplo PNG a JPG, JPG a WEBP o WEBP a PNG. Sube uno de esos formatos y exporta cualquiera de los otros.'),
    "What's the difference between PNG, JPG, WEBP and AVIF?":
        ('¿Cuál es la diferencia entre PNG, JPG, WEBP y AVIF?',
         'El PNG es sin pérdidas y admite transparencia, lo que lo hace ideal para logotipos, iconos y capturas de pantalla. El JPG es un formato pequeño y con pérdidas, mejor para fotografías, pero no tiene transparencia. WEBP y AVIF son formatos modernos que combinan archivos pequeños con transparencia — el AVIF suele ser el más pequeño y el WEBP tiene la compatibilidad más amplia.'),
}
