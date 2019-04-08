# -*- coding: utf-8 -*-
"""
Create a cert with pyOpenSSL for tests.

Heavily based on python-opsi's OPSI.Util.Task.Certificate.
Source: https://github.com/opsi-org/python-opsi/blob/stable/OPSI/Util/Task/Certificate.py
"""
import argparse
import os
import random
import socket
from tempfile import NamedTemporaryFile

from OpenSSL import crypto

try:
	import secrets
except ImportError:
	secrets = None


def createCertificate(path):
	"""
	Creates a certificate.
	"""
	cert = crypto.X509()
	cert.get_subject().C = "DE"  # Country
	cert.get_subject().ST = "HE"  # State
	cert.get_subject().L = "Wiesbaden"  # Locality
	cert.get_subject().O = "pytest-tornado"  # Organisation
	cert.get_subject().OU = "Testing Department"  # organisational unit
	cert.get_subject().CN = socket.getfqdn()  # common name

	# As described in RFC5280 this value is required and must be a
	# positive and unique integer.
	# Source: http://tools.ietf.org/html/rfc5280#page-19
	cert.set_serial_number(random.randint(0, pow(2, 16)))

	cert.gmtime_adj_notBefore(0)
	cert.gmtime_adj_notAfter(60 * 60)  # Valid 1 hour

	k = crypto.PKey()
	k.generate_key(crypto.TYPE_RSA, 2048)

	cert.set_issuer(cert.get_subject())
	cert.set_pubkey(k)
	cert.set_version(2)

	cert.sign(k, 'sha512')

	certcontext = b"".join(
		(
			crypto.dump_certificate(crypto.FILETYPE_PEM, cert),
			crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
		)
	)

	with open(path, "wt") as certfile:
		certfile.write(certcontext.decode())

	try:
		with NamedTemporaryFile(mode="wb", delete=False) as randfile:
			randfile.write(randomBytes(512))

			command = u"openssl dhparam -rand {tempfile} 512 >> {target}".format(
				tempfile=randfile.name, target=path
			)
		os.system(command)
	finally:
		os.remove(randfile.name)


def randomBytes(length):
	"""
	Return _length_ random bytes.

	:rtype: bytes
	"""
	if secrets:
		return secrets.token_bytes(512)
	else:
		return os.urandom(512)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Create certificate for testing')
	parser.add_argument('--cert', dest='cert', default="testcert.pem",
	                    help='Name of the certificate')

	args = parser.parse_args()
	createCertificate(args.cert)
