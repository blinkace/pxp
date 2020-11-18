class Column:

    def __init__(self, name):
        self.name = name
        pass


class FactColumn(Column):

    def __init__(self, name, columns):
        super().__init__(name)
        self.columns = columns

