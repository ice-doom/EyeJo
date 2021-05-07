mkdir /etc/nginx/certs
cd /etc/nginx/certs
# 生成私钥
openssl genrsa -out ca.key 4096
# 生成自签名证书
openssl req -new -x509 -sha256 -extensions v3_ca -key ca.key -out ca.crt -days 3650 -subj "/C=CN/ST=Shanghai/L=Shanghai/O=EyeJo/CN=EyeJo"


# 生成私钥
openssl genrsa -out eyejo.key 4096
# 生成证书请求
openssl req -new -key eyejo.key -out eyejo.csr -subj "/C=CN/ST=Shanghai/L=Shanghai/O=EyeJo/CN=EyeJo"
echo "01" > ca.srl
# 生成用户证书
openssl x509 -req -sha256 -days 3650 -in eyejo.csr -CA ca.crt -CAkey ca.key -out eyejo.crt
cp ca.crt eyejo_chain.pem

cd /root/
wget https://nmap.org/dist/nmap-7.91.tar.bz2 && \
bzip2 -cd nmap-7.91.tar.bz2 | tar xvf - && \
cd nmap-7.91 && \
./configure && \
make && \
make install && \
cd /root/ && \
wget https://github.com/vanhauser-thc/thc-hydra/archive/refs/tags/v9.2.zip && \
unzip v9.2.zip && \
cd thc-hydra-9.2/ && \
./configure && \
make && \
make install && \
rm -rf /root/thc-hydra-9.2 /root/v9.2.zip /root/nmap-7.91.tar.bz2 /root/nmap-7.91
