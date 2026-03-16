import hashlib
import base64
import itertools
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from multiprocessing import Pool, cpu_count

# 1. Teks Cipher asli dari puzzle.html
msg = "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"

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
