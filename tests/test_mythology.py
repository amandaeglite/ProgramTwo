import sys
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import mythology as m
from migrate import migrate


@pytest.fixture
def con(tmp_path):
    """A fresh, migrated database for every test."""
    db_path = str(tmp_path / "test.db")
    migrate(db_path)
    connection = m.connect(db_path)
    yield connection
    connection.close()


def test_migrations_create_table_with_category(con):
    columns = [r["name"] for r in con.execute("PRAGMA table_info(mythology_symbols)")]
    assert columns == ["id", "name", "meaning", "category"]


def test_migrate_twice_is_safe(tmp_path):
    db_path = str(tmp_path / "twice.db")
    migrate(db_path)
    migrate(db_path)
    connection = m.connect(db_path)
    applied = connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
    connection.close()
    assert applied == 2


def test_add_and_get_symbol(con):
    new_id = m.add_symbol(con, "Auseklis", "Rīta zvaigzne", "zīme")
    rows = m.get_all_symbols(con)
    assert len(rows) == 1
    assert rows[0]["id"] == new_id
    assert rows[0]["name"] == "Auseklis"


def test_empty_name_is_rejected(con):
    with pytest.raises(ValueError):
        m.add_symbol(con, "   ")


def test_get_by_category(con):
    m.add_symbol(con, "Auseklis", "Rīta zvaigzne", "zīme")
    m.add_symbol(con, "Mārtiņa krusts", "Aizsardzība", "zīme")
    m.add_symbol(con, "Jāņi", "Vasaras saulgrieži", "svētki")
    names = [r["name"] for r in m.get_by_category(con, "zīme")]
    assert names == ["Auseklis", "Mārtiņa krusts"]


def test_search_finds_by_meaning(con):
    m.add_symbol(con, "Auseklis", "Rīta zvaigzne", "zīme")
    m.add_symbol(con, "Jāņi", "Vasaras saulgrieži", "svētki")
    results = m.search_symbols(con, "zvaig")
    assert [r["name"] for r in results] == ["Auseklis"]


def test_search_no_match_returns_empty(con):
    assert m.search_symbols(con, "nothing") == []