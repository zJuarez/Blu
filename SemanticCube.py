class SemanticCube:
    def __init__(self):
        self.cube = {
            "INT": {
                "+": {"INT": "INT", "FLOAT": "FLOAT"},
                "-": {"INT": "INT", "FLOAT": "FLOAT"},
                "*": {"INT": "INT", "FLOAT": "FLOAT"},
                "/": {"INT": "INT", "FLOAT": "FLOAT"},
                "%": {"INT": "INT"},
                ">": {"INT": "BOOL", "FLOAT": "BOOL"},
                "<": {"INT": "BOOL", "FLOAT": "BOOL"},
                ">=": {"INT": "BOOL", "FLOAT": "BOOL"},
                "<=": {"INT": "BOOL", "FLOAT": "BOOL"},
                "==": {"INT": "BOOL", "FLOAT": "BOOL"},
                "!=": {"INT": "BOOL", "FLOAT": "BOOL"},
                "&&": None,
                "||": None
            },
            "FLOAT": {
                "+": {"INT": "FLOAT", "FLOAT": "FLOAT"},
                "-": {"INT": "FLOAT", "FLOAT": "FLOAT"},
                "*": {"INT": "FLOAT", "FLOAT": "FLOAT"},
                "/": {"INT": "FLOAT", "FLOAT": "FLOAT"},
                "%": None,
                ">": {"INT": "BOOL", "FLOAT": "BOOL"},
                "<": {"INT": "BOOL", "FLOAT": "BOOL"},
                ">=": {"INT": "BOOL", "FLOAT": "BOOL"},
                "<=": {"INT": "BOOL", "FLOAT": "BOOL"},
                "==": {"INT": "BOOL", "FLOAT": "BOOL"},
                "!=": {"INT": "BOOL", "FLOAT": "BOOL"},
                "&&": None,
                "||": None
            },
            "STRING": {
                "+": {"STRING" : "STRING"},
                ">": {"STRING" : "BOOL"},
                "<": {"STRING" : "BOOL"},
                ">=": {"STRING" : "BOOL"},
                "<=": {"STRING" : "BOOL"},
                "==": {"STRING" : "BOOL"},
                "!=": {"STRING" : "BOOL"},
                "&&": None,
                "||": None
            },
            "CHAR": {
                "+": {"CHAR" : "STRING"},
                "-": None,
                "*": None,
                "/": None,
                "%": None,
                ">": None,
                "<": None,
                ">=": None,
                "<=": None,
                "==": None,
                "!=": None,
                "&&": None,
                "||": None
            },
            "BOOL": {
                ">": None,
                "<": None,
                ">=": None,
                "<=": None,
                "==": {"BOOL" : "BOOL"},
                "!=": {"BOOL" : "BOOL"},
                "&&": {"BOOL" : "BOOL"},
                "||": {"BOOL" : "BOOL"},
                "+": None,
                "-": None,
                "*": None,
                "/": None,
                "%": None
            }
        }

    def get_type(self, op1_type, operator, op2_type):
        """
        Returns the result type of the operation given by the operator between
        operands with types op1_type and op2_type. Raises an exception if the
        operation is not valid.
        """
        if op1_type in self.cube and operator in self.cube[op1_type]:
            op_row = self.cube[op1_type][operator]
            if op2_type in op_row:
                return op_row[op2_type]
            elif op_row is not None:
                return op_row
        raise Exception(f"Invalid operation: {op1_type} {operator} {op2_type}")
