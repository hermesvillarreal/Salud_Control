
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Hash from the dump for user 'Hermes'
# Assuming we don't know the password, but we can test if it even works with a test hash
test_password = "password123" # I don't know the actual password
test_hash = pwd_context.hash(test_password)

print(f"Test Password: {test_password}")
print(f"Generated Hash: {test_hash}")
print(f"Verification result: {verify_password(test_password, test_hash)}")

# Hash from dump
dump_hash = "$2b$12$YHxLI4aH2Om3fR.VRxk1.Oe00bcifgAJM5hkcnsQDYWhHF3gHKnSm"
print(f"Dump Hash length: {len(dump_hash)}")
# We can't verify 'Hermes' without the original password, but we can verify if the context accepts the hash format.
try:
    # This won't work without the right password, but it shouldn't raise an error about format
    verify_password("any", dump_hash)
    print("Dump hash format is valid for bcrypt scheme.")
except Exception as e:
    print(f"Error validating dump hash format: {e}")
