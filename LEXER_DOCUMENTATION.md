# TenSym Lexer Documentation

## Overview

The TenSym lexer is a sophisticated tokenization system designed for mathematical and tensor computation expressions. It supports Python-like indentation-based syntax, Unicode mathematical symbols, Greek letters, and complex operator sequences. The lexer is built with a focus on mathematical notation and scientific computing.

## Architecture

The lexer consists of several key components:

1. **Token Kinds** (`_kind.py`) - Defines all possible token types
2. **Token Utilities** (`utils.py`) - Core tokenization logic and indentation handling
3. **Lexer Implementation** (`_lexer.py`) - Main lexer interface
4. **Iterator Support** (`iterator.py`) - Provides iteration utilities for token processing

## Token Categories

### 1. Identifiers and Literals

| Token Kind | Description | Examples |
|------------|-------------|----------|
| `ID` | Regular identifiers | `variable`, `func_name` |
| `LATEX_ID` | LaTeX-style identifiers | `\alpha`, `\beta` |
| `TENSOR_ID` | Tensor identifiers | `T_ij`, `g^{mu nu}` |
| `FUNC_ID` | Function identifiers | `sin`, `cos`, `log` |
| `INTEGER` | Integer literals | `42`, `123` |
| `FLOAT` | Floating-point literals | `3.14`, `2.718e10` |
| `STRING` | String literals | `"hello"`, `'world'` |

### 2. Keywords and Language Constructs

#### Core Language Keywords
- `KW_LET` - Variable declaration (`let`)
- `KW_DEF` - Function definition (`def`)
- `KW_WITH` - Context management (`with`)
- `KW_CONST` - Constant declaration (`const`)
- `KW_PRINT` - Print statement (`print`)
- `KW_DECLARE` - Declaration (`declare`)
- `KW_CONSTANT` - Constant (`constant`)
- `KW_METRIC` - Metric tensor (`metric`)

#### Control Flow
- `KW_IF` - Conditional (`if`)
- `KW_THEN` - Then clause (`then`)
- `KW_ELSE` - Else clause (`else`)
- `KW_ELIF` - Else-if (`elif`)

#### Logical Operators
- `KW_NOT` - Logical not (`not`)
- `KW_AND` - Logical and (`and`)
- `KW_OR` - Logical or (`or`)

### 3. Mathematical Constants and Symbols

#### Mathematical Constants
- `KW_PI` - Pi constant (`pi`)
- `KW_E` - Euler's number (`e`)
- `KW_INFTY` - Infinity (`infty`, `oo`)
- `KW_D` - Differential (`d`)

#### Calculus and Analysis
- `KW_SUM` - Summation (`sum`, `∑`)
- `KW_PROD` - Product (`prod`, `∏`)
- `KW_INT` - Integration (`int`, `∫`)
- `KW_LIM` - Limit (`lim`)
- `KW_PARTIAL` - Partial derivative (`partial`, `∂`)
- `KW_PDV` - Partial derivative vector (`pdv`, `∇`)
- `KW_DV` - Derivative (`dv`)
- `KW_SQRT` - Square root (`sqrt`, `√`)

#### Greek Letters
- `KW_GREEK` - All Greek letters (both names and Unicode symbols)
  - Names: `alpha`, `beta`, `gamma`, `delta`, etc.
  - Symbols: `α`, `β`, `γ`, `δ`, etc.

### 4. Operators

#### Arithmetic Operators
| Token | ASCII | Unicode | Description |
|-------|-------|---------|-------------|
| `OP_PLUS` | `+` | | Addition |
| `OP_MINUS` | `-` | `−` (U+2212) | Subtraction |
| `OP_MUL` | `*` | `×`, `·`, `⋅` | Multiplication |
| `OP_DIV` | `/` | `÷` | Division |
| `OP_MOD` | `%` | | Modulo |

#### Assignment Operators
- `ASSIGNMENT` - Assignment (`:=`)
- `OP_EQUATE` - Equality assignment (`=`)
- `OP_PLUSEQUAL` - Plus assignment (`+=`)
- `OP_MINUSEQUAL` - Minus assignment (`-=`)
- `OP_MULEQUAL` - Multiply assignment (`*=`)
- `OP_DIVEQUAL` - Divide assignment (`/=`)

