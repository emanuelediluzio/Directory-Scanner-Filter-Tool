import os
import platform
import sys
import io
import shutil # Necessario per le operazioni di copia file/cartelle

# --- Funzioni di Utilità (invariate) ---

def get_validated_input(prompt, validation_func, error_message, allow_empty=False):
    """
    Chiede un input all'utente e lo valida usando una funzione specificata.
    Continua a chiedere finché l'input non è valido o vuoto (se consentito).
    """
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            if allow_empty:
                return None # Ritorna None per input vuoto consentito
            else:
                print("Errore: L'input non può essere vuoto. Riprova.")
                continue
        # Normalizza il percorso per coerenza
        # Determina se la funzione di validazione opera su percorsi
        is_path_validation = any(func_name in validation_func.__code__.co_names for func_name in ['os', 'shutil'])
        normalized_input = os.path.normpath(user_input) if is_path_validation else user_input

        if validation_func(normalized_input):
            return normalized_input
        else:
            print(error_message) # Mostra l'errore specifico della validazione

def is_valid_dir(path):
    """Controlla se il percorso è una directory esistente."""
    try:
        return os.path.isdir(path)
    except Exception as e:
        print(f"[Debug] Eccezione in is_valid_dir per '{path}': {e}")
        return False

def is_valid_file(path):
    """Controlla se il percorso è un file esistente."""
    try:
        return os.path.isfile(path)
    except Exception as e:
        print(f"[Debug] Eccezione in is_valid_file per '{path}': {e}")
        return False

def is_valid_txt_file(path):
    """Controlla se il percorso è un file esistente con estensione .txt."""
    if not is_valid_file(path):
        return False
    return path.lower().endswith('.txt')

# --- Funzione Scan (invariata) ---

def sanitize_filename(name, is_dir=False):
    """
    Rimuove caratteri potenzialmente problematici da un nome file/dir e
    assicura l'estensione .txt per i file.
    """
    if not name:
        return "output.txt" if not is_dir else "output_dir"

    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '_')

    if not is_dir and not name.lower().endswith('.txt'):
        name += '.txt'

    reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
    if name.upper() in reserved_names:
        name = "_" + name

    return name

def scan_directory(directory_path, output_filename):
    """
    Esegue la scansione della directory, gestendo vari errori possibili.
    Restituisce True in caso di successo, False altrimenti.
    (Codice identico alla versione precedente)
    """
    normalized_dir = os.path.normpath(directory_path)
    sanitized_output_filename = sanitize_filename(output_filename)
    output_path = os.path.join(os.getcwd(), sanitized_output_filename)

    print(f"\n[*] Avvio scansione directory: '{normalized_dir}'")
    try:
        if not os.path.isdir(normalized_dir):
             print(f"[Errore] Il percorso specificato non è una directory valida: '{normalized_dir}'")
             return False
        print(f"[*] Lettura contenuto...")
        items = os.listdir(normalized_dir)
        print(f"[*] Trovati {len(items)} elementi.")
        print(f"[*] Tentativo di scrittura risultati su: '{output_path}'")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in items:
                    try:
                        f.write(item + '\n')
                    except UnicodeEncodeError:
                        print(f"[Attenzione] Impossibile scrivere il nome file '{item}' (problema di encoding?). Verrà omesso.")
                        f.write(f" NOME_FILE_NON_SCRIVIBILE (Encoding Error)\n")
            print(f"\n[Successo] Scansione completata.")
            print(f"[Info] Risultati salvati in: '{output_path}'")
            return True
        except (IOError, OSError) as e:
            print(f"\n[Errore Grave] Impossibile scrivere il file di output '{output_path}': {e}")
            return False
        except PermissionError:
             print(f"\n[Errore Grave] Permessi insufficienti per creare/scrivere il file '{output_path}' nella directory corrente.")
             return False
    except Exception as e:
        print(f"[Errore Imprevisto] Si è verificato un errore non gestito durante la scansione: {e}")
        import traceback
        traceback.print_exc()
        return False

# --- Funzione Compare (MODIFICATA) ---

