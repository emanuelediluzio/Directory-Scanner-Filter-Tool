# Directory Scanner & Filter Tool

Un semplice ma utile script Python da riga di comando per analizzare il contenuto di una directory o per filtrare e copiare il contenuto di una directory basandosi su un elenco di esclusione.

## Descrizione

Questo strumento offre due funzionalità principali:

1.  **Scan Mode:** Analizza una directory specificata e genera un file di testo (`.txt`) contenente l'elenco di tutti i file e le sottodirectory presenti al primo livello di quella directory.
2.  **Filter Mode:** Confronta il contenuto di una directory sorgente con un elenco di nomi fornito in un file di testo (`.txt`). Crea una nuova directory (con suffisso `_filtrato` accanto alla sorgente) e copia al suo interno tutti i file e le cartelle presenti nella directory sorgente **ad eccezione** di quelli i cui nomi sono elencati nel file `.txt`.

Lo script è progettato per essere interattivo e guidare l'utente attraverso le scelte e l'inserimento dei percorsi necessari.

## Funzionalità Principali

* **Modalità Scan:** Genera un elenco testuale del contenuto di una directory.
* **Modalità Filter:** Crea una copia filtrata di una directory, escludendo elementi specificati in un file di riferimento.
* **Interfaccia a Riga di Comando:** Facile da usare da qualsiasi terminale.
* **Cross-Platform:** Testato (dovrebbe funzionare) su Windows, macOS e Linux.
* **Gestione Errori:** Include la gestione di base per percorsi non validi, permessi mancanti ed errori di I/O.
* **Nessuna Dipendenza Esterna:** Utilizza solo la libreria standard di Python.

## Requisiti

* **Python:** È richiesta una versione di **Python 3.8 o successiva**.
    * *(Nota: La versione 3.8+ è consigliata per la piena funzionalità della modalità "filter", in particolare per la gestione della copia in directory di destinazione preesistenti (`dirs_exist_ok=True` in `shutil.copytree`). La modalità "scan" dovrebbe funzionare anche con versioni leggermente precedenti di Python 3).*

## Installazione

Non è necessaria alcuna installazione di pacchetti esterni. Lo script usa solo moduli inclusi nella libreria standard di Python.

Basta scaricare (o clonare) il file `.py` dello script.

## Come Usare lo Script

1.  **Salva lo Script:** Assicurati di avere il file Python (es. `directory_tool.py`) salvato sul tuo computer.
2.  **Apri un Terminale:** Apri il Prompt dei comandi (Windows), Terminal (macOS/Linux) o PowerShell (Windows).
3.  **Naviga alla Cartella:** Usa il comando `cd` per spostarti nella directory dove hai salvato il file `.py`.
    ```bash
    cd percorso/dove/hai/salvato/lo/script
    ```
4.  **Esegui lo Script:** Lancia lo script usando il comando `python` (o `python3` a seconda della tua configurazione):
    ```bash
    python directory_tool.py
    ```
    o
    ```bash
    python3 directory_tool.py
    ```
5.  **Segui le Istruzioni:** Lo script ti guiderà interattivamente:
    * Ti chiederà di confermare/specificare il sistema operativo (principalmente a scopo informativo).
    * Ti chiederà di scegliere l'azione: `scan` o `filter`.
    * **Se scegli `scan`:**
        * Ti chiederà il percorso assoluto della directory da analizzare.
        * Ti chiederà il nome desiderato per il file `.txt` di output (che verrà creato nella directory corrente da cui hai lanciato lo script).
    * **Se scegli `filter`:**
        * Ti chiederà il percorso assoluto della directory *sorgente* da filtrare.
        * Ti chiederà il percorso assoluto del file `.txt` contenente l'elenco dei nomi da **escludere** (un nome per riga).
        * Lo script creerà automaticamente una nuova directory accanto alla sorgente (es. `nome_sorgente_filtrato`) e vi copierà dentro gli elementi non esclusi.

## Output

* **Modalità Scan:** Crea un file `.txt` (con il nome specificato) nella directory di lavoro corrente, contenente l'elenco dei file/cartelle della directory scansionata.
* **Modalità Filter:** Crea una nuova directory (es. `nome_sorgente_filtrato`) nella stessa posizione della directory sorgente. Questa nuova directory conterrà una copia dei file e delle sottodirectory della sorgente che *non* erano elencati nel file `.txt` di riferimento.

## Licenza

Questo progetto è rilasciato sotto la Licenza MIT. Vedi il file `LICENSE` per maggiori dettagli (o puoi aggiungere qui i dettagli della licenza se preferisci non avere un file separato).

---

*(Facoltativo: puoi aggiungere sezioni come "Come Contribuire", "Autore", "Problemi Noti", ecc.)*
