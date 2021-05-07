import ssl
import socket
import OpenSSL.crypto as crypto


def get_https_cert(ip, port):
    dst = (ip, int(port))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(15)
        s.connect(dst)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(s, server_hostname=dst[0])
        cert_bin = s.getpeercert(True)
        x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_bin)
        X509Name_subject = x509.get_subject()
        s.close()
        ssl_Organization = X509Name_subject.organizationName
        if ssl_Organization == None:
            ssl_Organization = ""
        return ssl_Organization
    except:
        return ""

