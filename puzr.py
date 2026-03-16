import hashlib
import base64
import itertools
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from multiprocessing import Pool, cpu_count

# 1. Teks Cipher asli dari puzzle.html
msg = "U2FsdGVkX18fDwMiir2vqpWNLgbPWRSfUTF46w0Bd8DI5e4m2pOdUXScDSuq4Epko3EMrd5LO9qvu1Y7JQGFN+QAUHpmHKttOu/mSzXLobfSqzyuYuU0YFvHN+I1ldufP2bilXaKzW8c4w2/a1FOakMYK59C4J/xTijgo3jX3Utr2zP1gMmryz5o6uU4SghsMrhJ3trFua/e3dsLmXpWjvka/4Q0+na8OVQzZuxyb7dwcLM2SC+SVO9wye6A5gTha8uQjkUPNsKMaN+JlJ1HrUyEGOVm4dHLjE3qp79oz/JH3WzJggls5MulW2pH+zojmdQGoO8MwbCQXI+SfBvOEZOfsGsdTeKu+8H3ILUv2GuJoEjpf0d5+WBMrHHPirhQ4bDB1FsiU757kaiB/nHnULLYF+ks9tL9ZGFTxqw0Gj3d25JKeRvndkrrK"

# 2. Decode Base64
raw_data = base64.b64decode(msg)
salt = raw_data[8:16]  # Salt berada pada byte 8-16
actual_ciphertext = raw_data[16:]

# 3. Daftar Kata dari panel puzzle.html (Hanya huruf kecil karena code.toLowerCase())
panel_words = [
    ["wand","anid","sand","wind","rand","arwv","seed","bind","knot","cord","node","data","lang","curl","site","tags","name","anon","meta","arql"],
    ["hash","code","perm","sort","sale","sell","date","code","sign","view","head","main","romb","bash"],
    ["shax","sh25","sha2","sh38","sha3","s256","s384","mine","asic","a384"],
    ["swap","exch","trad","fiat","when","coin","swap","sell","cash"],
    ["eire","scan","nord","oslo","port","1984","scan","maps","LOKI","view",".erl","lang"],
    ["tree","wood","root","seed","SILO","ASMT","beam","node","data","list","9788","4432","size","peer"],
    ["aust","vest","pool","pull"],
    ["dots","node","peer","mesh","dust","base","sell","swap","1000","list","desk"]
]

def evpkdf_cryptojs(password, salt, key_len, iv_len, iterations=1):
    """Simulasi OpenSSL / CryptoJS EvpKDF untuk AES-256-CBC."""
    target_len = key_len + iv_len
    derived_bytes = b""
    last_block = b""
    while len(derived_bytes) < target_len:
        h = hashlib.md5(last_block + password + salt).digest()
        for _ in range(1, iterations):
            h = hashlib.md5(h).digest()
        last_block = h
        derived_bytes += h
    return derived_bytes[:key_len], derived_bytes[key_len:target_len]

def hash_loop(text):
    """Replikasi fungsi hashloop() di puzzle.html yang melakukan MD5 10.000 kali."""
    h = text
    for _ in range(10000):
        h = hashlib.md5(h.encode('utf-8')).hexdigest()
    return h

def try_decrypt(pwd):
    """Fungsi untuk mencoba satu password."""
    # 1. Jalankan hashloop seperti di JS
    passphrase_hex = hash_loop(pwd)
    
    # 2. Derive key & IV menggunakan EvpKDF (default CryptoJS)
    key, iv = evpkdf_cryptojs(passphrase_hex.encode('utf-8'), salt, 32, 16, 1)
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        pt = cipher.decrypt(actual_ciphertext)
        pt_unpad = unpad(pt, AES.block_size)
        
        # VALIDASI KRITIKAL: Cek apakah hasil dekripsi diawali dengan format JWK yang valid
        # Arweave keyfile yang benar pasti berupa JSON dan diawali dengan {"kty"
        if pt_unpad.startswith(b'{"kty"'):
            return pt_unpad
    except:
        return None
    return None

def worker(pwd):
    res = try_decrypt(pwd)
    if res:
        return pwd, res
    return None

def main():
    # Hitung total kombinasi (Sekarang jauh lebih sedikit karena hanya huruf kecil)
    total = 1
    for g in panel_words:
        total *= len(g)
    
    num_workers = min(cpu_count(), 20)
    print(f"--- Arweave Puzzle Solver ---")
    print(f"Total Kombinasi: {total}")
    print(f"Menggunakan {num_workers} core...")

    # Generator untuk kombinasi kata
    passwords_gen = ("".join(combo) for combo in itertools.product(*panel_words))

    with Pool(processes=num_workers) as pool:
        count = 0
        for res in pool.imap_unordered(worker, passwords_gen):
            count += 1
            if count % 100 == 0:
                print(f"Progress: {count}/{total} percobaan...", end='\r')
            
            if res is not None:
                pwd, data = res
                print(f"\n\n[!!!] KUNCI VALID DITEMUKAN: {pwd}")
                print("-" * 50)
                
                # Simpan hasil ke file
                with open("arweave_keyfile_RECOVERED.json", "wb") as f:
                    f.write(data)
                
                print(f"SUCCESS: Keyfile telah disimpan ke 'arweave_keyfile_RECOVERED.json'")
                pool.terminate()
                return

    print("\n\nSelesai. Tidak ada kunci yang cocok.")

if __name__ == "__main__":
    main()
