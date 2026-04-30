# Primerjava: baseline LLM proti RAG odgovoru

Ta dokument prikazuje kvalitativno primerjavo dveh načinov odgovarjanja na ista uporabniška vprašanja.

Uporabljen je isti lokalni jezikovni model: `llama3.1:8b` prek Ollame.

Razlika ni v modelu, ampak v promptu.

## Kaj je baseline

Baseline pomeni, da vprašanje pošljemo direktno v LLM brez podatkov iz našega dataseta.

Poenostavljeno:

```text
uporabnikovo vprašanje -> Ollama -> odgovor
```

Prompt za baseline je bil:

```text
You are a helpful fitness assistant.

Answer the user's fitness question directly.
If you are uncertain, say so clearly.

Question:
{question}

Answer:
```

To pomeni, da model odgovarja iz svojega splošnega znanja. Ne ve, katere vaje so v našem MegaGym datasetu.

## Kaj je RAG

RAG pomeni Retrieval-Augmented Generation.

Pri RAG odgovoru najprej poiščemo relevantne vaje v Qdrantu, potem pa jih dodamo v prompt za isti LLM.

Poenostavljeno:

```text
uporabnikovo vprašanje -> embedding -> Qdrant -> relevantne vaje -> Ollama -> odgovor
```

Prompt za RAG vsebuje dodatni del:

```text
Retrieved exercise entries:
{context}

Question:
{question}

Answer:
```

Celoten RAG prompt modelu tudi naroči:

- naj uporablja samo pridobljene exercise entryje
- naj preferira ujemanje po mišični skupini, opremi in težavnosti
- naj odstrani duplikate
- naj ne izmišljuje vaj, ki niso podprte s kontekstom

## Kaj smo primerjali

Za istih 5 vprašanj smo generirali:

1. baseline odgovor brez retrieval konteksta
2. RAG odgovor z retrieved kontekstom iz Qdranta

Primerjava je kvalitativna. Namen za trenutno fazo ni še polna avtomatska ocena odgovorov, ampak prikaz, kako RAG spremeni tip odgovora.

## Povzetek opažanj

| Vidik | Baseline | RAG |
| --- | --- | --- |
| Vir informacij | Splošno znanje modela | MegaGym dataset + LLM |
| Konkretna imena vaj | Včasih splošna ali parafrazirana | Pogosteje točna imena iz dataseta |
| Grounding | Ni vezan na naš dataset | Vezan na retrieved context |
| Tveganje halucinacij | Višje | Nižje, če je retrieval dober |
| Slabost | Lahko poda dobro splošno priporočilo, ki ni v datasetu | Če retrieval vrne slabe zadetke, je slabši tudi odgovor |

## Primer 1: vaje za prsa z ročkami

**Vprašanje**

```text
What chest exercises can I do with dumbbells?
```

### Baseline odgovor

Baseline poda splošno uporaben odgovor:

- Dumbbell Bench Press
- Dumbbell Flyes
- Dumbbell Dips
- Dumbbell Chest Press

Odgovor je razumljiv, vendar ni vezan na naš dataset. Model doda tudi vajo `Dumbbell Dips`, ki ni nujno podprta z retrieved podatki v našem sistemu.

### RAG odgovor

RAG odgovor uporabi retrieved vaje iz MegaGym dataseta:

- Dumbbell Chest Fly
- Dumbbell Bench Press-
- Dumbbell Flyes
- Incline Dumbbell Flyes

Pri vsaki vaji navede:

- zakaj se ujema z vprašanjem
- kratko razlago
- težavnost, če je na voljo

### Interpretacija

To je dober primer, kjer RAG deluje bolje za naš namen. Odgovor je bolj vezan na dataset in uporablja dejanska imena vaj, ki jih je naš sistem našel v Qdrantu.

## Primer 2: triceps vaje na kablu

**Vprašanje**

```text
Which triceps exercises use a cable machine?
```

### Baseline odgovor

Baseline poda kratek splošen odgovor:

- Cable Tricep Pushdowns
- Cable Overhead Tricep Extensions

Odgovor je pravilen v splošnem fitness smislu, ampak ni zelo bogat.

