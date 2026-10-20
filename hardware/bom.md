# Distinta componenti

Stato: **bozza**, quantità ricavate dal modello in [`cad/build.py`](../cad/build.py).

## Elettronica

| Q.tà | Componente | Note |
|---|---|---|
| 1 | ESP32-D (WROOM-32D) devkit | |
| 1 | Modulo RTC **DS3231** + batteria CR2032 | I²C |
| 1 | Lettore **FDX-B 134.2 kHz** (es. WL-134) con bobina | UART · verificare livello logico del TX |
| 1 | Sensore ToF **VL53L0X** (GY-VL53L0XV2, 26 × 12 mm circa) | I²C · misurare la schedina prima di stampare il coperchio |
| 1 | Driver **TMC2209** (modulo StepStick) | UART + DIAG |
| 1 | Motore **NEMA 17**, 42 × 42 × 40 mm, albero Ø 5 mm con piano (D) | ~0,4 Nm |
| 1 | Alimentatore **12V 2A**, spina 5,5 × 2,1 mm | |
| 1 | Jack DC da pannello 5,5 × 2,1 mm (foro Ø 8 mm) | |
| 1 | Step-down 12V → 5V (es. MP1584 / LM2596) | |
| 1 | Condensatore elettrolitico ≥ 100 µF / 25V | su `VM` del TMC2209 |
| 1 | Resistenza 1 kΩ | UART single-wire del TMC2209 |
| — | Millefori, cavetti, connettori JST/Dupont | |

## Consumabili

| Q.tà | Componente | Note |
|---|---|---|
| 1 | **Sacchetto di gel di silice da 5 g** (~40 × 30 × 6 mm) | nella camera del coperchio, non tocca il cibo · rigenerabile in forno |

## Zavorra

| Q.tà | Componente | Note |
|---|---|---|
| 4 | **Barra piatta in acciaio 40 × 5 mm**, tagliata a **140 mm** | da una barra da 1 m (negozi di bricolage) · ~0,9 kg in totale |

## Viteria

| Q.tà | Vite | Dove |
|---|---|---|
| 2 | M4 × 20 + dado M4 + rondella | base anteriore ↔ posteriore |
| 2 | M4 × 16 + dado M4 + rondella | schienale ↔ base posteriore |
| 4 | M3 × 12 + dado M3 | corpo coclea ↔ base posteriore |
| 4 | M3 × 8 | NEMA 17 ↔ flangia |
| 8 | M3 × 8 autofilettante + rondella larga Ø 9 | fermi delle barre di zavorra |
| 2 | M3 × 8 autofilettante | sportello del vano elettronica |
| 1 | Grano M3 × 6 | mozzo della coclea sull'albero motore (sul piano a D) |
| 4 | Vite Ø 4 mm, testa ≤ 8,5 mm + tassello | fissaggio a muro (asole) |

## Pezzi stampati

Materiale consigliato: **PETG** (alimentare per ciotola, coclea, corpo coclea e cisterna). Piatto minimo **180 × 180 × 180 mm**.

| Pezzo | File | Ingombro (mm) |
|---|---|---|
| Base anteriore | `front-base` | 170 × 160 × 25 |
| Base posteriore | `rear-base` | 170 × 160 × 55 |
| Sportello vano | `bay-door` | 128 × 46 × 2,5 |
| Ciotola | `bowl` | 130 × 130 × 45 |
| Corpo coclea | `auger-housing` | 150 × 85 × 71 |
| Coclea | `auger` | 144 × Ø 38 |
| Cisterna, segmento **× N** (consigliato 2) | `hopper-segment` | 125 × Ø 85 |
| Coperchio (sensore + camera antiumidità) | `lid` | Ø 96 × 22 |
| Tappo camera antiumidità | `desiccant-cover` | 94 × 41 × 2 |
| Schienale | `back-plate` | 170 × 170 × 6 |
| Staffa superiore (solo con N ≥ 2) | `upper-bracket` | 154 × 120 × 90 |

### Capienza

Segmenti tutti uguali e impilabili: ognuno ha un anello in cima in cui entra il successivo (o il coperchio).

| N | Altezza dispenser | Croccantini | Autonomia (~55 g/giorno) |
|---|---|---|---|
| 1 | ~245 mm | ~200 g | ~3–4 giorni |
| 2 | ~360 mm | ~400 g | ~7 giorni |
| 3 | ~475 mm | ~600 g | ~11 giorni |
| 4 | ~590 mm | ~800 g | ~14 giorni |

- **N ≤ 4** consigliato: oltre, la portata del VL53L0X su croccantini va verificata al banco
- Con N ≥ 3 fissare a muro: la torre diventa alta
- Cambiando N, aggiornare **Distance when empty** (Home Assistant o BLE)
- Per l'assieme con N segmenti: `exec(..., {"SEGMENTS": N})`, vedi `cad/build.py`

File in [`cad/export/`](../cad/export/), formati STEP e STL, in posizione di assemblaggio: l'orientamento di stampa si sceglie nello slicer.
