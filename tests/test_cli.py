from unittest.mock import patch

import cli

ITEM = {"id": 1, "name": "Nutella", "brand": "Ferrero", "price": 5.99,
        "stock": 40, "barcode": "301", "ingredients": "sugar"}


@patch("cli.call", return_value=(200, [ITEM]))
def test_list(mock_call, capsys):
    assert cli.main(["list"]) == 0
    assert "Nutella" in capsys.readouterr().out


@patch("cli.call", return_value=(200, []))
def test_list_empty(mock_call, capsys):
    cli.main(["list"])
    assert "empty" in capsys.readouterr().out


@patch("cli.call", return_value=(200, ITEM))
def test_view(mock_call, capsys):
    assert cli.main(["view", "1"]) == 0
    assert "Ingredients" in capsys.readouterr().out


@patch("cli.call", return_value=(404, {"error": "Item not found"}))
def test_view_not_found(mock_call, capsys):
    assert cli.main(["view", "99"]) == 1
    assert "Item not found" in capsys.readouterr().out


@patch("cli.call", return_value=(201, ITEM))
def test_add(mock_call):
    assert cli.main(["add", "Nutella", "--price", "5.99", "--stock", "40"]) == 0
    method, path = mock_call.call_args[0]
    assert (method, path) == ("POST", "/inventory")
    assert mock_call.call_args[1]["json"]["price"] == 5.99


@patch("cli.call", return_value=(200, ITEM))
def test_update(mock_call):
    assert cli.main(["update", "1", "--stock", "3"]) == 0
    assert mock_call.call_args[1]["json"] == {"stock": 3}


def test_update_needs_a_field(capsys):
    assert cli.main(["update", "1"]) == 1


@patch("cli.call", return_value=(200, {"message": "Item 1 deleted"}))
def test_delete(mock_call, capsys):
    assert cli.main(["delete", "1"]) == 0
    assert "deleted" in capsys.readouterr().out


@patch("cli.call", return_value=(200, {"name": "X", "brand": "", "barcode": "1"}))
def test_find_barcode(mock_call, capsys):
    assert cli.main(["find", "--barcode", "1"]) == 0
    assert mock_call.call_args[0][1] == "/lookup/barcode/1"


@patch("cli.call", return_value=(200, []))
def test_find_name_no_results(mock_call, capsys):
    cli.main(["find", "--name", "zzz"])
    assert "No products" in capsys.readouterr().out


@patch("cli.call", return_value=(201, ITEM))
def test_import(mock_call):
    assert cli.main(["import", "301", "--price", "2", "--stock", "5"]) == 0


@patch("cli.call", return_value=(502, {"error": "OpenFoodFacts request failed"}))
def test_import_api_failure(mock_call, capsys):
    assert cli.main(["import", "301"]) == 1
    assert "failed" in capsys.readouterr().out


@patch("cli.call", side_effect=ConnectionError("Cannot reach the API"))
def test_server_down(mock_call, capsys):
    assert cli.main(["list"]) == 2
    assert "Cannot reach" in capsys.readouterr().out
