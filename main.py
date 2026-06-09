from mpqp import *
import numpy as np
import random

class Alice():
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits
        self.states = []
        self.bases = []
        self.qc = QCircuit(nb_qubits)
        self.agreed_states = []
        self.sk = []

    def prepare(self):
        for i in range(self.nb_qubits):
            r_num = np.random.randint(4)
            if r_num == 0:
                self.states.append(0)
                self.bases.append("0/1")
            elif r_num == 1:
                self.states.append(1)
                self.bases.append("0/1")
                self.qc.add(X(i))
            elif r_num == 2:
                self.states.append(0)
                self.bases.append("+/-")
                self.qc.add(H(i))
            elif r_num == 3:
                self.states.append(1)
                self.bases.append("+/-")
                self.qc.add(X(i))
                self.qc.add(H(i))

    def find_matching_bases(self, other_basis):
        agreed_index = [i for i, (a, b) in enumerate(zip(self.bases, other_basis)) if a == b]
        self.agreed_states = [self.states[i] for i in agreed_index]
        return agreed_index
    
    def check_agree(self):
        random_check = np.random.randint(len(self.agreed_states), size=len(self.agreed_states)//3)
        return random_check, [self.agreed_states[i] for i in random_check]
    
    def fix_sk(self, indices):
        self.sk = [self.agreed_states[i] for i in range(len(self.agreed_states)) if i not in indices]

class Bob:
    def __init__(self, nb_qubits, circ):
        self.nb_qubits = nb_qubits
        self.circ = circ
        self.bases = []
        self.results = []
        self.agreed_states = []

    def measure(self):
        for i in range(self.nb_qubits):
            base = "0/1" if random.randint(0, 1) == 0 else "+/-"
            self.bases.append(base)

            if base == "+/-":
                self.circ.add(H(i))
                
        self.circ.add(BasisMeasure(basis=ComputationalBasis(), shots=0))
                
        result = run(self.circ, [AWSDevice.BRAKET_LOCAL_SIMULATOR])
        amps = result[0].amplitudes
        probabilities = np.abs(amps) ** 2
        idx_max = np.argmax(probabilities)
            
        bin_str = format(idx_max, f'0{self.nb_qubits}b')
        self.results = [int(i) for i in bin_str]

    def agree_on_bases(self, agreed_index):
        self.agreed_states = [self.results[i] for i in agreed_index]
    
    def fix_sk(self, indices):
        self.sk = [self.agreed_states[i] for i in range(len(self.agreed_states)) if i not in indices]

class Eve:
    def __init__(self, nb_qubits, qc):
        self.nb_qubits = nb_qubits
        self.qc = qc
        self.bases = []
        self.results = []

    def hack(self):
        for i in range(self.nb_qubits):
            base = "0/1" if random.randint(0, 1) == 0 else "+/-"
            self.bases.append(base)

            if base == "+/-":
                self.qc.add(H(i))

        self.qc.add(BasisMeasure(basis=ComputationalBasis(), shots=0))
                
        result = run(self.qc, [AWSDevice.BRAKET_LOCAL_SIMULATOR])
        amps = result[0].amplitudes
        probabilities = np.abs(amps) ** 2
        idx_max = np.argmax(probabilities)
            
        bin_str = format(idx_max, f'0{self.nb_qubits}b')
        self.results = [int(i) for i in bin_str]

def bb84_protocol_test():
    nb_qubits = 11
    print(f"=== LANCEMENT DU TEST BB84 SUR {nb_qubits} QUBITS ===\n")
    
    #PARTIE ALICE
    alice = Alice(nb_qubits)
    alice.prepare()
    print("--- 1. ÉTATS SOUHAITÉS PAR ALICE ---")
    print("Bases d'Alice        :", alice.bases)
    print("Bits secrets d'Alice :", alice.states)
    print("-" * 40 + "\n")
    
    #PARTIE BOB
    bob = Bob(nb_qubits, alice.qc)
    bob.measure()
    print("--- 2. MESURES DE BOB ---")
    print("Bases de Bob        :", bob.bases)
    print("Bits mesurés        :", bob.results)
    print("-" * 40 + "\n")
    
    agreed_index = alice.find_matching_bases(bob.bases)
    bob.agree_on_bases(agreed_index)
    
    print("--- 3. RÉCONCILIATION DES BASES ---")
    print("Indices partagés (bases identiques) :", agreed_index)
    print("Bits conservés par Alice            :", alice.agreed_states)
    print("Bits conservés par Bob              :", bob.agreed_states)
    print("-" * 40 + "\n")
    
    indices_test, bits_test_alice = alice.check_agree()
    bits_test_bob = [bob.agreed_states[i] for i in indices_test]
    
    print(f"--- 4. TEST DE SÉCURITÉ (Échantillon choisi : {indices_test}) ---")
    print("Bits de contrôle d'Alice :", bits_test_alice)
    print("Bits de contrôle de Bob   :", bits_test_bob)
    
    if bits_test_alice == bits_test_bob:
        print("\n[RÉSULTAT] Succès : Aucun espionnage détecté.")
        alice.fix_sk(indices_test)
        bob.fix_sk(indices_test)
        print("-> Clé secrète finale d'Alice :", alice.sk)
        print("-> Clé secrète finale de Bob   :", bob.sk)
    else:
        print("\n[RÉSULTAT] Alerte : Les bits de test diffèrent ! Le canal est corrompu.")



def bb84_protocol_test_with_eve():
    nb_qubits = 11
    print(f"=== LANCEMENT DU TEST BB84 SUR {nb_qubits} QUBITS ===\n")
    
    #PARTIE ALICE
    alice = Alice(nb_qubits)
    alice.prepare()
    print("--- 1. ÉTATS SOUHAITÉS PAR ALICE ---")
    print("Bases d'Alice        :", alice.bases)
    print("Bits secrets d'Alice :", alice.states)
    print("-" * 40 + "\n")

    #PARTIE EVE
    eve = Eve(nb_qubits, alice.qc)
    eve.hack()
    print("--- !!! ÉTATS PERTURBES PAR EVE !!! ---")
    print("Bases d'Eve        :", eve.bases)
    print("Bits mesurés par Eve :", eve.results)
    print("-" * 40 + "\n")
    
    #PARTIE BOB
    bob = Bob(nb_qubits, eve.qc.without_measurements())
    bob.measure()
    print("--- 2. MESURES DE BOB ---")
    print("Bases de Bob        :", bob.bases)
    print("Bits mesurés        :", bob.results)
    print("-" * 40 + "\n")
    
    agreed_index = alice.find_matching_bases(bob.bases)
    bob.agree_on_bases(agreed_index)
    
    print("--- 3. RÉCONCILIATION DES BASES ---")
    print("Indices partagés (bases identiques) :", agreed_index)
    print("Bits conservés par Alice            :", alice.agreed_states)
    print("Bits conservés par Bob              :", bob.agreed_states)
    print("-" * 40 + "\n")
    
    indices_test, bits_test_alice = alice.check_agree()
    bits_test_bob = [bob.agreed_states[i] for i in indices_test]
    
    print(f"--- 4. TEST DE SÉCURITÉ (Échantillon choisi : {indices_test}) ---")
    print("Bits de contrôle d'Alice :", bits_test_alice)
    print("Bits de contrôle de Bob   :", bits_test_bob)
    
    if bits_test_alice == bits_test_bob:
        print("\n[RÉSULTAT] Succès : Aucun espionnage détecté.")
        alice.fix_sk(indices_test)
        bob.fix_sk(indices_test)
        print("-> Clé secrète finale d'Alice :", alice.sk)
        print("-> Clé secrète finale de Bob   :", bob.sk)
    else:
        print("\n[RÉSULTAT] Alerte : Les bits de test diffèrent ! Le canal est corrompu.")


def main():
    bb84_protocol_test()

if __name__ == "__main__":
    main()
