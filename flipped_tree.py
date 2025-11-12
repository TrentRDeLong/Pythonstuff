def make_tree(leaf, height, width):
    for x in range(height):
        print(leaf * width)
        width -= 1


make_tree("@", 20, 20)
