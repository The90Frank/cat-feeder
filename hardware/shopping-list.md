# Lista della spesa

Cosa comprare per costruire il dispenser, raggruppato per tipo di negozio. Quantità e specifiche da [`bom.md`](bom.md).
Prezzi **indicativi** (ordine di grandezza, ottobre 2026), da verificare al momento dell'acquisto.

Già disponibile: **ESP32-D devkit**.

## Elettronica (negozio online di componenti)

| ☐ | Q.tà | Articolo | Cosa controllare | ~€ |
|---|---|---|---|---|
| ☐ | 1 | **Lettore FDX-B 134.2 kHz con bobina**, uscita TTL (es. WL-134) | ISO 11784/11785 · **include l'antenna** · tensione di alimentazione (5V?) · livello del TX (3.3V o 5V) | 8–15 |
| ☐ | 1 | **Tag di prova FDX-B 134.2 kHz** (capsula in vetro o tessera) | per i test al banco senza il gatto | 2–5 |
| ☐ | 1 | **Driver TMC2209** (modulo StepStick, es. BTT v1.3) | pin **PDN_UART** e **DIAG** accessibili · Rsense 0.11 Ω (il più comune) | 4–8 |
| ☐ | 1 | **Motore NEMA 17**, 42 × 42 × 40 mm (es. 17HS4401) | albero **Ø 5 mm con piano (D)** · ~1,5 A · ~0,4 Nm · cavo incluso | 8–12 |
| ☐ | 1 | **Sensore ToF VL53L0X** (GY-VL53L0XV2) | dimensioni schedina ≈ 26 × 12 mm (sede nel coperchio) | 3–6 |
| ☐ | 1 | **Modulo RTC DS3231** (es. ZS-042) | ⚠️ vedi nota sotto sulla batteria | 2–4 |
| ☐ | 1 | Batteria **CR2032** (o LIR2032, vedi nota) | | 1–2 |
| ☐ | 1 | **Alimentatore 12V 2A**, spina 5,5 × 2,1 mm | | 8–12 |
| ☐ | 1 | **Jack DC da pannello** 5,5 × 2,1 mm | foro di montaggio **Ø 8 mm** | 1 |
| ☐ | 1 | **Step-down 12V → 5V** (MP1584EN o LM2596) | se regolabile: tarare a 5,0 V prima di collegare l'ESP32 | 1–3 |
| ☐ | 1 | Condensatore elettrolitico **100 µF 35V** | | <1 |
| ☐ | 1 | Resistenza **1 kΩ** | | <1 |
| ☐ | 1 | Millefori 5 × 7 cm + strip di pin femmina/maschio | per montare ESP32, driver e moduli | 2–4 |
| ☐ | 1 | Cavetti Dupont F-F / M-F + connettori JST-XH | | 3–5 |

**Subtotale elettronica: ~45–80 €**

## Ferramenta / bricolage

| ☐ | Q.tà | Articolo | Note | ~€ |
|---|---|---|---|---|
| ☐ | 1 | **Barra piatta in acciaio 40 × 5 mm, 1 m** | da tagliare in **4 pezzi da 140 mm** (zavorra) · sbavare i tagli | 6–10 |
| ☐ | 1 | **Kit viti M3** (8, 12 mm) + dadi + rondelle | serve: 4 × M3×12 + dadi, 4 × M3×8 | 5–8 |
| ☐ | 8 | Rondelle M3 **larghe** (Ø esterno ~9 mm) | fermi della zavorra | — |
| ☐ | 10 | Viti **autofilettanti M3 × 8** (per plastica) | zavorra (8) + sportello (2) | 2 |
| ☐ | 2 | **Grani M3 × 6** (punta piana) | beccuccio + mozzo coclea | 1 |
| ☐ | 2 + 2 | **Bulloni M4 × 20** e **M4 × 16** + 4 dadi + 4 rondelle | giunzione basi, schienale | 2 |
| ☐ | 4 | Viti **Ø 4 mm**, testa **≤ 8,5 mm** + tasselli | fissaggio a muro (opzionale) | 2 |

**Subtotale ferramenta: ~18–25 €**

## Stampa 3D

| ☐ | Q.tà | Articolo | Note | ~€ |
|---|---|---|---|---|
| ☐ | 1 | **PETG**, bobina 1 kg | tutti i pezzi stanno in una bobina · per ciotola e percorso del cibo meglio un PETG dichiarato per alimenti | 20–30 |

## Note prima di comprare

- ⚠️ **DS3231 ZS-042 e batteria**: il modulo ha un circuito di ricarica pensato per la **LIR2032** (ricaricabile). Con una **CR2032** (non ricaricabile) va **dissaldato il diodo o la resistenza** di ricarica, altrimenti la batteria può gonfiarsi. In alternativa: usare una LIR2032
- ⚠️ **WL-134 alimentato a 5V**: se il TX esce a 5V serve un partitore (es. 10 kΩ + 20 kΩ) verso GPIO16, l'ESP32 regge solo 3.3V
- **TMC2209**: alcuni moduli richiedono un ponticello di saldatura per abilitare l'UART su PDN; verificare la scheda tecnica del modulo scelto
- Il **tag di prova** permette di collaudare lettore, logica ed erogazione senza coinvolgere il gatto

## Totale indicativo

**~85–135 €**, esclusi ESP32 (già disponibile) e stampante.
