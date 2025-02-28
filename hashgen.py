import hashlib

IID = "507107095328528014720505792227154443307601488798491974447846560"  
CID = "000000000000000000000000000000000000000000000000"

combined_data = IID.encode("utf-16-le") + b"\0\0" + CID.encode("utf-16-le") + b"\0\0"
hash_result = hashlib.sha256(combined_data).hexdigest()

print(f"SHA-256 hash: {hash_result}")