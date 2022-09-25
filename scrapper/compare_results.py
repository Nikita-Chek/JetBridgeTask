# In order to compare breakdowns in different periods, you can compare each point to each point.
# n^2

# But it is better to sort the two arrays, and go through them (taking into account that some points may have no similar ones in the other array).
# Sorting n log(n) + while loop n = n log(n)

def compare_results_by_broken_index(new_data: list | tuple,
                                    old_data: list | tuple) -> tuple[tuple]:
    """
    Compare two lists of dictionaries by the index of the broken ice cream
    machine. Results should be sorted by coordinates.

    Args:
        new_data (list | tuple): Sorted by coordinates list of new results
        old_data (list | tuple): Sorted by coordinates list of old results

    Returns:
        tuple[tuple]: (
            mcdonalds with fixed ice cream machines,
            mcdonalds with broken ice cream machines
            )
    """
    old_len, new_len = len(old_data), len(new_data)
    i, j = 0, 0
    started_working, stoped_working = [], []
    while (i < new_len) and (j < old_len):
        if new_data[i]['coordinates'] == old_data[j]['coordinates']:
            if new_data[i]['is_broken'] and (not old_data[j]['is_broken']):
                stoped_working.append(new_data[i])
            if (not new_data[i]['is_broken']) and old_data[j]['is_broken']:
                started_working.append(new_data[i])
            i += 1
            j += 1
        elif new_data[i]['coordinates'] > old_data[j]['coordinates']:
            j += 1
        else:
            i += 1
    return tuple(started_working), tuple(stoped_working)
