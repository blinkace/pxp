from .values import ParameterReference
from .column import FactColumn, CommentColumn

class TableTemplate:

    def __init__(self, name, columns, properties, rowIdColumn):
        self.name = name
        self.columns = columns
        self.properties = properties
        for c in self.columns.values():
            c.template = self
        self.report = None
        self.rowIdColumn = rowIdColumn


    @property
    def nonCommentColumns(self):
        return [ c for c in self.columns.values() if not isinstance(c, CommentColumn) ]
                    




