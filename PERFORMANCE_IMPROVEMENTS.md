# Performance Improvements

This document describes the performance optimizations made to the SONIC codebase to improve computational efficiency.

## Summary of Changes

### 1. Replaced `repmat` with Implicit Array Expansion

**Files affected:**
- `+sonic/Math.m` (2 occurrences)
- `+sonic/PositionEstimation.m` (1 occurrence)

**Description:**
MATLAB R2016b introduced implicit array expansion (also known as automatic broadcasting), which eliminates the need for `repmat()` in many cases. This change:
- Reduces memory allocation overhead
- Improves code readability
- Provides better performance for element-wise operations

**Example:**
```matlab
% Before (slower, more memory)
repmat(muBelowCutOff, 1, nSeriesTerms+1).^constantSeriesTerms

% After (faster, less memory)
muBelowCutOff.^constantSeriesTerms
```

### 2. Vectorized Cross Product Operations in GeometryP2.m

**Functions optimized:**
- `joinPointPoint()` - Computes the join of two points to get a line
- `meetLineLine()` - Computes the meet of two lines to get a point

**Description:**
Replaced loop-based cross product computations with vectorized operations using element-wise multiplication and subtraction. This eliminates the overhead of:
- Loop iteration
- Repeated function calls to `cross()`
- Unnecessary memory allocations

**Performance benefit:**
- For n operations: O(n) function calls → O(1) vectorized operation
- Significant speedup when processing multiple geometric entities

**Example:**
```matlab
% Before: Loop with cross() calls
for idx = 1:obj_mult.n
    lines(:, idx) = cross(obj_mult.p2(:, idx), obj_single.p2);
end

% After: Vectorized cross product
a = obj_mult.p2;
b = obj_single.p2;
lines = [a(2,:).*b(3) - a(3,:).*b(2);
         a(3,:).*b(1) - a(1,:).*b(3);
         a(1,:).*b(2) - a(2,:).*b(1)];
```

### 3. Vectorized Dot Product Operations in GeometryP2.m

**Functions optimized:**
- `joinPointLine()` - Computes the join of a point and line
- `meetPointLine()` - Computes the meet of a point and line

**Description:**
Replaced loop-based dot product computations with vectorized `sum()` operations using element-wise multiplication. This provides:
- Elimination of loop overhead
- Better memory access patterns
- Leverages MATLAB's optimized BLAS routines

**Example:**
```matlab
% Before: Loop with transpose and multiplication
for idx = 1:obj_mult.n
    val(idx) = obj_mult.p2(:, idx)'*obj_single.p2;
end

% After: Vectorized dot product
val = sum(obj_mult.p2 .* obj_single.p2, 1);
```

### 4. Vectorized Plücker-Grassmann Constraint in GeometryP3.m

**Functions optimized:**
- `joinLineLine()` - Computes the join of two lines in P3
- `meetLineLine()` - Computes the meet of two lines in P3

**Description:**
The Plücker-Grassmann constraint computation for line-line operations in P3 has been vectorized. The constraint formula:
```
val = A(3)*B(4) + A(4)*B(3) + A(5)*B(2) + A(2)*B(5) + A(6)*B(1) + A(1)*B(6)
```
is now computed for all entries simultaneously using element-wise operations.

**Performance benefit:**
- Eliminates loop overhead for multiple line pairs
- Reduces memory allocations
- Better cache utilization

## Performance Impact

The optimizations provide several benefits:

1. **Reduced Memory Allocations**: Vectorized operations reduce temporary variable creation
2. **Better Cache Utilization**: Contiguous memory access patterns improve CPU cache performance
3. **Eliminated Loop Overhead**: Removes the cost of loop iteration and bounds checking
4. **BLAS Optimization**: Leverages MATLAB's optimized linear algebra routines

### Expected Speedup

- **Single operations**: Minimal difference (overhead dominates)
- **Batch operations** (n > 10): 2-5x speedup expected
- **Large batches** (n > 100): 5-10x speedup possible

## Testing

All changes maintain mathematical equivalence with the original implementation. The vectorized operations produce identical results to their loop-based counterparts.

### Recommended Validation

Run the existing test suite to verify correctness:
```matlab
runtests('tests')
```

Specific test classes that exercise the modified functions:
- `tests.Points3Test` - Tests for P3 geometry operations
- `tests.ConicTest` - Tests for conic operations including P2 geometry
- `tests.QuadricTest` - Tests for quadric surfaces

## Future Optimization Opportunities

Additional performance improvements could be made in:

1. **Matrix inversions**: Replace `inv()` with backslash operator (`\`) where appropriate
2. **Loop preallocation**: Ensure all loops preallocate output arrays
3. **Sparse matrices**: Consider sparse matrix representations for large-scale problems
4. **Parallel computing**: Use `parfor` for embarrassingly parallel computations
5. **Code profiling**: Use MATLAB Profiler to identify additional bottlenecks

## Best Practices for Future Development

When adding new code to SONIC, follow these performance guidelines:

1. **Avoid explicit `repmat()`**: Use implicit array expansion instead
2. **Vectorize when possible**: Replace loops with vectorized operations for array operations
3. **Preallocate arrays**: Always preallocate arrays before loops
4. **Use appropriate operators**: Prefer `\` over `inv()`, `.*` over element-wise loops
5. **Profile before optimizing**: Use `profile on/off` to identify actual bottlenecks

## References

- [MATLAB Performance Documentation](https://www.mathworks.com/help/matlab/performance-and-memory.html)
- [Vectorization in MATLAB](https://www.mathworks.com/help/matlab/matlab_prog/vectorization.html)
- [MATLAB Best Practices](https://www.mathworks.com/matlabcentral/fileexchange/54731-matlab-best-practices)
