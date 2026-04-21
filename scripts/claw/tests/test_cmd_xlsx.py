import pytest
import json
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli

NOUN = "xlsx"

def test_xlsx_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0
    assert "Usage:" in res.output

def test_xlsx_new(runner: CliRunner, tmp_path: Path):
    pytest.importorskip("openpyxl")
    out = tmp_path / "new.xlsx"
    res = runner.invoke(cli, [NOUN, "new", str(out), "--sheet", "S1", "--sheet", "S2"])
    assert res.exit_code == 0
    assert out.exists()

def test_xlsx_read(runner: CliRunner, sample_xlsx):
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "read", str(p), "--json"])
    assert res.exit_code == 0
    assert isinstance(json.loads(res.output), list)

def test_xlsx_append(runner: CliRunner, sample_xlsx, sample_csv):
    p = sample_xlsx()
    csv_p = sample_csv()
    res = runner.invoke(cli, [NOUN, "append", str(p), "--sheet", "Data", "--data", str(csv_p), "--force"])
    assert res.exit_code == 0

def test_xlsx_style(runner: CliRunner, sample_xlsx):
    pytest.importorskip("openpyxl")
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "style", str(p), "--sheet", "Data", "--range", "A1:C1", "--bold", "--color", "FF0000", "--force"])
    assert res.exit_code == 0

def test_xlsx_format(runner: CliRunner, sample_xlsx):
    pytest.importorskip("openpyxl")
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "format", str(p), "--sheet", "Data", "--range", "B2:B4", "--number-format", "0.00", "--force"])      
    assert res.exit_code == 0

def test_xlsx_sql(runner: CliRunner, sample_xlsx):
    p = sample_xlsx()
    # QUERY is a positional argument after SRC
    res = runner.invoke(cli, [NOUN, "sql", str(p), "SELECT sum(b) as total FROM Data", "--json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert "total" in data[0]

def test_xlsx_to_csv(runner: CliRunner, sample_xlsx):
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "to-csv", str(p), "--sheet", "Data"])
    assert res.exit_code == 0
    assert "a,b,c" in res.output

def test_xlsx_chart(runner: CliRunner, sample_xlsx):
    pytest.importorskip("openpyxl")
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "chart", str(p), "--sheet", "Data", "--type", "bar", "--data", "B2:B4", "--force"])
    assert res.exit_code == 0

def test_xlsx_conditional(runner: CliRunner, sample_xlsx):
    pytest.importorskip("openpyxl")
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "conditional", str(p), "--sheet", "Data", "--range", "A2:C4", "--cell-is", "greaterThan:5", "--fill", "#00FF00", "--force"])
    assert res.exit_code == 0

def test_xlsx_meta(runner: CliRunner, sample_xlsx):
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "meta", "get", str(p), "--json"])
    assert res.exit_code == 0
    assert "creator" in json.loads(res.output)

def test_xlsx_stat(runner: CliRunner, sample_xlsx):
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "stat", str(p), "--sheet", "Data"])
    assert res.exit_code == 0
    assert "mean" in res.output.lower()

def test_xlsx_freeze(runner: CliRunner, sample_xlsx):
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "freeze", str(p), "--sheet", "Data", "--rows", "1", "--force"])
    assert res.exit_code == 0

def test_xlsx_filter(runner: CliRunner, sample_xlsx):
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "filter", str(p), "--sheet", "Data", "--range", "A1:C4", "--force"])
    assert res.exit_code == 0

def test_xlsx_table(runner: CliRunner, sample_xlsx):
    pytest.importorskip("openpyxl")
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "table", str(p), "--sheet", "Data", "--range", "A1:C4", "--name", "MyTable", "--force"])
    assert res.exit_code == 0

def test_xlsx_name(runner: CliRunner, sample_xlsx):
    pytest.importorskip("openpyxl")
    p = sample_xlsx()
    res = runner.invoke(cli, [NOUN, "name", "add", str(p), "--name", "TestName", "--refers-to", "=Data!$A$1:$A$3", "--force"])
    assert res.exit_code == 0
