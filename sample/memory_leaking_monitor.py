from pympler import asizeof
import time

class MemoryLeakExample:
    def __init__(self):
        self.data = []

    def add_data(self):
        self.data.append([i for i in range(1000000)])

if __name__ == "__main__":
    class_variable = MemoryLeakExample()
    outer_variable = []

    while True:
        outer_variable.append([i for i in range(1000000)])
        #class_variable.add_data()

        # Accurate object-specific memory usage
        mem_usage_outer = asizeof.asizeof(outer_variable)
        print(f"Outer Data Memory Usage: {mem_usage_outer / (1024 ** 2):.2f} MB")

        mem_usage_class = asizeof.asizeof(class_variable)
        print(f"MemoryLeakExample Memory Usage: {mem_usage_class / (1024 ** 2):.2f} MB")
        time.sleep(1)

