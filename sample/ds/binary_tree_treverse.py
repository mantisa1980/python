class Node(object):
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def get_left(self):
        return self.left
    
    def get_right(self):
        return self.right

    def get_value(self):
        return self.value

    def set_left(self, node):
        self.left = node

    def set_right(self, node):
        self.right = node

class Tree(object):
    def __init__(self, root):
        self.root = root

    def run_inorder_traverse(self):
        self.__in_order(self.root)

    def run_preorder_traverse(self):
        self.__pre_order(self.root)

    def __in_order(self, node):
        if node == None:
            return
        self.__in_order(node.get_left())
        print node.get_value()
        self.__in_order(node.get_right())

    def __pre_order(self, node):
        if node == None:
            return
        print node.get_value()
        self.__pre_order(node.get_left())
        self.__pre_order(node.get_right())

    def insert(self, node):
        n = self.root
        while True: 
            if node.get_value() > n.get_value():
                if n.get_right() == None:
                    n.set_right(node)
                    break
                else:
                    n = n.get_right()
            else:
                if n.get_left() == None:
                    n.set_left(node)
                    break
                else:
                    n = n.get_left()

def run(numbers):
    print "Running sequence:{}".format(numbers)
    tree = None
    for i in numbers:
        if tree == None:
            tree = Tree(Node(i))
        else:
            tree.insert(Node(i))
    print "Traverse preorder:"
    tree.run_preorder_traverse()
    print "Traverse inorder:"
    tree.run_inorder_traverse() 

def main():
    inputs = list()
    while True:
        #numbers = raw_input("Input integers separated by ' '\n")
        numbers = "5 1 2 3 4"
        numbers = [int(i) for i in numbers.split(" ") ]
        run(numbers)
        break


if __name__ == "__main__":
    main()


