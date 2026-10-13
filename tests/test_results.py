from lab1.lab1_test import main, run_ga_with_migraions
from lab1.island_ga import GAResult


def test_cli_zero_successes_does_not_divide_by_zero(capsys):
    main(['--matrix','ideal_matrice','--runs','3','--seed','1',
          '--num-islands','1','--population-size','1',
          '--mutation-probability','0','--max-iterations','1'])
    assert 'Exact success:' in capsys.readouterr().out


def test_compatibility_runner_returns_diagnostic_result():
    r = run_ga_with_migraions(5,0,2,5,3,10,10,1, [[1]], seed=5)
    assert isinstance(r, GAResult)
    assert r.best_cost == 1
    assert r.completed_generations == 3
