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
| 1 | Grano M3 × 6 | beccuccio sul corpo coclea |
| 1 | Grano M3 × 6 | mozzo della coclea sull'albero motore (sul piano a D) |
| 4 | Vite Ø 4 mm, testa ≤ 8,5 mm + tassello | fissaggio a muro (asole) |

## Pezzi stampati

Materiale consigliato: **PETG** (alimentare per ciotola, coclea, beccuccio e cisterna). Piatto minimo **180 × 180 × 180 mm**.

| Pezzo | File | Ingombro (mm) |
|---|---|---|
| Base anteriore | `front-base` | 170 × 160 × 25 |
| Base posteriore | `rear-base` | 170 × 160 × 55 |
| Sportello vano | `bay-door` | 128 × 46 × 2,5 |
| Ciotola | `bowl` | 130 × 130 × 45 |
| Corpo coclea | `auger-housing` | 140 × 85 × 71 |
| Beccuccio | `spout` | 68 × 56 × 30 |
| Coclea | `auger` | 134 × Ø 38 |
| Cisterna, segmento 1 | `hopper-segment1` | 125 × Ø 85 |
| Cisterna, segmento 2 | `hopper-segment2` | 115 × Ø 79 |
| Coperchio | `lid` | Ø 85 × 15 |
| Schienale | `back-plate` | 170 × 170 × 6 |
| Staffa superiore | `upper-bracket` | 154 × 120 × 90 |

File in [`cad/export/`](../cad/export/), formati STEP e STL, in posizione di assemblaggio: l'orientamento di stampa si sceglie nello slicer.
