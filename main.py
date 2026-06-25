import subprocess
import uuid
import os
import requests
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

EASY_RSA = Path("/etc/openvpn/easy-rsa")
CLIENTS  = Path("/etc/openvpn/clients")
TEMPLATE = Path("/etc/openvpn/client-template.txt")

CLIENTS.mkdir(parents=True, exist_ok=True)


def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=3).text.strip()
    except Exception:
        return "127.0.0.1"


@app.get("/get_vpn")
def get_vpn(username: str):
    PUBLIC_IP = get_public_ip()

    cn = f"{username}-{uuid.uuid4().hex[:6]}"
    os.chdir(EASY_RSA)

    subprocess.run(
        ["./easyrsa", "--batch", "build-client-full", cn, "nopass"],
        check=True,
        capture_output=True
    )

    ca   = (EASY_RSA / "pki" / "ca.crt").read_text()
    crt  = (EASY_RSA / "pki" / "issued" / f"{cn}.crt").read_text()
    key  = (EASY_RSA / "pki" / "private" / f"{cn}.key").read_text()
    ta   = Path("/etc/openvpn/server/ta.key").read_text()

    ovpn = TEMPLATE.read_text()
    ovpn = ovpn.replace("PUBLIC_IP", PUBLIC_IP)
    ovpn = ovpn.replace("CA_CERT", ca.strip())
    ovpn = ovpn.replace("CLIENT_CERT", crt.strip())
    ovpn = ovpn.replace("CLIENT_KEY", key.strip())
    ovpn = ovpn.replace("TA_KEY", ta.strip())

    out = CLIENTS / f"{cn}.ovpn"
    out.write_text(ovpn)

    return FileResponse(
        out,
        media_type="application/x-openvpn-profile",
        filename=f"{username}.ovpn"
    )