import pytest
import json
import os
from unittest.mock import MagicMock, patch
from src.agent import save_order_to_file

def test_save_order_to_file():
    order = {
        "drinkType": "Coffee",
        "size": "Medium",
        "milk": "Whole",
        "extras": [],
        "name": "Test User"
    }
    
    with patch("builtins.open", new_callable=MagicMock) as mock_file:
        with patch("os.makedirs") as mock_makedirs:
            save_order_to_file(order)
            
            mock_makedirs.assert_called_with("backend/src", exist_ok=True)
            mock_file.assert_called_with("backend/src/orders.json", "a")
            
            # Verify that json.dump was called (it writes to the file object)
            # We can check if write was called on the file handle
            handle = mock_file.return_value
            # json.dump writes chunks, so we might see multiple write calls
            # But we definitely expect the newline
            handle.write.assert_any_call("\n")