#### Comparison Operators
| Token | ASCII | Unicode | Description |
|-------|-------|---------|-------------|
| `OP_EQ` | `==` | | Equality |
| `OP_NE` | `!=` | `≠` | Not equal |
| `OP_LT` | `<` | | Less than |
| `OP_LE` | `<=` | `≤` | Less than or equal |
| `OP_GT` | `>` | | Greater than |
| `OP_GE` | `>=` | `≥` | Greater than or equal |

#### Bitwise and Logical Operators
- `OP_SHL` - Left shift (`<<`)
- `OP_SHR` - Right shift (`>>`)
- `OP_SHL_EQUAL` - Left shift assignment (`<<=`)
- `OP_SHR_EQUAL` - Right shift assignment (`>>=`)
- `OP_AND` - Logical AND (`&&`, `∧`)
- `OP_OR` - Logical OR (`||`, `∨`)
- `OP_BAND` - Bitwise AND (`&`)
- `OP_BOR` - Bitwise OR (`|`)
- `OP_BXOR` - Bitwise XOR (`^`)
- `OP_NOT` - Logical NOT (`!`, `¬`)
- `OP_TILDE` - Bitwise NOT (`~`)

#### Special Operators
- `OP_PRIME` - Prime notation (`'`, `′`, `″`, `‴`)
- `KW_RIGHTARROW` - Right arrow (`->`, `→`, `⇒`, `↦`)
- `KW_LEFTARROW` - Left arrow (`<-`, `←`, `⇐`)
- `KW_EQUIV` - Equivalence (`equiv`, `≡`)

### 5. Punctuation and Delimiters

#### Brackets and Parentheses
- `LBRACKET` / `RBRACKET` - Square brackets (`[`, `]`)
- `LPAREN` / `RPAREN` - Parentheses (`(`, `)`)
- `LBRACE` / `RBRACE` - Curly braces (`{`, `}`)

