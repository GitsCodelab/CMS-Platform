FROM wso2/wso2am:4.3.0

# Download and add PostgreSQL JDBC driver
RUN cd /home/wso2carbon/wso2am-4.3.0/lib && \
    curl -L -o postgresql-42.5.0.jar https://jdbc.postgresql.org/download/postgresql-42.5.0.jar && \
    chmod 644 postgresql-42.5.0.jar

# Copy deployment configuration
COPY ./deployment.toml /home/wso2carbon/wso2am-4.3.0/repository/conf/deployment.toml

# Expose ports
EXPOSE 8280 8243 9443 9611

CMD ["/home/wso2carbon/wso2am-4.3.0/bin/api-manager.sh"]
