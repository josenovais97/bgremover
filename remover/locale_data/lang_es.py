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
    "Remove Image Backgrounds": "Quita el Fondo de Tus Imágenes",
    "Automatically & Free": "Automático y Gratis",
    "Drop an image and get a clean, transparent PNG in seconds. No sign-up, no watermarks, no quality loss — the AI runs entirely on your device.":
        "Suelta una imagen y obtén un PNG limpio y transparente en segundos. Sin registro, sin marcas de agua y sin pérdida de calidad — la IA funciona por completo en tu dispositivo.",
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
            {"icon": "fa-palette", "title": "Cualquier color de fondo", "text": "Combina con una paleta de marca o un fondo de estudio liso, y exporta en PNG, JPG o WEBP."},
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
            {"icon": "fa-file-signature", "title": "Lista para documentos", "text": "Consigue tinta transparente que puedes colocar directamente en PDF, contratos y cartas."},
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
            {"icon": "fa-car", "title": "Limpio como un concesionario", "text": "Cambia un aparcamiento desordenado por un fondo de estudio impecable que mantiene el foco en el coche."},
            {"icon": "fa-layer-group", "title": "Lotes completos", "text": "Suelta decenas de fotos a la vez y descárgalas juntas en un ZIP."},
            {"icon": "fa-bolt", "title": "Instantáneo y gratis", "text": "Sin coste por foto y sin marca de agua — resolución completa siempre."},
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
            {"icon": "fa-shirt", "title": "Vendible en segundos", "text": "Recortes limpios de tops, vestidos y zapatos que encajan en cualquier cuadrícula de tienda."},
            {"icon": "fa-tags", "title": "Anuncios uniformes", "text": "Dale a cada prenda el mismo fondo cuidado para que tu escaparate se vea profesional."},
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
            {"icon": "fa-paw", "title": "Genial con el pelo", "text": "Preparada para bordes suaves, pelo y bigotes, para un recorte de aspecto natural."},
            {"icon": "fa-wand-magic-sparkles", "title": "Refina a mano", "text": "Limpia el fondo que sobra o recupera detalles finos con el pincel de bordes integrado."},
            {"icon": "fa-heart", "title": "Lista para imprimir y pegar", "text": "PNG transparentes a resolución completa para tazas, pegatinas, impresiones y memes."},
        ],
    },
    "youtube-thumbnail": {
        "nav": "Miniaturas de YouTube",
        "title": "Quitar el Fondo para Miniaturas de YouTube — Gratis",
        "description": "Recórtate de una foto para una miniatura de YouTube que invite a hacer clic. PNG transparentes gratis para cualquier fondo — privado, en tu navegador.",
        "h1": "Quita el Fondo para Miniaturas de YouTube",
        "tagline": "Recórtate a ti o a tu sujeto con limpieza y ponlo sobre un fondo llamativo para miniaturas que se ganan el clic — gratis e ilimitado.",
        "intro": [
            "Las miniaturas que mejor funcionan ponen un recorte nítido de una persona o un producto sobre un fondo contundente. Sube tu foto y la IA quita el fondo en segundos, y te deja un PNG transparente para componer en tu editor de miniaturas.",
            "Corre entero en tu navegador a resolución completa, así que puedes sacar miniaturas rápido — sin subidas, sin suscripciones y sin marca de agua.",
        ],
        "benefits": [
            {"icon": "fa-clapperboard", "title": "Hecho para creadores", "text": "Recortes limpios de ti o de tu sujeto para que destaquen sobre cualquier fondo de miniatura."},
            {"icon": "fa-bolt", "title": "Resultados rápidos", "text": "Quita el fondo en segundos para que cierres la miniatura y le des a publicar."},
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
            {"icon": "fa-tag", "title": "Vende más rápido", "text": "Los fondos blancos y limpios hacen que los artículos se vean profesionales y generan confianza."},
            {"icon": "fa-layer-group", "title": "Procesa el inventario en lote", "text": "Suelta decenas de artículos a la vez y descárgalos juntos en un ZIP."},
            {"icon": "fa-bolt", "title": "Gratis e ilimitado", "text": "Sin coste por foto y sin marca de agua — resolución completa siempre."},
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
            {"icon": "fa-circle-user", "title": "Avatares nítidos", "text": "Recortes limpios que se leen bien incluso en el tamaño pequeño de los avatares de Discord."},
            {"icon": "fa-palette", "title": "Cualquier color o degradado", "text": "Pon tu recorte sobre un color sólido, un degradado o un fondo desenfocado, y recórtalo en círculo."},
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
            {"icon": "fa-tower-broadcast", "title": "Sin croma", "text": "Consigue un recorte limpio de cualquier foto — sin croma ni montaje de estudio."},
            {"icon": "fa-icons", "title": "Paneles y emotes", "text": "PNG transparentes listos para overlays, paneles, horarios y arte de emotes."},
            {"icon": "fa-crop-simple", "title": "Calidad completa", "text": "Exportaciones a resolución completa y sin marca de agua para cualquier herramienta de diseño de directos."},
        ],
    },
}

# --- FAQs, keyed by the English question -------------------------------------
# Each value is a (question, answer) pair — the question is translated too, so
# the accordion and the FAQPage JSON-LD both speak Spanish.
FAQS = {
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
}
