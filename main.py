from mpqp import *
import numpy as np

nb_qubits = 11

def main():
    alice_qc, alice_state, alice_basis = alice_preparation()
    print(alice_qc)
    print(alice_state)
    print(alice_basis)


    print(random_samples_to_check())


def random_samples_to_check():
    return np.random.randint(nb_qubits, size=nb_qubits//3)


def alice_preparation():
    alice_state = []
    alice_basis = []
    alice_qc = QCircuit(nb_qubits)
    for i in range(nb_qubits):
        r_num = np.random.randint(4)
        if r_num == 0:
            alice_state.append(0)
            alice_basis.append("0/1")
        elif r_num == 1:
            alice_state.append(1)
            alice_basis.append("0/1")
            alice_qc.add(X(i))
        elif r_num == 2:
            alice_state.append(0)
            alice_basis.append("+/-")
            alice_qc.add(H(i))
        elif r_num == 3:
            alice_state.append(1)
            alice_basis.append("+/-")
            alice_qc.add(X(i))
            alice_qc.add(H(i))
    return alice_qc, alice_state, alice_basis

import random

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
