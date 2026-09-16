FROM frrouting/frr:latest
RUN apk add --no-cache openssh sudo
RUN adduser -D -s /bin/sh admin && \
    echo "admin:cisco" | chpasswd && \
    echo "admin ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN ssh-keygen -A && \
    sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN echo '#!/bin/sh' > /start.sh && \
    echo '/usr/lib/frr/docker-start &' >> /start.sh && \
    echo '/usr/sbin/sshd -D' >> /start.sh && \
    chmod +x /start.sh
EXPOSE 22
CMD ["/start.sh"]