#### Other Punctuation
- `COLON` - Colon (`:`)
- `SEMICOLON` - Semicolon (`;`)
- `DOT` - Period (`.`)
- `UNDERSCORE` - Underscore (`_`)
- `BACKSLASH` - Backslash (`\`)
- `HASHTAG` - Hash/comment (`#`)
- `STRING_DELIM` - String delimiter (`"`)

### 6. Structural Tokens

#### Indentation and Layout
- `NEWLINE` - Line terminator
- `INDENT` - Indentation increase
- `DEDENT` - Indentation decrease

#### Special Tokens
- `EOF` - End of file
- `ERROR` - Error token

## Indentation System

The TenSym lexer uses Python-like indentation to define code blocks. The indentation system has several key features:

### Indentation Rules

1. **Tab Width**: Default tab width is 4 spaces
2. **Enforcement**: Indentation must be a multiple of 4 spaces (configurable)
3. **Mixed Tabs/Spaces**: Tabs are expanded to spaces based on tab width
4. **Consistency**: All indentation within a block must use the same method

### Indentation Behavior

#### Normal Indentation
```python
with X:
    a = 1    # INDENT token generated
    b = 2    # Same level, no token
c = 3        # DEDENT token generated
```

#### Blank Lines and Comments
Blank lines and comment-only lines **do not affect indentation**:

```python
with X:
    # This comment doesn't trigger INDENT
    
    # Neither does this one
    
    a = 1    # INDENT token generated here
```

#### Nested Indentation
```python
with X:
    with Y:      # First INDENT
        a = 1    # Second INDENT
    b = 2        # First DEDENT
c = 3            # Second DEDENT
```

#### Implicit Line Joining
Inside parentheses, brackets, or braces, newlines don't generate indentation tokens:

```python
result = function(
    arg1,        # No indentation tokens
    arg2,        # inside parentheses
    arg3
)                # Back to normal indentation rules
```

### Indenter Class

The `Indenter` class manages indentation state:

```python
@dataclass
class Indenter:
    tab_width: int = 4                    # Tab expansion width
    enforce_multiple: Optional[int] = 4   # Enforce multiple of N
    stack: List[int] = [0]               # Indentation level stack
    paren_depth: int = 0                 # Parentheses nesting depth
```

## Unicode Support

The lexer has extensive Unicode support for mathematical notation:

### Mathematical Operators
- Arithmetic: `×`, `·`, `⋅`, `÷`, `−`
- Comparison: `≤`, `≥`, `≠`, `≡`
- Logic: `∧`, `∨`, `¬`
- Arrows: `→`, `⇒`, `↦`, `←`, `⇐`

### Mathematical Symbols
- Calculus: `∂`, `∇`, `∑`, `∏`, `∫`, `√`, `∞`
- Primes: `′`, `″`, `‴`

### Greek Letters
Both spelled-out names and Unicode symbols are supported:
- Names: `alpha`, `beta`, `gamma`, `Delta`, etc.
- Symbols: `α`, `β`, `γ`, `Δ`, etc.

## Tokenization Process

### 1. Character Processing
The lexer processes input character by character, using an `Iterator` for position tracking.

### 2. Longest Match
For operators and symbols, the lexer uses a longest-match algorithm to handle multi-character operators like `>>=` correctly.

### 3. Context Awareness
The lexer maintains context for:
- Parentheses depth (for implicit line joining)
- Indentation stack (for block structure)
- Comment handling

### 4. Error Handling
- Invalid indentation raises `ValueError`
- Inconsistent dedentation raises `ValueError`
- Malformed tokens generate `ERROR` tokens

## Usage Examples

### Basic Tokenization
```python
from tensym.interpreter.token.utils import scan

# Simple expression
tokens = scan("a + b = c")
# Generates: [OP_PLUS, OP_EQUATE, NEWLINE]

# With indentation
tokens = scan("with X:\n    a = 1\n")
# Generates: [COLON, NEWLINE, INDENT, OP_EQUATE, NEWLINE, DEDENT]
```

### Mathematical Expressions
```python
# Unicode operators
tokens = scan("α ≤ β → γ")
# Generates: [KW_GREEK, OP_LE, KW_GREEK, KW_RIGHTARROW, KW_GREEK]

# Complex operators
tokens = scan("a >>= b <<= c")
# Generates: [OP_SHR_EQUAL, OP_SHL_EQUAL]
```

### Indented Blocks
```python
# Nested blocks
source = """
with X:
    with Y:
        a = 1
    b = 2
c = 3
"""
tokens = scan(source)
# Generates appropriate INDENT/DEDENT pairs
```

## Testing

The lexer includes comprehensive tests covering:

- Basic indentation scenarios
- Comment and blank line handling
- Unicode operator recognition
- Nested parentheses and implicit line joining
- Complex operator sequences
- Edge cases and error conditions

Run tests with:
```bash
python -m pytest tests/test_token_utils.py -v
```

## Configuration

### Tab Width
```python
from tensym.interpreter.token.utils import Indenter

# Custom tab width
indenter = Indenter(tab_width=8)
```

### Indentation Enforcement
```python
# Require indentation to be multiple of 2
indenter = Indenter(enforce_multiple=2)

# Disable enforcement
indenter = Indenter(enforce_multiple=None)
```

## Implementation Notes

### Performance
- Uses prefix trees for efficient operator matching
- Sentinel-based iteration for robust boundary handling
- Minimal backtracking for optimal performance

### Extensibility
- Token kinds are easily extensible via the `TokenKind` enum
- Operator maps can be modified to add new operators
- Unicode support can be expanded by updating the token maps

### Compatibility
- Designed to work with Python 3.8+
- Uses modern Python features like dataclasses and type hints
- Compatible with standard testing frameworks

## Future Enhancements

Potential areas for future development:

1. **String Interpolation**: Support for embedded expressions in strings
2. **Regex Literals**: Native regular expression support
3. **Number Formats**: Scientific notation, complex numbers, fractions
4. **Custom Operators**: User-defined operator precedence and associativity
5. **Macro System**: Preprocessor-like macro expansion
6. **Source Maps**: Enhanced debugging with precise source location tracking

## Conclusion

The TenSym lexer provides a robust foundation for mathematical and scientific computing languages. Its combination of Python-like syntax, extensive Unicode support, and mathematical notation makes it well-suited for tensor computation and symbolic mathematics applications.
