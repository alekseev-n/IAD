"""Backward-compatible entrypoint; uses the single tested island GA core."""
try:
    from .lab1_test import main, run_ga_with_migraions, matrices
except ImportError:
    from lab1_test import main, run_ga_with_migraions, matrices

if __name__ == '__main__':
    main()
