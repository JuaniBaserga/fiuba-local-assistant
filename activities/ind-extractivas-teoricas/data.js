window.STUDY_DATA = [
  {
    id: "trituracion",
    title: "Trituracion",
    accent: "#d55f3f",
    summary: "Equipos, mecanismos de rotura, esquemas funcionales y rangos de uso.",
    questions: [
      {
        type: "mc",
        difficulty: "Conceptual",
        q: "En una trituradora de mandibulas tipo Blake, que debe quedar claro en el esquema funcional?",
        options: [
          "Que una placa queda fija, la otra movil genera el movimiento de masticacion y los apoyos permiten esa movilidad.",
          "Que ambas placas giran libremente alrededor de un eje central.",
          "Que la rotura ocurre por centrifugacion del material contra la carcasa.",
          "Que el producto sale por rebalse superior."
        ],
        answer: 0,
        explain: "El repaso insiste en que el esquema sea simple pero funcione: apoyos, biela/rotor y desplazamiento coherente de la placa movil.",
        keywords: ["placa fija", "placa movil", "masticacion", "apoyo", "biela"]
      },
      {
        type: "mc",
        difficulty: "Diferencias",
        q: "Cual es la diferencia entre particulas prismaticas, lajas y cubicas?",
        options: [
          "Prismaticas: predomina una dimension; lajas: predominan dos sobre la tercera; cubicas: dimensiones equilibradas.",
          "Prismaticas: son finas; lajas: son magneticas; cubicas: son siempre ganga.",
          "Prismaticas: flotan; lajas: sedimentan; cubicas: se disuelven.",
          "No hay diferencia operativa, solo cambia el nombre comercial."
        ],
        answer: 0,
        explain: "Es una definicion muy preguntable: sirve para explicar forma de particula y comportamiento frente a la rotura.",
        keywords: ["dimension", "predomina", "laja", "equilibradas"]
      },
      {
        type: "mc",
        difficulty: "Equipos",
        q: "Para trituracion primaria, que equipos aparecen como opciones tipicas?",
        options: [
          "Mandibulas Blake y giratorias.",
          "Molino de bolas y filtro prensa.",
          "Hidrociclon y mesa del minero.",
          "Celda de flotacion y clasificador de rastrillo."
        ],
        answer: 0,
        explain: "En el repaso se marca que Blake es exclusivamente primaria y que las giratorias pueden usarse en primaria y otras etapas segun tipo.",
        keywords: ["blake", "giratoria", "primaria"]
      },
      {
        type: "mc",
        difficulty: "Aplicacion",
        q: "Si una pregunta pide trituradora de martillos, que conviene incluir?",
        options: [
          "Esquema 2D con ingreso, rotor, martillos, zona de impacto y salida, mas explicacion del funcionamiento.",
          "Solo una tabla de produccion mundial.",
          "Un esquema 3D detallado de todos los bulones.",
          "La formula de velocidad critica."
        ],
        answer: 0,
        explain: "Los esquemas pedidos son 2D y deben funcionar; si se pide desarrollo, conviene explicar recorrido y mecanismo de rotura.",
        keywords: ["rotor", "martillos", "impacto", "ingreso", "salida"]
      },
      {
        type: "mc",
        difficulty: "Rangos",
        q: "Como estudiar cuadros numericos de trituradoras segun la orientacion del repaso?",
        options: [
          "Por rangos, usos y comparaciones: mayor capacidad, etapas posibles, potencia relativa.",
          "Memorizando cada numero exacto sin interpretar.",
          "Ignorandolos porque nunca pueden entrar.",
          "Solo copiando el titulo de cada columna."
        ],
        answer: 0,
        explain: "El docente aclara que los cuadros numericos se entienden por rangos y usos, no como recitado ciego.",
        keywords: ["rango", "uso", "capacidad", "potencia", "etapa"]
      },
      {
        type: "mc",
        difficulty: "Esquema",
        q: "Si el enunciado pide esquema y funcionamiento de una trituradora, como se reparte la respuesta?",
        options: [
          "Hay que dibujar componentes funcionales y explicar como el movimiento produce la rotura; son partes evaluables por separado.",
          "Alcanza con hacer un dibujo lindo, aunque no se explique el funcionamiento.",
          "Conviene escribir solo definiciones generales y evitar el esquema.",
          "Se responde con una tabla historica del equipo."
        ],
        answer: 0,
        explain: "El repaso insiste en que esquema y desarrollo suman por separado; el dibujo debe ser coherente con la explicacion.",
        keywords: ["esquema", "funcionamiento", "componentes", "rotura", "separado"]
      },
      {
        type: "mc",
        difficulty: "Etapas",
        q: "Que trituradora se menciona como exclusivamente de trituracion primaria?",
        options: [
          "La trituradora de mandibulas Blake.",
          "El molino de barras.",
          "El clasificador de cono doble.",
          "El filtro rotatorio."
        ],
        answer: 0,
        explain: "En el repaso se remarca Blake como equipo de primaria; las giratorias tienen usos mas amplios segun configuracion.",
        keywords: ["blake", "mandibulas", "primaria"]
      },
      {
        type: "mc",
        difficulty: "Volumetria",
        q: "Por que importa distinguir la forma de las particulas en trituracion?",
        options: [
          "Porque la geometria influye en el modo de solicitacion y rotura, por ejemplo flexion en piezas alargadas.",
          "Porque solo las particulas cubicas pueden entrar al equipo.",
          "Porque define si el material es magnetico.",
          "Porque reemplaza al caudal de alimentacion."
        ],
        answer: 0,
        explain: "La forma no es decorativa: prismas, lajas y particulas equilibradas responden distinto ante compresion, impacto o flexion.",
        keywords: ["geometria", "solicitacion", "rotura", "flexion", "forma"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Como explicarias la diferencia entre una trituradora giratoria y una de mandibulas sin dibujar?",
        answerText: "La de mandibulas trabaja con una placa fija y otra movil que produce una accion tipo masticacion. La giratoria usa un elemento conico que se mueve dentro de una carcasa o manto, generando compresion continua del material.",
        keywords: ["mandibulas", "placa fija", "placa movil", "giratoria", "cono", "manto", "compresion"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Que significa que un esquema de trituradora 'funcione'?",
        answerText: "Significa que los apoyos, ejes, bielas o rotores dibujados permiten realmente el movimiento que se explica. No alcanza con copiar formas: el mecanismo debe poder transmitir movimiento y producir la rotura indicada.",
        keywords: ["apoyos", "ejes", "biela", "movimiento", "mecanismo", "rotura"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Explica por que una pieza alargada puede romper por flexion dentro de una trituradora.",
        answerText: "La particula queda solicitada por fuerzas de contacto que generan flexion, especialmente cuando su geometria es alargada. Tambien puede existir compresion, pero en piezas prismaticas largas la flexion suele explicar la rotura.",
        keywords: ["fuerzas", "contacto", "flexion", "alargada", "compresion"]
      }
    ]
  },
  {
    id: "molienda",
    title: "Molienda",
    accent: "#39736a",
    summary: "Velocidad critica, elementos moledores, rebalse, molienda seca/humeda y circuitos.",
    questions: [
      {
        type: "mc",
        difficulty: "Clave",
        q: "Que ocurre si un molino supera la velocidad critica?",
        options: [
          "Particulas y elementos moledores se pegan a la pared por aceleracion centrifuga y deja de producirse molienda efectiva.",
          "La descarga se vuelve automaticamente mas fina sin consumo extra.",
          "El molino pasa de circuito cerrado a abierto.",
          "Los elementos moledores flotan y aumentan la recuperacion."
        ],
        answer: 0,
        explain: "Es uno de los conceptos mas marcados: por encima de la velocidad critica no hay caida util de los cuerpos moledores.",
        keywords: ["velocidad critica", "centrifuga", "pared", "no muele"]
      },
      {
        type: "mc",
        difficulty: "Formula",
        q: "Si piden deducir o usar velocidad critica, que debe acompanarse ademas de la formula?",
        options: [
          "La secuencia de obtencion y que representa cada termino.",
          "Solo el resultado numerico final.",
          "Un grafico historico de produccion.",
          "La densidad de todos los minerales conocidos."
        ],
        answer: 0,
        explain: "Para coloquio o desarrollo pueden pedir obtencion; conviene nombrar terminos, unidades e hipotesis.",
        keywords: ["deduccion", "terminos", "formula", "unidades"]
      },
      {
        type: "mc",
        difficulty: "Conceptual",
        q: "Que idea distingue al rebalse en molinos?",
        options: [
          "El material sale cuando excede un nivel; por eso debe existir una condicion que permita ese excedente.",
          "El material sale por una cinta magnetica.",
          "El material se descarga solo por tamizado seco.",
          "El material queda siempre retenido hasta parar el molino."
        ],
        answer: 0,
        explain: "El repaso remarca razonar la palabra rebalse: exceder nivel y descargar por esa condicion.",
        keywords: ["nivel", "excede", "descarga", "rebalse"]
      },
      {
        type: "mc",
        difficulty: "Comparacion",
        q: "Que conviene entender de molienda seca y humeda?",
        options: [
          "Sus condiciones de operacion, tipo de descarga y consecuencias sobre transporte/clasificacion.",
          "Solo el color del mineral tratado.",
          "Que una es teorica y la otra no existe industrialmente.",
          "Que se diferencian unicamente por el motor."
        ],
        answer: 0,
        explain: "No es un cuadro para repetir sin sentido: hay que conectar medio, descarga y operacion.",
        keywords: ["seca", "humeda", "descarga", "operacion"]
      },
      {
        type: "mc",
        difficulty: "Circuitos",
        q: "Que debe poder explicar alguien que entiende circuito abierto y cerrado en molienda?",
        options: [
          "Si el producto pasa una sola vez o si una fraccion retorna mediante clasificacion.",
          "Si el molino usa electricidad o vapor.",
          "Si el mineral es magnetico o no magnetico.",
          "Si el equipo se dibuja en 2D o 3D."
        ],
        answer: 0,
        explain: "La diferencia operativa es el retorno de material no suficientemente fino en circuito cerrado.",
        keywords: ["abierto", "cerrado", "retorno", "clasificacion"]
      },
      {
        type: "mc",
        difficulty: "Descarga",
        q: "Por que una molienda seca necesita una forma de descarga distinta a una por rebalse?",
        options: [
          "Porque para rebalsar debe haber un medio que exceda un nivel; en seco se requieren aberturas u otro sistema de salida.",
          "Porque en seco el molino no puede girar.",
          "Porque la molienda seca siempre es magnetica.",
          "Porque el material seco sale por flotacion."
        ],
        answer: 0,
        explain: "La idea es razonar el principio: rebalse implica nivel y fluido; en seco el mecanismo de salida debe ser otro.",
        keywords: ["seca", "rebalse", "nivel", "aberturas", "salida"]
      },
      {
        type: "mc",
        difficulty: "Elementos",
        q: "Que rol cumplen los elementos moledores en un molino?",
        options: [
          "Transmiten energia al material por impacto, compresion o abrasion al moverse dentro del cilindro.",
          "Funcionan como colectores de flotacion.",
          "Separan magneticos de no magneticos.",
          "Miden la humedad del mineral sin intervenir en la rotura."
        ],
        answer: 0,
        explain: "Bolas, barras u otros cuerpos moledores son los que realizan la reduccion de tamano al caer o desplazarse.",
        keywords: ["elementos moledores", "impacto", "abrasion", "compresion", "cilindro"]
      },
      {
        type: "mc",
        difficulty: "Formula",
        q: "Que error conceptual hay en usar una formula de molienda sin definir sus terminos?",
        options: [
          "Se puede llegar a un numero sin demostrar que se entiende la magnitud fisica ni sus unidades.",
          "Ninguno: en teoria solo importan los numeros.",
          "Solo afecta si el resultado da negativo.",
          "Hace que el molino pase a circuito abierto."
        ],
        answer: 0,
        explain: "El repaso enfatiza nombrar cada termino, incluso los basicos, especialmente en deducciones de velocidad critica.",
        keywords: ["terminos", "unidades", "magnitud", "formula", "velocidad critica"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Explica por que un molino no muele bien cuando los cuerpos moledores quedan pegados a la pared.",
        answerText: "La molienda necesita que los cuerpos moledores caigan o se desplacen relativo al material. Si la velocidad hace que queden centrifugados contra la pared, no hay impacto ni abrasion util y la reduccion de tamano cae.",
        keywords: ["cuerpos moledores", "caen", "centrifugados", "pared", "impacto", "abrasion"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Como responderias una comparacion breve entre molienda humeda y seca?",
        answerText: "Compararia el medio de operacion, la forma de descarga, el transporte del producto y la clasificacion posterior. En humeda hay pulpa y puede haber rebalse; en seca se requieren sistemas de descarga y manejo de polvo acordes.",
        keywords: ["humeda", "seca", "pulpa", "descarga", "transporte", "polvo"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Explica por que no alcanza con memorizar el dibujo de un molino si te piden funcionamiento.",
        answerText: "Porque el dibujo debe estar vinculado con la operacion: alimentacion, cuerpo cilíndrico, elementos moledores, tipo de descarga y movimiento. Si el esquema no explica como se produce la molienda y como sale el producto, queda incompleto.",
        keywords: ["alimentacion", "elementos moledores", "descarga", "movimiento", "funcionamiento"]
      }
    ]
  },
  {
    id: "transporte",
    title: "Transporte",
    accent: "#b2872f",
    summary: "Transporte interno/externo, equipos de solidos, liquidos y gases.",
    questions: [
      {
        type: "mc",
        difficulty: "Clasificacion",
        q: "Que diferencia general hay entre transporte externo e interno?",
        options: [
          "El externo vincula la planta con origen/destino fuera del establecimiento; el interno mueve materiales dentro del proceso o planta.",
          "El externo siempre es manual y el interno siempre es por avion.",
          "El externo mueve liquidos y el interno solo gases.",
          "No hay diferencia tecnica posible."
        ],
        answer: 0,
        explain: "Es un concepto teorico basico antes de entrar en equipos.",
        keywords: ["externo", "interno", "planta", "proceso"]
      },
      {
        type: "mc",
        difficulty: "Equipo",
        q: "Como describirias una pala mecanica en desarrollo corto?",
        options: [
          "Equipo sobre ruedas u orugas, con cabina, brazos moviles y cangilon para recoger material.",
          "Un molino con elementos moledores esfericos.",
          "Un filtro de placas con estacion de lavado.",
          "Una cuba con inyeccion de gas y colector."
        ],
        answer: 0,
        explain: "El repaso da esa forma de respuesta: descripcion sintetica, componentes y uso.",
        keywords: ["ruedas", "orugas", "cabina", "brazos", "cangilon"]
      },
      {
        type: "mc",
        difficulty: "Diferencias",
        q: "Que distingue una pala excavadora de una retroexcavadora segun el sentido de trabajo?",
        options: [
          "La excavadora trabaja en sentido ascendente; la retroexcavadora en sentido descendente.",
          "La excavadora transporta gases; la retroexcavadora transporta liquidos.",
          "La excavadora no tiene cabina; la retroexcavadora no tiene brazo.",
          "Solo cambia la marca comercial."
        ],
        answer: 0,
        explain: "Es una diferencia textual del repaso, util para respuestas teoricas breves.",
        keywords: ["ascendente", "descendente", "excavadora", "retroexcavadora"]
      },
      {
        type: "mc",
        difficulty: "Esquema",
        q: "Si dibujas un puente grua, que error te haria perder funcionalidad?",
        options: [
          "Olvidar componentes que permiten desplazar o levantar la carga.",
          "Dibujarlo sin sombras realistas.",
          "No ponerle color al gancho.",
          "No hacerlo en perspectiva 3D."
        ],
        answer: 0,
        explain: "La catedra puntua esquema y desarrollo por separado; el dibujo debe poder funcionar.",
        keywords: ["desplazar", "levantar", "carga", "componentes"]
      },
      {
        type: "mc",
        difficulty: "Gases",
        q: "Por que transporte de gases suele estudiarse con cuidado para parcial?",
        options: [
          "Porque puede aparecer como problema independiente y requiere reconocer ecuaciones, perdidas y equipos.",
          "Porque se evalua solo con una definicion historica.",
          "Porque reemplaza todos los temas de separacion.",
          "Porque nunca se combina con calculos."
        ],
        answer: 0,
        explain: "En el repaso se lo menciona como tema frecuente y habitualmente independiente.",
        keywords: ["gases", "problema", "perdidas", "equipos"]
      },
      {
        type: "mc",
        difficulty: "Equipos",
        q: "Que equipo se asocia naturalmente con movimiento de cargas en planta mediante traslacion y elevacion?",
        options: [
          "Puente grua.",
          "Celda de flotacion.",
          "Hidrociclon.",
          "Filtro Nucha."
        ],
        answer: 0,
        explain: "El puente grua debe mostrar traslacion del puente/carro y mecanismo de izaje para levantar la carga.",
        keywords: ["puente grua", "traslacion", "elevacion", "izaje", "carga"]
      },
      {
        type: "mc",
        difficulty: "Continuidad",
        q: "Que diferencia practica hay entre un equipo continuo y uno discontinuo de transporte?",
        options: [
          "El continuo mueve material sin ciclos individuales marcados; el discontinuo trabaja por cargas o maniobras separadas.",
          "El continuo solo sirve para liquidos y el discontinuo solo para gases.",
          "El continuo no consume energia.",
          "El discontinuo nunca se usa en plantas."
        ],
        answer: 0,
        explain: "Es una clasificacion util para ordenar cintas/elevadores frente a palas, autoelevadores o puente grua.",
        keywords: ["continuo", "discontinuo", "cargas", "ciclos", "transporte"]
      },
      {
        type: "mc",
        difficulty: "Descripcion",
        q: "Si te piden describir un autoelevador, que enfoque conviene?",
        options: [
          "Indicar que es un equipo movil para tomar, elevar y trasladar cargas mediante horquillas.",
          "Explicar velocidad critica y elementos moledores.",
          "Dibujar un tambor con zona imantada.",
          "Responder solo que es 'una maquina'."
        ],
        answer: 0,
        explain: "Para equipos de transporte interno conviene nombrar funcion, partes caracteristicas y tipo de operacion.",
        keywords: ["autoelevador", "movil", "elevar", "trasladar", "horquillas"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Explica que tendria que aparecer en un esquema minimo de puente grua.",
        answerText: "Deberia verse la estructura o vigas de apoyo, el puente que se desplaza, el carro o mecanismo de traslacion y el sistema de izaje con gancho o elemento para levantar la carga.",
        keywords: ["vigas", "puente", "carro", "traslacion", "izaje", "gancho"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Como distinguirias transporte de solidos, liquidos y gases al estudiar?",
        answerText: "Los distinguiria por el material transportado y por los equipos y variables dominantes: solidos con equipos mecanicos o cintas, liquidos con caudales y perdidas en conducciones, y gases con compresion, soplantes o ventiladores y perdidas de carga.",
        keywords: ["solidos", "liquidos", "gases", "equipos", "caudal", "perdidas"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Arma una respuesta corta para 'clasificacion de maquinas de transporte interno'.",
        answerText: "Se pueden clasificar segun el tipo de material, continuidad de operacion, trayectoria y equipo: por ejemplo equipos discontinuos como palas, autoelevadores o puente grua, y equipos continuos como cintas, elevadores o transportadores.",
        keywords: ["clasificar", "material", "continuo", "discontinuo", "cinta", "puente grua"]
      }
    ]
  },
  {
    id: "separaciones",
    title: "Separaciones",
    accent: "#5267a3",
    summary: "Zarandas, separacion magnetica, hidraulica, neumatica, sedimentacion y filtros.",
    questions: [
      {
        type: "mc",
        difficulty: "Zarandas",
        q: "Por que una zaranda electromagnetica se clasifica como separacion mecanica?",
        options: [
          "Porque el electroiman solo genera el movimiento vibratorio; la separacion ocurre por tamano mediante la zaranda.",
          "Porque separa magneticos de no magneticos por atraccion directa.",
          "Porque disuelve las particulas en agua.",
          "Porque no tiene partes moviles."
        ],
        answer: 0,
        explain: "El electroiman mueve la armadura; no es el principio de separacion del material.",
        keywords: ["electroiman", "movimiento", "vibracion", "tamano", "mecanica"]
      },
      {
        type: "mc",
        difficulty: "Magnetica",
        q: "Como funciona un separador magnetico de tambor?",
        options: [
          "El material magnetico queda adherido en la zona imantada y cae en otra salida cuando deja de estar bajo el iman; el no magnetico cae antes.",
          "Todos los materiales se adhieren por igual y luego se lavan.",
          "El tambor tritura por impacto hasta separar.",
          "El material fino rebalsa y el grueso sedimenta."
        ],
        answer: 0,
        explain: "La clave es distinguir trayectoria de magneticos y no magneticos.",
        keywords: ["magnetico", "tambor", "iman", "adherido", "no magnetico"]
      },
      {
        type: "mc",
        difficulty: "Hidraulica",
        q: "En una caja de sedimentacion simple, que particulas caen primero?",
        options: [
          "Las mas gruesas o pesadas, mientras las mas finas siguen mas tiempo con la corriente.",
          "Las mas finas siempre caen primero por capilaridad.",
          "Todas caen en el mismo punto sin clasificacion.",
          "Solo caen las particulas magneticas."
        ],
        answer: 0,
        explain: "El principio usado es la sedimentacion diferencial por tamano/densidad y arrastre del liquido.",
        keywords: ["gruesas", "pesadas", "finas", "corriente", "sedimentacion"]
      },
      {
        type: "mc",
        difficulty: "Conos",
        q: "Que mejora agrega un clasificador de cono doble frente al cono sencillo?",
        options: [
          "Permite regular mejor el caudal o distribucion mediante el cono distribuidor movil.",
          "Convierte la separacion hidraulica en magnetica.",
          "Elimina la corriente ascendente de agua.",
          "Solo cambia la pintura exterior."
        ],
        answer: 0,
        explain: "El cono distribuidor puede moverse para controlar el comportamiento de separacion.",
        keywords: ["cono doble", "distribuidor", "caudal", "regular"]
      },
      {
        type: "mc",
        difficulty: "Rastrillo",
        q: "En un clasificador de rastrillo, que hace el rastrillo?",
        options: [
          "Arrastra el material grueso sedimentado hacia su salida, mientras los finos salen por rebalse/suspension.",
          "Inyecta colector para volver hidrofobico el mineral.",
          "Imanta las particulas para pegarlas al tambor.",
          "Muele el material por velocidad critica."
        ],
        answer: 0,
        explain: "La entrada en suspension separa por sedimentacion: gruesos al fondo, finos por rebalse.",
        keywords: ["rastrillo", "grueso", "sedimentado", "fino", "rebalse"]
      },
      {
        type: "mc",
        difficulty: "Filtros",
        q: "Que tipo de contenido del cuadro de filtros puede pedirse?",
        options: [
          "Clasificacion, tipo de filtro, nombre y uso/aplicacion.",
          "Solo fechas historicas de invencion.",
          "Solo densidades de minerales.",
          "Solo dibujos 3D."
        ],
        answer: 0,
        explain: "El repaso remarca que ese cuadro se estudia por contenido, no por rangos numericos.",
        keywords: ["clasificacion", "tipo", "filtro", "uso", "aplicacion"]
      },
      {
        type: "mc",
        difficulty: "Filtros",
        q: "Que similitud ayuda a recordar el filtro rotatorio y el separador magnetico?",
        options: [
          "Ambos usan un cilindro/tambor giratorio, aunque el principio de separacion es distinto.",
          "Ambos separan por el mismo campo magnetico.",
          "Ambos son molinos de rebalse.",
          "Ambos funcionan sin movimiento."
        ],
        answer: 0,
        explain: "La asociacion visual sirve, pero no hay que mezclar principios: adherencia/filtracion versus magnetismo.",
        keywords: ["cilindro", "tambor", "giratorio", "principio distinto"]
      },
      {
        type: "mc",
        difficulty: "Zarandas",
        q: "Que determina la cantidad de fracciones que puede separar una zaranda con varios pisos?",
        options: [
          "La cantidad de superficies de tamizado y sus aberturas; en general mas pisos permiten mas cortes de tamano.",
          "La presencia de colector quimico.",
          "La velocidad critica del tambor.",
          "La ley metalica del concentrado final."
        ],
        answer: 0,
        explain: "Cada piso o superficie de cribado agrega una posibilidad de corte granulometrico.",
        keywords: ["zaranda", "pisos", "aberturas", "tamano", "fracciones"]
      },
      {
        type: "mc",
        difficulty: "Tromel",
        q: "Como separa un tromel o criba de tambor?",
        options: [
          "Por giro de un cilindro perforado, dejando pasar particulas segun tamano por sus aberturas.",
          "Por adherencia de burbujas a minerales hidrofobicos.",
          "Por compresion entre placas filtrantes.",
          "Por aceleracion centrifuga de cuerpos moledores."
        ],
        answer: 0,
        explain: "El tromel es una separacion mecanica por tamano mediante un tambor perforado que gira.",
        keywords: ["tromel", "tambor", "perforado", "giro", "tamano"]
      },
      {
        type: "mc",
        difficulty: "Hidrociclon",
        q: "Que principio general aprovecha un hidrociclon?",
        options: [
          "El giro de la suspension, donde las particulas mas gruesas pierden energia y tienden a salir por el fondo.",
          "La imantacion de la polea motora.",
          "La compactacion de tortas entre placas.",
          "La accion de un colector sobre burbujas."
        ],
        answer: 0,
        explain: "La clase lo explica por movimiento giratorio y separacion de gruesos y finos por trayectorias distintas.",
        keywords: ["hidrociclon", "giro", "gruesas", "fondo", "suspension"]
      },
      {
        type: "mc",
        difficulty: "Neumatica",
        q: "En un separador neumatico de polvos, que funcion cumplen los flejes o deflectores?",
        options: [
          "Direccionan la corriente y favorecen trayectorias distintas para polvo fino y grueso.",
          "Generan una zona imantada permanente.",
          "Actuan como elementos moledores.",
          "Cierran las placas de un filtro prensa."
        ],
        answer: 0,
        explain: "Los flejes ayudan a guiar la suspension gaseosa y separar fracciones por comportamiento aerodinamico.",
        keywords: ["neumatico", "polvos", "flejes", "deflectores", "corriente"]
      },
      {
        type: "mc",
        difficulty: "Sedimentacion",
        q: "Que diferencia conceptual hay entre sedimentar por gravedad y prensar entre placas?",
        options: [
          "En sedimentacion se espera la caida de particulas; en prensado se fuerza la separacion compactando solidos y evacuando liquido.",
          "Son exactamente el mismo proceso y se dibujan igual.",
          "La sedimentacion usa imanes y el prensado usa burbujas.",
          "El prensado solo sirve para gases."
        ],
        answer: 0,
        explain: "El repaso contrasta procesos lentos por sedimentacion con filtros de placas donde se compacta.",
        keywords: ["sedimentacion", "gravedad", "prensado", "placas", "compactar"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Explica el clasificador de cono sencillo en pocas lineas.",
        answerText: "Entra una suspension y se agrega una corriente ascendente de agua. Las particulas gruesas o mas densas vencen el arrastre y salen por el fondo, mientras las finas se mantienen suspendidas y salen por rebalse.",
        keywords: ["suspension", "corriente ascendente", "gruesas", "fondo", "finas", "rebalse"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Como evitarias confundir separador magnetico con filtro rotatorio?",
        answerText: "Los asociaria por la forma de tambor giratorio, pero separaria el principio: el magnetico retiene particulas magneticas por un campo imanado; el filtro rotatorio forma una capa o torta sobre el cilindro y la retira por lavado, compactacion o raspado.",
        keywords: ["tambor", "magnetico", "campo", "filtro rotatorio", "torta", "raspado"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Explica un filtro prensa usando una analogia simple.",
        answerText: "Puede compararse con una cafetera de embolo, pero con varias placas o marcos. La suspension queda entre placas, al cerrarse se compactan los solidos y el liquido atraviesa o se evacua, quedando una torta que luego se retira o lava.",
        keywords: ["placas", "marcos", "suspension", "compacta", "liquido", "torta"]
      }
    ]
  },
  {
    id: "flotacion",
    title: "Flotacion",
    accent: "#8b5fbf",
    summary: "Colectores, burbujas, balances, recuperacion y dimensionamiento de celdas.",
    questions: [
      {
        type: "mc",
        difficulty: "Principio",
        q: "Que rol cumple el colector en flotacion?",
        options: [
          "Se adhiere selectivamente al mineral para volverlo afin a la burbuja y permitir que suba con ella.",
          "Aumenta la velocidad critica del molino.",
          "Transforma el mineral en material magnetico.",
          "Hace sedimentar todos los finos."
        ],
        answer: 0,
        explain: "La transcripcion explica que el colector se pega al mineral; luego la burbuja lo arrastra por empuje.",
        keywords: ["colector", "mineral", "burbuja", "hidrofobico", "empuje"]
      },
      {
        type: "mc",
        difficulty: "Circuito",
        q: "En el circuito desbastadora-recuperadora de flotacion, que representan B y E?",
        options: [
          "B es concentrado final; E son colas finales.",
          "B es agua de lavado; E es colector.",
          "B es alimentacion; E es retorno a desbastadora.",
          "B es ganga pura; E es mineral comprado."
        ],
        answer: 0,
        explain: "A alimenta, B es concentrado, C colas del desbaste, D concentrado de recuperadora que retorna y E colas finales.",
        keywords: ["B", "concentrado", "E", "colas finales"]
      },
      {
        type: "mc",
        difficulty: "Balances",
        q: "Por que se plantean balances de masa en flotacion?",
        options: [
          "Para calcular caudales desconocidos de cada corriente usando concentraciones y regimen permanente.",
          "Para estimar el color del concentrado.",
          "Para reemplazar el dibujo del circuito.",
          "Para evitar definir entradas y salidas."
        ],
        answer: 0,
        explain: "Se usan balances globales y por equipo, para mena/mineral/ganga, hasta despejar flujos.",
        keywords: ["balance", "masa", "caudal", "concentracion", "regimen permanente"]
      },
      {
        type: "mc",
        difficulty: "Rendimiento",
        q: "Como se interpreta una recuperacion de flotacion cercana a 96%?",
        options: [
          "Es alta y razonable; sirve como chequeo de que no se perdio demasiado mineral valioso.",
          "Es imposible porque toda recuperacion debe ser menor a 50%.",
          "Indica que las celdas no tienen agua.",
          "Solo mide la potencia instalada."
        ],
        answer: 0,
        explain: "La clase menciona rendimientos altos, tipicamente entre 90 y 100%, como control de cuentas.",
        keywords: ["recuperacion", "rendimiento", "90", "100", "chequeo"]
      },
      {
        type: "mc",
        difficulty: "Dimensionamiento",
        q: "Al dimensionar celdas de flotacion, por que importa el tiempo de contacto?",
        options: [
          "Porque el volumen requerido es caudal volumetrico por tiempo de residencia/contacto.",
          "Porque define la ley del mineral de mina.",
          "Porque reemplaza la densidad del solido.",
          "Porque elimina la necesidad de balances."
        ],
        answer: 0,
        explain: "Una vez conocido el caudal de pulpa, el tiempo de contacto define volumen total necesario.",
        keywords: ["tiempo", "contacto", "caudal", "volumen", "residencia"]
      },
      {
        type: "mc",
        difficulty: "Seleccion",
        q: "Si hay que elegir modelo de celda, que criterio aparece en la clase?",
        options: [
          "Limitar cantidad operativa de celdas y elegir menor potencia por capacidad entre modelos viables.",
          "Comprar siempre la celda mas chica posible.",
          "Elegir por color o marca.",
          "Usar modelos distintos para cada etapa aunque encarezcan sin razon."
        ],
        answer: 0,
        explain: "Se menciona evitar cantidades absurdas y comparar potencia/capacidad; tambien se busca usar celdas iguales si corresponde.",
        keywords: ["cantidad", "potencia", "capacidad", "modelo", "viable"]
      },
      {
        type: "mc",
        difficulty: "Reactivos",
        q: "Por que la flotacion no es una separacion puramente mecanica?",
        options: [
          "Porque intervienen fenomenos quimicos/electroquimicos y reactivos que modifican afinidades superficiales.",
          "Porque no existe movimiento de fluidos.",
          "Porque solo separa por tamano de particula.",
          "Porque siempre usa un tambor imantado."
        ],
        answer: 0,
        explain: "La flotacion se apoya en la afinidad mineral-burbuja y en reactivos como colectores, no solo en tamiz o gravedad.",
        keywords: ["quimica", "electroquimica", "reactivos", "superficie", "colector"]
      },
      {
        type: "mc",
        difficulty: "Balances",
        q: "En un balance global de la planta de flotacion, que corrientes externas se comparan?",
        options: [
          "La alimentacion A con las salidas finales B y E.",
          "Solo C con D, porque las otras no importan.",
          "El agua de lavado con el motor.",
          "El colector con la potencia instalada."
        ],
        answer: 0,
        explain: "Mirando el sistema completo, A entra y B/E salen; C y D son corrientes internas o intermedias.",
        keywords: ["balance global", "A", "B", "E", "corrientes externas"]
      },
      {
        type: "mc",
        difficulty: "Pulpa",
        q: "Cuando se calcula volumen para dimensionar celdas, que precaucion aparece con la relacion liquido/solido?",
        options: [
          "Ver si la relacion esta dada en peso y no confundir masa con volumen al sumar solidos y agua.",
          "Usarla siempre como porcentaje de recuperacion.",
          "Aplicarla solo al concentrado B.",
          "Ignorarla porque el agua no ocupa volumen."
        ],
        answer: 0,
        explain: "En la clase se remarca que la relacion L/S esta en peso; luego se convierte a volumen segun densidades.",
        keywords: ["liquido", "solido", "peso", "masa", "volumen", "densidad"]
      },
      {
        type: "mc",
        difficulty: "Recuperadora",
        q: "Por que una recuperadora suele operar con mas tiempo de contacto o mayor dilucion?",
        options: [
          "Porque busca rescatar mineral remanente de las colas, aumentando la probabilidad de encuentro mineral-colector-burbuja.",
          "Porque procesa el concentrado final B para venderlo.",
          "Porque reemplaza a la etapa de trituracion.",
          "Porque no usa agua ni gas."
        ],
        answer: 0,
        explain: "La recuperadora trata colas del desbaste y necesita favorecer el contacto para recuperar lo que queda.",
        keywords: ["recuperadora", "colas", "tiempo", "dilucion", "burbuja"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Como verificarias si un resultado de recuperacion de flotacion tiene sentido?",
        answerText: "Compararia el mineral valioso recuperado en el concentrado contra el mineral valioso alimentado. Si da un valor razonable, por ejemplo alto pero menor o igual a 100%, sirve como control; si da muy bajo o mayor a 100%, revisaria balances y concentraciones.",
        keywords: ["recuperacion", "concentrado", "alimentado", "100", "balance", "control"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Explica por que D vuelve a la desbastadora en el circuito de flotacion visto en clase.",
        answerText: "D es el concentrado de la recuperadora, de calidad intermedia. Como no alcanza la calidad final del concentrado B, se recicla a la desbastadora para reprocesarlo y mejorar la separacion.",
        keywords: ["D", "concentrado", "recuperadora", "intermedia", "recicla", "desbastadora"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Explica en palabras el recorrido A-B-C-D-E de una flotacion con desbaste y recuperacion.",
        answerText: "A alimenta la desbastadora. De ella sale B como concentrado final y C como colas del desbaste. C entra a la recuperadora; de alli D es un concentrado intermedio que retorna a la desbastadora y E son colas finales.",
        keywords: ["A", "desbastadora", "B", "concentrado", "C", "recuperadora", "D", "retorna", "E", "colas"]
      }
    ]
  },
  {
    id: "proyecto-minero",
    title: "Proyecto minero y minerales",
    accent: "#6f7f3b",
    summary: "Conceptos de proyecto, minerales, impactos y criterios de estudio.",
    questions: [
      {
        type: "mc",
        difficulty: "Estudio",
        q: "Segun el repaso, que tipo de contenido no conviene priorizar para evaluacion teorica?",
        options: [
          "Aspectos historicos y cuadros de participacion/produccion.",
          "Procesos, formulas indicadas, impactos y esquemas funcionales.",
          "Funcionamiento de equipos.",
          "Diferencias entre metodos de separacion."
        ],
        answer: 0,
        explain: "El repaso dice explicitamente que historia y cuadros de participacion/produccion no van, mientras procesos si.",
        keywords: ["historicos", "produccion", "participacion", "no va"]
      },
      {
        type: "mc",
        difficulty: "Esquemas",
        q: "Que tipo de esquema suele esperarse cuando piden dibujar equipos?",
        options: [
          "Esquema 2D simple, funcional, con componentes y explicacion coherente.",
          "Render 3D detallado.",
          "Una imagen decorativa sin componentes.",
          "Solo una lista de marcas industriales."
        ],
        answer: 0,
        explain: "Se repite mucho: no 3D, si 2D funcional. Si piden desarrollo y esquema, ambos suman por separado.",
        keywords: ["2D", "funcional", "componentes", "explicacion"]
      },
      {
        type: "mc",
        difficulty: "Minerales",
        q: "Cuando el docente dice 'sepan formulas', a que apunta en el apunte de minerales?",
        options: [
          "A formulas quimicas relevantes de minerales indicadas en el material.",
          "A formulas de marketing minero.",
          "A todas las constantes fisicas universales.",
          "A ecuaciones de programacion."
        ],
        answer: 0,
        explain: "El repaso aclara que en ese contexto se refiere a formulas quimicas de minerales.",
        keywords: ["formula", "quimica", "minerales"]
      },
      {
        type: "mc",
        difficulty: "Impacto",
        q: "Que lugar tienen los impactos ambientales dentro del estudio teorico?",
        options: [
          "Pueden entrar aunque exista una clase especifica de impacto ambiental.",
          "Nunca se preguntan si aparecen en el apunte.",
          "Solo se evalua su historia.",
          "Reemplazan todos los procesos metalurgicos."
        ],
        answer: 0,
        explain: "El repaso remarca que los impactos que correspondan al apunte van.",
        keywords: ["impacto", "ambiental", "apunte"]
      },
      {
        type: "mc",
        difficulty: "Criterio",
        q: "Que frase resume mejor el criterio de estudio que aparece en el repaso?",
        options: [
          "Entender procesos, esquemas funcionales, formulas marcadas e impactos; no quedarse en copiar slides.",
          "Memorizar solo titulos y saltear los equipos.",
          "Estudiar unicamente cuadros historicos.",
          "Preparar solo ejercicios numericos sin teoria."
        ],
        answer: 0,
        explain: "El docente aclara que gran parte de la teoria sale de lo explicado en clase, no solo de la diapositiva visible.",
        keywords: ["procesos", "esquemas", "formulas", "impactos", "clase"]
      },
      {
        type: "mc",
        difficulty: "Coloquio",
        q: "Que aclaracion del repaso conviene recordar sobre evaluacion y coloquio?",
        options: [
          "Muchos criterios de lo que va o no va tambien orientan el coloquio, aunque algunos temas se reserven mas para esa instancia.",
          "El coloquio no incluye ningun tema teorico.",
          "El coloquio solo pregunta historia de la mineria.",
          "Lo que no se vio en clase nunca puede aparecer."
        ],
        answer: 0,
        explain: "Varias aclaraciones del repaso se presentan como criterio para evaluacion y tambien para coloquio.",
        keywords: ["coloquio", "evaluacion", "criterio", "teoria"]
      },
      {
        type: "mc",
        difficulty: "Desarrollo",
        q: "Si el enunciado dice 'desarrollar', que tipo de respuesta se espera?",
        options: [
          "Una explicacion escrita ordenada, con conceptos, etapas y relaciones causales, no solo un cuadro.",
          "Unicamente un dibujo sin texto.",
          "Solo elegir verdadero o falso.",
          "Copiar una formula aislada sin definir nada."
        ],
        answer: 0,
        explain: "El repaso distingue cuando piden desarrollo de cuando piden cuadro, diagrama o esquema.",
        keywords: ["desarrollar", "explicacion", "etapas", "conceptos", "causal"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Como responderias si te piden 'indique en un cuadro' un proceso o clasificacion?",
        answerText: "Organizaria filas y columnas con criterio claro: etapa o tipo, principio, equipo o componente, entrada, salida y uso. Evitaria escribir un parrafo largo si el enunciado pide cuadro.",
        keywords: ["cuadro", "filas", "columnas", "etapa", "principio", "entrada", "salida"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Que significa estudiar 'desde los contenidos de clase' y no solo desde el slide?",
        answerText: "Significa recuperar la explicacion oral: que se dijo que iba, que se excluyo, como funciona cada equipo, que comparaciones hizo el docente y que errores remarco. El slide es guia, pero la respuesta sale del concepto explicado.",
        keywords: ["clase", "explicacion", "funciona", "comparaciones", "errores", "concepto"]
      },
      {
        type: "open",
        difficulty: "Oral",
        q: "Como encararias una pregunta de desarrollo sobre un proceso de obtencion?",
        answerText: "Primero nombraria el objetivo y la materia prima, luego ordenaria las etapas principales con entradas y salidas, agregaria reacciones o formulas si fueron marcadas como importantes y cerraria con productos, subproductos e impactos relevantes.",
        keywords: ["objetivo", "materia prima", "etapas", "entradas", "salidas", "formulas", "impactos"]
      }
    ]
  }
];
