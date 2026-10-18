"""Lightweight runtime localization for the Universal Downloader UI.
All technical identifiers, URLs, file names and user-provided content remain untouched.
"""
LANGUAGES = {'en': 'English', 'hi': 'हिन्दी', 'es': 'Español'}

# Keys are source-English UI strings. English fallback is the original phrase.
TRANSLATIONS = {
'hi': {
'Add multiple URLs':'कई URL जोड़ें','Paste one video URL per line:':'हर पंक्ति में एक वीडियो URL पेस्ट करें','Toggle light/dark theme':'लाइट/डार्क थीम बदलें','Universal Downloader brings link inspection, format selection, downloading, conversion and file organization into one clean desktop workspace. The goal is to reduce repetitive steps and help you get to your saved media faster.':'Universal Downloader लिंक जाँच, फ़ॉर्मैट चयन, डाउनलोड, कन्वर्ज़न और फ़ाइल व्यवस्था को एक साफ़ डेस्कटॉप ऐप में जोड़ता है ताकि कम चरणों में मीडिया सेव किया जा सके।','Reduce motion':'कम एनिमेशन','Animation preferences':'एनिमेशन प्राथमिकताएँ','Reduce motion enabled':'कम एनिमेशन चालू','Reduce motion disabled':'कम एनिमेशन बंद','Download   •   Convert   •   Organize':'डाउनलोड • कन्वर्ट • व्यवस्थित करें','Choose download folder':'डाउनलोड फ़ोल्डर चुनें','✦  All caught up!':'✦  सब अपडेट है!','0 queued':'0 कतार में',
'MP4 (Premiere-friendly)':'MP4 (Premiere के लिए अनुकूल)','MP3 (audio only)':'MP3 (केवल ऑडियो)','MKV':'MKV','WEBM':'WEBM','M4A (audio only)':'M4A (केवल ऑडियो)','Best available':'सबसे अच्छी उपलब्ध गुणवत्ता','8K (4320p)':'8K (4320p)','4K (2160p)':'4K (2160p)','1440p':'1440p','1080p':'1080p','720p':'720p','480p':'480p','360p':'360p',
'Choose a save location first.':'पहले सेव करने की जगह चुनें।','Saved successfully:':'सफलतापूर्वक सेव हुआ:','Remove all items from the app history? Downloaded files will not be deleted.':'क्या ऐप इतिहास के सभी आइटम हटाएँ? डाउनलोड की गई फ़ाइलें डिलीट नहीं होंगी।','File is no longer at:':'फ़ाइल अब यहाँ नहीं है:','Run this command:':'यह कमांड चलाएँ:','Universal Downloader could not start':'Universal Downloader शुरू नहीं हो सका',
'Views unavailable':'व्यू उपलब्ध नहीं','Download complete.':'डाउनलोड पूरा हुआ।','Download failed — see error details.':'डाउनलोड विफल — त्रुटि विवरण देखें।','Starting queued download…':'कतार वाला डाउनलोड शुरू हो रहा है…','Inspection complete.':'जाँच पूरी हुई।','Inspecting source and available formats…':'सोर्स और उपलब्ध फ़ॉर्मैट जाँचे जा रहे हैं…',
'Paste a supported public video or media URL. The app uses yt-dlp to identify the source and available media formats.':'समर्थित सार्वजनिक वीडियो या मीडिया URL पेस्ट करें। ऐप स्रोत और उपलब्ध फ़ॉर्मैट पहचानने के लिए yt-dlp का उपयोग करता है।','Check details before you download.':'डाउनलोड से पहले विवरण जाँचें।','MP4, WebM, MKV and more.':'MP4, WebM, MKV और अन्य।','Progress, speed and ETA.':'प्रगति, गति और अनुमानित समय।','Access your downloads anytime.':'अपने डाउनलोड कभी भी देखें।',
'Could not convert':'कन्वर्ट नहीं कर सके','Copy failed':'कॉपी नहीं हो सका','Paste failed':'पेस्ट नहीं हो सका','Language changed':'भाषा बदल दी गई','Download transferred — preparing output…':'डाउनलोड पूरा हुआ — आउटपुट तैयार हो रहा है…','Converting to H.264 MP4…':'H.264 MP4 में कन्वर्ट हो रहा है…','Remuxing compatible streams (fast, no re-encode)':'संगत स्ट्रीम जोड़ी जा रही हैं (तेज़, दोबारा एन्कोड नहीं)','Copying video; converting audio to AAC':'वीडियो कॉपी हो रहा है; ऑडियो AAC में बदला जा रहा है','Converting video to H.264 and audio to AAC':'वीडियो H.264 और ऑडियो AAC में कन्वर्ट हो रहा है','Download':'डाउनलोड','Completed':'पूर्ण','About & Features':'ऐप के बारे में','Dark mode':'डार्क मोड','Light mode':'लाइट मोड',
'Video URL':'वीडियो URL','Paste a video URL here…':'यहाँ वीडियो URL पेस्ट करें…','Paste':'पेस्ट करें','Inspect':'जाँचें',
'Output Format':'आउटपुट फ़ॉर्मैट','Max Resolution':'अधिकतम रिज़ॉल्यूशन','Save Location':'सेव करने की जगह','Choose folder':'फ़ोल्डर चुनें','Open save folder':'सेव किया गया फ़ोल्डर खोलें',
'Video Details':'वीडियो विवरण','Inspect a link to see its title, duration, uploader and available formats.':'शीर्षक, अवधि, अपलोडर और उपलब्ध फ़ॉर्मैट देखने के लिए लिंक जाँचें।',
'Add to Queue & Start':'कतार में जोड़ें और शुरू करें','Add Multiple URLs':'कई URL जोड़ें','Paste multiple URLs, one per line':'हर पंक्ति में एक URL पेस्ट करें','Download queue':'डाउनलोड कतार','Clear queued':'कतार साफ़ करें',
'Queued URLs are saved locally and restored when the app restarts.':'कतार के URL आपके कंप्यूटर पर सेव होते हैं और ऐप दोबारा खुलने पर लौट आते हैं।',
'Ready — paste a video link to begin':'तैयार — शुरू करने के लिए वीडियो लिंक पेस्ट करें','Completed downloads':'पूरे हुए डाउनलोड','Open downloads folder':'डाउनलोड फ़ोल्डर खोलें','Clear history':'इतिहास साफ़ करें',
'Download only content you own or have permission to save. Private, DRM-protected or access-restricted media isn’t supported.':'केवल वही सामग्री डाउनलोड करें जिसकी अनुमति आपके पास है। निजी, DRM-सुरक्षित या प्रतिबंधित मीडिया समर्थित नहीं है।',
'Search and filter your local download library. Removing an entry never deletes the actual video.':'अपने डाउनलोड खोजें और फ़िल्टर करें। रिकॉर्ड हटाने से वीडियो फ़ाइल डिलीट नहीं होती।',
'Search titles or filenames…':'शीर्षक या फ़ाइल नाम खोजें…','All Websites':'सभी वेबसाइटें','Latest first':'नवीनतम पहले','Oldest first':'सबसे पुराने पहले','Clear filters':'फ़िल्टर साफ़ करें',
'No downloads match these filters.':'इन फ़िल्टर से कोई डाउनलोड नहीं मिला।','Your completed downloads will appear here.':'आपके पूरे हुए डाउनलोड यहाँ दिखेंगे।',
'A B O U T':'ऐप के बारे में','A simpler way to save media':'मीडिया सेव करने का आसान तरीका','Made to make saving media simpler':'मीडिया सेव करना आसान बनाने के लिए',
'Universal Downloader helps you fetch, convert and organize your media files —\nquickly, easily and without unnecessary steps.':'Universal Downloader आपकी मीडिया फ़ाइलें डाउनलोड, कन्वर्ट और व्यवस्थित करने में मदद करता है — आसानी से और कम चरणों में।',
'Built for your workflow':'आपके काम के लिए बनाया गया','Paste & inspect link':'लिंक पेस्ट करें और जाँचें','Inspect before downloading':'डाउनलोड से पहले जाँचें','Choose format and quality':'फ़ॉर्मैट और गुणवत्ता चुनें','Track progress':'प्रगति देखें','Keep downloads organized':'डाउनलोड व्यवस्थित रखें','Your history stays local':'आपका इतिहास आपके कंप्यूटर पर रहता है',
'At a glance':'एक नज़र में','Link inspection':'लिंक जाँच','Format selection':'फ़ॉर्मैट चुनें','Download tracking':'डाउनलोड की स्थिति','Local history':'स्थानीय इतिहास',
'Created by Arth Awasthi':'Arth Awasthi द्वारा बनाया गया','Follow me @arth_lives':'@arth_lives पर फ़ॉलो करें','Instagram  ↗':'Instagram  ↗',
'Only download content you own or have permission to save. Respect creators’ rights.':'केवल वही सामग्री डाउनलोड करें जिसकी अनुमति आपके पास है। क्रिएटर्स के अधिकारों का सम्मान करें।',
'Link copied':'लिंक कॉपी हो गया','Source URL copied':'सोर्स URL कॉपी हो गया','Link pasted':'लिंक पेस्ट हो गया','Clipboard is empty.':'क्लिपबोर्ड खाली है।','Copied to clipboard':'क्लिपबोर्ड पर कॉपी किया गया',
'Language':'भाषा','Language & Region':'भाषा और क्षेत्र','English':'English','हिन्दी':'हिन्दी','Español':'Español',
'Choose a folder':'फ़ोल्डर चुनें','Please choose a save location first.':'पहले सेव करने की जगह चुनें।','Download in progress':'डाउनलोड जारी है','The active download cannot be cancelled safely yet. Only waiting items will be removed.':'अभी चल रहे डाउनलोड को सुरक्षित रूप से रद्द नहीं किया जा सकता। केवल प्रतीक्षा कर रहे आइटम हटेंगे।',
'Download complete':'डाउनलोड पूरा हुआ','Download failed':'डाउनलोड विफल','Inspection complete.':'जाँच पूरी हुई।','Inspecting source and available formats…':'सोर्स और उपलब्ध फ़ॉर्मैट जाँचे जा रहे हैं…','Starting queued download…':'कतार वाला डाउनलोड शुरू हो रहा है…','Download complete.':'डाउनलोड पूरा हुआ।','Download failed — see error details.':'डाउनलोड विफल — त्रुटि विवरण देखें।',
'All Websites':'सभी वेबसाइटें','Size unknown':'आकार उपलब्ध नहीं','Duration unavailable':'अवधि उपलब्ध नहीं',
'active':'सक्रिय','queued':'कतार में','downloads completed':'डाउनलोड पूरे हुए','of':'में से','downloads':'डाउनलोड','Queued':'कतार में','Downloading':'डाउनलोड हो रहा है','Completed':'पूर्ण','Failed':'विफल','Cancelled':'रद्द',
'No new valid URLs were added (duplicates are skipped).':'कोई नया मान्य URL नहीं जोड़ा गया (डुप्लिकेट छोड़े गए)।',
'Choose a folder':'फ़ोल्डर चुनें','Download destination folder':'डाउनलोड फ़ोल्डर','Open containing folder':'फ़ाइल वाला फ़ोल्डर खोलें','Open file':'फ़ाइल खोलें','Copy source URL':'सोर्स URL कॉपी करें','Remove from history (keeps the file)':'इतिहास से हटाएँ (फ़ाइल सुरक्षित रहेगी)','Show file path':'फ़ाइल का पथ दिखाएँ','Play video / open downloaded file':'वीडियो चलाएँ / डाउनलोड की गई फ़ाइल खोलें',
'Enter a URL':'URL दर्ज करें','Paste a full video URL beginning with https://':'https:// से शुरू होने वाला पूरा वीडियो URL पेस्ट करें','yt-dlp is missing':'yt-dlp मौजूद नहीं है','File not found':'फ़ाइल नहीं मिली','Saved file':'सेव की गई फ़ाइल','Could not open':'खोल नहीं सके',
'Views unavailable':'व्यू उपलब्ध नहीं','AVAILABLE VIDEO FORMATS':'उपलब्ध वीडियो फ़ॉर्मैट','video + audio':'वीडियो + ऑडियो','video only':'केवल वीडियो','Size unknown':'आकार उपलब्ध नहीं','Duration unavailable':'अवधि उपलब्ध नहीं',
'Link inspection':'लिंक जाँच','Paste a supported public video or media URL. The app uses yt-dlp to identify the source and available media formats.':'समर्थित सार्वजनिक वीडियो या मीडिया URL पेस्ट करें। ऐप स्रोत और उपलब्ध फ़ॉर्मैट पहचानने के लिए yt-dlp का उपयोग करता है।',
'Inspect before downloading':'डाउनलोड से पहले जाँचें','View the title, uploader, duration, views when available, and a selection of available resolutions and formats.':'शीर्षक, अपलोडर, अवधि, उपलब्ध होने पर व्यू, और रिज़ॉल्यूशन व फ़ॉर्मैट के विकल्प देखें।',
'Choose format and quality':'फ़ॉर्मैट और गुणवत्ता चुनें','MP4 conversion probes codecs first: compatible streams are copied, audio-only conversion is used when possible, and video is re-encoded only when needed.':'MP4 कन्वर्ज़न पहले कोडेक जाँचता है: संगत स्ट्रीम कॉपी होती हैं, संभव होने पर केवल ऑडियो बदला जाता है और ज़रूरत पर ही वीडियो दोबारा एन्कोड होता है।',
'Track progress':'प्रगति देखें','Progress updates are throttled to keep the interface smooth. Speed and ETA appear when the source provides them.':'इंटरफ़ेस को सहज रखने के लिए प्रगति अपडेट नियंत्रित हैं। स्रोत उपलब्ध कराए तो गति और अनुमानित समय दिखता है।',
'Keep downloads organized':'डाउनलोड व्यवस्थित रखें','Completed items show a title, thumbnail when available, date, format and detected website. Click the thumbnail to open the saved video or use the folder action to locate it.':'पूरे हुए आइटम में शीर्षक, उपलब्ध होने पर थंबनेल, तारीख, फ़ॉर्मैट और वेबसाइट दिखती है। वीडियो खोलने के लिए थंबनेल पर क्लिक करें या फ़ोल्डर विकल्प चुनें।',
'Your history stays local':'आपका इतिहास आपके कंप्यूटर पर रहता है','Preferences, download history and cached thumbnails are stored on your computer. Clearing history removes its records, not the downloaded media files.':'पसंद, डाउनलोड इतिहास और कैश किए गए थंबनेल आपके कंप्यूटर पर सेव होते हैं। इतिहास साफ़ करने से रिकॉर्ड हटते हैं, मीडिया फ़ाइलें नहीं।',
'Check details before you download.':'डाउनलोड से पहले विवरण जाँचें।','MP4, WebM, MKV and more.':'MP4, WebM, MKV और अन्य।','Progress, speed and ETA.':'प्रगति, गति और अनुमानित समय।','Access your downloads anytime.':'अपने डाउनलोड कभी भी देखें।',
'Universal Downloader was developed by Arth Awasthi to make everyday video-saving workflows quicker and less cumbersome. Instead of jumping between separate websites and conversion tools, it brings link inspection, quality selection, downloading, conversion and history together in one place — helping you spend less time managing files and more time using your media.':'Universal Downloader को Arth Awasthi ने रोज़मर्रा के वीडियो सेव करने के काम को तेज़ और आसान बनाने के लिए विकसित किया। अलग-अलग वेबसाइट और कन्वर्ज़न टूल के बीच जाने के बजाय, यह लिंक जाँच, गुणवत्ता चयन, डाउनलोड, कन्वर्ज़न और इतिहास को एक जगह लाता है।',
'Link copied':'लिंक कॉपी हो गया','Source URL copied':'सोर्स URL कॉपी हो गया','Link pasted':'लिंक पेस्ट हो गया','Clipboard is empty.':'क्लिपबोर्ड खाली है।','Copied to clipboard':'क्लिपबोर्ड पर कॉपी किया गया','Language changed':'भाषा बदल दी गई',
},
'es': {
'Add multiple URLs':'Añadir varias URL','Paste one video URL per line:':'Pega una URL de vídeo por línea:','Toggle light/dark theme':'Cambiar entre tema claro y oscuro','Universal Downloader brings link inspection, format selection, downloading, conversion and file organization into one clean desktop workspace. The goal is to reduce repetitive steps and help you get to your saved media faster.':'Universal Downloader reúne el análisis de enlaces, la selección de formato, las descargas, la conversión y la organización de archivos en un espacio de trabajo sencillo para reducir pasos repetitivos.','Reduce motion':'Reducir movimiento','Animation preferences':'Preferencias de animación','Reduce motion enabled':'Movimiento reducido activado','Reduce motion disabled':'Movimiento reducido desactivado','Download   •   Convert   •   Organize':'Descargar • Convertir • Organizar','Choose download folder':'Elegir carpeta de descargas','✦  All caught up!':'✦  Todo al día','0 queued':'0 en cola',
'MP4 (Premiere-friendly)':'MP4 (compatible con Premiere)','MP3 (audio only)':'MP3 (solo audio)','MKV':'MKV','WEBM':'WEBM','M4A (audio only)':'M4A (solo audio)','Best available':'Mejor calidad disponible','8K (4320p)':'8K (4320p)','4K (2160p)':'4K (2160p)','1440p':'1440p','1080p':'1080p','720p':'720p','480p':'480p','360p':'360p',
'Choose a save location first.':'Primero elige una ubicación de guardado.','Saved successfully:':'Guardado correctamente:','Remove all items from the app history? Downloaded files will not be deleted.':'¿Eliminar todos los elementos del historial? Los archivos descargados no se borrarán.','File is no longer at:':'El archivo ya no está en:','Run this command:':'Ejecuta este comando:','Universal Downloader could not start':'No se pudo iniciar Universal Downloader',
'Views unavailable':'Visualizaciones no disponibles','Download complete.':'Descarga completada.','Download failed — see error details.':'La descarga falló; consulta los detalles del error.','Starting queued download…':'Iniciando descarga en cola…','Inspection complete.':'Análisis completado.','Inspecting source and available formats…':'Analizando el origen y los formatos disponibles…',
'Could not convert':'No se pudo convertir','Copy failed':'Error al copiar','Paste failed':'Error al pegar','Language changed':'Idioma cambiado','Download transferred — preparing output…':'Descarga transferida; preparando el archivo…','Converting to H.264 MP4…':'Convirtiendo a H.264 MP4…','Remuxing compatible streams (fast, no re-encode)':'Reempaquetando secuencias compatibles (rápido, sin recodificar)','Copying video; converting audio to AAC':'Copiando vídeo; convirtiendo audio a AAC','Converting video to H.264 and audio to AAC':'Convirtiendo vídeo a H.264 y audio a AAC','Download':'Descargar','Completed':'Completados','About & Features':'Acerca de','Dark mode':'Modo oscuro','Light mode':'Modo claro',
'Video URL':'URL del vídeo','Paste a video URL here…':'Pega aquí la URL del vídeo…','Paste':'Pegar','Inspect':'Analizar',
'Output Format':'Formato de salida','Max Resolution':'Resolución máxima','Save Location':'Ubicación de guardado','Choose folder':'Elegir carpeta','Open save folder':'Abrir carpeta de guardado',
'Video Details':'Detalles del vídeo','Inspect a link to see its title, duration, uploader and available formats.':'Analiza un enlace para ver el título, la duración, el autor y los formatos disponibles.',
'Add to Queue & Start':'Añadir a la cola e iniciar','Add Multiple URLs':'Añadir varias URL','Paste multiple URLs, one per line':'Pega una URL por línea','Download queue':'Cola de descargas','Clear queued':'Vaciar cola',
'Queued URLs are saved locally and restored when the app restarts.':'Las URL de la cola se guardan localmente y se restauran al reiniciar la aplicación.',
'Ready — paste a video link to begin':'Listo: pega un enlace de vídeo para comenzar','Completed downloads':'Descargas completadas','Open downloads folder':'Abrir carpeta de descargas','Clear history':'Borrar historial',
'Download only content you own or have permission to save. Private, DRM-protected or access-restricted media isn’t supported.':'Descarga solo contenido propio o que tengas permiso para guardar. No se admite contenido privado, protegido por DRM o restringido.',
'Search and filter your local download library. Removing an entry never deletes the actual video.':'Busca y filtra tu biblioteca local. Quitar un registro no elimina el archivo de vídeo.',
'Search titles or filenames…':'Buscar títulos o nombres de archivo…','All Websites':'Todos los sitios','Latest first':'Más recientes primero','Oldest first':'Más antiguos primero','Clear filters':'Borrar filtros',
'No downloads match these filters.':'Ninguna descarga coincide con estos filtros.','Your completed downloads will appear here.':'Tus descargas completadas aparecerán aquí.',
'A B O U T':'ACERCA DE','A simpler way to save media':'Una forma más sencilla de guardar contenido','Made to make saving media simpler':'Diseñado para guardar contenido con facilidad',
'Universal Downloader helps you fetch, convert and organize your media files —\nquickly, easily and without unnecessary steps.':'Universal Downloader te ayuda a descargar, convertir y organizar archivos multimedia de forma rápida y sencilla.',
'Built for your workflow':'Diseñado para tu flujo de trabajo','Paste & inspect link':'Pegar y analizar enlace','Inspect before downloading':'Analizar antes de descargar','Choose format and quality':'Elegir formato y calidad','Track progress':'Seguir el progreso','Keep downloads organized':'Organizar las descargas','Your history stays local':'Tu historial permanece local',
'At a glance':'Resumen','Link inspection':'Análisis de enlaces','Format selection':'Selección de formato','Download tracking':'Seguimiento de descargas','Local history':'Historial local',
'Created by Arth Awasthi':'Creado por Arth Awasthi','Follow me @arth_lives':'Sígueme en @arth_lives','Instagram  ↗':'Instagram  ↗',
'Only download content you own or have permission to save. Respect creators’ rights.':'Descarga solo contenido propio o autorizado. Respeta los derechos de los creadores.',
'Link copied':'Enlace copiado','Source URL copied':'URL de origen copiada','Link pasted':'Enlace pegado','Clipboard is empty.':'El portapapeles está vacío.','Copied to clipboard':'Copiado al portapapeles',
'Language':'Idioma','Language & Region':'Idioma y región','English':'English','हिन्दी':'हिन्दी','Español':'Español',
'Choose a folder':'Elegir una carpeta','Please choose a save location first.':'Primero elige una ubicación para guardar.','Download in progress':'Descarga en curso','The active download cannot be cancelled safely yet. Only waiting items will be removed.':'Aún no se puede cancelar de forma segura la descarga activa. Solo se eliminarán los elementos en espera.',
'Download complete':'Descarga completada','Download failed':'Error de descarga','Inspection complete.':'Análisis completado.','Inspecting source and available formats…':'Analizando el origen y los formatos disponibles…','Starting queued download…':'Iniciando descarga en cola…','Download complete.':'Descarga completada.','Download failed — see error details.':'La descarga falló; consulta los detalles del error.',
'All Websites':'Todos los sitios','Size unknown':'Tamaño desconocido','Duration unavailable':'Duración no disponible',
'active':'activos','queued':'en cola','downloads completed':'descargas completadas','of':'de','downloads':'descargas','Queued':'En cola','Downloading':'Descargando','Completed':'Completado','Failed':'Error','Cancelled':'Cancelado',
'No new valid URLs were added (duplicates are skipped).':'No se añadieron URL válidas nuevas (se omiten los duplicados).',
'Choose a folder':'Elegir una carpeta','Download destination folder':'Carpeta de destino','Open containing folder':'Abrir carpeta contenedora','Open file':'Abrir archivo','Copy source URL':'Copiar URL de origen','Remove from history (keeps the file)':'Quitar del historial (conserva el archivo)','Show file path':'Mostrar la ruta del archivo','Play video / open downloaded file':'Reproducir vídeo / abrir archivo descargado',
'Enter a URL':'Introduce una URL','Paste a full video URL beginning with https://':'Pega una URL completa de vídeo que empiece por https://','yt-dlp is missing':'Falta yt-dlp','File not found':'Archivo no encontrado','Saved file':'Archivo guardado','Could not open':'No se pudo abrir',
'Views unavailable':'Vistas no disponibles','AVAILABLE VIDEO FORMATS':'FORMATOS DE VÍDEO DISPONIBLES','video + audio':'vídeo + audio','video only':'solo vídeo','Size unknown':'Tamaño desconocido','Duration unavailable':'Duración no disponible',
'Paste a supported public video or media URL. The app uses yt-dlp to identify the source and available media formats.':'Pega una URL pública compatible de vídeo o contenido multimedia. La aplicación usa yt-dlp para identificar el origen y los formatos disponibles.',
'View the title, uploader, duration, views when available, and a selection of available resolutions and formats.':'Consulta el título, autor, duración, visualizaciones cuando estén disponibles y una selección de resoluciones y formatos.',
'MP4 conversion probes codecs first: compatible streams are copied, audio-only conversion is used when possible, and video is re-encoded only when needed.':'La conversión MP4 comprueba primero los códecs: copia las secuencias compatibles, convierte solo el audio cuando es posible y vuelve a codificar el vídeo únicamente cuando hace falta.',
'Progress updates are throttled to keep the interface smooth. Speed and ETA appear when the source provides them.':'Las actualizaciones de progreso se limitan para mantener la fluidez. La velocidad y el tiempo estimado aparecen cuando el origen los proporciona.',
'Completed items show a title, thumbnail when available, date, format and detected website. Click the thumbnail to open the saved video or use the folder action to locate it.':'Los elementos completados muestran título, miniatura si está disponible, fecha, formato y sitio detectado. Pulsa la miniatura para abrir el vídeo o usa la acción de carpeta para localizarlo.',
'Preferences, download history and cached thumbnails are stored on your computer. Clearing history removes its records, not the downloaded media files.':'Las preferencias, el historial de descargas y las miniaturas en caché se guardan en tu equipo. Borrar el historial elimina los registros, no los archivos multimedia.',
'Check details before you download.':'Comprueba los detalles antes de descargar.','MP4, WebM, MKV and more.':'MP4, WebM, MKV y más.','Progress, speed and ETA.':'Progreso, velocidad y tiempo estimado.','Access your downloads anytime.':'Accede a tus descargas cuando quieras.',
'Universal Downloader was developed by Arth Awasthi to make everyday video-saving workflows quicker and less cumbersome. Instead of jumping between separate websites and conversion tools, it brings link inspection, quality selection, downloading, conversion and history together in one place — helping you spend less time managing files and more time using your media.':'Universal Downloader fue desarrollado por Arth Awasthi para agilizar y simplificar el guardado de vídeos. En lugar de alternar entre sitios web y herramientas de conversión, reúne el análisis de enlaces, la selección de calidad, las descargas, la conversión y el historial en un solo lugar.',
'Link copied':'Enlace copiado','Source URL copied':'URL de origen copiada','Link pasted':'Enlace pegado','Clipboard is empty.':'El portapapeles está vacío.','Copied to clipboard':'Copiado al portapapeles','Language changed':'Idioma cambiado',
}}

