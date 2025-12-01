import math
import sys

# -------------------------
# Stack class
# -------------------------
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

# -------------------------
# Tokenization
# -------------------------
def tokenize(expr):
    """
    Convert expression string into tokens: numbers (ints/floats), operators, parentheses.
    Handles unary minus by representing it as 'u-' token.
    """
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch in '()+-*/':
            # Detect unary minus:
            if ch == '-':
                # Unary if at start or after '(' or another operator
                prev = tokens[-1] if tokens else None
                if prev is None or prev in ('(', '+', '-', '*', '/', 'u-'):
                    tokens.append('u-')
                else:
                    tokens.append('-')
            else:
                tokens.append(ch)
            i += 1
            continue


        if ch.isdigit() or ch == '.':
            num_chars = []
            dot_count = 0
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    dot_count += 1
                    if dot_count > 1:
                        raise ValueError(f"Invalid number with multiple dots at position {i} in '{expr}'")
                num_chars.append(expr[i])
                i += 1
            num_str = ''.join(num_chars)

            if '.' in num_str:
                tokens.append(float(num_str))
            else:
                tokens.append(int(num_str))
            continue

        # Unknown character
        raise ValueError(f"Unknown character '{ch}' in expression '{expr}'")
    return tokens

# -------------------------
# Precedence & associativity
# -------------------------
operators = {
    '+': {'prec': 1, 'assoc': 'L'},
    '-': {'prec': 1, 'assoc': 'L'},
    '*': {'prec': 2, 'assoc': 'L'},
    '/': {'prec': 2, 'assoc': 'L'},
    'u-': {'prec': 3, 'assoc': 'R'},
}

# -------------------------
# Infix -> Postfix (Shunting-yard)
# -------------------------
def infix_to_postfix(tokens):
    out = []
    op_stack = Stack()

    for token in tokens:
        if isinstance(token, (int, float)):
            out.append(token)
        elif token == '(':
            op_stack.push(token)
        elif token == ')':
            # pop until '('
            while not op_stack.is_empty() and op_stack.peek() != '(':
                out.append(op_stack.pop())
            if op_stack.is_empty():
                raise ValueError("Mismatched parentheses: missing '('")
            op_stack.pop()  # remove '('
        elif token in operators:
            o1 = token
            while True:
                o2 = op_stack.peek()
                if o2 is None or o2 == '(':
                    break
                if o2 not in operators:
                    break
                p1 = operators[o1]['prec']
                p2 = operators[o2]['prec']
                if (operators[o1]['assoc'] == 'L' and p1 <= p2) or (operators[o1]['assoc'] == 'R' and p1 < p2):
                    out.append(op_stack.pop())
                else:
                    break
            op_stack.push(o1)
        else:
            raise ValueError(f"Unknown token in infix_to_postfix: {token}")

    while not op_stack.is_empty():
        top = op_stack.pop()
        if top in ('(', ')'):
            raise ValueError("Mismatched parentheses")
        out.append(top)

    return out

# -------------------------
# Postfix evaluation
# -------------------------
def apply_operator(op, a, b=None):

    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return a / b
    if op == 'u-':
        return -a

    raise ValueError(f"Unsupported operator: {op}")

def evaluate_postfix(postfix_tokens):
    stack = Stack()
    for tok in postfix_tokens:
        if isinstance(tok, (int, float)):
            stack.push(tok)
        elif tok in operators:
            if tok == 'u-':
                # unary minus: pop one operand
                val = stack.pop()
                if val is None:
                    raise ValueError("Not enough operands for unary minus")
                stack.push(apply_operator('u-', val))
            else:

                b = stack.pop()
                a = stack.pop()
                if a is None or b is None:
                    raise ValueError(f"Not enough operands for operator '{tok}'")
                stack.push(apply_operator(tok, a, b))
        else:
            raise ValueError(f"Unknown token in postfix evaluation: {tok}")

    result = stack.pop()
    if not stack.is_empty():
        raise ValueError("Malformed expression: leftover values in stack after evaluation")
    return result

# -------------------------
# Main expression evaluation
# -------------------------
def evaluate_expression(expr):

    if expr.strip() == '':
        raise ValueError("Empty expression")
    tokens = tokenize(expr)
    postfix = infix_to_postfix(tokens)
    result = evaluate_postfix(postfix)


    if isinstance(result, float) and abs(result - round(result)) < 1e-9:
        return int(round(result))
    return result


# File processing

def process_file(input_path='input.txt', output_path='output.txt', separator='-----'):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()
    except FileNotFoundError:
        print(f"Input file '{input_path}' not found.")
        sys.exit(1)

    # We'll preserve blank lines and separators. Evaluate lines that look like expressions.
    out_lines = []
    for raw in raw_lines:
        line = raw.rstrip('\n')
        stripped = line.strip()
        if stripped == '':

            out_lines.append('')
        elif stripped == separator:
            out_lines.append(separator)
        else:
            # try to evaluate; if error -> write an error message
            try:
                value = evaluate_expression(stripped)
                out_lines.append(str(value))
            except Exception as e:
                out_lines.append(f"ERROR: {type(e).__name__}: {e}")

    with open(output_path, 'w', encoding='utf-8') as f:
        for l in out_lines:
            f.write(l + '\n')

    print(f"Processed '{input_path}' -> '{output_path}'. {len(out_lines)} lines written.")


# Command-line
if __name__ == '__main__':
    input_file = 'input.txt'
    output_file = 'output.txt'
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    process_file(input_file, output_file)


