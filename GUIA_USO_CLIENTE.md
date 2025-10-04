# 📖 Guía de Uso - Sistema de Reclutamiento con IA

## Bienvenida 👋

Este sistema te permite cargar contactos de LinkedIn, enriquecer sus datos automáticamente, y buscar candidatos ideales usando inteligencia artificial.

---

## 🎯 Paso a Paso: Cómo Usar la Aplicación

### **Pestaña 1: Upload & Enrich (Cargar y Enriquecer)**

#### **Paso 1: Cargar Contactos de LinkedIn**

1. Prepara un archivo Excel (.xlsx) o CSV con una columna que contenga URLs de LinkedIn
   - La columna puede llamarse: `LinkedIn URL`, `Profile URL`, `linkedin_url`, etc.
   - Ejemplo de URL: `https://www.linkedin.com/in/nombre-persona/`

2. Haz clic en **"Browse files"** (Examinar archivos)

3. Selecciona tu archivo Excel o CSV

4. La aplicación mostrará una vista previa de los contactos cargados

#### **Paso 2: Agregar Contactos a la Planilla Principal**

1. Revisa la vista previa de tus contactos

2. Haz clic en el botón **"Add to Spreadsheet"** (Agregar a Planilla)

3. **IMPORTANTE**: Confirma que entiendes que esto borrará los datos anteriores
   - Cada vez que agregues nuevos contactos, la planilla se limpia automáticamente
   - Esto es normal y necesario para evitar duplicados

4. Verás un mensaje de confirmación: "✅ Successfully added X contacts to spreadsheet"

#### **Paso 3: Enriquecer Datos con IA**

1. Después de agregar los contactos, haz clic en **"🚀 Start Data Enrichment"** (Iniciar Enriquecimiento)

2. La aplicación comenzará a buscar información adicional sobre cada contacto:
   - Título del trabajo actual
   - Empresa actual
   - Educación y grados académicos
   - Habilidades (skills)
   - Descripción profesional
   - Experiencia laboral

3. Verás una barra de progreso que muestra el avance:
   - "⏳ Processing..." mientras trabaja
   - "✅ Completed" cuando termine

4. **Tiempo estimado**: 2-5 minutos dependiendo de la cantidad de contactos

5. Una vez completado, verás una vista previa de los datos enriquecidos

#### **⚠️ Notas Importantes:**

- **No uses los mismos datos dos veces seguidas**: Si necesitas probar nuevamente, usa un archivo Excel diferente con URLs distintas
- **Límite de ejecuciones paralelas**: Si ves un mensaje de "máximo de ejecuciones paralelas alcanzado", espera 5-10 minutos antes de intentar nuevamente
- **Datos de demostración**: Si solo quieres probar la aplicación sin esperar el enriquecimiento, puedes usar los datos de demostración que vienen precargados

---

### **Pestaña 2: Search Candidates (Buscar Candidatos con IA)**

Esta es la pestaña más poderosa - aquí puedes conversar con la IA para encontrar candidatos ideales.

#### **Estado del Sistema**

Al entrar a esta pestaña, verás uno de estos mensajes:

- ✅ **"OpenAI GPT-4o is active and ready"** = Todo funciona perfecto
- ❌ **"OpenAI API key not configured"** = Contacta al equipo técnico

#### **Cómo Buscar Candidatos**

**Opción A: Usar Preguntas Predefinidas**

1. En la parte superior verás botones con preguntas sugeridas:
   - "Quien tiene magíster en finanzas?"
   - "Quien trabajó en marketing digital?"
   - "Quien tiene experiencia en minería?"
   - etc.

2. Haz clic en cualquier pregunta que te interese

3. La IA analizará automáticamente todos los candidatos y mostrará solo los más relevantes

4. **IMPORTANTE - Ubicación de la Respuesta**:
   - Después de hacer clic, **desplázate hacia abajo** para ver la respuesta de la IA
   - La respuesta aparecerá en la sección "Chat History" en la parte inferior
   - O bien, haz clic en **"🗑️ Clear Chat"** después de cada búsqueda para mantener la pantalla limpia