# Additional labels used in dynamically-created widgets and status messages.
# Kept separately so new UI strings are easy to audit and extend.
EXTRA_TRANSLATIONS = {
    "hi": {
        "Universal Downloader": "Universal Downloader",
        "Universal\nDownloader": "Universal\nDownloader",
        "Download   •   Convert   •   Organize": "डाउनलोड • कन्वर्ट • व्यवस्थित करें",
        "Download destination folder": "डाउनलोड के लिए फ़ोल्डर",
        "Paste multiple URLs, one per line": "कई URL पेस्ट करें, हर पंक्ति में एक",
        "Ready — paste a video link to begin": "तैयार — शुरू करने के लिए वीडियो लिंक पेस्ट करें",
        "Download only content you own or have permission to save. Private, DRM-protected or access-restricted media isn’t supported.": "केवल वही सामग्री डाउनलोड करें जिसे सेव करने का अधिकार आपके पास है। निजी, DRM-सुरक्षित या प्रतिबंधित मीडिया समर्थित नहीं है।",
        "Search and filter your local download library. Removing an entry never deletes the actual video.": "अपनी डाउनलोड लाइब्रेरी में खोजें और फ़िल्टर लगाएँ। रिकॉर्ड हटाने से असली वीडियो डिलीट नहीं होता।",
        "A B O U T": "ऐप के बारे में",
        "A simpler way to save media": "मीडिया सेव करने का आसान तरीका",
        "Made to make saving media simpler": "मीडिया सेव करना आसान बनाने के लिए",
        "Built for your workflow": "आपके वर्कफ़्लो के लिए",
        "At a glance": "एक नज़र में",
        "Universal Downloader was developed by Arth Awasthi to make everyday video-saving workflows quicker and less cumbersome. Instead of jumping between separate websites and conversion tools, it brings link inspection, quality selection, downloading, conversion and history together in one place — helping you spend less time managing files and more time using your media.": "Universal Downloader को Arth Awasthi ने वीडियो सेव करने की प्रक्रिया को आसान और तेज़ बनाने के लिए बनाया है। अलग-अलग वेबसाइट और कन्वर्ज़न टूल इस्तेमाल करने के बजाय, यह लिंक जाँच, गुणवत्ता चयन, डाउनलोड, कन्वर्ज़न और इतिहास को एक जगह लाता है।",
        "Only download content you own or have permission to save. Respect creators’ rights.": "केवल वही सामग्री डाउनलोड करें जिसे सेव करने की अनुमति आपके पास है। क्रिएटर्स के अधिकारों का सम्मान करें।",
        "Follow me @arth_lives": "@arth_lives पर फ़ॉलो करें",
        "Instagram  ↗": "Instagram  ↗",
        "Open file": "फ़ाइल खोलें",
        "Open containing folder": "फ़ाइल वाला फ़ोल्डर खोलें",
        "Copy source URL": "सोर्स URL कॉपी करें",
        "Remove from history (keeps the file)": "इतिहास से हटाएँ (फ़ाइल सुरक्षित रहेगी)",
        "Show file path": "फ़ाइल का पथ दिखाएँ",
        "Play video / open downloaded file": "वीडियो चलाएँ / डाउनलोड की गई फ़ाइल खोलें",
        "No downloads match these filters.": "इन फ़िल्टर से कोई डाउनलोड नहीं मिला।",
        "Your completed downloads will appear here.": "आपके पूरे हुए डाउनलोड यहाँ दिखाई देंगे।",
        "✦  All caught up!": "✦  सब अपडेट है!",
        "0 queued": "0 कतार में",
        "No new valid URLs were added (duplicates are skipped).": "कोई नया मान्य URL नहीं जोड़ा गया (डुप्लिकेट छोड़ दिए गए)।",
        "Link inspection": "लिंक जाँच",
        "Format selection": "फ़ॉर्मैट चयन",
        "Download tracking": "डाउनलोड की स्थिति",
        "Local history": "स्थानीय इतिहास",
        "Paste & inspect link": "लिंक पेस्ट करें और जाँचें",
        "Keep downloads organized": "डाउनलोड व्यवस्थित रखें",
        "Your history stays local": "आपका इतिहास आपके कंप्यूटर पर रहता है",
        "Progress updates are throttled to keep the interface smooth. Speed and ETA appear when the source provides them.": "इंटरफ़ेस को सुचारु रखने के लिए प्रगति अपडेट नियंत्रित हैं। स्रोत उपलब्ध कराए तो गति और अनुमानित समय भी दिखेंगे।",
        "Completed items show a title, thumbnail when available, date, format and detected website. Click the thumbnail to open the saved video or use the folder action to locate it.": "पूरे हुए डाउनलोड में शीर्षक, उपलब्ध होने पर थंबनेल, तारीख, फ़ॉर्मैट और वेबसाइट दिखाई जाती है। वीडियो खोलने के लिए थंबनेल पर क्लिक करें या फ़ोल्डर विकल्प इस्तेमाल करें।",
    },
    "es": {
        "Universal Downloader": "Universal Downloader",
        "Universal\nDownloader": "Universal\nDownloader",
        "Download   •   Convert   •   Organize": "Descargar • Convertir • Organizar",
        "Download destination folder": "Carpeta de destino de descarga",
        "Paste multiple URLs, one per line": "Pega varias URL, una por línea",
        "Ready — paste a video link to begin": "Listo: pega un enlace de vídeo para empezar",
        "Download only content you own or have permission to save. Private, DRM-protected or access-restricted media isn’t supported.": "Descarga solo contenido propio o autorizado. No se admite contenido privado, protegido por DRM o con acceso restringido.",
        "Search and filter your local download library. Removing an entry never deletes the actual video.": "Busca y filtra tu biblioteca local de descargas. Quitar una entrada nunca elimina el vídeo original.",
        "A B O U T": "ACERCA DE",
        "A simpler way to save media": "Una forma más sencilla de guardar contenido",
        "Made to make saving media simpler": "Creado para simplificar el guardado de contenido",
        "Built for your workflow": "Diseñado para tu flujo de trabajo",
        "At a glance": "De un vistazo",
        "Universal Downloader was developed by Arth Awasthi to make everyday video-saving workflows quicker and less cumbersome. Instead of jumping between separate websites and conversion tools, it brings link inspection, quality selection, downloading, conversion and history together in one place — helping you spend less time managing files and more time using your media.": "Universal Downloader fue desarrollado por Arth Awasthi para agilizar el guardado de vídeos. En lugar de alternar entre sitios web y herramientas de conversión, reúne el análisis de enlaces, la selección de calidad, las descargas, la conversión y el historial en un solo lugar.",
        "Only download content you own or have permission to save. Respect creators’ rights.": "Descarga solo contenido propio o autorizado. Respeta los derechos de los creadores.",
        "Follow me @arth_lives": "Sígueme en @arth_lives",
        "Instagram  ↗": "Instagram  ↗",
        "Open file": "Abrir archivo",
        "Open containing folder": "Abrir carpeta contenedora",
        "Copy source URL": "Copiar URL de origen",
        "Remove from history (keeps the file)": "Quitar del historial (conserva el archivo)",
        "Show file path": "Mostrar la ruta del archivo",
        "Play video / open downloaded file": "Reproducir vídeo / abrir archivo descargado",
        "No downloads match these filters.": "Ninguna descarga coincide con estos filtros.",
        "Your completed downloads will appear here.": "Tus descargas completadas aparecerán aquí.",
        "✦  All caught up!": "✦  Todo al día",
        "0 queued": "0 en cola",
        "No new valid URLs were added (duplicates are skipped).": "No se añadieron URL válidas nuevas (se omiten los duplicados).",
        "Link inspection": "Análisis de enlaces",
        "Format selection": "Selección de formato",
        "Download tracking": "Seguimiento de descargas",
        "Local history": "Historial local",
        "Paste & inspect link": "Pegar y analizar enlace",
        "Keep downloads organized": "Mantén tus descargas organizadas",
        "Your history stays local": "Tu historial permanece en tu equipo",
        "Progress updates are throttled to keep the interface smooth. Speed and ETA appear when the source provides them.": "Las actualizaciones de progreso se limitan para mantener la interfaz fluida. La velocidad y el tiempo estimado aparecen cuando el origen los proporciona.",
        "Completed items show a title, thumbnail when available, date, format and detected website. Click the thumbnail to open the saved video or use the folder action to locate it.": "Los elementos completados muestran el título, una miniatura si está disponible, la fecha, el formato y el sitio detectado. Haz clic en la miniatura para abrir el vídeo o usa la opción de carpeta para localizarlo.",
    },
}
for _language, _entries in EXTRA_TRANSLATIONS.items():
    TRANSLATIONS.setdefault(_language, {}).update(_entries)


def translate(text: str, language: str = 'en') -> str:
    """Translate a UI string with tolerant whitespace and punctuation matching.

    Unknown strings intentionally fall back to the source text, so URLs, filenames,
    user-entered content and technical values are never corrupted.
    """
    if not isinstance(text, str) or language == 'en':
        return text
    table = TRANSLATIONS.get(language, {})
    if not table:
        return text
    if text in table:
        return table[text]

    # UI strings can acquire extra spaces/newlines from Qt layouts or rich text.
    import re
    normalized = re.sub(r'\s+', ' ', text).strip()
    if normalized in table:
        return table[normalized]

    # Build a normalized lookup once per language, preserving the authored mapping.
    cache = getattr(translate, '_normalized_cache', None)
    if cache is None:
        cache = {}
        setattr(translate, '_normalized_cache', cache)
    if language not in cache:
        cache[language] = {re.sub(r'\s+', ' ', key).strip().casefold(): value
                           for key, value in table.items()}
    return cache[language].get(normalized.casefold(), text)