### RAG odgovor

RAG vrne več konkretnih vaj iz dataseta:

- Cable Overhead Triceps Extension - Gethin Variation
- Lying cable triceps extension
- Triceps Overhead Extension with Rope - Gethin Variation
- Cable Triceps Extension - Gethin Variation
- 30 Arms Underhand Cable Straight-Bar Push-Down

### Interpretacija

RAG je tukaj boljši, ker poda več konkretnih vaj in jih poveže z opremo `Cable` ter mišično skupino `Triceps`. To dobro pokaže vrednost retrievala.

## Primer 3: začetniške bodyweight vaje za noge

**Vprašanje**

```text
Give me beginner leg exercises using bodyweight.
```

### Baseline odgovor

Baseline poda zelo uporaben splošen odgovor:

- Squats
- Lunges
- Glute Bridges
- Calf Raises
- Wall Sits

Za uporabnika je to dober odgovor.

### RAG odgovor

RAG odgovor je manj prepričljiv, ker retrieval ni vrnil idealnih zadetkov. Vrnjen kontekst vsebuje tudi vaje, ki niso dobro ujemanje z vprašanjem, na primer abdominalno vajo ali vajo z napravo.

RAG zato predlaga predvsem:

- Alternating Leg Swing
- Alternate Leg Diagonal Bound

### Interpretacija

To je pomemben negativen primer. Pokaže, da RAG ni avtomatsko boljši. Če retrieval najde slab kontekst, bo tudi generiran odgovor slabši ali manj uporaben.

Za predstavitev je ta primer koristen, ker pokaže realno omejitev trenutnega prototipa:

- dataset ima nekatere prazne ali nekonsistentne vrednosti pri `Equipment`
- vprašanje je precej široko
- trenutni retrieval uporablja samo semantično podobnost, brez dodatnega filtriranja po metapodatkih

## Primer 4: vaje za hrbet na pull-up baru

**Vprašanje**

```text
Which back exercises can I do with a pull-up bar?
```

### Baseline odgovor

Baseline navede splošne vaje:

- Pull-ups
- Lat Pulldowns
- Chin-ups

Tu je odgovor delno problematičen, ker `Lat Pulldowns` običajno niso vaja na pull-up baru, ampak na napravi ali kablu.

### RAG odgovor

RAG se bolj opira na retrieved kontekst in vrne:

- Around-the-world pull-up
- Upside-down pull-up
- Pull-up kot splošno oziroma implicitno vajo

### Interpretacija

RAG je bolj vezan na najdene podatke, baseline pa vključi tudi širše fitnes znanje. To pokaže razliko med "splošno uporabnim" in "dataset-grounded" odgovorom.

## Primer 5: biceps z drogom

**Vprašanje**

```text
Show me barbell exercises for biceps.
```

### Baseline odgovor

Baseline poda pričakovane splošne vaje, kot so barbell curls in reverse curls.

### RAG odgovor

RAG uporabi konkretne retrieved zadetke iz dataseta, na primer:

- Preacher Curl
- Paul Carter Barbell Curl
- Barbell curl-
- Barbell Curl

### Interpretacija

Ta primer je soliden za RAG, čeprav se vidi tudi težava z duplikati oziroma podobnimi zapisi v datasetu. To je dober argument za naslednji korak: čiščenje oziroma deduplikacija podatkov.

## Zaključek

Za trenutno fazo projekta ta primerjava pokaže osnovno vrednost RAG pristopa:

- baseline zna dati dobre splošne fitness odgovore
- RAG zna odgovore vezati na naš dataset
- RAG je najboljši, ko retrieval vrne kakovosten kontekst
- RAG lahko odpove, če retrieval vrne napačne ali šibke zadetke

Glavni naslednji korak ni nujno bolj kompleksen LLM, ampak boljši retrieval:

- filtriranje po metapodatkih, na primer `BodyPart`, `Equipment`, `Level`
- čiščenje praznih ali nekonsistentnih vrednosti v datasetu
- odstranjevanje duplikatov oziroma near-duplicate vaj
- večji eval set z ročno ocenjenimi primeri
