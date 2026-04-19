# probes — Adversarial Probe Library

Owned by Intelligence Officers. Used to validate KB documents and
test agent robustness before merges to main.

## Tools

### `injection_tester.py`
Tests a KB document for prompt injection vulnerabilities.

```bash
python probes/injection_tester.py --doc kb/domain/my_document.md
python probes/injection_tester.py --doc kb/domain/my_document.md --output probes/results/doc_injection_test.json
```

Exit code 0 = PASS, 1 = FAIL.

Every new KB document must show a PASS before merging (see `kb/CHANGELOG.md`).

## Adding New Probes

Add probe scripts to this directory. Each script should:
1. Accept `--doc` or `--question` as input
2. Return a JSON result with `status: PASS | FAIL`
3. Exit with code 0 (PASS) or 1 (FAIL)
