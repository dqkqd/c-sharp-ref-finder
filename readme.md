# Find modified identifiers in a function

## Installation

```bash
pip install .
```

## Test

```bash
python main.py
```

**Sample code in `main.py`**

```CSharp
using System;

namespace HelloWorld
{
  class Program
  {
    static void ModifyVariable(int x, int y) { x += 1; y += 2}
    static void ModifyVariableNested(int x) { int y = 2; ModifyVariable(x, y); }
    static void Main(string[] args)
    {
      Console.WriteLine("Hello World!");    
   }
  }
}
```

**Result**

```bash
--------------------------------------------------
Function location: ModifyVariable, line 6, column 30
Params location:
 x, line 6, column 36
 y, line 6, column 43
Modified vars location:
 x, line 6, column 48
 y, line 6, column 56
--------------------------------------------------
Function location: ModifyVariableNested, line 7, column 36
Params location:
 x, line 7, column 42
Modified vars location:
 x, line 7, column 73
```
