# Configurazione locale via BLE

Il dispositivo espone un servizio GATT per configurarlo **senza rete**, con un client generico come **nRF Connect** (Android/iOS).

## Sicurezza

- **Lettura** libera: chiunque nel raggio BLE vede configurazione e stato
- **Scrittura** solo da un telefono **accoppiato**: al primo collegamento il telefono chiede la **passkey a 6 cifre**, stampata sull'adesivo del dispositivo
- La passkey è in `firmware/esphome/secrets.yaml` (`ble_passkey`), mai nel repo
- Pairing LE Secure Connections con protezione MITM e bonding: dopo il primo accoppiamento il telefono si ricollega senza chiedere di nuovo
- Il pulsante **Forget BLE devices** (Home Assistant) cancella tutti i telefoni accoppiati

## Servizio

UUID: `6e3c0000-1a2b-4c5d-8e9f-0a1b2c3d4e5f` (nome pubblicizzato: `cat-feeder`)

Tutte le caratteristiche sono **testo UTF-8**: in nRF Connect scrivere con il formato *Text*. Ognuna ha una descrizione (descrittore 0x2901) visibile nell'app.

| UUID | Nome | Accesso | Formato | Esempio |
|---|---|---|---|---|
| `6e3c0001-…` | Dose | R/W | passi, 200–32000 | `4800` |
| `6e3c0002-…` | Override dose | R/W | passi, 0 = dose standard | `0` |
| `6e3c0003-…` | Soglia livello basso | R/W | %, 0–50 | `10` |
| `6e3c0004-…` | Pausa | R/W | `0` / `1` | `0` |
| `6e3c0005-…` | Fasce | R/W | `HH:MM-HH:MM` × 3, separate da virgola | `06:00-11:59,12:00-17:59,18:00-23:59` |
| `6e3c0006-…` | Chip autorizzato 1 | R/W | 15 cifre, vuoto = nessuno | `380123456789012` |
| `6e3c0007-…` | Eroga ora | W | vuoto = dose (override o standard), oppure passi | `3200` |
| `6e3c0008-…` | Azzera flag fasce | W | qualsiasi valore | `1` |
| `6e3c0009-…` | Stato | R | chiave=valore separati da `;` | `level=45%;doses=12;fed=100;paused=0;time=2026-10-20 17:05;chip=-` |

Il suffisso di tutti gli UUID è `-1a2b-4c5d-8e9f-0a1b2c3d4e5f`.

### Campi dello stato

| Campo | Significato |
|---|---|
| `level` | livello della cisterna in %, `?` se il sensore non risponde |
| `doses` | dosi residue stimate, `?` finché la calibrazione non ha dati |
| `fed` | flag fasce 1-2-3 del gatto 1 (`1` = già mangiato) |
| `paused` | `1` = erogazione automatica in pausa |
| `time` | ora del dispositivo, `invalid` se non sincronizzata |
| `chip` | ultimo microchip letto |

I valori leggibili si aggiornano ogni 5 s e subito dopo ogni scrittura.

## Uso con nRF Connect

1. *Scanner* → `cat-feeder` → **Connect**
2. Il telefono chiede l'accoppiamento: inserire la **passkey** dell'adesivo
3. Aprire il servizio `6e3c0000-…`
4. Per leggere: freccia ↓ sulla caratteristica
5. Per scrivere: freccia ↑ → formato **Text** → valore → *Send*

Scritture non valide o da telefoni non accoppiati sono ignorate e segnalate nel log del dispositivo.

## Regole dell'override

"Eroga ora" segue le regole dell'override manuale di [`plan.md`](plan.md): ignora microchip, fascia, flag, soglia, ora e pausa; non consuma la fascia; dopo un override i successivi sono ignorati per 10 s; StallGuard resta attivo.
