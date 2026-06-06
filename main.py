from mpqp import *
import numpy as np
import random

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
            circ_qubit.add(BasisMeasure([i], basis=HadamardBasis(1), shots=0))
        else:
            circ_qubit.add(BasisMeasure([i], basis=ComputationalBasis(1), shots=0))

        result = run(
            circ_qubit,
            [AWSDevice.BRAKET_LOCAL_SIMULATOR]
        )
        amps = result[0].amplitudes
        probabilities = np.abs(amps) ** 2
        idx_max = np.argmax(probabilities)
        bin_str = format(idx_max, f'0{nb_qubits}b')
        bit_interet = bin_str[i]
        bits_mesures.append(bit_interet)

    return bases_bob, bits_mesures

#c, _, _ = alice_preparation()
c = QCircuit(3)
bases, bits = bob_measurement(c)
print(bases)
print(bits)
#print("Bases de Bob :", bases)
#print("Bits mesurés :", bits)


if __name__ == "__main__":
    main()
