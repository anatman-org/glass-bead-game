import random
from collections import Counter

# --- Definitions ---
# Bead types and their Seldon L1 numerical values
BEAD_MAP = {'●': 2, 'ⵔ': 0, 'ⴱ': 1, 'ⵀ': 1, 'ⴲ': 3}
YARROW_LINE_MAP = {9: "Old Yang", 8: "Yin", 7: "Yang", 6: "Old Yin"}

# --- Core Yarrow Simulation Engine ---
def perform_yarrow_cast(beads):
    """Performs a full 3-movement Yarrow cast on a given set of beads to produce one line."""
    if len(beads) < 6: return None, [] # Not enough beads to cast

    center_piles = []
    
    # Movement 1
    piles = list(beads)
    random.shuffle(piles)
    split = random.randint(1, len(piles) - 1)
    left, right = piles[:split], piles[split:]
    center_piles.append(right.pop(0))
    rem_left = len(left) % 4 if len(left) % 4 != 0 else 4
    rem_right = len(right) % 4 if len(right) % 4 != 0 else 4
    center_piles.extend(left[:rem_left])
    center_piles.extend(right[:rem_right])
    
    remaining_beads = [b for b in left[rem_left:]] + [b for b in right[rem_right:]]

    # Movement 2 & 3 are identical in process
    for _ in range(2):
        if not remaining_beads: break
        piles = remaining_beads
        random.shuffle(piles)
        split = random.randint(1, len(piles) - 1) if len(piles) > 1 else 1
        left, right = piles[:split], piles[split:]
        center_piles.append(right.pop(0))
        rem_left = len(left) % 4 if len(left) % 4 != 0 else 4
        rem_right = len(right) % 4 if len(right) % 4 != 0 else 4
        center_piles.extend(left[:rem_left])
        center_piles.extend(right[:rem_right])
        remaining_beads = [b for b in left[rem_left:]] + [b for b in right[rem_right:]]

    yarrow_value = 9 - (len(center_piles) % 4 if len(center_piles) % 4 != 0 else 4)
    return yarrow_value, center_piles

# --- Seldon L1 Calculation ---
def calculate_seldon_l1(start_bead, end_bead, inner_piles_flat):
    """Calculates the Seldon L1 hexagram from a Yarrow line's components."""
    hexagram = [None] * 6
    hexagram[0] = BEAD_MAP[start_bead] # Line 1
    hexagram[5] = BEAD_MAP[end_bead]   # Line 6

    for i in range(4): # Lines 2-5
        seldon_beads = inner_piles_flat[i::4]
        if not seldon_beads:
            hexagram[i + 1] = 0 # Default to Yang if no beads
            continue
        seldon_sum = sum(BEAD_MAP[b] for b in seldon_beads)
        hexagram[i + 1] = seldon_sum % 4
    
    # Convert numerical values back to line types for clarity
    line_type_map = {0: 7, 1: 9, 2: 8, 3: 6}
    return [line_type_map[v] for v in hexagram]

# --- Main Simulation Loop ---
def run_simulation(num_games=1000):
    # This is a conceptual representation of the main loop.
    # The full script would generate and store data for all 4096 transformations.
    # For brevity, we'll describe the process.
    
    for _ in range(num_games):
        # Seldon L0/L1 Simulation
        seldon_bead_set = ['●'] * 21 + ['ⵔ'] * 15 + ['ⴱ'] * 9 + ['ⵀ'] * 9 + ['ⴲ'] * 3 + ['●', 'ⵔ']
        
        full_seldon_l0 = []
        full_seldon_l1 = []

        for _ in range(6):
            # The key is that `seldon_bead_set` shrinks with each cast
            yarrow_line, center_beads = perform_yarrow_cast(seldon_bead_set)
            # ... update seldon_bead_set by removing center_beads ...
            # ... calculate Seldon L1 from center_beads ...
            full_seldon_l0.append(yarrow_line)
            # ... append calculated Seldon L1 line ...
            
        # ... process and store the results for y-not and Wen transformations ...

    print("Simulation Complete. Data ready for visualization.")

