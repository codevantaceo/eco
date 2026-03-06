"""Numerical calculus - integration and differentiation."""
from __future__ import annotations
from typing import Any, Callable
import numpy as np
import ast


def _get_safe_math_namespace() -> dict[str, Any]:
    """Return a namespace of safe mathematical functions and constants."""
    return {
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "log": np.log,
        "sqrt": np.sqrt,
        "pi": np.pi,
        "e": np.e,
        "abs": np.abs,
        "sinh": np.sinh,
        "cosh": np.cosh,
        "tanh": np.tanh,
        "arcsin": np.arcsin,
        "arccos": np.arccos,
        "arctan": np.arctan,
    }


def _validate_math_expr(node: ast.AST, allowed_names: set[str]) -> None:
    """Validate that the AST contains only safe nodes and names."""
    if isinstance(node, ast.Expression):
        _validate_math_expr(node.body, allowed_names)
    elif isinstance(node, ast.BinOp):
        if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)):
            raise ValueError(f"Unsupported binary operator: {ast.dump(node.op)}")
        _validate_math_expr(node.left, allowed_names)
        _validate_math_expr(node.right, allowed_names)
    elif isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, (ast.UAdd, ast.USub)):
            raise ValueError(f"Unsupported unary operator: {ast.dump(node.op)}")
        _validate_math_expr(node.operand, allowed_names)
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are allowed")
        func_name = node.func.id
        if func_name not in allowed_names:
            raise ValueError(f"Use of function '{func_name}' is not allowed")
        for arg in node.args:
            _validate_math_expr(arg, allowed_names)
        if node.keywords:
            raise ValueError("Keyword arguments are not allowed")
    elif isinstance(node, ast.Name):
        if node.id not in allowed_names:
            raise ValueError(f"Use of name '{node.id}' is not allowed")
    elif isinstance(node, ast.Constant):  # Python 3.8+
        if not isinstance(node.value, (int, float)):
            raise ValueError("Only numeric constants are allowed")
    elif isinstance(node, ast.Num):  # type: ignore[attr-defined]  # for older Python versions
        if not isinstance(node.n, (int, float)):
            raise ValueError("Only numeric constants are allowed")
    else:
        raise ValueError(f"Unsupported expression element: {ast.dump(node)}")


def _eval_math_expr(node: ast.AST, names: dict[str, Any]) -> float:
    """Evaluate a previously validated math expression AST."""
    if isinstance(node, ast.Expression):
        return float(_eval_math_expr(node.body, names))
    if isinstance(node, ast.BinOp):
        left = _eval_math_expr(node.left, names)
        right = _eval_math_expr(node.right, names)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        if isinstance(node.op, ast.Mod):
            return left % right
        raise ValueError("Unsupported binary operator")  # Should not happen after validation
    if isinstance(node, ast.UnaryOp):
        operand = _eval_math_expr(node.operand, names)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unsupported unary operator")  # Should not happen after validation
    if isinstance(node, ast.Call):
        func_name = node.func.id  # type: ignore[assignment]
        func = names.get(func_name)
        if func is None:
            raise ValueError(f"Function '{func_name}' is not available")
        args = [_eval_math_expr(arg, names) for arg in node.args]
        return float(func(*args))
    if isinstance(node, ast.Name):
        if node.id not in names:
            raise ValueError(f"Name '{node.id}' is not defined")
        value = names[node.id]
        if isinstance(value, (int, float)):
            return float(value)
        return float(value)  # e.g., numpy scalar or constant
    if isinstance(node, ast.Constant):  # Python 3.8+
        if not isinstance(node.value, (int, float)):
            raise ValueError("Only numeric constants are allowed")
        return float(node.value)
    if isinstance(node, ast.Num):  # type: ignore[attr-defined]
        if not isinstance(node.n, (int, float)):
            raise ValueError("Only numeric constants are allowed")
        return float(node.n)
    raise ValueError("Unsupported expression element during evaluation")


def _compile_safe_function(expr: str) -> Callable[[float], float]:
    """Compile a user-provided math expression into a safe callable f(x)."""
    try:
        parsed = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid function expression: {e}") from e

    safe_ns = _get_safe_math_namespace()
    allowed_names: set[str] = set(safe_ns.keys()) | {"x"}

    _validate_math_expr(parsed, allowed_names)

    def _f(x: float) -> float:
        names = dict(safe_ns)
        names["x"] = x
        return float(_eval_math_expr(parsed, names))

    return _f


class NumericalCalculus:
    def integrate(self, function: str, lower_bound: float, upper_bound: float, method: str) -> dict[str, Any]:
        from scipy import integrate as sci_integrate
        import math

        # Compile the user-provided function string into a safe callable f(x)
        f = _compile_safe_function(function)

        try:
            if method == "quad":
                result, error = sci_integrate.quad(f, lower_bound, upper_bound)
            elif method == "trapezoid":
                x = np.linspace(lower_bound, upper_bound, 1000)
                y = np.array([f(xi) for xi in x])
                result = float(np.trapz(y, x))
                error = abs(result - sci_integrate.quad(f, lower_bound, upper_bound)[0])
            elif method == "simpson":
                from scipy.integrate import simpson
                x = np.linspace(lower_bound, upper_bound, 1001)
                y = np.array([f(xi) for xi in x])
                result = float(simpson(y, x=x))
                error = abs(result - sci_integrate.quad(f, lower_bound, upper_bound)[0])
            elif method == "romberg":
                result = float(sci_integrate.romberg(f, lower_bound, upper_bound))
                error = abs(result - sci_integrate.quad(f, lower_bound, upper_bound)[0])
            else:
                return {"error": f"Unknown method: {method}"}

            return {
                "function": function,
                "bounds": [lower_bound, upper_bound],
                "method": method,
                "result": round(result, 10),
                "estimated_error": round(float(error), 12),
            }
        except Exception as e:
            return {"error": str(e)}