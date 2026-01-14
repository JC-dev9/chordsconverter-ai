import os

# Compatibilidade com versões recentes do TensorFlow
os.environ["TF_USE_LEGACY_KERAS"] = "1"

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from collections import defaultdict

# Ficheiro de entrada
WAV_FILE = "musica.wav"

if not os.path.exists(WAV_FILE):
    print(f"❌ Erro: O ficheiro '{WAV_FILE}' não existe.")
    exit()

# Mapeamento nota -> número (0-11)
NOTA_PARA_NUM = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}
NUM_PARA_NOTA = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def identificar_acorde(lista_notas):
    """Recebe lista de notas (ex: ['C4','E4','G4']) e tenta identificar o acorde."""
    if not lista_notas:
        return ""

    # Remover oitavas e duplicados
    notas_limpas = set()
    for n in lista_notas:
        nota_sem_numero = ''.join([c for c in n if not c.isdigit()])
        notas_limpas.add(nota_sem_numero)

    notas_unicas = list(notas_limpas)
    if len(notas_unicas) < 3:
        return f"Nota(s): {', '.join(notas_unicas)}"

    numeros = sorted([NOTA_PARA_NUM[n] for n in notas_unicas if n in NOTA_PARA_NUM])

    for raiz in numeros:
        intervalos = set()
        for outra_nota in numeros:
            distancia = (outra_nota - raiz) % 12
            intervalos.add(distancia)

        nome_raiz = NUM_PARA_NOTA[raiz]
        if {0, 4, 7}.issubset(intervalos):
            return f"{nome_raiz} Maior"
        if {0, 3, 7}.issubset(intervalos):
            return f"{nome_raiz} Menor"

    return f"Notas: {', '.join(notas_unicas)}"

print(f"A ler: {WAV_FILE}")
print("A analisar áudio e teoria musical...")

try:
    model_output, midi_data, note_events = predict(WAV_FILE, ICASSP_2022_MODEL_PATH)
    midi_data.write("resultado_final.mid")
except Exception as e:
    print(f"❌ Erro: {e}")
    exit()

acordes_raw = defaultdict(list)

def midi_to_note_name(midi_number):
    """Converter número MIDI (int) para nome de nota, ex: 60 -> C4."""
    pitch = int(midi_number)
    oitava = (pitch // 12) - 1
    nota = NUM_PARA_NOTA[pitch % 12]
    return f"{nota}{oitava}"

for note in note_events:
    tempo = round(note[0], 1)
    acordes_raw[tempo].append(midi_to_note_name(note[2]))

print("\nRESULTADO DA ANÁLISE:\n")
print(f"{'TEMPO':<10} | {'ACORDE / NOTAS'}")
print("-" * 30)

for tempo in sorted(acordes_raw.keys()):
    notas = sorted(set(acordes_raw[tempo]))
    nome_acorde = identificar_acorde(notas)
    print(f"{tempo}s".ljust(10) + f" | {nome_acorde}")

print("\nMIDI salvo como 'resultado_final.mid'")