# oracle_patch.py
import sys
import oracledb

# Make Django think cx_Oracle is present
sys.modules["cx_Oracle"] = oracledb

# Define the missing Database.Binary type expected by Django
class _Binary(bytes):
    pass

# Inject this dummy type so isinstance() checks succeed
oracledb.Binary = _Binary
