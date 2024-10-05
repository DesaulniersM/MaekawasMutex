import math

# make_new_quorum makes a new quorum given coordinates and an i,j pair.
def _make_new_quorum(i, j, quorum_square):
    side_length = len(quorum_square)

    new_quorum = []

    # take col i
    new_quorum.append(quorum_square[i][:])
    # Take row j
    new_quorum.append([row[j] for row in quorum_square])

    # Remove duplicate entries and flatten. sweet, sweet stack exchange helping me by pythonic
    new_quorum = [item for row in new_quorum for item in row]
    new_quorum = list(set(new_quorum))
    return new_quorum


# Generates a list of complete quorums. The outputs are integers and can be used to create id's for threads or could be appended to subnets for multicast groups
def generate_quorums(num_of_processes):
    # Calculatre the side length of a square that is /sqrt(num_of_processes) wide
    side_length = math.ceil(math.sqrt(num_of_processes))

    # Create square with lists
    integer_list = [i for i in range(side_length ** 2)]
    quorum_square = [[0] * side_length for i in range(side_length)]

    # reshape quorum list to square
    for i in range(side_length):
        quorum_square[i] = integer_list[
            i * side_length : (i * side_length) + (side_length)
        ]

    # Now that we have the quorum square, we create the subset quorums by selecting the row and column of each i,j pair that maps
    # to an individual process

    quorum_list = []

    for i in range(side_length):
        for j in range(side_length):
            quorum_list.append(_make_new_quorum(i, j, quorum_square))

    # now just remove dummies
    i = 0
    for quorum in quorum_list:
        quorum = [member for member in quorum if member < num_of_processes]
        quorum_list[i] = quorum
        i += 1
    # And remove the sets associated with the dummies
    quorum_list = quorum_list[:num_of_processes]

    return quorum_list

if __name__ == "__main__":
    import pprint

    print("hello")
    print(generate_quorums(13))

    subset_dict = {}
    subset_quorum_list = generate_quorums(13)

    for i in range(len(subset_quorum_list)):
        subset_quorum_list[i].remove(i)
        subset_dict[i] = subset_quorum_list[i]

    
    

