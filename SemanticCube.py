from State import Tipo 
class SemanticCube:
    def __init__(self):
        self.cube = {
            Tipo.INT: {
                "+": {Tipo.INT: Tipo.INT, Tipo.FLOAT: Tipo.FLOAT},
                "-": {Tipo.INT: Tipo.INT, Tipo.FLOAT: Tipo.FLOAT},
                "*": {Tipo.INT: Tipo.INT, Tipo.FLOAT: Tipo.FLOAT},
                "/": {Tipo.INT: Tipo.INT, Tipo.FLOAT: Tipo.FLOAT},
                "%": {Tipo.INT: Tipo.INT},
                ">": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "<": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                ">=": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "<=": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "==": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "!=": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "&&": None,
                "||": None
            },
            Tipo.FLOAT: {
                "+": {Tipo.INT: Tipo.FLOAT, Tipo.FLOAT: Tipo.FLOAT},
                "-": {Tipo.INT: Tipo.FLOAT, Tipo.FLOAT: Tipo.FLOAT},
                "*": {Tipo.INT: Tipo.FLOAT, Tipo.FLOAT: Tipo.FLOAT},
                "/": {Tipo.INT: Tipo.FLOAT, Tipo.FLOAT: Tipo.FLOAT},
                "%": None,
                ">": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "<": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                ">=": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "<=": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "==": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "!=": {Tipo.INT: Tipo.BOOL, Tipo.FLOAT: Tipo.BOOL},
                "&&": None,
                "||": None
            },
            Tipo.STRING: {
                "+": {Tipo.STRING : Tipo.STRING},
                ">": {Tipo.STRING : Tipo.BOOL},
                "<": {Tipo.STRING : Tipo.BOOL},
                ">=": {Tipo.STRING : Tipo.BOOL},
                "<=": {Tipo.STRING : Tipo.BOOL},
                "==": {Tipo.STRING : Tipo.BOOL},
                "!=": {Tipo.STRING : Tipo.BOOL},
                "&&": None,
                "||": None
            },
            Tipo.CHAR: {
                "+": {Tipo.CHAR : Tipo.STRING},
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
            Tipo.BOOL: {
                ">": None,
                "<": None,
                ">=": None,
                "<=": None,
                "==": {Tipo.BOOL : Tipo.BOOL},
                "!=": {Tipo.BOOL : Tipo.BOOL},
                "&&": {Tipo.BOOL : Tipo.BOOL},
                "||": {Tipo.BOOL : Tipo.BOOL},
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
            else:
                return None
        return None
