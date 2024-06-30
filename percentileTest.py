def percentile(data, num):
    dim1 = len(data)
    dim2 = len(data[0])
    dim3 = len(data[0][0])
    num = int(num / 100 * len(data))

    listOfListOfColumns = []
    for z in range(dim3):
        listOfColumns = []
        for y in range(dim2):
            columns = []
            for x in range(dim1):
                columns.append(data[x][z][y])
            if num % 2 == 0:
                listOfColumns.append((sorted(columns)[num] + sorted(columns)[num - 1]) / 2)
            else:
                listOfColumns.append(sorted(columns)[num])
        listOfListOfColumns.append(listOfColumns)

    return listOfListOfColumns

data = [[[5, 4, 1],
         [7, 9, 8],
         [6, 3, 2]],

        [[9, 8, 7],
         [6, 2, 4],
         [3, 5, 1]],

        [[1, 2, 3],
         [5, 4, 6],
         [7, 8, 9]],
         
        [[4, 3, 2],
         [1, 6, 7],
         [5, 9, 8]]]

print(percentile(data, 50))

