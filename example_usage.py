"""Example usage of tensym architecture.

This demonstrates the complete pipeline:
1. Compile-time: symbol table with slot allocation
2. Instruction generation with slot-based addressing  
3. VM execution with pluggable backends
"""
from tensym.ai_interpreter.symbol_table import SymbolTable, TensorType, TensorVariance
from tensym.ai_vm.bytecode import Instr, Op, ExecHint
from tensym.ai_vm.executor import Executor
from tensym.ai_vm.backend import SymPyBackend
from tensym.ai_vm.values import TensorValue


def example_einstein_sum():
    """Example: W_a = T_{ab} V^b (Einstein summation)"""
    
    # 1. COMPILE TIME: Set up symbol table and allocate slots
    symbols = SymbolTable()
    
    # Define tensors with types and get slot assignments
    T_type = TensorType(rank=2, indices=[("a", TensorVariance.COVARIANT), 
                                        ("b", TensorVariance.COVARIANT)])
    V_type = TensorType(rank=1, indices=[("b", TensorVariance.CONTRAVARIANT)])
    W_type = TensorType(rank=1, indices=[("a", TensorVariance.COVARIANT)])
    
    T_sym = symbols.define("T", T_type)  # Gets slot 0
    V_sym = symbols.define("V", V_type)  # Gets slot 1  
    W_sym = symbols.define("W", W_type)  # Gets slot 2
    
    print(f"Symbol slots: T={T_sym.slot_id}, V={V_sym.slot_id}, W={W_sym.slot_id}")
    
    # 2. INSTRUCTION GENERATION: Emit slot-based bytecode
    # This would normally be done by ir_builder.py after lowering HIR
    code = [
        # Load T and V tensors
        Instr(Op.LOAD_GLOBAL, args=(T_sym.slot_id,)),
        Instr(Op.LOAD_GLOBAL, args=(V_sym.slot_id,)),
        
        # Contract over index 'b' with parallelism hint
        Instr(Op.CONTRACT, args=([(("b", "b"))],), 
              hint=ExecHint(parallel=True, max_workers=4)),
        
        # Store result in W
        Instr(Op.STORE_GLOBAL, args=(W_sym.slot_id,)),
        
        # Return the result
        Instr(Op.LOAD_GLOBAL, args=(W_sym.slot_id,)),
        Instr(Op.RETURN),
    ]
    
    # 3. VM EXECUTION: Run with SymPy backend
    backend = SymPyBackend()
    constants = []  # No constants in this example
    executor = Executor(backend, constants)
    
    # Initialize global slots with tensor values
    T_data = TensorValue(value="T_symbolic", indices=[("a", -1), ("b", -1)])
    V_data = TensorValue(value="V_symbolic", indices=[("b", 1)])
    
    executor.memory.store_global(T_sym.slot_id, T_data)
    executor.memory.store_global(V_sym.slot_id, V_data)
    
    # Execute the code
    result = executor.run(code)
    
    print(f"Result: {result}")
    print(f"Result indices: {result.indices}")
    
    return result


def example_backend_swapping():
    """Demonstrate swapping backends for the same computation."""
    
    # Same computation, different backends
    backends = {
        "SymPy": SymPyBackend(),
        # "NumPy": NumPyBackend(),      # Would implement for numeric
        # "Mathematica": MathematicaBackend(),  # Would implement for Mathematica
    }
    
    # Simple tensor product: A ⊗ B  
    symbols = SymbolTable()
    A_sym = symbols.define("A", TensorType(rank=1, indices=[("i", TensorVariance.COVARIANT)]))
    B_sym = symbols.define("B", TensorType(rank=1, indices=[("j", TensorVariance.COVARIANT)]))
    
    code = [
        Instr(Op.LOAD_GLOBAL, args=(A_sym.slot_id,)),
        Instr(Op.LOAD_GLOBAL, args=(B_sym.slot_id,)),
        Instr(Op.TENSOR_PRODUCT, args=(2,)),  # 2 tensors
        Instr(Op.RETURN),
    ]
    
    A_data = TensorValue(value="A_data", indices=[("i", -1)])
    B_data = TensorValue(value="B_data", indices=[("j", -1)])
    
    for name, backend in backends.items():
        print(f"\n--- Using {name} backend ---")
        executor = Executor(backend, constants=[])
        executor.memory.store_global(A_sym.slot_id, A_data)
        executor.memory.store_global(B_sym.slot_id, B_data)
        
        result = executor.run(code)
        print(f"Result: {result}")


if __name__ == "__main__":
    print("=== Tensym Architecture Example ===\n")
    
    print("1. Einstein summation example:")
    example_einstein_sum()
    
    print("\n2. Backend swapping example:")
    example_backend_swapping()
    
    print("\nArchitecture summary:")
    print("✓ Compile-time symbol table with slot allocation")
    print("✓ Slot-based VM instructions (no string lookups at runtime)")
    print("✓ Pluggable backends for different engines")
    print("✓ Parallelism hints for heavy tensor operations")
    print("✓ Clean separation of concerns")
