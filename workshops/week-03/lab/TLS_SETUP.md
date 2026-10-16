# Certificate-authenticated RMS Modbus gateway

The RMS gateway uses mutual TLS on port 5062 to authenticate individuals and
protect Modbus communication. It carries standard Modbus TCP MBAP frames inside
TLS. Use `rms_gateway_client.py`, or verify that another client's TLS framing is
compatible. This implementation does not include every feature of the standardized
Modbus Security protocol.

The gateway requires a trusted client certificate AND its exact SHA-256 certificate
fingerprint in an allowlist. Every admitted certificate gets `partner_read` only.
No credential enables gateway writes. Missing configuration prevents startup;
TLS is required for every gateway connection.

## Create the lab CA and server certificate

On the plant host as `rms`, deploy the source and public extension files into
`~/lab`. From `~/lab`, use OpenSSL to create a private lab CA and server certificate:

```bash
umask 077
mkdir -p tls
openssl req -x509 -newkey rsa:3072 -nodes -days 30 -subj "/CN=RMS Workshop CA" -keyout tls/ca.key -out tls/ca.pem -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign"
openssl req -new -newkey rsa:3072 -nodes -subj "/CN=localhost" -keyout tls/server.key -out tls/server.csr
openssl x509 -req -in tls/server.csr -CA tls/ca.pem -CAkey tls/ca.key -CAcreateserial -days 7 -sha256 -extfile gateway-server.ext -out tls/server.pem
```

Do this once for a new setup, not on each restart. Keep `ca.key` and `server.key`
private to RMS. The server certificate is for `localhost` / `127.0.0.1`, matching
the loopback client. For another hostname, deliberately update its SANs before
issuing a certificate; do not disable hostname verification.

The private keys are unencrypted for this supervised lab workflow, so account and
file permissions matter. A production deployment needs stronger key custody.
The `tls/` directory and `.key` files are ignored by Git; still inspect files before
committing. Never share a CA or server private key with an authenticated individual.

## Enroll an authenticated individual

The individual requesting access runs these commands in their own `~/lab`
directory as `sfpcm`:

```bash
umask 077
mkdir -p tls
openssl req -new -newkey rsa:3072 -nodes -subj "/CN=sfpcm-partner" -keyout tls/partner.key -out tls/partner.csr
```

They keep `partner.key` private and send ONLY `partner.csr` to you through your
agreed channel. Verify the CSR belongs to the individual you intend to enroll before
signing. Place the received CSR at `~/lab/tls/partner.csr` in your RMS account:

```bash
openssl req -in tls/partner.csr -noout -verify -subject
openssl x509 -req -in tls/partner.csr -CA tls/ca.pem -CAkey tls/ca.key -CAcreateserial -days 7 -sha256 -extfile gateway-client.ext -out tls/partner.pem
openssl x509 -in tls/partner.pem -noout -fingerprint -sha256
```

Return ONLY `partner.pem` and `ca.pem` to the individual. Confirm the CA fingerprint
through your trusted coordination channel before they trust it:

```bash
openssl x509 -in tls/ca.pem -noout -fingerprint -sha256
```

The client certificate identifies possession of its private key, not a physical
person. Give each person a separate key/certificate and maintain a fingerprint-to-
person inventory; a shared certificate loses that distinction.

## Configure and restart RMS

Add these entries to the existing RMS `~/lab/.env` without overwriting its HMI/SIEM
settings. Replace the fingerprint placeholder with the individual's certificate
SHA-256 fingerprint, removing colons and the OpenSSL label (64 hexadecimal digits):

```dotenv
RMS_GATEWAY_CERT=/home/rms/lab/tls/server.pem
RMS_GATEWAY_KEY=/home/rms/lab/tls/server.key
RMS_GATEWAY_CA=/home/rms/lab/tls/ca.pem
RMS_GATEWAY_CLIENT_SHA256=<64-hex-digit-client-certificate-fingerprint>
```

Use your actual absolute home path if it is not `/home/rms`. Multiple approved
fingerprints can be comma-separated, but include only one if only this individual
should have access. The service already reads `.env`.

```bash
chmod 600 .env tls/*.key
cp units/plant-rms-relay.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user restart plant-rms-relay
systemctl --user status plant-rms-relay
journalctl --user -u plant-rms-relay -n 20 --no-pager
```

Confirm `mutual_tls=required approved_certificates=1` in the startup log.
Restart after changing the allowlist, including revocation, so existing sessions
are closed too. TLS checks validity dates; there is no CRL/OCSP integration here.
Remove a revoked certificate fingerprint and restart. The gateway does not
automatically reload configuration or map certificates to write-capable roles.

## Authenticated access verification

Provide `rms_gateway_client.py` to the authenticated individual for use in their
own `~/lab` directory. From that directory:

```bash
python3 rms_gateway_client.py --ca tls/ca.pem --cert tls/partner.pem --key tls/partner.key
```

This only reads the threshold. For the agreed authorized write-denial test:

```bash
python3 rms_gateway_client.py --ca tls/ca.pem --cert tls/partner.pem --key tls/partner.key --test-write
```

Expected: threshold 250, write response `8601` (Illegal Function), threshold still
250. The probe stops before writing if the baseline differs. If a write is not
explicitly denied, it attempts restoration and exits with an error; a broken
connection may prevent restoration, so coordinate with the RMS owner and verify
state independently after failures. Retain timestamped client output and journal
records showing the certificate fingerprint, `role=partner_read`, and denied FC6.

For authentication evidence, separately try a TLS client without a certificate,
an untrusted certificate, and a trusted but unlisted certificate. None should
receive process data or reach the backend through the gateway. TLS 1.3 can report
server rejection on the first read rather than at the client's initial connect.
Handshake failures occur before the application handler and are not guaranteed
to produce a gateway decision record; keep client-side failure evidence too.

Finally test whether the individual can reach backend port 5061 directly. Direct
backend access remains a gateway bypass until the host administrator restricts it.
Do not claim that the whole RMS is restricted to authenticated individuals on the
strength of the gateway tests alone. No live deployment or host isolation is
performed by the local test suite.
