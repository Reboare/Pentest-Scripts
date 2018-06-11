FROM ubuntu

RUN apt update
RUN apt install git -y
RUN apt install tmux -y
RUN apt install openvpn -y
RUN apt install sudo -y
RUN apt install neovim -y
RUN apt install inetutils-ping -y
RUN apt install netcat -y
RUN apt install socat -y
RUN apt install nmap -y
RUN apt install ssh -y
RUN apt install socat -y
RUN apt install wget -y
RUN apt install cherrytree -y


COPY Booj.ovpn /root/Booj.ovpn
RUN mkdir /root/.ssh/
COPY config/id_rsa.pub /root/.ssh/authorized_keys

COPY config/tmux.conf /etc/tmux.conf

RUN git clone https://github.com/pwndbg/pwndbg
RUN cd pwndbg && ./setup.sh
RUN pip install pwntools
RUN sudo pip install capstone==3.0.5rc2

ENV HOME /root