def filter_and_copy_directory(directory_path, txt_file_path):
    """
    Confronta il contenuto della directory con il file txt.
    Crea una nuova cartella '_filtrato' e copia al suo interno
    gli elementi della directory NON presenti nel file txt.
    Restituisce True in caso di successo generale, False altrimenti.
    """
    normalized_dir = os.path.normpath(directory_path)
    normalized_txt_path = os.path.normpath(txt_file_path)

    print(f"\n[*] Avvio filtraggio e copia:")
    print(f"    Directory Sorgente : '{normalized_dir}'")
    print(f"    File Riferimento   : '{normalized_txt_path}'")

    items_copied_count = 0
    items_failed_count = 0
    destination_dir_path = None # Inizializza a None

    try:
        # --- Fase 1: Lettura File di Riferimento (.txt) ---
        print(f"[*] Lettura file di riferimento: '{normalized_txt_path}'...")
        names_in_file = set()
        try:
            with open(normalized_txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    stripped_line = line.strip()
                    if stripped_line:
                        names_in_file.add(stripped_line)
            if not names_in_file:
                 print(f"[Attenzione] Il file di riferimento '{normalized_txt_path}' è vuoto o non contiene nomi validi.")
            else:
                print(f"[*] Letti {len(names_in_file)} nomi unici dal file di riferimento (da escludere).")
        except Exception as e: # Cattura generica per errori lettura file
            print(f"[Errore Grave] Impossibile leggere il file di riferimento '{normalized_txt_path}': {e}")
            return False # Non possiamo procedere senza il file

        # --- Fase 2: Lettura Contenuto Directory Sorgente ---
        print(f"[*] Lettura contenuto directory sorgente: '{normalized_dir}'...")
        try:
             if not os.path.isdir(normalized_dir):
                 print(f"[Errore] Il percorso sorgente '{normalized_dir}' non è (o non è più) una directory valida.")
                 return False
             items_in_directory_list = os.listdir(normalized_dir)
             items_in_directory = set(items_in_directory_list)
             print(f"[*] Trovati {len(items_in_directory)} elementi nella directory sorgente.")
        except Exception as e: # Cattura generica per errori lettura dir
            print(f"[Errore Grave] Impossibile leggere il contenuto della directory sorgente '{normalized_dir}': {e}")
            return False

        # --- Fase 3: Identificazione Elementi da Copiare ---
        print("[*] Identificazione elementi da copiare (non presenti nel file .txt)...")
        items_to_copy = items_in_directory - names_in_file
        if not items_to_copy:
            print("[Info] Nessun elemento trovato nella directory che non sia nel file di riferimento.")
            print("[*] Operazione terminata: nessuna copia necessaria.")
            return True # Successo, anche se non si è copiato nulla
        else:
             print(f"[*] Trovati {len(items_to_copy)} elementi da copiare.")

        # --- Fase 4: Creazione Directory Destinazione ---
        parent_dir = os.path.dirname(normalized_dir)
        base_name = os.path.basename(normalized_dir)
        # Sanifica il nome base prima di aggiungere il suffisso
        sanitized_base_name = sanitize_filename(base_name, is_dir=True)
        new_dir_name = f"{sanitized_base_name}_filtrato"
        destination_dir_path = os.path.join(parent_dir, new_dir_name)

        print(f"[*] Creazione directory destinazione: '{destination_dir_path}'")
        try:
            # exist_ok=True: non dà errore se esiste già
            # dirs_exist_ok=True in copytree (Python 3.8+) gestirà la copia in una dir esistente
            os.makedirs(destination_dir_path, exist_ok=True)
        except OSError as e:
            print(f"[Errore Grave] Impossibile creare la directory di destinazione '{destination_dir_path}': {e}")
            return False
        except Exception as e: # Altri errori imprevisti
             print(f"[Errore Grave] Errore imprevisto durante creazione directory '{destination_dir_path}': {e}")
             return False

        # --- Fase 5: Copia Elementi ---
        print("[*] Avvio copia elementi...")
        for item_name in items_to_copy:
            source_path = os.path.join(normalized_dir, item_name)
            destination_path = os.path.join(destination_dir_path, item_name)
            item_type = "Sconosciuto"

            try:
                if os.path.isfile(source_path):
                    item_type = "File"
                    print(f"  - Copia {item_type}: '{item_name}'...", end="")
                    shutil.copy2(source_path, destination_path) # copy2 preserva metadata
                    print(" OK")
                    items_copied_count += 1
                elif os.path.isdir(source_path):
                    item_type = "Directory"
                    print(f"  - Copia {item_type}: '{item_name}'...")
                    # dirs_exist_ok=True (Python 3.8+): permette la copia anche se la dir destinazione esiste
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                    print(f"    '{item_name}' OK")
                    items_copied_count += 1
                else:
                    # Potrebbe essere un link simbolico, socket, ecc. Lo ignoriamo per ora.
                    item_type = "Speciale (Ignorato)"
                    print(f"  - Ignora {item_type}: '{item_name}' (non è file né directory regolare)")
                    # Non incrementiamo né copied né failed per gli ignorati

            except (shutil.Error, OSError, IOError) as e:
                print(f" ERRORE: {e}")
                items_failed_count += 1
            except Exception as e: # Cattura errori imprevisti durante la copia di un singolo item
                print(f" ERRORE IMPREVISTO: {e}")
                items_failed_count += 1

        # --- Fase 6: Riepilogo ---
        print("\n[*] Riepilogo Copia:")
        print(f"    Elementi copiati con successo: {items_copied_count}")
        print(f"    Elementi con errori durante la copia: {items_failed_count}")
        print(f"    Directory destinazione: '{destination_dir_path}'")

        if items_failed_count > 0:
            print("[Attenzione] Alcuni elementi non sono stati copiati a causa di errori.")
            return False # Consideriamo fallimento se anche un solo item fallisce? O successo parziale? Mettiamo False.
        else:
            print("\n[Successo] Filtraggio e copia completati.")
            return True

    except Exception as e:
        # Catch-all per errori imprevisti nel processo generale
        print(f"[Errore Imprevisto Globale] Si è verificato un errore non gestito durante il processo: {e}")
        import traceback
        traceback.print_exc()
        # Se l'errore avviene prima della creazione della dir dest, destination_dir_path sarà None
        if destination_dir_path:
             print(f"[Info] La directory di destinazione parziale potrebbe esistere: '{destination_dir_path}'")
        return False

# --- Blocco Principale di Esecuzione (Modificato per 'compare') ---
def main():
    print("--- Utility Avanzata Scan/Filter Directory ---")

    # ... (Parte Sistema Operativo invariata) ...
    print("\n--- Sistema Operativo ---")
    try:
        detected_os = platform.system()
        print(f"[*] Sistema Operativo Rilevato: {detected_os} ({platform.machine()})")
    except Exception as e:
        print("[Attenzione] Impossibile rilevare OS:", e)
        detected_os = "Sconosciuto"
    confirm_os = input(f"[*] Procedere con OS '{detected_os}'? (Invio per sì, 'n' per no, o specifica Windows/Linux/Darwin): ").strip().lower()
    chosen_os = detected_os
    if confirm_os == 'n':
        chosen_os = input(" > Inserisci OS (es. Windows, Linux, Darwin): ").strip().capitalize()
    elif confirm_os and confirm_os != 'y':
         chosen_os = confirm_os.capitalize()
    print(f"[*] OS considerato per l'esecuzione: {chosen_os}")


    # 2. Scelta Azione (Modificato nome opzione 'compare' in 'filter')
    print("\n--- Selezione Azione ---")
    action = None
    while action not in ['scan', 'filter']: # Cambiato 'compare' in 'filter'
        action = input(" > Scegli azione ('scan' o 'filter'): ").strip().lower()
        if action not in ['scan', 'filter']:
            print("[Errore] Input non valido. Scrivi 'scan' o 'filter'.")

    print("-" * 40)

    # 3. Esecuzione Azione
    success = False
    if action == 'scan':
        print("[Azione: Scan Directory]")
        target_dir = get_validated_input(
            prompt=" > Inserisci percorso assoluto directory da scansionare: ",
            validation_func=is_valid_dir,
            error_message="[Errore] Il percorso non è una directory valida o non esiste. Riprova."
        )
        output_scan_filename = input(" > Nome desiderato per il file .txt di output [scan_output.txt]: ").strip()
        if not output_scan_filename:
             output_scan_filename = "scan_output.txt"
             print(f"   [Info] Usato nome default: '{output_scan_filename}'")
        success = scan_directory(target_dir, output_scan_filename)

    elif action == 'filter': # Cambiato da 'compare'
        print("[Azione: Filter Directory based on Text File]")
        target_dir = get_validated_input(
            prompt=" > Inserisci percorso assoluto directory sorgente da filtrare: ",
            validation_func=is_valid_dir,
            error_message="[Errore] Il percorso non è una directory valida o non esiste. Riprova."
        )
        source_txt_file = get_validated_input(
            prompt=" > Inserisci percorso assoluto del file .txt con gli elementi da ESCLUDERE: ",
            validation_func=is_valid_txt_file,
            error_message="[Errore] Il percorso non è un file .txt valido o non esiste. Riprova."
        )
        # Non chiediamo più il nome del file di output, ma chiamiamo la nuova funzione
        success = filter_and_copy_directory(target_dir, source_txt_file)

    # --- Conclusione (invariata) ---
    print("\n" + "=" * 40)
    if success:
        print("[*] Operazione completata.")
        sys.exit(0)
    else:
        print("[!] Operazione terminata con errori o parzialmente.")
        sys.exit(1)

# Entry point dello script (invariato)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Operazione interrotta dall'utente.")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERRORE GLOBALE CRITICO] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)