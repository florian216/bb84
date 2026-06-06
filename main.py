from mpqp import *
import numpy as np
import random

class Alice():
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits

    def alice_preparation(self):
        alice_states = []
        alice_basis = []
        alice_qc = QCircuit(self.nb_qubits)
        for i in range(self.nb_qubits):
            r_num = np.random.randint(4)
            if r_num == 0:
                alice_states.append(0)
                alice_basis.append("0/1")
            elif r_num == 1:
                alice_states.append(1)
                alice_basis.append("0/1")
                alice_qc.add(X(i))
            elif r_num == 2:
                alice_states.append(0)
                alice_basis.append("+/-")
                alice_qc.add(H(i))
            elif r_num == 3:
                alice_states.append(1)
                alice_basis.append("+/-")
                alice_qc.add(X(i))
                alice_qc.add(H(i))
        self.qc = alice_qc
        self.states = alice_states
        self.basis = alice_basis

    def agree_on_basis(self, other_basis):
        agreed_index = [i for i, (a, b) in enumerate(zip(self.basis, other_basis)) if a == b]
        self.agreed_states = [self.basis[i] for i in agreed_index]
        return agreed_index
    
    def check_agree(self):
        random_check = np.random.randint(len(self.agreed_states), size=len(self.agreed_states)//3)
        return random_check, [self.basis[i] for i in random_check]
    
    def fix_sk(self, agreed):
        self.sk = [self.agreed_states[i] for i in agreed]

def main():
    nb_qubits = 12
    alice = Alice()


def bob_measurement(circ):
    nb_qubits = circ.nb_qubits
    bases_bob = []
    bits_mesures = []

    gates = circ.to_gate()
    for i in range(nb_qubits):
        base = "0/1" if random.randint(0, 1) == 0 else "+/-"
        bases_bob.append(base)
        circ_qubit = QCircuit()
        circ_qubit.add(gates)
        if base == "+/-":
            circ_qubit.add(BasisMeasure([i], basis=HadamardBasis(), shots=1000))
        else:
            circ_qubit.add(BasisMeasure([i], basis=ComputationalBasis(), shots=1000))
        result = run(
            circ_qubit,
            [AWSDevice.BRAKET_LOCAL_SIMULATOR]
        )
        bit_string = result.results[0].job
        print(bit_string)

    return bases_bob


if __name__ == "__main__":
    main()