**Opción B: Hacer Tu Propia Pregunta**

1. En el cuadro de texto grande escribe tu pregunta en lenguaje natural

2. Ejemplos de preguntas efectivas:
   - "Quién tiene experiencia en desarrollo web y habla inglés?"
   - "Necesito un ingeniero comercial con experiencia en ventas B2B"
   - "Busco alguien con Python y experiencia en startups"
   - "Quién estudió en la Universidad de Chile y trabajó en finanzas?"
   - "Necesito un contador con conocimientos de IFRS"

3. Haz clic en **"🔍 Search"** (Buscar)

4. Espera unos segundos mientras ves: "🤖 AI is analyzing candidates..."

5. **Revisa los resultados**:
   - Desplázate hacia abajo para ver la respuesta en "Chat History"
   - La IA te mostrará solo los candidatos relevantes con explicación de por qué coinciden
   - Verás información detallada de cada candidato: nombre, cargo, empresa, educación, habilidades

#### **💡 Consejos para Mejores Resultados**

✅ **HAZ preguntas específicas**:
- "Quién tiene MBA y experiencia en retail?"
- "Necesito un desarrollador Full Stack con React"

❌ **EVITA preguntas muy vagas**:
- "Quién es bueno?"
- "Dame candidatos"

✅ **Combina múltiples criterios**:
- "Quién tiene magíster en ingeniería Y trabajó en minería?"
- "Busco alguien con Excel avanzado que haya trabajado en banca"

✅ **Usa términos en español**: La IA entiende perfectamente el español chileno

#### **Gestión del Chat**

- **Historial de conversación**: Todas tus búsquedas se guardan en "Chat History" al final de la página
- **Limpiar el chat**: Usa el botón **"🗑️ Clear Chat"** para empezar de nuevo
- **Scroll automático**: Después de cada búsqueda, **baja al final de la página** para ver la respuesta más reciente

---

### **Pestaña 3: Data View (Vista de Datos)**

Esta pestaña te muestra todos los datos enriquecidos en formato tabla.

#### **Qué Verás Aquí**

1. **Información Personal**:
   - Nombre completo (First Name, Last Name)
   - LinkedIn URL

2. **Información Profesional**:
   - Headline (título profesional actual)
   - Company Name (empresa actual)
   - Job Title (cargo actual)
   - Job Description (descripción del trabajo)

3. **Educación**:
   - School Name (universidad/institución)
   - School Degree (grado académico)

4. **Habilidades y Más**:
   - Skills Label (habilidades listadas en LinkedIn)
   - Description (descripción del perfil)
   - Ubicación
   - Fechas de trabajo

5. **Datos Técnicos**:
   - Profile URL
   - Imagen URL
   - Timestamps

#### **Descargar Datos**

- Al final de la página encontrarás un botón **"📥 Download CSV"**
- Descarga todos los datos enriquecidos en formato Excel/CSV
- Úsalo para compartir con tu equipo o importar a otros sistemas

---

## 🎬 Flujo de Trabajo Recomendado

### **Primera Vez / Demostración Completa**

1. **Cargar datos nuevos**:
   - Upload & Enrich → Cargar archivo Excel
   - Add to Spreadsheet
   - Start Data Enrichment
   - Esperar 3-5 minutos

2. **Explorar candidatos**:
   - Search Candidates → Probar preguntas predefinidas
   - Hacer preguntas personalizadas
   - Revisar respuestas de la IA

3. **Revisar datos completos**:
   - Data View → Ver toda la información
   - Descargar CSV si es necesario

### **Solo Probar la IA (Modo Rápido)**

Si solo quieres demostrar la capacidad de búsqueda inteligente:

1. **NO subas datos nuevos** - usa los datos de demostración que ya están cargados

2. Ve directo a **"Search Candidates"**

3. Prueba diferentes preguntas y muestra cómo la IA filtra candidatos inteligentemente

4. Esto es perfecto para reuniones rápidas o demos sin tiempo de espera

