# Evalvacija retrieval komponente

Ta evalvacija preverja samo prvi del RAG sistema: ali sistem iz Qdranta najde relevantne vaje za uporabnikovo vprašanje.

Pomembno: pri tej evalvaciji se Ollama oziroma LLM sploh ne uporablja. Tukaj merimo samo iskanje po vektorski bazi.

## Kaj smo primerjali

Za vsako testno vprašanje smo ročno določili pričakovane lastnosti relevantnih vaj:

- ciljno mišično skupino oziroma `BodyPart`
- opremo oziroma `Equipment`
- po potrebi težavnost oziroma `Level`
- nekaj ključnih besed, ki se pričakujejo v imenu ali opisu vaje

Primer:

```json
{
  "question": "What chest exercises can I do with dumbbells?",
  "expected_body_part": ["Chest"],
  "expected_equipment": ["Dumbbell"],
  "expected_keywords": ["press", "fly"]
}
```

Nato sistem za vsako vprašanje naredi naslednje:

1. vprašanje pretvori v embedding z modelom `sentence-transformers/all-MiniLM-L6-v2`
2. pošlje embedding v Qdrant
3. Qdrant vrne top 5 najbolj podobnih vaj
4. skripta preveri, koliko vrnjenih vaj ustreza ročno določenim pričakovanim kriterijem

## Metrike

| Metrika | Pomen |
| --- | --- |
| `Hit@1` | Ali je prvi vrnjeni rezultat relevanten? |
| `Hit@3` | Ali je vsaj eden izmed prvih treh rezultatov relevanten? |
| `Hit@5` | Ali je vsaj eden izmed prvih petih rezultatov relevanten? |
| `Precision@5` | Kolikšen delež prvih petih rezultatov je relevanten? |
| `MRR` | Mean Reciprocal Rank; višje pomeni, da se prvi relevanten rezultat pojavi bolj pri vrhu. |

## Rezultati

| Metrika | Vrednost |
| --- | ---: |
| Število vprašanj | 12 |
| `Hit@1` | 0.500 |
| `Hit@3` | 0.917 |
| `Hit@5` | 0.917 |
| `Precision@5` | 0.583 |
| `MRR` | 0.694 |

## Interpretacija

Rezultati kažejo, da retrieval komponenta v večini primerov najde vsaj eno relevantno vajo med prvimi petimi rezultati. `Hit@5 = 0.917` pomeni, da je bil pri 11 od 12 vprašanj vsaj en relevanten zadetek v top 5 rezultatih.

`Hit@1 = 0.500` je nižji, kar pomeni, da prvi rezultat ni vedno najboljši. To je pričakovano pri začetnem prototipu, ker uporabljamo generični embedding model in dataset ima nekaj nepopolnih ali nekonsistentnih polj.

`Precision@5 = 0.583` pomeni, da je bilo v povprečju približno 58 % prvih petih rezultatov relevantnih glede na naše ročne kriterije.

## Podrobnosti po vprašanjih

| ID | `Hit@5` | `Precision@5` | Top 5 vrnjenih vaj |
| --- | ---: | ---: | --- |
| `chest_dumbbell` | 1 | 1.00 | Dumbbell chest fly; Dumbbell bench press-; Dumbbell Flyes; Dumbbell Chest Press - Gethin Variation; Incline Dumbbell Flyes |
| `triceps_cable` | 1 | 0.80 | Cable Overhead Triceps Extension - Gethin Variation; Lying cable triceps extension; Triceps Overhead Extension with Rope - Gethin Variation; Cable Triceps Extension - Gethin Variation; 30 Arms Underhand Cable Straight-Bar Push-Down |
| `beginner_bodyweight_legs` | 0 | 0.00 | Alternate Leg Diagonal Bound; 30 Flat Bench Leg Raise; Alternating Leg Swing; Single Leg Push-off; Single-leg leg extension- |
| `pullup_bar_back` | 1 | 0.40 | Upside-down pull-up; UP Squat; Around-the-world pull-up; Barbell press sit-up; 30 Back Straight-Arm Bar Pull-Down |
| `biceps_barbell` | 1 | 0.80 | Preacher Curl; Paul Carter Barbell Curl; Barbell curl-; Barbell Curl; Biceps curl to shoulder press |
| `abs_ball` | 1 | 0.40 | Exercise Ball Cable Crunch - Gethin Variation; Exercise Ball Cable Crunch - Gethin Variation; Exercise ball crunch; AM Ball Crunch; Exercise ball torso rotation |
| `shoulders_dumbbell` | 1 | 1.00 | Dumbbell front raise to lateral raise; Alternating dumbbell front raise; Dumbbell shoulder press with body rotation; Dumbbell external shoulder rotation; Dumbbell lateral raise |
| `hamstrings_machine` | 1 | 0.60 | Lying Hamstring Curls - Gethin Variation; UP Hamstring Curl; Total Fitness Hamstring Slide; Hamstring slide; Seated Hamstring Curl - Gethin Variation |
| `calves_beginner` | 1 | 0.60 | Standing Dumbbell Calf Raise; Calf Stretch Elbows Against Wall; Single-leg standing dumbbell calf raise; Calf Press; Calf Raises - With Bands |
| `lower_back_bodyweight` | 1 | 0.60 | Lower Back Stretch - Yates Variation; Back Extension - Gethin Variation; Back extension; Weighted back extension; Lying cross-over lower back stretch |
| `chest_bands` | 1 | 0.60 | Cross Over - With Bands; Band chest fly; HM Banded Cross-Over Pull; Band push-up; Taylor Band-Assisted One-Arm Push-Up |
| `quadriceps_barbell` | 1 | 0.20 | Barbell step-up; Close-stance dumbbell front squat; Barbell squat with plate slide; Standing quad stretch; Jumping jack- |

## Kaj lahko povemo pri predstavitvi

Ta evalvacija je namenoma lahka in primerna za trenutno fazo projekta. Ne trdimo, da gre za končno znanstveno evalvacijo. Pokaže pa, da retrieval del prototipa že deluje dovolj dobro, da v večini primerov vrne relevantne vaje, hkrati pa razkrije nekaj omejitev.

Najbolj očitna omejitev je primer `beginner_bodyweight_legs`, kjer rezultati niso dovolj dobri. Razlog je verjetno kombinacija splošnega vprašanja, nepopolnih opisov v datasetu in praznih oziroma nekonsistentnih vrednosti pri polju `Equipment`.
