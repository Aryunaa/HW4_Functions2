from typing import Iterable

PROT_SET_1 = frozenset('ARNDCEQGHILKMFPSTWYV')
PROT_SET_3 = frozenset({'Ala','Arg', 'Asn', 'Asp', 'Cys',
                        'Gln', 'Glu', 'Gly', 'His', 'Ile',
                        'Leu', 'Lys', 'Met', 'Phe', 'Pro',
                        'Ser', 'Thr', 'Trp', 'Tyr', 'Val'})
AA_TR_DICT = {'Ala': 'A', 'Arg': 'R', 'Asn': 'N', 'Asp': 'D',
              'Cys': 'C', 'Gln': 'E', 'Glu': 'Q', 'Gly': 'G',
              'His': 'H', 'Ile': 'I', 'Leu': 'L', 'Lys': 'K',
              'Met': 'M', 'Phe': 'F', 'Pro': 'P', 'Ser': 'S',
              'Thr': 'T', 'Trp': 'W', 'Tyr': 'Y', 'Val': 'V'}
AA_UNIPROT_CONTENT = {
"A": 9.03, "R": 5.84, "N": 3.79, "D": 5.47, "C": 1.29,
"Q": 3.80, "E": 6.24, "G": 7.27, "H": 2.22, "I": 5.53,
"L": 9.85, "K": 4.93, "M": 2.33, "F": 3.88, "P": 4.99,
"S": 6.82, "T": 5.55, "W": 1.30, "Y": 2.88, "V": 6.86
}
AA_CHARGES = {
"A": 0, "R": 1, "N": 0, "D": -1, "C": 0,
"Q": 0, "E": -1, "G": 0, "H": 1, "I": 0,
"L": 0, "K": 1, "M": 0, "F": 0, "P": 0,
"S": 0, "T": 0, "W": 0, "Y": 0, "V": 0
}


def Mann_Whitney_U(seq1: Iterable[int], seq2: Iterable[int]) -> bool:
    """
    Mann-Whitney U-test. Used to compare aminoacids composition in sequence with average composition provided by Uniprot.
    Used as a second step in `check_seq` function if sequence is 1-letter abbreviation.
    """
    len_seq1, len_seq2 = len(seq1), len(seq2)
    r1, r2 = dict.fromkeys(map(str, seq1), 0), dict.fromkeys(map(str, seq2), 0)

    r = sorted(list(seq1) + list(seq2))
    r_dict = dict.fromkeys(map(str, r), ())
    
    for index, value in enumerate(r):
        value = str(value)
        r_dict[value] = r_dict[value] + (index + 1,)
    for elem in r_dict:
        r_dict[elem] = sum(r_dict[elem]) / len(r_dict[elem])

    for value in seq1:
        value = str(value)
        r1[value] = r1[value] + r_dict[value]
    
    for value in seq2:
        value = str(value)
        r2[value] = r2[value] + r_dict[value]

    u1 = (len_seq1 * len_seq2) + len_seq1 * (len_seq1 + 1) / 2 - sum(r1.values())
    u2 = (len_seq1 * len_seq2) + len_seq2 * (len_seq2 + 1) / 2 - sum(r2.values())

    u_stat = min(u1, u2)

    if u_stat <= 127:
        return False
    return True


def decomposition(seq):
    len_seq, dec_seq = len(seq), []
    for i in range(0, len_seq, 3):
        dec_seq.append(seq[i:i+3].lower().capitalize())
    return dec_seq


def seq_transform(seq: list):
    seq_tr = ''
    for aa in seq:
        seq_tr += AA_TR_DICT[aa]
    
    return seq_tr


def check_seq(seq: Iterable, abbreviation: int = 1) -> bool:
    """
    Checks whether the string is protein.                                                                               
    """
    if abbreviation == 3:
        seq = decomposition(seq)
        exit_code = set(seq).issubset(PROT_SET_3)
        if exit_code:
            seq = seq_transform(seq)
    elif abbreviation == 1:
        seq_set = set(seq.upper())
        exit_code = seq_set.issubset(PROT_SET_1)
        if exit_code:
            seq_content, uniprot_content = aa_content_check(seq).values(), AA_UNIPROT_CONTENT.values()
            seq_Mann_Whitney_U = Mann_Whitney_U(seq_content, uniprot_content) if len(seq_set) == 20 else True
            exit_code = seq_Mann_Whitney_U
    
    return exit_code, seq


def seq_length(seq: str) -> int:
    return len(seq)


def print_result(result: list, corrupt_seqs: list):
    len_seq, len_corr_seq = len(result), len(corrupt_seqs)
    len_seqs = len_seq + len_corr_seq
    success = ["+" for _ in range(len_seqs)]
    if not len_corr_seq:
        print(f"All {len_seqs} sequence(s) processed successfully")
    elif len_corr_seq:
        for i in corrupt_seqs:
            success[i[0]] = "-"
        print(f'Processing result: [{"".join(success)}]\n')
        print(f"{len_seq} sequence(s) out of {len_seq + len_corr_seq} given have been processed successfully.")
        print(f"{len_corr_seq} has been recognized as corrupted, i.e. non-protein")


OPERATIONS = {"content_check": aa_content_check, "seq_length": seq_length, "protein_formula": protein_formula, "protein_mass": protein_mass, "charge": aa_chain_charge}


def run_protein_analyzer_tool(*args, abbreviation: int = 1):
    """
    Docstring
    """
    *seqs, operation = args
    if operation not in OPERATIONS:
        raise ValueError(f'Unknown operation `{operation}`. Please, select from: "content_check", "seq_length", "protein_formula", "protein_mass", "charge"')

    result, corrupt_seqs = [], []
    for seq_index, seq in enumerate(seqs):
        is_seq_valid, seq = check_seq(seq, abbreviation)
        if is_seq_valid:
            result.append(OPERATIONS[operation](seq))
        elif not is_seq_valid:
            corrupt_seqs.append((seq_index, seq))

    print_result(result, corrupt_seqs)

    res_len, cor_seq_len = len(result), len(corrupt_seqs)
    result = result[0] if res_len >= 1 else result
    corrupt_seqs = corrupt_seqs[0] if cor_seq_len >= 1 else corrupt_seqs
    return result, corrupt_seqs