---

## ⚠️ Solución de Problemas Comunes

### "Service account key file not found"
- **Solución**: Contacta al equipo técnico - problema de configuración

### "Maximum parallel executions limit reached"
- **Problema**: Ya hay un proceso de enriquecimiento corriendo
- **Solución**: Espera 5-10 minutos y vuelve a intentar

### "0 leads updated" o "No data enriched"
- **Problema**: Las URLs de LinkedIn pueden estar incorrectas o el servicio está ocupado
- **Solución**: 
  1. Verifica que las URLs sean válidas (formato: `https://www.linkedin.com/in/nombre/`)
  2. Intenta con un archivo diferente
  3. Si persiste, contacta al equipo técnico

### La IA muestra todos los candidatos en vez de filtrar
- **Problema**: Puede haber un error temporal con OpenAI
- **Solución**: 
  1. Verifica que veas el mensaje verde "✅ OpenAI GPT-4o is active"
  2. Si ves error rojo, contacta al equipo técnico
  3. Haz clic en "Clear Error" y vuelve a intentar

### No veo la respuesta después de hacer una pregunta
- **Solución**: **Desplázate hacia abajo** - la respuesta está en "Chat History" al final de la página

---

## 📊 Datos de Ejemplo para Probar

Si necesitas archivos Excel de muestra para probar, el equipo técnico te proporcionará varios archivos con diferentes URLs de LinkedIn.

**Recuerda**: No uses el mismo archivo dos veces seguidas. Alterna entre los diferentes archivos de muestra que te proporcionamos.

---

## 💬 ¿Preguntas o Problemas?

Si encuentras algún problema o tienes preguntas:

1. Toma una captura de pantalla del error
2. Anota qué estabas haciendo cuando ocurrió
3. Contacta al equipo técnico

---

## ✨ Tips para Impresionar a Clientes

1. **Prepara datos de muestra relevantes**: Si vas a presentar a un cliente del sector financiero, usa contactos de LinkedIn de ese sector

2. **Practica las preguntas**: Antes de la demo, piensa qué tipo de preguntas haría tu cliente y pruébalas

3. **Muestra la velocidad**: Destaca que encontrar candidatos específicos con IA toma segundos vs. horas de búsqueda manual

4. **Compara resultados**: Haz una pregunta amplia primero ("Quién trabajó en finanzas?") y luego una más específica ("Quién tiene MBA en finanzas y trabajó en banca internacional?") para mostrar la precisión

5. **Usa el modo rápido**: Para demos ejecutivas de 10-15 minutos, usa los datos de demostración precargados y enfócate solo en "Search Candidates"

---

## 🎯 Casos de Uso Reales

**Ejemplo 1: Reclutamiento para Startup Tech**
- Pregunta: "Quién tiene experiencia en desarrollo web con React o Vue?"
- Pregunta: "Necesito alguien que haya trabajado en startups y tenga skills de frontend"

**Ejemplo 2: Búsqueda Ejecutiva para Minería**
- Pregunta: "Quién tiene título de ingeniero y experiencia en minería?"
- Pregunta: "Busco ejecutivos con MBA que hayan trabajado en proyectos mineros"

**Ejemplo 3: Búsqueda de Contador**
- Pregunta: "Quién es contador auditor con experiencia en IFRS?"
- Pregunta: "Necesito un contador senior que haya trabajado en consultoras grandes"

---

## 📝 Resumen Rápido

1. ✅ **Upload & Enrich**: Sube Excel → Add to Spreadsheet → Start Enrichment → Espera
2. ✅ **Search Candidates**: Haz preguntas → Scroll down para ver respuestas → Clear chat cuando termines
3. ✅ **Data View**: Revisa todos los datos → Descarga CSV
4. ⚠️ **Importante**: Usa archivos diferentes cada vez, no repitas los mismos datos
5. 🚀 **Modo Demo Rápido**: Salta el upload y usa datos precargados para demos rápidas

---

**¡Éxito con tus presentaciones! 🎉**

